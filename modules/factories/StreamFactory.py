# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 14:19:26 2022

@author: lambe
"""

from modules.VideoStreamModule import VideoDroneStream, WebcamStream
from modules.AudioStreamModule import ComputerMicrophoneStream


class StreamFactory:
    VideoDrone = "VideoDrone"
    VideoPC = "VideoPC"
    AudioPC = "AudioPC"

    def __init__(self):
        pass

    def create_input(self, type_input_media, drone=None):
        input_media = None
        if type_input_media == self.VideoDrone:
            assert drone is not None
            input_media = VideoDroneStream(drone)
        if type_input_media == self.VideoPC:
            input_media = WebcamStream()
        if type_input_media == self.AudioPC:
            input_media = ComputerMicrophoneStream()

        return input_media


if __name__ == "__main__":
    import cv2

    sf = StreamFactory()
    inputMedia = sf.create_input(StreamFactory.VideoPC)

    try:
        while True:
            img = inputMedia.get_stream_frame()
            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
    finally:
        inputMedia.release_stream()
        cv2.destroyAllWindows()
