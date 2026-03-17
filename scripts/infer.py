from ultralytics import YOLO

# Load a pretrained YOLO26n model
model = YOLO("runs/detect/train/weights/best.pt")
#model  = YOLO("weights/yolo2best.pt")
# Run inference on 'bus.jpg' with arguments
filepath = "captures/Channel-kkYybcn5VoM/20260315_191912.jpg"
filepath = "captures_copy/17.png"

filepath = "/home/xtn/projets/school/place_publique/datasets/fish-detection/valid/images/"
filename = "1_jpeg.rf.9232f1ebe77731096519108646a84f6f.jpg"
filepath = "/home/xtn/projets/school/place_publique/captures/Channel-kkYybcn5VoM/20260315_191915.jpg"
#filepath = filepath + filename
result = model(filepath)

filepath = "toto/"+ filename

print(result[0].names)
result[0].save("result.jpg")