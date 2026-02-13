#!/bin/bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <dataset-name>"
  exit 1
fi

DATASET=$1
ENV_FILE=".env"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck source=/dev/null
  source "$ENV_FILE"
else
  echo "Warning: $ENV_FILE not found. Ensure ROBOFLOW_API_KEY is exported."
fi

if [[ -z "${ROBOFLOW_API_KEY:-}" ]]; then
  echo "Error: ROBOFLOW_API_KEY is not set. Export it or add it to $ENV_FILE."
  exit 1
fi

DESTDIR="datasets/$DATASET"

if [[ -d "$DESTDIR" ]]; then
  echo "$DESTDIR already created"
  exit 0
fi

mkdir -p "$DESTDIR"
curl -fL "https://universe.roboflow.com/ds/zgmYOM0mZA?key=$ROBOFLOW_API_KEY" -o roboflow.zip
unzip -q roboflow.zip -d "$DESTDIR"
rm roboflow.zip

sed -i -e 's/train: \.\./train: \./' \
       -e 's/val: \.\./val: \./' \
       -e 's/test: \.\./test: \./' \
       "$DESTDIR/data.yaml"

# yolo task=detect mode=train model=$MODEL data=$DESTDIR/data.yaml epochs=50
# imgsz=640 batch=16 lr0=0.01
