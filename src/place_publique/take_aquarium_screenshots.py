import re
import time
from pathlib import Path

import cv2
from ultralytics import YOLO

# SOURCE = "https://youtu.be/zQ8caaUxIvY"
SOURCE = "https://youtu.be/kkYybcn5VoM"
SECONDS_INTERVAL = 3
MAX_IMAGES_PER_SESSION = 20
RESTART_SLEEP_SECONDS = 2

# IMPORTANT: absolute path so you never write into a different folder by accident
OUT_DIR = Path("/Users/julienrm/Workspace/formation/place_publique/our_aquarium_images")


def next_index(out_dir: Path) -> int:
    """
    Find next index by looking for any filename ending in _NNNNNN.jpg (6 digits).
    Works even if the prefix/timestamp differs.
    """
    pattern = re.compile(r"_(\d{6})\.jpg$", re.IGNORECASE)
    max_idx = -1

    for p in out_dir.glob("*.jpg"):
        m = pattern.search(p.name)
        if m:
            max_idx = max(max_idx, int(m.group(1)))

    return max_idx + 1


def run_session(model: YOLO, start_idx: int) -> int:
    results = model.predict(
        source=SOURCE,
        stream=True,
        show=False,
        verbose=False,
    )

    last_saved = 0.0
    saved_in_session = 0
    idx = start_idx

    try:
        for r in results:
            now = time.time()
            if now - last_saved < SECONDS_INTERVAL:
                continue

            frame = getattr(r, "orig_img", None)
            if frame is None:
                continue

            ts = time.strftime("%Y%m%d-%H%M%S")
            filename = OUT_DIR / f"aquarium_{ts}_{idx:06d}.jpg"

            if cv2.imwrite(str(filename), frame):
                print(f"Saved: {filename}")
                idx += 1
                saved_in_session += 1
                last_saved = now

            if saved_in_session >= MAX_IMAGES_PER_SESSION:
                print(f"Reached {MAX_IMAGES_PER_SESSION} images. Restarting capture session...")
                break
    finally:
        try:
            results.close()
        except Exception:
            pass

    return idx


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    idx = next_index(OUT_DIR)
    print(f"Output folder: {OUT_DIR}")
    print(f"Resuming at index: {idx:06d}")

    model = YOLO("/Users/julienrm/Workspace/formation/test_vision/runs/detect/train7/weights/best.pt")

    while True:
        idx = run_session(model, idx)
        time.sleep(RESTART_SLEEP_SECONDS)


if __name__ == "__main__":
    main()