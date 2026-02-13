import os
import re
import time
import subprocess
from pathlib import Path

import cv2
from ultralytics import YOLO


SOURCE = "https://youtu.be/kkYybcn5VoM"

# ✅ Take one screenshot / inference every 5 seconds
SECONDS_INTERVAL = 5

MAX_IMAGES_PER_SESSION = 20
RESTART_SLEEP_SECONDS = 2
OUT_DIR = Path("/Users/julienrm/Workspace/formation/place_publique/our_aquarium_images")

# Retry behavior
OPEN_RETRIES = 5
READ_FAIL_MAX = 30          # consecutive failed reads before we refresh URL
REOPEN_BACKOFF_SECONDS = 1  # base backoff for reopen attempts

# ✅ Your trained model
MODEL_PATH = "/Users/julienrm/Workspace/formation/test_vision/runs/detect/train10/weights/best.pt"
model = YOLO(MODEL_PATH)


def next_index(out_dir: Path) -> int:
    pattern = re.compile(r"_(\d{6})\.jpg$", re.IGNORECASE)
    max_idx = -1
    for p in out_dir.glob("*.jpg"):
        m = pattern.search(p.name)
        if m:
            max_idx = max(max_idx, int(m.group(1)))
    return max_idx + 1


def get_stream_url(youtube_url: str) -> str:
    """
    Prefer HLS for live streams (often more stable than direct googlevideo MP4 URLs).
    """
    fmt = "best[protocol=m3u8]/best"
    cmd = ["yt-dlp", "-g", "-f", fmt, youtube_url]
    out = subprocess.check_output(cmd, text=True).strip().splitlines()
    if not out:
        raise RuntimeError("yt-dlp did not return a stream URL")
    return out[0].strip()


def open_capture(url: str) -> cv2.VideoCapture:
    """
    OpenCV -> FFmpeg options:
    - disable persistent HTTP connections (helps when host changes)
    - set timeouts
    - enable reconnect
    """
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
        "rtsp_transport;tcp|"
        "http_persistent;0|"
        "reconnect;1|reconnect_streamed;1|reconnect_delay_max;5|"
        "stimeout;5000000"
    )
    return cv2.VideoCapture(url, cv2.CAP_FFMPEG)


def run_session(start_idx: int) -> int:
    idx = start_idx
    last_infer_ts = 0.0
    saved_in_session = 0

    # Try opening stream with retries
    cap = None
    stream_url = None
    for attempt in range(1, OPEN_RETRIES + 1):
        try:
            stream_url = get_stream_url(SOURCE)
            cap = open_capture(stream_url)
            if cap.isOpened():
                break
        except Exception as e:
            print(f"[open attempt {attempt}/{OPEN_RETRIES}] failed: {e}")
        time.sleep(REOPEN_BACKOFF_SECONDS * attempt)

    if cap is None or not cap.isOpened():
        raise RuntimeError("Impossible d’ouvrir le flux vidéo (even after retries).")

    read_failures = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                read_failures += 1
                time.sleep(0.05)

                if read_failures >= READ_FAIL_MAX:
                    print("Too many read failures; refreshing stream URL and reopening...")
                    try:
                        cap.release()
                    except Exception:
                        pass

                    reopened = False
                    for attempt in range(1, OPEN_RETRIES + 1):
                        try:
                            stream_url = get_stream_url(SOURCE)
                            cap = open_capture(stream_url)
                            if cap.isOpened():
                                reopened = True
                                read_failures = 0
                                break
                        except Exception as e:
                            print(f"[reopen attempt {attempt}/{OPEN_RETRIES}] failed: {e}")
                        time.sleep(REOPEN_BACKOFF_SECONDS * attempt)

                    if not reopened:
                        print("Failed to reopen stream; ending session.")
                        break

                continue

            read_failures = 0

            now = time.time()
            if now - last_infer_ts < SECONDS_INTERVAL:
                # Don’t process every frame; only every 5s
                time.sleep(0.01)
                continue

            # ✅ this frame is the "screenshot" we will pass to the model
            ts = time.strftime("%Y%m%d-%H%M%S")
            filename = OUT_DIR / f"aquarium_{ts}_{idx:06d}.jpg"

            # (Optional) save screenshot to disk
            if cv2.imwrite(str(filename), frame):
                print(f"Saved screenshot: {filename}")
            else:
                print("Warning: failed to save screenshot")

            # ✅ Run inference/tracking on this screenshot frame
            # If you need tracking IDs over time, keep persist=True.
            results = model.track(
                frame,
                persist=True,
                conf=0.5,
                iou=0.7,
                max_det=20,
                verbose=False,
            )

            r = results[0]
            if r.boxes is not None and len(r.boxes) > 0:
                print("\n--- DETECTIONS ---")
                for box in r.boxes:
                    cls_id = int(box.cls.item())
                    class_name = model.names[cls_id]
                    track_id = int(box.id.item()) if getattr(box, "id", None) is not None and box.id is not None else None
                    print(f"class: {class_name} | track_id: {track_id}")

            # bookkeeping
            idx += 1
            saved_in_session += 1
            last_infer_ts = now

            if saved_in_session >= MAX_IMAGES_PER_SESSION:
                print(f"Reached {MAX_IMAGES_PER_SESSION} screenshots. Restarting capture session...")
                break

    finally:
        try:
            cap.release()
        except Exception:
            pass

    return idx


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    idx = next_index(OUT_DIR)
    print(f"Output folder: {OUT_DIR}")
    print(f"Resuming at index: {idx:06d}")

    while True:
        try:
            idx = run_session(idx)
        except Exception as e:
            print(f"[session error] {e}")
        time.sleep(RESTART_SLEEP_SECONDS)


if __name__ == "__main__":
    main()