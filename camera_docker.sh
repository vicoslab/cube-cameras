#! /bin/bash

ECHO="/tmp/echo.sock"

CAMERACONFIGFOLDER="$(dirname "$0")/allied_vision/config"

FLYCAPUTRECAMERADEVICE="/dev/bus/usb/002"
ALLIEDVISIONDEVICE="/dev/bus/usb"


docker run -it \
--device=${ALLIEDVISIONDEVICE}:${ALLIEDVISIONDEVICE} \
--mount src=${CAMERACONFIGFOLDER},target=/opt/config,type=bind \
--mount src=${ECHO},target=${ECHO},type=bind \
camerafeed_allied:v1

