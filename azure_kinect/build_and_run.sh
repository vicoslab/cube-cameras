#! /bin/bash
UBUNTU_VERSION="22.04"
ECHO="/tmp/echo.sock"
CAMERACONFIG="./config.py"

docker build -t camera_azure:${UBUNTU_VERSION} \
    --build-arg UBUNTU_VERSION=${UBUNTU_VERSION} \
    .

xhost +local:docker

docker run -it \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ${CAMERACONFIG}:/opt/config.py \
    -v ${ECHO}:${ECHO} \
    --device /dev/bus/usb:/dev/bus/usb \
    --gpus 'all,"capabilities=compute,utility,graphics"' \
    camera_azure:${UBUNTU_VERSION}

