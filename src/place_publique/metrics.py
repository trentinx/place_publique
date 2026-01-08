def iou_score(box1, box2):
    """Calculate Intersection over Union (IoU) between two bounding boxes.
    Args:
        box1: Tuple of (x1, y1, x2, y2) for the first box
        box2: Tuple of (x1, y1, x2, y2) for the second box
    Returns:
        IoU score as a float
    """
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2

    inter_min_x = max(x1_min, x2_min)
    inter_min_y = max(y1_min, y2_min)
    inter_max_x = min(x1_max, x2_max)
    inter_max_y = min(y1_max, y2_max)

    if inter_max_x < inter_min_x or inter_max_y < inter_min_y:
        return 0.0

    inter_area = (inter_max_x - inter_min_x) * (inter_max_y - inter_min_y)
    union_area = ((x1_max - x1_min) * (y1_max - y1_min) +
                  (x2_max - x2_min) * (y2_max - y2_min) - inter_area)

    return inter_area / union_area if union_area > 0 else 0.0

def is_same_object(det1, det2, iou_threshold=0.5):
    """Determine if two detections correspond to the same object based on IoU.
    Args:
        det1: First detection dictionary with 'class', 'x1', 'y1', 'x2', 'y2'
        det2: Second detection dictionary with 'class', 'x1', 'y1', 'x2', 'y2'
        iou_threshold: IoU threshold to consider as the same object
    Returns:
        True if the detections are of the same object, False otherwise
    """
    if det1['class'] != det2['class']:
        return False

    box1 = (det1['x1'], det1['y1'], det1['x2'], det1['y2'])
    box2 = (det2['x1'], det2['y1'], det2['x2'], det2['y2'])

    return iou_score(box1, box2) > iou_threshold