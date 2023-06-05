#!/bin/bash

docker run -it --rm \
        -v /tmp/echo.sock:/tmp/echo.sock \
        camera-astra:latest