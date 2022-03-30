# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 12:43:10 2022

@author: lambe
"""

from modules.factories.StreamFactory import StreamFactory
# from modules.factories.ControlRecognitionFactory import ControlRecognitionFactory
from modules import ControlModule

class GlobalFactory:
    VideoDrone = "VideoDrone"
    VideoPC = "VideoPC"
    AudioPC = "AudioPC"

    def __init__(self):
        self.sf = StreamFactory()
        #self.crf = ControlRecognitionFactory()

    def createInput(self, typeMedia, drone):
        stream = None
        command_recognition = None
        control = None
        if typeMedia == self.VideoDrone:
            stream = self.sf.createInput(StreamFactory.VideoDrone)
            # command_recognition = self.crf.createInput(ControlRecognitionFactory.Video)
            control = ControlModule.ControlModule(drone)
        if typeMedia == self.VideoPC:
            stream = self.sf.createInput(StreamFactory.VideoPC)
            # command_recognition = self.crf.createInput(ControlRecognitionFactory.Video)
            control = ControlModule.ControlModule(drone)
        if typeMedia == self.AudioPC:
            stream = self.sf.createInput(StreamFactory.AudioPC)
            # command_recognition = self.crf.createInput(ControlRecognitionFactory.Audio)
            control = ControlModule.ControlModule(drone)

        return stream, command_recognition, control


if __name__ == "__main__":
    # import cv2

    # fim = StreamFactory()
    # inputMedia = fim.createInput(StreamFactory.VideoPC)

    # try:
    #     while True:
    #         img = inputMedia.get_stream()
    #         cv2.imshow("Image", img)
    #         key = cv2.waitKey(1)
    #         if key == 27: # ESC
    #             break
    # finally:
    #     inputMedia.release_stream()
    #     cv2.destroyAllWindows()
    pass