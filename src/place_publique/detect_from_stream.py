from ultralytics import YOLO

model = YOLO("/Users/julienrm/Workspace/formation/test_vision/runs/detect/train10/weights/best.pt")

# Run inference on a single image
results = model.predict(
    "aquarium_20260212-143846_6d_jpg.rf.4dcce7fdd20ab10cbc8d43ce23a63171.jpg",
    conf=0.4,
    iou=0.7,
    max_det=20,
)

# Or even simpler:
# results = model("path/to/your/image.jpg")

# Process results
for r in results:
    r.save(filename="output.jpg") 
    if r.boxes is not None:
        print("\n--- DETECTIONS ---")
        for box in r.boxes:
            cls_id = int(box.cls.item())
            class_name = model.names[cls_id]
            confidence = float(box.conf.item())
            
            print(
                f"class: {class_name} | "
                f"confidence: {confidence:.2f}"
            )