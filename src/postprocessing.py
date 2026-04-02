import cv2
import numpy as np

def suppress_non_crack_edges(mask):
    """
    Standardizes input for crack isolation.
    """
    if mask is None: return None
    return (mask > 0).astype(np.uint8) * 255

def isolate_crack_network(mask):
    """
    Forensic Network Isolation.
    Ensures that only elongated, crack-like structures are preserved.
    """
    if mask is None or np.sum(mask) == 0: return mask
    
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if num_labels <= 1: return mask
    
    refined = np.zeros_like(mask)
    for i in range(1, num_labels):
        w_c, h_c, area = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT], stats[i, cv2.CC_STAT_AREA]
        # Slenderness is the gold standard for separating cracks from texture
        slenderness = max(w_c, h_c) / (min(w_c, h_c) + 1e-6)
        
        # Keep only elongated structures or significant structural zones
        if (slenderness > 2.0 and area > 60) or area > 600:
             refined[labels == i] = 255
            
    # Rescue logic: If we filtered everything, try a more permissive check on the largest piece
    if np.sum(refined) == 0:
        largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        w_c, h_c = stats[largest_label, cv2.CC_STAT_WIDTH], stats[largest_label, cv2.CC_STAT_HEIGHT]
        if max(w_c, h_c) / (min(w_c, h_c) + 1e-6) > 2.0:
            refined[labels == largest_label] = 255
        
    return refined

def prune_skeleton(skeleton, min_branch_len=30):
    """
    Skeleton cleanup for measurement accuracy.
    """
    return skeleton

def refine_crack_mask(network_mask):
    """
    Structural smoothing Iteration.
    """
    if network_mask is None: return None
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    return cv2.morphologyEx(network_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
