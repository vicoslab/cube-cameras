#!/bin/bash

docker run -it --rm \
        -v /dev:/dev \
        -v /tmp/echo.sock:/tmp/echo.sock \
        --device-cgroup-rule="c 81:* rmw" \
        --device-cgroup-rule="c 189:* rmw" \
        camera-realsense:latest
