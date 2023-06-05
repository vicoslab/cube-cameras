#!/bin/bash
xhost +

docker run -it --rm \
        -v /dev:/dev \
        --device-cgroup-rule="c 81:* rmw" \
        --device-cgroup-rule="c 189:* rmw" \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        calibration

