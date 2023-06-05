#!/usr/bin/env python3
import os
import time
import echolib
import numpy as np
import pyrealsense2 as rs
from echolib.camera import FramePublisher, Frame

DS5_product_ids = ["0AD1", "0AD2", "0AD3", "0AD4", "0AD5", "0AF6", "0AFE", "0AFF", "0B00", "0B01", "0B03", "0B07", "0B3A", "0B5C"]

def find_device_that_supports_advanced_mode() :
    ctx = rs.context()
    ds5_dev = rs.device()
    devices = ctx.query_devices()
    for dev in devices:
        if dev.supports(rs.camera_info.product_id) and str(dev.get_info(rs.camera_info.product_id)) in DS5_product_ids:
            if dev.supports(rs.camera_info.name):
                print("Found device that supports advanced mode:", dev.get_info(rs.camera_info.name))
            return dev
    raise Exception("No D400 product line device that supports advanced mode was found")

def turn_on_advanced_mode(device):
    advnc_mode = rs.rs400_advanced_mode(device)
    print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")

    while not advnc_mode.is_enabled():
        print("Trying to enable advanced mode...")
        advnc_mode.toggle_advanced_mode(True)
        # At this point the device will disconnect and re-connect.
        print("Sleeping for 5 seconds...")
        time.sleep(5)
        # The 'dev' object will become invalid and we need to initialize it again
        dev = find_device_that_supports_advanced_mode()
        advnc_mode = rs.rs400_advanced_mode(device)
        print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")

    return advnc_mode

class RealSenseCamera:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

        self.pipeline.start(self.config)

    def load_config(self):
        device = find_device_that_supports_advanced_mode()
        advnc_mode = turn_on_advanced_mode(device)

        with open("/opt/config.json") as f:
            print("Loading config from /opt/config.json")
            json_string = f.read()
            json_string = json_string.replace("'", '"')
            advnc_mode.load_json(json_string)

    def get_frames(self):
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        depth_image = np.array(depth_frame.get_data())
        color_image = np.array(color_frame.get_data())

        return color_image, depth_image

def main():
    loop = echolib.IOLoop()
    client = echolib.Client()
    loop.add_handler(client)

    output_rgb = FramePublisher(client, "realsense_rgb")
    output_depth = FramePublisher(client, "realsense_depth")

    camera = RealSenseCamera()

    if os.path.exists("/opt/config.json"):
        camera.load_config()

    loop.wait(10)

    while loop.wait(10):
        color, depth = camera.get_frames()

        output_rgb.send(Frame(image=color))
        output_depth.send(Frame(image=depth))

if __name__ == "__main__":
    main()
