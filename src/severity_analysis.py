import cv2
import numpy as np
from skimage.morphology import skeletonize

def analyze_crack_severity(mask):
    """
    Sophisticated civil engineering crack analysis.
    Calculates length, width, density, and maps to specific repair actions.
    """
    # 1. Structural Validation (Hough Lines)
    lines = cv2.HoughLinesP(mask, 1, np.pi/180, threshold=40, minLineLength=25, maxLineGap=15)
    
    # 2. Contour Analysis
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    major_regions = [cnt for cnt in contours if cv2.contourArea(cnt) > 30]
    
    # 3. Geometric Metrics
    # OPTIMIZATION: Skeletonization is slow on high-res images. 
    # If mask is large, we downscale for geometry calculation then upscale results.
    h, w = mask.shape
    max_dim = 1000
    scale = 1.0
    
    if h > max_dim or w > max_dim:
        scale = max_dim / max(h, w)
        down_mask = cv2.resize(mask, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_NEAREST)
        contours_down, _ = cv2.findContours(down_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        major_regions_down = [cnt for cnt in contours_down if cv2.contourArea(cnt) > (30 * scale * scale)]
        
        filtered_mask_down = np.zeros_like(down_mask)
        if major_regions_down:
            cv2.drawContours(filtered_mask_down, major_regions_down, -1, 255, -1)
        
        bool_mask_down = filtered_mask_down > 0
        crack_length = 0
        skeleton = None
        if np.any(bool_mask_down):
            skeleton_down = skeletonize(bool_mask_down)
            crack_length = (np.sum(skeleton_down) / scale) # Scale back to original
            # Upscale skeleton for visualization
            skeleton = cv2.resize(skeleton_down.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST) > 0
            
        total_area = np.sum(mask > 0) # Use original for area count
        avg_width = total_area / crack_length if crack_length > 0 else 0
        
    else:
        filtered_mask = np.zeros_like(mask)
        if major_regions:
            cv2.drawContours(filtered_mask, major_regions, -1, 255, -1)

        # Skeletonization for true length
        bool_mask = filtered_mask > 0
        crack_length = 0
        skeleton = None
        if np.any(bool_mask):
            skeleton = skeletonize(bool_mask)
            crack_length = np.sum(skeleton)

        # Width Estimation (Approximate)
        avg_width = 0
        if crack_length > 0:
            total_area = np.sum(filtered_mask > 0)
            avg_width = total_area / crack_length

    # 4. Density & Coverage
    total_pixels = mask.size
    crack_pixels = np.sum(filtered_mask > 0)
    density = (crack_pixels / total_pixels) * 100
    
    # 5. Civil Engineering Classification Logic
    # Based on ACI/Eurocode style thresholds for crack widths (mm scale approximated to pixel ratios)
    if not major_regions or density < 0.05:
        severity = "None"
        level = "Safe"
        action = "Inspection Passed"
        rec = "No major issue detected. Continue routine maintenance."
    elif avg_width < 1.5 and crack_length < 300:
        severity = "Mild"
        level = "Low"
        action = "Surface Sealing"
        rec = "Hairline surface cracks detected. Monitor periodically. Surface sealing recommended if cracks widen."
    elif avg_width < 3.5 and crack_length < 800:
        severity = "Moderate"
        level = "Medium"
        action = "Crack Filling"
        rec = "Visible active cracking. Crack filling or epoxy injection recommended to prevent moisture ingress."
    elif avg_width < 6.0 and crack_length < 1500:
        severity = "Severe"
        level = "High"
        action = "Structural Patching"
        rec = "Significant structural cracking. Epoxy injection and structural patch repair required."
    else:
        severity = "Critical"
        level = "Very High"
        action = "Urgent Engineering Review"
        rec = "Critical structural failure signs. Detailed internal engineer inspection needed urgently. Immediate structural stabilization required."

    return {
        "crack_count": len(major_regions),
        "estimated_length_px": round(float(crack_length), 2),
        "avg_width_px": round(float(avg_width), 2),
        "density_percentage": round(float(density), 4),
        "severity_level": severity,
        "hazard_level": level,
        "recommended_action": action,
        "detailed_recommendation": rec,
        "significant_contours": major_regions,
        "skeleton": skeleton,
        "has_linear_structure": lines is not None
    }
