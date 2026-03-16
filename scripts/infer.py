from ultralytics import YOLO

# Load a pretrained YOLO26n model
model = YOLO("runs/detect/trial_1/weights/best.pt")
#model  = YOLO("weights/yolo2best.pt")
# Run inference on 'bus.jpg' with arguments
filepath = "captures/Channel-kkYybcn5VoM/20260315_191912.jpg"
filepath = "captures_copy/17.png"
result = model(filepath, conf=0.95)

filepath = filepath.replace("captures_copy", "toto")
print(result[0].names)
result[0].save(filepath)