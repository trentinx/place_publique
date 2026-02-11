#!/bin/bash

DATASET=$1
MODEL=yolov8n.pt

DESTDIR=datasets/${DATASET}
. .env


[ -d ${DESTDIR} ] && echo "${DESTDIR} already created" && exit 0


mkdir -p ${DESTDIR}
curl -L "https://${ROBOFLOW_HOST}/ds/${ROBOFLOW_DATASET}?key=${ROBOFLOW_API_KEY}" -o  roboflow.zip
unzip -q roboflow.zip -d ${DESTDIR} 
rm roboflow.zip

sed -i -e 's/train: \.\./train: \./' \
       -e 's/val: \.\./val: \./' \
       -e 's/test: \.\./test: \./' \
       ${DESTDIR}/data.yaml

yolo task=detect mode=train model=${MODEL} data=${DESTDIR}/data.yaml epochs=3
# imgsz=640 batch=16 lr0=0.01
