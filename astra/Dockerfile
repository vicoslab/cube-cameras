# Dockerfile modified from 
# https://github.com/IntelRealSense/librealsense/blob/master/scripts/Docker/Dockerfile

ARG UBUNTU_VERSION=20.04
ARG BASE_IMAGE=echolib:${UBUNTU_VERSION}

FROM $BASE_IMAGE

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -qq -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    freeglut3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /lib
RUN curl https://s3.amazonaws.com/com.occipital.openni/OpenNI-Linux-x64-2.2.0.33.tar.bz2 -o openni.tar.bz2
RUN tar -xf openni.tar.bz2 \
    && rm openni.tar.bz2

RUN mkdir -p /etc/udev/rules.d/
RUN cd OpenNI-Linux-x64-2.2 && ./install.sh

