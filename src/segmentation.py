import cv2
import numpy as np

def filter_thin_elongated_components(mask, mode="all"):
    """
    Forensic geometry filter: strictly isolates crack-like geometry.
    Rejects surface pits/grains (blobs) and salt-and-pepper noise.
    """
    if mask is None or np.sum(mask) == 0: return mask
    
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    refined = np.zeros_like(mask)
    
    for i in range(1, num_labels):
        w_c, h_c, area = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT], stats[i, cv2.CC_STAT_AREA]
        slenderness = max(w_c, h_c) / (min(w_c, h_c) + 1e-6)
        
        # Forensic refinement based on detection focus
        min_area, min_slend = 60, 2.5
        if mode == "hairline":
            min_area, min_slend = 25, 3.5
        elif mode == "alligator":
            min_area, min_slend = 40, 1.4 # Networks are less slender but connected
        elif mode == "structural":
            min_area, min_slend = 150, 1.8
        elif mode == "thermal":
            min_area, min_slend = 80, 2.8
            
        if (slenderness > min_slend and area > min_area) or area > 450:
            if slenderness > 1.1: 
                refined[labels == i] = 255
                
    return refined

def structural_forensic_segmentation(image, model=None, device="cpu", use_dl=False, detection_mode="all"):
    """
    Hybrid adaptive signal acquisition.
    Tuned for forensic accuracy. (Ultra-Lightweight CV Engine)
    """
    if image is None: return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Small 3x3 blur to help connectivity while preserving precision
    blurred = cv2.GaussianBlur(gray, (3,3), 0)
    
    # Adaptive thresholding: C=8 (Proven forensic standard)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 8)
    
    return filter_thin_elongated_components(thresh, mode=detection_mode)
