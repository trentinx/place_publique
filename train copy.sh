#!/bin/bash

DATASET=$1
MODEL=yolov8n.pt

DESTDIR=datasets/$DATASET
. env


[ -d $DESTDIR ] && echo "$DESTDIR already created" && exit 0


mkdir -p $DESTDIR
# curl -L "https://universe.roboflow.com/ds/O4ncNnKjMD?key=$ROBOFLOW_API_KEY" -o  roboflow.zip
curl -L "https://app.roboflow.com/ds/O4ncNnKjMD?key=$ROBOFLOW_API_KEY" -o roboflow.zip
# curl -L "https://app.roboflow.com/ds/O4ncNnKjMD?key=$ROBOFLOW_API_KEY" > roboflow.zip; unzip roboflow.zip; rm roboflow.zip
# "https://universe.roboflow.com/ds/O4ncNnKjMD?key=$ROBOFLOW_API_KEY"
# "https://app.roboflow.com/ds/O4ncNnKjMD?key=yAbfdfGogx"
unzip roboflow.zip -d $DESTDIR -q
rm roboflow.zip

sed -i -e 's/train: \.\./train: \./' \
       -e 's/val: \.\./val: \./' \
       -e 's/test: \.\./test: \./' \
       $DESTDIR/data.yaml

# yolo task=detect mode=train model=$MODEL data=$DESTDIR/data.yaml epochs=50
# imgsz=640 batch=16 lr0=0.01