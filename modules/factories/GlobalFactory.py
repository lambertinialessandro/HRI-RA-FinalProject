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
        # self.crf = ControlRecognitionFactory()

    def create_input(self, type_media, drone=None):
        stream = None
        command_recognition = None
        control = None
        if type_media == self.VideoDrone:
            stream = self.sf.create_input(StreamFactory.VideoDrone, drone)
            # command_recognition = self.crf.createInput(ControlRecognitionFactory.Video)
            control = ControlModule.ControlModule(drone)
        if type_media == self.VideoPC:
            stream = self.sf.create_input(StreamFactory.VideoPC)
            # command_recognition = self.crf.createInput(ControlRecognitionFactory.Video)
            control = ControlModule.ControlModule(drone)
        if type_media == self.AudioPC:
            stream = self.sf.create_input(StreamFactory.AudioPC)
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