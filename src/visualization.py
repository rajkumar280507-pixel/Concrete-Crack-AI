import cv2
import numpy as np

def visualize_results(image, results):
    """
    Forensic Visualization Dashboard.
    Dynamic overlay with glassmorphism-style metadata HUD.
    """
    if image is None: return None
    overlay = image.copy()
    h, w = image.shape[:2]
    
    is_detected = results.get('crack_detected', False)
    measurements = results.get('measurements', {})
    classification = results.get('classification', {})
    geometry = results.get('geometry', {})
    
    # Forensic Severity Colors
    COLOR_SCHEMA = {
        "Trace": (200, 255, 0), "Hairline": (0, 255, 255), "Fine": (255, 120, 0), "Mild": (0, 255, 255),
        "Moderate": (0, 165, 255), "Severe": (0, 0, 255), "Non-crack": (200, 200, 200)
    }
    severity = classification.get('severity', "Non-crack")
    color = COLOR_SCHEMA.get(severity, (255, 255, 255))

    if is_detected:
        mask = results.get('mask_binary')
        if mask is not None:
             mask_uint8 = (mask > 0).astype(np.uint8) * 255
             cnts, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
             
             # Structural Highlighting
             color_layer = np.zeros_like(image)
             color_layer[:] = color
             colored_region = cv2.bitwise_and(color_layer, color_layer, mask=mask_uint8)
             overlay = cv2.addWeighted(overlay, 1.0, colored_region, 0.65, 0)
             cv2.drawContours(overlay, cnts, -1, (255, 255, 255), 1)

             # Visualizing Branch Points
             branch_pts = geometry.get('branch_points', [])
             roi_offset = geometry.get('roi_offset', (0, 0))
             for pt in branch_pts:
                 # Luminous Branch Detection Dots (Larger & Higher Contrast)
                 gx, gy = int(pt[0] + roi_offset[0]), int(pt[1] + roi_offset[1])
                 cv2.circle(overlay, (gx, gy), 8, (255, 255, 255), -1) # Background Glow
                 cv2.circle(overlay, (gx, gy), 6, (0, 0, 255), -1) # Luminous Red Core
                 cv2.circle(overlay, (gx, gy), 8, (255, 255, 255), 1) # Sharp Outer Rim

        # Redesigned Forensic HUD: Vertical Stack for Zero-Overlap
        hud_h = 160
        hud_y = h - hud_h
        cv2.rectangle(overlay, (0, hud_y), (w, h), (10, 10, 10), -1) # Solid dark footer
        
        # Overlay back onto original with 85% opacity for professional glass look
        image_hud = image.copy()
        cv2.rectangle(image_hud, (0, hud_y), (w, h), (20, 20, 20), -1)
        overlay = cv2.addWeighted(image_hud, 0.85, overlay, 0.15, 0)
        
        font = cv2.FONT_HERSHEY_DUPLEX
        conf = float(results.get('confidence_percent', 0.0))
        severity = classification.get('severity', "Non-crack").upper()
        
        # Single Vertical Column for metrics
        margin_left = 25
        line_height = 28
        curr_y = hud_y + 35
        
        # Line 1: Status & Severity (Prominent)
        cv2.putText(overlay, f"INSPECTION: SUCCESSFUL | SEVERITY: {severity}", (margin_left, curr_y), font, 0.65, color, 2)
        
        # Line 2: Hazard / Crack Type
        curr_y += line_height
        hazard = classification.get('hazard', 'None').upper()
        c_type = classification.get('crack_type', 'N/A').upper()
        cv2.putText(overlay, f"HAZARD: {hazard} | TYPE: {c_type}", (margin_left, curr_y), font, 0.45, (220, 220, 220), 1)
        
        # Line 3: Dimensions
        curr_y += line_height
        l_val = measurements.get('length_val', 0.0)
        w_val = measurements.get('avg_width_val', 0.0)
        unit = measurements.get('unit', 'mm')
        metrics_line = f"DIMENSIONS: {l_val:.2f}{unit} length | {w_val:.2f}{unit} avg width"
        cv2.putText(overlay, metrics_line, (margin_left, curr_y), font, 0.55, (200, 200, 200), 1)
        
        # Line 4: Geometry & Depth
        curr_y += line_height
        orient = geometry.get('orientation', 'n/a').upper()
        branches = geometry.get('branch_count', 0)
        d_val = measurements.get('depth_val', 0.0)
        extra_line = f"GEOMETRY: {orient} | BRANCHES: {branches} | DEPTH EST: {d_val:.2f}{unit if unit != 'px' else 'mm'}"
        cv2.putText(overlay, extra_line, (margin_left, curr_y), font, 0.55, (200, 200, 200), 1)
        
        # Line 5: Confidence (Footer)
        curr_y += line_height - 5
        cv2.putText(overlay, f"FORENSIC CONFIDENCE: {conf:.1f}%", (margin_left, curr_y), font, 0.45, (150, 150, 150), 1)
    else:
        # Case: No Structural Signal
        cv2.rectangle(overlay, (0, h - 60), (w, h), (10, 50, 10), -1)
        cv2.putText(overlay, "FORENSIC SYSTEM: NO STRUCTURAL DISTRESS DETECTED", (20, h - 25), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 255, 0), 1)

    return overlay
