from vapix_python.VapixAPI import VapixAPI
from vapix_python.PTZControl import PTZControl
import os, cv2
from ultralytics import YOLO
import numpy as np

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


# (-157.7625, -0.0, 1.0)

def construct_command_string(pan, tilt, zoom, brightness=5000, autofocus="on"):

	# s = f'pan={pan}\r\ntilt={tilt}\r\nzoom={zoom}\r\nbrightness={brightness}\r\nautofocus={autofocus}'
	s = f'pan={pan}\r\ntilt=-0.0000\r\nzoom={zoom}\r\nbrightness={brightness}\r\nautofocus={autofocus}'

	return s

def main():

	# Initialize the API caller with the base URL

	host = '192.168.0.90'
	user = ''
	password = ''

	zoom_delta = 100
	move_delta = 10
	speed = 20

	# vapix_api = VapixAPI(os.environ.get('host'), os.environ.get('user'), os.environ.get('password'))
	vapix_api = VapixAPI(host, user, password)

	print(vapix_api.ptz.get_current_ptz())

	control = PTZControl(vapix_api)

	cur_pos = control.get_current_position()
	# (-157.7625, -0.0, 1.0)

	stream_url = f'http://{host}/mjpg/video.mjpg'
	print(stream_url)

	model = YOLO("yolo11s.pt")

	class_colors = generate_colors(len(model.names))

	stream = cv2.VideoCapture(stream_url)
	while (stream.isOpened()):
		# pos = control.get_current_position()
		

		# Read a frame from the stream
		ret, img = stream.read()
		if ret: # ret == True if stream.read() was successful

			results = model.predict(img, verbose=False)

			display_detections(model, img, results, class_colors)

			cv2.imshow('Video Stream Monitor', img)
			key = cv2.waitKey(1)
			print(key)
			if key==27:
				exit()
			elif key==81: # left
				control.relative_move(-move_delta, 0, 0, speed)
			elif key==83: # right
				control.relative_move(move_delta, 0, 0, speed)
			elif key==82: # up
				control.relative_move(0, move_delta, 0, speed)
			elif key==84: # down
				control.relative_move(0, -move_delta, 0, speed)
			elif key==43: # +
				control.relative_move(0, 0, zoom_delta, speed)
			elif key==45: # -
				control.relative_move(0, 0, -zoom_delta, speed)


if __name__=='__main__':
	main()

