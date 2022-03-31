# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 14:19:26 2022

@author: lambe
"""

import sys
sys.path.append('../../')

from modules.stream.VideoStreamModule import VideoDroneStream, WebcamStream
from modules.stream.AudioStreamModule import ComputerMicrophoneStream


class StreamFactory:
    VideoDrone = "VideoDrone"
    VideoPC = "VideoPC"
    AudioPC = "AudioPC"

    def __init__(self):
        pass

    def create(self, type_input, drone=None, CaptureAPI=None):
        stream = None
        if type_input == self.VideoDrone:
            assert drone is not None
            stream = VideoDroneStream(drone)
        elif type_input == self.VideoPC:
            stream = WebcamStream(CaptureAPI)
        elif type_input == self.AudioPC:
            stream = ComputerMicrophoneStream()

        return stream


if __name__ == "__main__":
    import cv2

    sf = StreamFactory()
    stream = sf.create(StreamFactory.VideoPC, CaptureAPI=cv2.CAP_DSHOW) # cv2.CAP_DSHOW, None

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
