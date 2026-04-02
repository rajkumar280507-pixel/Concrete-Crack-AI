import cv2
import numpy as np

def validate_surface(image):
    """
    Forensic Surface Integrity Check.
    Returns (is_valid, confidence)
    """
    if image is None: return False, 0.0
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Calculate Laplacian variance for focus/texture quality
    var = cv2.Laplacian(gray, cv2.CV_64F).var()
    # Focus Threshold: 100 is a standard for 'well-textured' surface
    focus_conf = min(var / 150.0, 1.0)
    
    return True, focus_conf

def extract_specimen_roi(image):
    """
    Isolates the core specimen using Otsu-based flood isolation.
    """
    if image is None: return None, None, None
    h, w = image.shape[:2]
    # In forensics, we usually analyze the full frame but skip edges
    margin = 5
    roi = image[margin:h-margin, margin:w-margin]
    bbox = (margin, margin, w-2*margin, h-2*margin)
    return roi, bbox, image

def enhance_roi(roi):
    """
    Signal optimization using CLAHE (Contrast Limited Adaptive Histogram Equalization).
    Essential for isolating hairline fissures in varied lighting.
    """
    if roi is None: return None
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
    return clahe.apply(gray)
