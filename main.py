from modules import VideoStreamModule


import cv2


video_stream_module = VideoStreamModule.WebcamStream()

try:
    while True:
        cv2.imshow("Webcam", video_stream_module.get_stream())
except KeyboardInterrupt:
    pass

video_stream_module.release_stream()
