# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 14:19:26 2022

@author: lambe
"""

import sys

from modules.stream.VideoStreamModule import VideoDroneStream, WebcamStream
from modules.stream.AudioStreamModule import ComputerMicrophoneStream

sys.path.append('../../')


class StreamFactory:
    VideoDrone = "VideoDrone"
    VideoPC = "VideoPC"
    AudioPC = "AudioPC"

    def __init__(self):
        pass

    @staticmethod
    def create(type_input, drone=None, capture_api=None):
        stream = None
        if type_input == StreamFactory.VideoDrone:
            assert drone is not None
            stream = VideoDroneStream(drone)
        elif type_input == StreamFactory.VideoPC:
            stream = WebcamStream(capture_api=capture_api)
        elif type_input == StreamFactory.AudioPC:
            stream = ComputerMicrophoneStream()

        return stream


if __name__ == "__main__":
    import cv2

    import platform
    capture_api = None
    if platform.system() == '':
        capture_api = cv2.CAP_DSHOW

    stream = StreamFactory.create(StreamFactory.VideoPC, capture_api=capture_api)

    try:
        while True:
            img = stream.get_stream_frame()
            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
    finally:
        stream.release_stream()
        cv2.destroyAllWindows()
