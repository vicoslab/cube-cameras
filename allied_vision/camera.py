#!/usr/bin/env python3

from math import floor
import numpy as np
from json import load

import echolib

from vimba import Vimba, PixelFormat, FrameStatus, Camera

from echolib.camera import FramePublisher, Frame

def setup_software_triggering(cam: Camera):
    # Always set the selector first so that folling features are applied correctly!
    cam.TriggerSelector.set('FrameStart')

    # optional in this example but good practice as it might be needed for hadware triggering
    cam.TriggerActivation.set('RisingEdge')

    # Make camera listen to Software trigger
    cam.TriggerSource.set('Software')
    cam.TriggerMode.set('On')

class VimbaCameraHandler():

    def __init__(self):

        self.frame = None
        self.n_frames = 0

        self.camera: Camera = None

        self.command_chain = []

        self.commands = \
        {
            "ExposureAuto":     lambda camera, v: camera.ExposureAuto.set(v),
            "BalanceWhiteAuto": lambda camera, v: camera.BalanceWhiteAuto.set(v),
            "BalanceRatio":     lambda camera, v: camera.BalanceRatio.set(v),
            "ExposureTime":     lambda camera, v: camera.ExposureTime.set(v)
        }

    def frame_handler(self, camera, frame):
        if frame.get_status() == FrameStatus.Complete:
            frame.convert_pixel_format(PixelFormat.Rgb8)
            frame_copy = frame.as_numpy_ndarray()

            self.frame = np.array(frame_copy)

            self.n_frames += 1

        camera.queue_frame(frame)

    def callback_camera_input(self, message):

        command = echolib.MessageReader(message).readString().split(" ")

        value   = command[1]
        command = command[0]

        try:
            print(f"Got command: {command} -> {value}")

            if command == "ExposureAuto":
                self.commands[command](self.camera, value)
            elif command == "BalanceWhiteAuto":
                self.commands[command](self.camera, value)
            elif command == "BalanceRatio":
                value = float(value)

                self.commands[command](self.camera, value)
            elif command == "ExposureTime":
                value = float(value)

                self.commands[command](self.camera, value)

            self.camera.stop_streaming()

            self.camera.AcquisitionFrameRateEnable.set(True)
            range = self.camera.get_feature_by_name("AcquisitionFrameRate").get_range()
            fr = floor(range[1])

            print(f"Frame rate range: [{range[0]}, {range[1]}]: setting {fr}")

            try:
                self.camera.AcquisitionFrameRate.set(fr)
            except Exception as e:
                    print(f"[ERROR] Setting camera frame rate failed: {e}") 

            self.camera.start_streaming(self.frame_handler, buffer_count = 1) 

        except Exception as e:
            print(f"[ERROR] Error while setting {command} = {value} | error print -> {e}")
            

def setup_args():
    import argparse
    parser = argparse.ArgumentParser(prog = 'Vimba Camera Streamer')
    parser.add_argument('--config', default='/opt/config/camera0.json', help='Path to camera configuration json file')  
    
    args = parser.parse_args()
    
    return args

def main():
    args = setup_args()
    
    ###########################
    # Load camera parameters  #
    ###########################

    def cameraSetBalanceRatioOnChannel(cam,v,ch):
        cam.BalanceRatioSelector.set(ch)
        cam.BalanceRatio.set(v)

    config = load(open(args.config))
    config_set_functions = \
    {
        "ExposureAuto": lambda camera, v: camera.ExposureAuto.set(v),
        "ExposureTime": lambda camera, v: camera.ExposureTime.set(v),
        "BalanceWhiteAuto": lambda camera, v: camera.BalanceWhiteAuto.set(v),
        "BalanceRatio":     lambda camera, v: camera.BalanceRatio.set(v),
        "BalanceRatioRed":     lambda camera, v: cameraSetBalanceRatioOnChannel(camera,v,"Red"),
        "BalanceRatioBlue":     lambda camera, v: cameraSetBalanceRatioOnChannel(camera,v,"Blue"),
        "DeviceLinkThroughputLimit":  lambda camera, v: camera.DeviceLinkThroughputLimit.set(int(v)),
        "AcquisitionFrameRateEnable": lambda camera, v: camera.AcquisitionFrameRateEnable.set(bool(int(v)))
    }

    ###########################

    handler = VimbaCameraHandler()

    loop   = echolib.IOLoop()
    client = echolib.Client()
    loop.add_handler(client)

    output = FramePublisher(client, "camera_stream_0")
    command_input  = echolib.Subscriber(client, "camera_stream_0_input", "string", handler.callback_camera_input)
    command_output = echolib.Publisher(client, "camera_stream_0_output", "string")

    loop.wait(100)
    
    ###########################

    with Vimba.get_instance() as vimba_instance:

        vimba_cameras = vimba_instance.get_all_cameras()

        with vimba_cameras[0] as vimba_camera:

            handler.camera = vimba_camera
    
            ###########################
            # Grab relevant ranges
            ###########################

            for f in ["BalanceRatio", "ExposureTime"]:
                range = vimba_camera.get_feature_by_name(f).get_range()

                writer = echolib.MessageWriter()
                writer.writeString(f"{f}Range {range[0]} {range[1]}")

                command_output.send(writer)

            ###########################
            # Set default camera values
            ###########################

            for feature in config_set_functions:
                if feature in config:
                    try:
                        print(f"Setting default feature {feature} with {config[feature]}")

                        config_set_functions[feature](vimba_camera, config[feature])
                    except Exception as e:
                        print(f"[ERROR] Setting camera feature {feature} failer: {e}")

            
            # Send default values to ui
            writer = echolib.MessageWriter()
            writer.writeString(f"BalanceRatio {vimba_camera.BalanceRatio.get()}")
            command_output.send(writer)
            
            writer = echolib.MessageWriter()
            writer.writeString(f"ExposureTime {vimba_camera.ExposureTime.get()}")
            command_output.send(writer)

            ##############################
            # Get and set max frame rate #
            ##############################

            range = vimba_camera.get_feature_by_name("AcquisitionFrameRate").get_range()
            fr = floor(range[1])

            print(f"Frame rate range: [{range[0]}, {range[1]}]: setting {fr}")

            try:
                vimba_camera.AcquisitionFrameRate.set(fr)
            except Exception as e:
                    print(f"[ERROR] Setting camera frame rate failed: {e}")  
            
            ###########################
            # Send completed frames  #
            ###########################

            vimba_camera.start_streaming(handler.frame_handler, buffer_count = 100)

            while loop.wait(1):
                if handler.frame is not None:
                    output.send(Frame(image = handler.frame))

                    handler.frame = None
#                    print("got frame")
#                else:
#                    print("handler frame is none")


            ###########################
        
            vimba_camera.stop_streaming()
        
        print("Stopped streaming?")

if __name__=='__main__':
    main()
