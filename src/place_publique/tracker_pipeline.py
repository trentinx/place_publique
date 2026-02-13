"""Utilities for preparing, training, and running BoT-SORT style trackers.

This module centralizes the paths and shell commands required to reproduce the
workflow described in the BoT-SORT README:

1. Prepare MOT-format datasets (defaults to ``datasets/d3``).
2. Generate FastReID patches via ``fast_reid/datasets/generate_mot_patches.py``.
3. Train the FastReID module with a dataset-specific config.
4. Train/finetune the YOLO detector on the same dataset.
5. Run BoT-SORT tracking on a live YouTube stream using OpenCV, similar to
   :mod:`place_publique.youtube`.

Each step is exposed as a function and can also be triggered via CLI subcommands:

.. code-block:: bash

    # Generate patches
    uv run python -m place_publique.tracker_pipeline patches --dataset d3

    # Train FastReID
    uv run python -m place_publique.tracker_pipeline train-reid --dataset d3

    # Train YOLO detector
    uv run python -m place_publique.tracker_pipeline train-detector --dataset d3

    # Track a live stream with the freshly trained weights
    uv run python -m place_publique.tracker_pipeline track \\
        --youtube-url https://www.youtube.com/watch?v=kkYybcn5VoM \\
        --model-path runs/detect/train/weights/best.pt
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Iterable, Optional

import cv2
from ultralytics import YOLO

from place_publique.youtube import get_direct_url

# Base paths used across the pipeline.
DATASETS_DIR = Path("datasets")
DEFAULT_DATASET = "d3"
FASTREID_ROOT = Path("fast_reid")
FASTREID_PATCH_SCRIPT = FASTREID_ROOT / "datasets" / "generate_mot_patches.py"
FASTREID_TRAIN_SCRIPT = FASTREID_ROOT / "tools" / "train_net.py"
FASTREID_CONFIG = FASTREID_ROOT / "configs" / "FishDataset" / "sbs_S50.yml"
DEFAULT_TRACKER_CONFIG = Path("botsort.yaml")
DEFAULT_MODEL_PATH = Path("runs/detect/train10/weights/best.pt")


def run_command(command: Iterable[str], cwd: Optional[Path] = None) -> None:
    """Run a shell command (very lightly wrapped)."""
    display_cmd = " ".join(command)
    print(f"→ {display_cmd}")
    subprocess.run(command, check=True, cwd=cwd)


def ensure_path(path: Path, description: str) -> None:
    """Raise a clear error if a required resource is missing."""
    if not path.exists():
        raise FileNotFoundError(f"{description} not found at {path}")


def generate_reid_patches(dataset_name: str = DEFAULT_DATASET) -> None:
    """Invoke FastReID's patch generator on the MOT dataset."""
    ensure_path(FASTREID_PATCH_SCRIPT, "FastReID patch generator script")
    dataset_root = DATASETS_DIR / dataset_name
    ensure_path(dataset_root, f"MOT dataset '{dataset_name}'")

    command = [
        "python3",
        str(FASTREID_PATCH_SCRIPT),
        "--data_path",
        str(DATASETS_DIR.resolve()),
        "--mot",
        dataset_name,
    ]
    run_command(command)


def train_reid_module(
    dataset_name: str = DEFAULT_DATASET,
    config_path: Path = FASTREID_CONFIG,
    device: str = "cuda:0",
) -> None:
    """Train the FastReID module with the dataset-specific config."""
    ensure_path(FASTREID_TRAIN_SCRIPT, "FastReID train_net.py")
    ensure_path(config_path, "FastReID config file")

    command = [
        "python3",
        str(FASTREID_TRAIN_SCRIPT),
        "--config-file",
        str(config_path),
        "MODEL.DEVICE",
        device,
        "DATASETS.NAMES",
        dataset_name,
    ]
    run_command(command)


