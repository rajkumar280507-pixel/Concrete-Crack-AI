from flask import Flask, render_template, request, redirect, url_for, Response
import os
import sys
import cv2
import uuid
import sqlite3
import datetime
import json

# Add parent directory to path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.detect_crack import ImprovedCrackDetector

app = Flask(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'model.h5')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize detector
detector = None
try:
    detector = ImprovedCrackDetector(MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load AI model at {MODEL_PATH}. {e}")

# Database Path
DB_PATH = os.path.join(BASE_DIR, 'history.db')

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                original_img TEXT,
                processed_img TEXT,
                label TEXT,
                score REAL,
                crack_count INTEGER,
                severity TEXT,
                hazard TEXT,
                action TEXT,
                recommendation TEXT,
                metrics_json TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("INFO: History database initialized.")
    except Exception as e:
        print(f"ERROR: Database initialization failed: {e}")

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_history')
def get_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scans ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            'id': row[0],
            'timestamp': row[1],
            'original_img': row[2],
            'processed_img': row[3],
            'label': row[4],
            'score': row[5],
            'crack_count': row[6],
            'severity': row[7],
            'hazard': row[8],
            'action': row[9],
            'recommendation': row[10]
        })
    return {"history": history}

@app.route('/delete_scan/<scan_id>', methods=['POST'])
def delete_scan(scan_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM scans WHERE id = ?', (scan_id,))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/download_report/<scan_id>')
def download_report(scan_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT metrics_json FROM scans WHERE id = ?', (scan_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            import json
            data = json.loads(row[0])
            response_content = json.dumps(data, indent=4)
            return Response(
                response_content,
                mimetype="application/json",
                headers={"Content-disposition": f"attachment; filename=report_{scan_id}.json"}
            )
        return "Not Found", 404
    except Exception as e:
        return str(e), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    global detector
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Output paths
        processed_filename = f"proc_{filename}"
        processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        
        # Improved Detection Pipeline
        print(f"DEBUG: Processing image {filename}...")
        if detector:
            try:
                report = detector.analyze_image(filepath, processed_path)
                label = report.get('classification_label', 'Unknown')
                score = report.get('confidence_score', 0.0)
                count = report.get('crack_count', 0)
                print(f"DEBUG: Model analysis successful. Label: {label}, Score: {score}")
            except Exception as e:
                print(f"DEBUG: Error during detector analysis: {e}")
                detector = None # Trigger fallback

        if not detector:
            print("DEBUG: Using fallback analysis mode.")
            label, score, count = "AI Engine Offline", 0.0, 0
            report = {
                "density_percentage": 0, 
                "estimated_length_px": 0, 
                "avg_width_px": 0,
                "crack_count": 0,
                "severity_level": "N/A",
                "hazard_level": "N/A",
                "recommended_action": "Check Engine Status",
                "detailed_recommendation": "The AI analysis module failed or the model is not loaded. Please check the server logs.",
                "has_linear_structure": False
            }
            # Just copy original to processed if no detector
            import shutil
            shutil.copy(filepath, processed_path)

        # Save to History Database
        try:
            scan_id = f"INS-{filename[:8].upper()}"
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scans (id, timestamp, original_img, processed_img, label, score, crack_count, severity, hazard, action, recommendation, metrics_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scan_id,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                filename,
                processed_filename,
                label,
                float(score),
                int(count),
                report.get('severity_level', 'Unknown'),
                report.get('hazard_level', 'Unknown'),
                report.get('recommended_action', 'N/A'),
                report.get('detailed_recommendation', 'N/A'),
                json.dumps(report, default=str)
            ))
            conn.commit()
            conn.close()
            print(f"DEBUG: Saved scan {scan_id} to history.")
        except Exception as db_err:
            print(f"DEBUG: Failed to save to database: {db_err}")

        return render_template('index.html', 
                               original_img=filename,
                               processed_img=processed_filename,
                               label=label,
                               score=f"{score:.2f}",
                               count=count,
                               report=report)

from collections import deque

def gen_frames(cam_id=0):
    global detector
    camera = cv2.VideoCapture(int(cam_id))
    severity_history = deque(maxlen=10)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            if detector:
                processed_frame, results = detector.analyze_frame(frame)
                severity_history.append(results['severity_level'])
                
                # Get most frequent severity in history
                stable_severity = max(set(severity_history), key=severity_history.count)
                
                # Professional overlay
                cv2.rectangle(processed_frame, (0,0), (300, 50), (15, 23, 42), -1)
                cv2.putText(processed_frame, f"STATUS: {stable_severity}", (15, 33), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            else:
                processed_frame = frame

            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    cam_id = request.args.get('cam', 0)
    return Response(gen_frames(cam_id), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # host='0.0.0.0' allows access from other devices (like your phone) on the same Wi-Fi
    app.run(host='0.0.0.0', debug=True, port=5000)
