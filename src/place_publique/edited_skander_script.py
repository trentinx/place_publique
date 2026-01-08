import cv2
import numpy as np
import time
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
import subprocess
import re

import torch
from ultralytics import YOLO
from ultralytics import RTDETR

# CONFIGURATION FLUX VIDÉO 

# "https://www.youtube.com/watch?v=Fz6sl9YJZE0"
# python -m yt_dlp -g https://www.youtube.com/watch?v=Fz6sl9YJZE0
# python -m yt_dlp -g https://youtu.be/Fz6sl9YJZE0

# functional python -m yt_dlp -g https://youtu.be/nhyaQwm-4GQ

# VIDEO_URL = "https://manifest.googlevideo.com/api/manifest/hls_playlist/expire/1767804920/ei/mDteafT1ENSJgMMPxeqUkAM/ip/37.26.187.6/id/nhyaQwm-4GQ.2/itag/95/source/yt_live_broadcast/requiressl/yes/ratebypass/yes/live/1/sgoap/gir%3Dyes%3Bitag%3D140/sgovp/gir%3Dyes%3Bitag%3D136/rqh/1/hls_chunk_host/rr3---sn-hgn7rnll.googlevideo.com/xpc/EgVo2aDSNQ%3D%3D/playlist_duration/30/manifest_duration/30/bui/AYUSA3BqIHBegwz1ew7l25LfYKlMdZrnYpRu_zJSkIaCfC_jODpYyXjpwIVwcazOmMwYdUcNbKbsn_QZ/spc/wH4QqzMeAN19jd1unlK7/vprv/1/playlist_type/DVR/met/1767783320,/mh/fr/mm/44/mn/sn-hgn7rnll/ms/lva/mv/u/mvi/3/pl/23/rms/lva,lva/dover/11/pacing/0/keepalive/yes/fexp/51552689,51565115,51565681,51580968/mt/1767781401/sparams/expire,ei,ip,id,itag,source,requiressl,ratebypass,live,sgoap,sgovp,rqh,xpc,playlist_duration,manifest_duration,bui,spc,vprv,playlist_type/sig/AJfQdSswRQIhAO-URm0LQT28nDw3NbY2q2YwMT2oC4YijmMHBWdGSUxJAiAwCIHus4zbjPvl0KKBcvy_9qv5zKzPZ3zHGAF11MVebA%3D%3D/lsparams/hls_chunk_host,met,mh,mm,mn,ms,mv,mvi,pl,rms/lsig/APaTxxMwRAIgRkYtu4_F5QPSSA6VWuYV_T81j8JJfhx_gP2BUfstuZYCICWeqSp9AdpITp5OfDySItGKSKvLeQB_lFslaGM4rjyN/playlist/index.m3u8"
# CHARGEMENT DU MODÈLE YOLO

def youtube_watch_to_short(url):
    """
    Convert YouTube watch URL to youtu.be short format
    
    Args:
        url: YouTube URL in format https://www.youtube.com/watch?v=VIDEO_ID
        
    Returns:
        Short URL in format https://youtu.be/VIDEO_ID
    """
    # Extract video ID using regex
    match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)', url)
    if match:
        video_id = match.group(1)
        return f"https://youtu.be/{video_id}"
    return url

def get_youtube_stream_url(youtube_url):
    """
    Extract the direct stream URL from a YouTube video using yt-dlp
    
    Args:
        youtube_url: The YouTube video URL
        
    Returns:
        The direct HLS manifest URL as a string
    """

    youtube_url = youtube_watch_to_short(youtube_url)
    print("Shortened YouTube URL:", youtube_url)
    try:
        result = subprocess.run(
            ['python', '-m', 'yt_dlp', '-g', youtube_url],
            capture_output=True,
            text=True,
            check=True
        )

        # The URL is in stdout, strip any whitespace
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting stream URL: {e}")
        return None

def load_yolo_model(model_name="yolo11x.pt"):
    print("Chargement du modèle YOLO...")
    # model = YOLO("yolov8n.pt")  # modèle stable
    if model_name.startswith("yolo"):
        model = YOLO(model_name)  # modèle rapide
    elif model_name.startswith("rtdetr"): 
        model = RTDETR('rtdetr-x.pt')
    
    return model