def train_yolo_detector(
    dataset_name: str = DEFAULT_DATASET,
    base_model: str = "yolov8n.pt",
    epochs: int = 50,
    image_size: int = 640,
    batch_size: int = 16,
    project: str = "runs/detect",
    run_name: str = "fish-tracker",
) -> None:
    """Train or fine-tune a YOLO detector on the MOT dataset."""
    dataset_yaml = DATASETS_DIR / dataset_name / "data.yaml"
    ensure_path(dataset_yaml, "YOLO data.yaml")

    command = [
        "yolo",
        "task=detect",
        "mode=train",
        f"model={base_model}",
        f"data={dataset_yaml}",
        f"epochs={epochs}",
        f"imgsz={image_size}",
        f"batch={batch_size}",
        f"project={project}",
        f"name={run_name}",
    ]
    run_command(command)


def track_youtube_stream(
    youtube_url: str,
    model_path: Path = DEFAULT_MODEL_PATH,
    tracker_config: Optional[Path] = DEFAULT_TRACKER_CONFIG,
    conf: float = 0.3,
) -> None:
    """Apply BoT-SORT tracking to a YouTube stream using OpenCV."""
    ensure_path(model_path, "YOLO model weights")
    if tracker_config is not None and tracker_config.exists():
        tracker_arg = str(tracker_config)
    else:
        tracker_arg = "botsort.yaml"

    stream_url = get_direct_url(youtube_url)
    print(f"Tracking stream: {stream_url}")
    model = YOLO(str(model_path))

    results_generator = model.track(
        source=stream_url,
        stream=True,
        tracker=tracker_arg,
        conf=conf,
        verbose=False,
    )

    window = "BoT-SORT Tracking"
    for results in results_generator:
        frame = results.plot()
        cv2.imshow(window, frame)
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Utilities to train and run BoT-SORT tracking locally.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET,
        help="Name of the MOT dataset under datasets/",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("patches", help="Generate FastReID patches")

    reid_parser = subparsers.add_parser("train-reid", help="Train FastReID module")
    reid_parser.add_argument(
        "--config",
        default=str(FASTREID_CONFIG),
        help="Path to the FastReID YAML config",
    )
    reid_parser.add_argument(
        "--device",
        default="cuda:0",
        help="Device string passed to FastReID (e.g., cuda:0 or cpu)",
    )

    detector_parser = subparsers.add_parser("train-detector", help="Train YOLO detector")
    detector_parser.add_argument("--model", default="yolov8n.pt", help="YOLO base weights")
    detector_parser.add_argument("--epochs", type=int, default=50)
    detector_parser.add_argument("--imgsz", type=int, default=640)
    detector_parser.add_argument("--batch", type=int, default=16)
    detector_parser.add_argument("--project", default="runs/detect")
    detector_parser.add_argument("--name", default="fish-tracker")

    track_parser = subparsers.add_parser("track", help="Track a YouTube stream locally")
    track_parser.add_argument("--youtube-url", required=True, help="Full YouTube URL")
    track_parser.add_argument(
        "--model-path",
        default=str(DEFAULT_MODEL_PATH),
        help="Path to YOLO weights (best.pt after training)",
    )
    track_parser.add_argument(
        "--tracker-config",
        default=str(DEFAULT_TRACKER_CONFIG),
        help="botsort.yaml path; falls back to Ultralytics default if missing",
    )
    track_parser.add_argument("--conf", type=float, default=0.3, help="Confidence threshold")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "patches":
        generate_reid_patches(args.dataset)
    elif args.command == "train-reid":
        train_reid_module(
            dataset_name=args.dataset,
            config_path=Path(args.config),
            device=args.device,
        )
    elif args.command == "train-detector":
        train_yolo_detector(
            dataset_name=args.dataset,
            base_model=args.model,
            epochs=args.epochs,
            image_size=args.imgsz,
            batch_size=args.batch,
            project=args.project,
            run_name=args.name,
        )
    elif args.command == "track":
        track_youtube_stream(
            youtube_url=args.youtube_url,
            model_path=Path(args.model_path),
            tracker_config=Path(args.tracker_config),
            conf=args.conf,
        )
    else:
        parser.error(f"Unknown command {args.command}")


if __name__ == "__main__":
    main()
