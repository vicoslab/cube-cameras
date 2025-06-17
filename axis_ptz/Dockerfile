ARG UBUNTU_VERSION=24.04
FROM vicoslab/echolib:${UBUNTU_VERSION}

RUN apt update && apt install ffmpeg libsm6 libxext6 -y --no-install-recommends
RUN python3 -m pip install vapix_python ultralytics --break-system-packages

WORKDIR /opt

COPY yolo11s.pt /opt/
COPY test.py /opt/
COPY track_test.py /opt/
COPY camera.py /opt/

ENTRYPOINT [ "python3", "camera.py" ]