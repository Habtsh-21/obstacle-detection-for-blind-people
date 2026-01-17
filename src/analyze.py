import os
import csv
import sys
from ultralytics import YOLO
from pathlib import Path
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer import AlertSystem, get_position, estimate_distance, format_distance, generate_description, get_navigation_summary

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_FOLDER = os.path.join(BASE_DIR, 'data', 'samples') 
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'data', 'output', 'annotated_images')
CSV_FILE = os.path.join(BASE_DIR, 'data', 'output', 'detection_results.csv')
YOLO_MODEL = os.path.join(BASE_DIR, 'models', 'yolov8s.pt')
IMG_SIZE = 640

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def process_file(img_path, model, alert_sys, writer):
    print(f"\n{'='*60}")
    print(f"Analyzing {img_path.name} ...")
    print(f"{'='*60}")
    
    try:
        img = Image.open(img_path)
        orig_width, orig_height = img.size
    except Exception as e:
        print(f"Warning: Could not read image dimensions for {img_path.name}: {e}")
        orig_width, orig_height = IMG_SIZE, IMG_SIZE
    
    results = model(str(img_path), imgsz=IMG_SIZE, verbose=False)

    for idx, r in enumerate(results):
        save_path = Path(OUTPUT_FOLDER) / f"{img_path.stem}_{idx}.jpg"
        r.save(filename=str(save_path))

    detections_desc = []
    frame_detections = []
    for r in results:
        boxes = r.boxes.xyxy
        scores = r.boxes.conf
        classes = r.boxes.cls
        
        for box, score, cls in zip(boxes, scores, classes):
            label = model.names[int(cls)]
            position = get_position(box, orig_width, orig_height)
            distance = estimate_distance(box, label, orig_height)
            description = generate_description(object_class=label, position=position, distance=distance, confidence=float(score))
            
            detections_desc.append(description)
            frame_detections.append({'label': label, 'pos': position, 'dist': distance})
            
            writer.writerow([
                img_path.name, label, float(score),
                float(box[0]), float(box[1]), float(box[2]), float(box[3]),
                position, f"{distance:.2f}", description
            ])
    
    if detections_desc:
        print(f"\nDetected {len(detections_desc)} object(s):")
        for i, desc in enumerate(detections_desc, 1):
            print(f"  {i}. {desc}")
        
        nav_summary = get_navigation_summary(frame_detections)
        print(f"\nNavigation Recommendation: {nav_summary}")
        alert_sys.speak_summary(nav_summary)
    else:
        print("  No objects detected.")
        alert_sys.speak_summary("The scene appears to be clear.")

def main():
    model = YOLO(YOLO_MODEL)
    alert_sys = AlertSystem()
    alert_sys.speak_summary("Vision system online. Initializing analysis.")
    
    target_paths = []
    if len(sys.argv) > 1:
        arg_path = Path(sys.argv[1])
        if arg_path.is_file():
            target_paths = [arg_path]
        elif arg_path.is_dir():
            IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
            target_paths = [p for p in arg_path.glob('*.*') if p.suffix.lower() in IMAGE_EXTENSIONS]
        else:
            print(f"Error: Path {sys.argv[1]} not found.")
            alert_sys.speak_summary(f"Error. Path {sys.argv[1]} not found.")
            alert_sys.stop()
            return
    else:
        IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        target_paths = [p for p in Path(IMAGE_FOLDER).glob('*.*') if p.suffix.lower() in IMAGE_EXTENSIONS]

    if not target_paths:
        print("No images found to process.")
        alert_sys.speak_summary("No images found to process.")
        alert_sys.stop()
        return

    try:
        with open(CSV_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Image', 'Class', 'Confidence', 'x1', 'y1', 'x2', 'y2', 'Position', 'Distance (m)', 'Description'])
            
            for path in target_paths:
                alert_sys.speak_summary(f"Analyzing {path.name}")
                process_file(path, model, alert_sys, writer)
                
        alert_sys.speak_summary("Analysis complete. Reports have been saved.")
    finally:
        alert_sys.stop()

    print(f"\n{'='*60}")
    print(f"Done! Results saved in 'data/output/'")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
