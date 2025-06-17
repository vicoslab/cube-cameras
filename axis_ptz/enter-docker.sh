#!/usr/bin/env bash
docker run -it --rm -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY --network host --gpus all --entrypoint bash camera-ptz