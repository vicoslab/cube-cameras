#!/usr/bin/env python3
from vapix_python.VapixAPI import VapixAPI
from vapix_python.PTZControl import PTZControl
import os, cv2

import numpy as np

import echolib

from echolib.camera import FramePublisher, Frame

class PTZCameraHandler():
    def __init__(self, host, user="", password=""):
        self.api = VapixAPI(host, user, password)
        self.control = PTZControl(self.api)
    
    def command_callback(self, message):

        command = echolib.MessageReader(message).readString().split(" ")
        
        if command[0] == "relative":
            pan, tilt, zoom, speed = map(float, command[1:])
            self.control.relative_move(pan, tilt, zoom, speed)
        elif command[0] == "absolute":
            pan, tilt, zoom, speed = map(int, command[1:])
            self.control.area_zoom(pan, tilt, zoom, speed)

def main():

    host = "192.168.0.90"

    handler = PTZCameraHandler(host)

    loop   = echolib.IOLoop()
    client = echolib.Client()
    loop.add_handler(client)

    output = FramePublisher(client, "camera_stream_ptz")
    command_input  = echolib.Subscriber(client, "camera_control_ptz", "string", handler.command_callback)

    stream_url = f'http://{host}/mjpg/video.mjpg'
    stream = cv2.VideoCapture(stream_url)

    loop.wait(100)

    while loop.wait(10) and stream.isOpened():
        
        ret, img = stream.read()
        if ret:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            output.send(Frame(image = img))

    print("Stopped streaming?")

if __name__=='__main__':
    main()