# IOU & TRACKING BASIQUE


def calculate_iou(box1, box2):
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
    if det1['class'] != det2['class']:
        return False

    box1 = (det1['x1'], det1['y1'], det1['x2'], det1['y2'])
    box2 = (det2['x1'], det2['y1'], det2['x2'], det2['y2'])

    return calculate_iou(box1, box2) > iou_threshold


# CAPTURE VIDÉO + DÉTECTION

def start_video_capture(model, video_url=None, resize_dim=(640, 480)):
    cap = cv2.VideoCapture(video_url, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        print(" Impossible d'ouvrir le flux vidéo")
        print("URL :", video_url)
        return

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    print("📡 Flux vidéo connecté")
    print("ESC pour quitter")

    csv_filename = f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_file = open(csv_filename, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        'Frame', 'Timestamp', 'Classe', 'Confiance',
        'X1', 'Y1', 'X2', 'Y2', 'Total_Personnes'
    ])

    frame_count = 0
    all_confidences = []
    class_stats = defaultdict(lambda: {'count': 0, 'total_conf': 0})
    previous_detections = []
    unique_objects = defaultdict(int)
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print(" Perte du flux vidéo")
            break

        frame_count += 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        if resize_dim:
            frame = cv2.resize(frame, resize_dim)
        

        results = model(frame, conf=0.5, verbose=False)

        detections = []
        person_count = 0

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model.names[cls]

                detections.append({
                    'class': class_name,
                    'confidence': conf,
                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2
                })

                all_confidences.append(conf)
                class_stats[class_name]['count'] += 1
                class_stats[class_name]['total_conf'] += conf

                if class_name == "person":
                    person_count += 1
                    color = (0, 255, 0)
                else:
                    color = (0, 165, 255)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{class_name} {conf:.2f}",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        for det in detections:
            is_new = True
            for prev in previous_detections:
                if is_same_object(det, prev):
                    is_new = False
                    break

            if is_new:
                csv_writer.writerow([
                    frame_count, timestamp,
                    det['class'], f"{det['confidence']:.4f}",
                    det['x1'], det['y1'], det['x2'], det['y2'],
                    person_count
                ])
                saved_count += 1
                unique_objects[det['class']] += 1

        previous_detections = detections

        cv2.putText(frame, f"Personnes: {person_count}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        cv2.imshow("YOLO - Flux Video", frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    csv_file.close()

    print("✓ CSV :", csv_filename)
    print("✓ Frames :", frame_count)
    print("✓ Détections enregistrées :", saved_count)
    print("✓ Objets uniques :", dict(unique_objects))

    generate_graphs(all_confidences, class_stats, frame_count)

# ==============================
# GRAPHIQUES
# ==============================

def generate_graphs(all_confidences, class_stats, total_frames):
    if not all_confidences:
        return

    accuracy = sum(c > 0.7 for c in all_confidences) / len(all_confidences) * 100

    class_names = list(class_stats.keys())
    map_scores = [
        (class_stats[c]['total_conf'] / class_stats[c]['count']) * 100
        for c in class_names
    ]

    plt.figure(figsize=(10, 5))
    plt.bar(class_names, map_scores)
    plt.ylabel("MAP (%)")
    plt.title("MAP par classe")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    # Usage:

    # dogs https://www.youtube.com/watch?v=QdEVb1rheRE
    # smalls fishs https://www.youtube.com/watch?v=1zcIUk66HX4
    # average amount of fish https://www.youtube.com/watch?v=kkYybcn5VoM
    # sea lions https://www.youtube.com/watch?v=4ElanH9Gzjw
    # foot https://www.youtube.com/live/9P9Vco9OzSo
    VIDEO_URL = "https://www.youtube.com/watch?v=kkYybcn5VoM"
    fish_live_cam_link = get_youtube_stream_url(VIDEO_URL)
    print("lien de la video: ", fish_live_cam_link)

    # models
    # yolo11x.pt
    # yolo11x-seg.pt
    # rtdetr-x.pt
    # yolo8n.pt

    model = load_yolo_model("yolo11x.pt")
    start_video_capture(model, video_url=fish_live_cam_link, resize_dim=False)