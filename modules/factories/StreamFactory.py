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

    def createInput(self, typeInputMedia, drone=None):
        inputMedia = None
        if typeInputMedia == self.VideoDrone:
            inputMedia = VideoDroneStream(drone)
        if typeInputMedia == self.VideoPC:
            inputMedia = WebcamStream()
        if typeInputMedia == self.AudioPC:
            inputMedia = ComputerMicrophoneStream()

        return inputMedia


if __name__ == "__main__":
    import cv2

    sf = StreamFactory()
    inputMedia = sf.createInput(StreamFactory.VideoPC)

    try:
        while True:
            img = inputMedia.get_stream_frame()
            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == 27: # ESC
                break
    finally:
        inputMedia.release_stream()
        cv2.destroyAllWindows()



