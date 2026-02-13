from place_publique.models import load_model
from place_publique.youtube import get_direct_url, start_video_capture


# Usage:
# dogs https://www.youtube.com/watch?v=QdEVb1rheRE
# smalls fishs https://www.youtube.com/watch?v=1zcIUk66HX4
# average amount of fish https://www.youtube.com/watch?v=kkYybcn5VoM
# sea lions https://www.youtube.com/watch?v=4ElanH9Gzjw
# foot https://www.youtube.com/live/9P9Vco9OzSo

VIDEO_URL = "https://www.youtube.com/watch?v=kkYybcn5VoM"
fish_live_cam_link = get_direct_url(VIDEO_URL)
print("lien de la video: ", fish_live_cam_link)

# models
# yolo11x.pt
# yolo11x-seg.pt
# rtdetr-x.pt
# yolo8n.pt

#model = load_model("yolo11x.pt")
# model = load_model("yolo2best.pt")
# model = load_model("runs/detect/train3/weights/best.pt")
model = load_model("/Users/julienrm/Workspace/formation/test_vision/runs/detect/train3/weights/best.pt")
start_video_capture(model, video_url=fish_live_cam_link, resize_dim=False)
