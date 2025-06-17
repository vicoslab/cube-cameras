import os
import cv2
import time
import numpy as np

from vapix_python.VapixAPI import VapixAPI
from vapix_python.PTZControl import PTZControl
from ultralytics import YOLO

def generate_colors(num_classes):
	"""Generate a list of unique colors for the given number of classes."""
	np.random.seed(42)  # For reproducibility
	colors = np.random.randint(0, 255, size=(num_classes, 3), dtype='uint8')
	return colors

def display_detections(model, frame, results, colors):
	"""Draw bounding boxes and labels on the frame."""
	for result in results:
		boxes = result.boxes.xyxy.cpu().numpy()  # Convert to numpy (x1, y1, x2, y2)
		scores = result.boxes.conf.cpu().numpy()  # Confidence scores
		labels = result.boxes.cls.cpu().numpy()  # Class IDs
		
		for box, score, label in zip(boxes, scores, labels):
			x1, y1, x2, y2 = map(int, box)
			
			# Get the color for the current class
			color = tuple(int(c) for c in colors[int(label)])
			
			# Draw the bounding box
			cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
			
			# Display label and confidence score
			text = f"{model.names[int(label)]}: {score:.2f}"
			cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

	return frame


def get_people(results):
	people_coords = []

	for result in results:
		boxes = result.boxes.xyxy.cpu().numpy()  # Convert to numpy (x1, y1, x2, y2)
		scores = result.boxes.conf.cpu().numpy()  # Confidence scores
		labels = result.boxes.cls.cpu().numpy()  # Class IDs
		
		for box, score, label in zip(boxes, scores, labels):
			if model.names[int(label)] == "person" and score > 0.6:
				x1, y1, x2, y2 = map(int, box)
				people_coords.append(((x1+x2)/2,(y1+y2)/2))

	return people_coords

def move_forward():
	control.absolute_move(-60, 16, 1.0, speed)

IP = '192.168.0.90'
speed = 20

sent_stamp = time.time()

control = PTZControl(VapixAPI(IP, '', ''))
control.set_autofocus(True)
move_forward()

stream_url = f'http://{IP}/mjpg/video.mjpg'

model = YOLO("yolo11s.pt")
class_colors = generate_colors(len(model.names))

stream = cv2.VideoCapture(stream_url)
while (stream.isOpened()):

	#print(control.get_current_ptz())
	
	ret, img = stream.read()
	if ret:

		results = model.predict(img, verbose=False)
		display_detections(model, img, results, class_colors)
		cv2.imshow('Video Stream Monitor', img)
		cv2.waitKey(1)

		deltatime = time.time() - sent_stamp 

		people = get_people(results)
		if len(people) > 0 and deltatime > 0.3:
			sent_stamp = time.time()
			pos = people[0] #just move to the first person for now
			control.center_move(pos[0], pos[1], speed)

		#haven't seen anyone for a bit?
		if deltatime > 40 and deltatime < 41:
			sent_stamp -= 2
			move_forward()
			print("Resetting!")

