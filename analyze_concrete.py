import os
import sys
import json
import cv2

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.detect_crack import ConcreteCrackDetector

def run_forensic_demonstration():
    # Setup paths
    input_img = "dataset/Positive/crack_0.jpg"
    output_dir = "forensic_demo_results"
    model_path = "models/unet_crack.pth"
    
    if not os.path.exists(input_img):
        print(f"Error: Input image {input_img} not found.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n[AI Vision Pipeline] Initializing Concrete Crack Intelligence Suite...")
    detector = ConcreteCrackDetector(model_path=model_path)
    
    print(f"[AI Vision Pipeline] Analyzing specimen: {input_img}")
    report = detector.detect_cracks(input_img, output_dir, scale_mm_per_px=0.25)
    
    print("\n[FORENSIC INSPECTION REPORT]")
    print(f"Inspection ID: {report.get('inspection_id')}")
    print(f"Surface Type: {report.get('surface_type')}")
    print(f"Crack Detected: {report.get('crack_detected')}")
    print(f"Status: {report.get('status').upper()}")
    print(f"Structural Confidence: {report.get('confidence_percent')}%")
    
    print("\n[GEOMETRIC MEASUREMENTS]")
    m = report.get('measurements', {})
    print(f"Length: {m.get('length_px')} px / {m.get('length_val')} {m.get('unit')} ")
    
    g = report.get('geometry', {})
    print(f"Structural Orientation: {g.get('orientation').upper()}")
    print(f"Skeleton Branching: {g.get('branch_count')}")
    
    print("\n[CLASSIFICATION]")
    c = report.get('classification', {})
    print(f"Severity: {c.get('severity').upper()}")
    print(f"Hazard Level: {c.get('hazard').upper()}")
    
    print("\n[AI ASSESSMENT]")
    print(f"Expert Summary: {report.get('assessment')}")
    
    print("\n[OUTPUT ARTIFACTS]")
    for stage, path in report.get('stages', {}).items():
        print(f"Panel {stage}: {path}")

    # Save full JSON report
    with open(os.path.join(output_dir, "inspection_report.json"), "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n[AI Vision Pipeline] Forensic analysis complete. Results saved to '{output_dir}/'")

if __name__ == "__main__":
    run_forensic_demonstration()
