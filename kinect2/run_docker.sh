#!/bin/bash
xhost +

docker run -it --rm \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /tmp/echo.sock:/tmp/echo.sock \
    --device /dev/bus/usb:/dev/bus/usb \
    --env DISPLAY=$DISPLAY \
    camera-kinect2

xhost -
