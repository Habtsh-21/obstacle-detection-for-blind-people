TYPICAL_OBJECT_SIZES = {
    'person': 1.7, 'car': 1.5, 'chair': 1.0, 'bottle': 0.25,
    'cell phone': 0.15, 'laptop': 0.3, 'door': 2.0, 'table': 0.75,
    'backpack': 0.5, 'umbrella': 1.0, 'handbag': 0.3, 'suitcase': 0.6
}
DEFAULT_OBJECT_SIZE = 0.5

def get_position(box, img_w, img_h):
    x1, y1, x2, y2 = float(box[0]), float(box[1]), float(box[2]), float(box[3])
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    
    if cx < img_w * 0.33:
        h_pos = "left"
    elif cx > img_w * 0.67:
        h_pos = "right"
    else:
        h_pos = "center"
        
    if cy < img_h * 0.33:
        v_pos = "top"
    elif cy > img_h * 0.67:
        v_pos = "bottom"
    else:
        v_pos = "center"
        
    if h_pos == "center" and v_pos == "center":
        return "straight ahead"
    return f"{v_pos} {h_pos}"

def estimate_distance(box, label, img_h):
    x1, y1, x2, y2 = float(box[0]), float(box[1]), float(box[2]), float(box[3])
    box_h = y2 - y1
    focal_length = 800 
    known_h = TYPICAL_OBJECT_SIZES.get(label, DEFAULT_OBJECT_SIZE)
    if box_h == 0: return 100.0
    distance = (known_h * focal_length) / box_h
    return round(float(distance), 2)

def format_distance(distance):
    if distance < 1:
        return f"{distance * 100:.0f}cm"
    else:
        return f"{distance:.1f}m"

def generate_description(object_class, position, distance, confidence):
    article = "a" if object_class[0].lower() not in 'aeiou' else "an"
    distance_str = format_distance(distance)
    return f"{article} {object_class} at {position}, approximately {distance_str} away"

def get_navigation_summary(detections):
    if not detections:
        return "The path ahead is completely clear. You can proceed safely."
    center_obstacles = [d for d in detections if "center" in d['pos'] or "straight ahead" in d['pos']]
    critical_obstacles = [d for d in center_obstacles if d['dist'] < 2.0]
    left_clear = not any(d for d in detections if "left" in d['pos'] and d['dist'] < 2.0)
    right_clear = not any(d for d in detections if "right" in d['pos'] and d['dist'] < 2.0)
    summary = ""
    if critical_obstacles:
        obs = critical_obstacles[0]
        summary = f"Stop! {obs['label']} is directly in front of you, only {format_distance(obs['dist'])} away. "
        if left_clear and right_clear:
            summary += "You can turn either left or right to avoid it."
        elif left_clear:
            summary += "The path to your left appears clearer. Try moving left."
        elif right_clear:
            summary += "The path to your right appears clearer. Try moving right."
        else:
            summary += "You are surrounded by obstacles. Please proceed with extreme caution or wait for assistance."
    else:
        nearest = min(detections, key=lambda x: x['dist'])
        if nearest['dist'] < 3.0:
            summary = f"The path is mostly clear, but there is {nearest['label']} about {format_distance(nearest['dist'])} away on your {nearest['pos']}. "
        else:
            summary = "The path ahead looks good. No immediate obstacles detected."
    return summary
