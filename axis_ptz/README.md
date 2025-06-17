This camera setup was adapted for vicos-cube from https://github.com/vicoslab/ptz_vicos.

#  AXIS 215 PTZ Resources

Manual: https://www.axis.com/dam/public/62/10/c9/axis-215ptz215ptz-e--users-manual-en-US-39697.pdf

Axis's Vapix library: https://github.com/derens99/vapix-python/tree/master

## Build docker
```bash
./build-docker.sh
```

## Run demos
```bash
# Enter docker environment
./enter-docker.sh

#WASD camera move, yolo detection
python3 test.py

#yolor person detection -> move camera to central pixel for tracking
python3 track_test.py
```
