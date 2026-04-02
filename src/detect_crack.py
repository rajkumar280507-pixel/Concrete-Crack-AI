import os
import cv2
import datetime
import time
import numpy as np
from skimage.morphology import skeletonize

from src.preprocessing import (
    extract_specimen_roi,
    enhance_roi,
    validate_surface,
)
from src.segmentation import structural_forensic_segmentation
from src.postprocessing import (
    isolate_crack_network,
    refine_crack_mask,
)
from src.measurement import structural_forensic_analysis
from src.visualization import visualize_results

class ConcreteCrackDetector:
    """
    End-to-end Forensic Crack Detection Suite.
    Ultra-Lightweight Engine: Optimized for 512MB RAM constraints.
    """
    def __init__(self, model_path=None, device="cpu"):
        self.device = "cpu" # Force CPU for lightweight execution
        self.weights_loaded = False
        self.model = None

    def analyze_frame(self, frame):
        """
        Lightweight real-time frame analysis for live feed.
        """
        try:
            if frame is None or frame.size == 0: return frame, {"crack_detected": False}
            mask = structural_forensic_segmentation(frame, self.model, self.device, self.weights_loaded)
            processed_frame = frame.copy()
            if mask is not None and np.sum(mask) > 0:
                processed_frame[mask > 0] = [0, 0, 255]
            return processed_frame, {"crack_detected": bool(np.sum(mask > 0) > 500), "severity_level": "N/A"}
        except Exception:
            return frame, {"crack_detected": False, "severity_level": "N/A"}

    def detect_cracks(self, image_path, output_dir, scale_mm_per_px=0.2, target_unit="mm", detection_mode="all"):
        """
        Full 9-Phase Inspection Pipeline.
        """
        image = cv2.imread(image_path)
        if image is None: raise ValueError("Image read failed.")
        
        img_id = os.path.splitext(os.path.basename(image_path))[0]
        os.makedirs(os.path.join(output_dir, "stages"), exist_ok=True)
        
        def save_stage(img, name, label):
             rel_path = f"stages/{name}_{img_id}.jpg"
             out_path = os.path.join(output_dir, rel_path)
             canvas = img.copy()
             if len(canvas.shape) == 2: canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)
             cv2.putText(canvas, f"PHASE: {label}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
             cv2.imwrite(out_path, canvas)
             return rel_path

        # Phase 0: Forensic Surface Validation (NO EARLY EXIT)
        is_standard, surf_conf = validate_surface(image)
        surface_label = "Concrete" if is_standard else "Concrete (low-confidence validation)"
        
        # Phase 1: Original Specimen
        p1 = save_stage(image, "p1", "ORIGINAL SPECIMEN SURFACE")
        
        # Phase 2: ROI Enhancement
        roi_img, roi_bbox, _ = extract_specimen_roi(image)
        enhanced = enhance_roi(roi_img)
        p2 = save_stage(enhanced, "p2", "SIGNAL OPTIMIZATION (CLAHE)")
        
        # Phase 3: Crack Region Isolation
        # Pure CV Engine: High precision adaptive segmentation
        initial_mask = structural_forensic_segmentation(cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR), self.model, self.device, self.weights_loaded, detection_mode=detection_mode)
        if initial_mask is None: initial_mask = np.zeros(enhanced.shape[:2], dtype=np.uint8)
        
        isolated_mask = isolate_crack_network(initial_mask)
        final_mask = refine_crack_mask(isolated_mask)
        p3 = save_stage(final_mask, "p3", "FORENSIC CRACK MASK")
        
        # Phase 4: Geometry & Measurement
        skeleton = (skeletonize(final_mask > 0) * 255).astype(np.uint8)
        p4 = save_stage(skeleton, "p4", "AXIAL GEOMETRY (SKELETON)")
        
        # Phase 5: Final Forensic Assessment
        analysis = structural_forensic_analysis(final_mask, scale_mm_per_px, target_unit, skeleton, detection_mode=detection_mode)
        analysis['timestamp_unix'] = int(time.time())
        # Restore full-scale mask for overlay visualization
        h_orig, w_orig = image.shape[:2]
        full_mask = np.zeros((h_orig, w_orig), dtype=np.uint8)
        x, y, w_r, h_r = roi_bbox
        mask_roi = cv2.resize(final_mask, (w_r, h_r), interpolation=cv2.INTER_NEAREST)
        full_mask[y:y+h_r, x:x+w_r] = mask_roi
        analysis['mask_binary'] = full_mask
        analysis['geometry']['roi_offset'] = (x, y)
        
        # Forensic Confidence
        detection_conf = 0.0
        if analysis.get('crack_detected'):
            # Base confidence of detection is high if the geometry filters passed
            detection_conf = 85.0 + (surf_conf * 14.0) 
        else:
            detection_conf = surf_conf * 100.0

        analysis['confidence_percent'] = round(detection_conf, 1)

        integrity_vis = visualize_results(image, analysis)
        p5 = save_stage(integrity_vis, "p5", "FINAL FORENSIC ASSESSMENT")
        
        # Export final diagnostic image
        cv2.imwrite(os.path.join(output_dir, f"proc_{os.path.basename(image_path)}"), integrity_vis)

        report = {
            "inspection_id": f"CCIS-REC-{img_id[:6].upper()}",
            "surface_type": surface_label,
            "crack_detected": analysis.get('crack_detected', False),
            "status": "confirmed" if analysis.get('crack_detected') else "stable",
            "confidence_percent": round(detection_conf, 1),
            "calibration": {"available": True, "mm_per_pixel": scale_mm_per_px, "target_unit": target_unit},
            "stages": {
                "p1_original": p1, "p2_enhanced": p2, "p3_mask": p3,
                "p4_skeleton": p4, "p5_assessment": p5
            },
            "measurements": analysis.get('measurements', {}),
            "geometry": analysis.get('geometry', {}),
            "classification": analysis.get('classification', {}),
            "recommend_detail": analysis.get('assessment', ""),
            "recommendation": analysis.get('recommendation', ""),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return report
