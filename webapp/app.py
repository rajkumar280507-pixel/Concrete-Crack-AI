from flask import Flask, render_template, request, redirect, Response, send_file, jsonify
import os
import sys
import cv2
import json
import uuid
import shutil
import sqlite3
import datetime
import numpy as np
import torch
from fpdf import FPDF

# Add Project Root to Path for 'src' package discovery
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Forensic Suite
from src.detect_crack import ConcreteCrackDetector

app = Flask(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'unet_crack.pth')
DB_PATH = os.path.join(BASE_DIR, 'forensic_v1.db')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize detector
detector = None
device = 'cuda' if torch.cuda.is_available() else 'cpu'
try:
    detector = ConcreteCrackDetector(model_path=MODEL_PATH, device=device)
except Exception as e:
    print(f"Warning: Could not initialize ConcreteCrackDetector. {e}")

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans_v2 (
                id TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                site_tag TEXT,
                surface_type TEXT,
                original_img TEXT,
                processed_img TEXT,
                crack_detected INTEGER,
                severity TEXT,
                hazard TEXT,
                confidence_percent FLOAT,
                length_px FLOAT,
                avg_width_px FLOAT,
                max_width_px FLOAT,
                depth_status TEXT,
                metrics_json TEXT
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"CRITICAL DB ERROR during init: {e}")

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global detector
    file = request.files.get('file')
    unit = request.form.get('unit', 'mm')
    scale_val = float(request.form.get('scale', 0.2))
    site_tag = request.form.get('site_tag', 'General Site')
    detection_mode = request.form.get('detection_mode', 'all')
    
    if file is None or file.filename == '':
        return redirect(request.url)
    
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Run Forensic Detection Pipeline
    report = {}
    if detector:
        try:
            # Execute 9-Phase Analysis with Calibration Scale & Mode
            report = detector.detect_cracks(filepath, app.config['UPLOAD_FOLDER'], 
                                           scale_mm_per_px=scale_val, 
                                           target_unit=unit,
                                           detection_mode=detection_mode)
        except Exception as e:
            print(f"PIPELINE CRITICAL FAIL: {e}")
            report = {}

    if not report:
        return "Critical Pipeline Error", 500

    # Persist Scan to Forensic Database
    scan_id = report.get('inspection_id', f"REC-{uuid.uuid4().hex[:6].upper()}")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scans_v2 (
                    id, site_tag, surface_type, original_img, processed_img, 
                    crack_detected, severity, hazard, confidence_percent, 
                    length_px, avg_width_px, max_width_px, depth_status, metrics_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scan_id, site_tag, report.get('surface_type', 'Concrete'), 
                filename, f"proc_{filename}", 
                1 if report.get('crack_detected') else 0,
                report.get('classification', {}).get('severity', 'Non-crack'),
                report.get('classification', {}).get('hazard', 'None'),
                report.get('confidence_percent', 0.0),
                report.get('measurements', {}).get('length_px', 0.0),
                report.get('measurements', {}).get('avg_width_px', 0.0),
                report.get('measurements', {}).get('max_width_px', 0.0),
                report.get('measurements', {}).get('depth_reason', 'N/A'),
                json.dumps(report, default=str)
            ))
            conn.commit()
    except Exception as db_err:
        print(f"DB SAVE ERROR: {db_err}")

    return render_template('index.html', original_img=filename, processed_img=f"proc_{filename}",
                           score=report.get('confidence_percent', 0), report=report, scan_id=scan_id)

@app.route('/get_history')
def get_history():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM scans_v2 ORDER BY timestamp DESC')
            rows = cursor.fetchall()
            history = [dict(row) for row in rows]
            return jsonify({"status": "success", "history": history})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete_scan/<scan_id>', methods=['POST'])
def delete_scan(scan_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scans_v2 WHERE id = ?", (scan_id,))
            conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download_report/<scan_id>')
def download_report(scan_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scans_v2 WHERE id = ?", (scan_id,))
            row = cursor.fetchone()
            if not row: return "Scan not found", 404
            
            report = json.loads(row['metrics_json'])
            
            # Generate Forensic PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="CONCRETE CRACK VISION AI | FORENSIC REPORT", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt=f"Inspection ID: {scan_id}", ln=True)
            pdf.cell(200, 10, txt=f"Timestamp: {row['timestamp']}", ln=True)
            pdf.ln(5)
            
            pdf.set_font("Arial", '', 11)
            pdf.cell(200, 10, txt=f"Surface Type: {row['surface_type']}", ln=True)
            pdf.cell(200, 10, txt=f"Crack Detected: {'YES' if row['crack_detected'] else 'NO'}", ln=True)
            pdf.cell(200, 10, txt=f"Severity: {row['severity']}", ln=True)
            pdf.cell(200, 10, txt=f"Hazard Level: {row['hazard']}", ln=True)
            pdf.ln(5)
            
            # Forensic Dimensions
            m = report.get('measurements', {})
            unit = m.get('unit', 'mm')
            pdf.cell(200, 10, txt=f"Length: {m.get('length_val', 0.0)} {unit}", ln=True)
            pdf.cell(200, 10, txt=f"Average Width: {m.get('avg_width_val', 0.0)} {unit}", ln=True)
            pdf.cell(200, 10, txt=f"Maximum Width: {m.get('max_width_val', 0.0)} {unit}", ln=True)
            pdf.cell(200, 10, txt=f"Estimated Depth: {m.get('depth_val', 0.0)} {unit if unit != 'px' else 'mm'}", ln=True)
            
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"report_{scan_id}.pdf")
            pdf.output(pdf_path)
            return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return f"PDF Error: {str(e)}", 500

def gen_frames():
    global detector
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success: break
        else:
            if detector:
                frame, _ = detector.analyze_frame(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', debug=True, port=port)
