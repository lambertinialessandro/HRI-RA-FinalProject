# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 12:43:10 2022

@author: lambe
"""

import sys
sys.path.append('../')

from modules.stream.StreamFactory import StreamFactory
from modules.command_recognition.CommandRecognitionFactory import CommandRecognitionFactory
from modules.control import ControlModule


class GlobalFactory:
    VideoDrone = "VideoDrone"
    VideoPC = "VideoPC"
    AudioPC = "AudioPC"

    def __init__(self):
        self.sf = StreamFactory()
        self.crf = CommandRecognitionFactory()

    def create(self, type_input, drone=None, CaptureAPI=None):
        stream = None
        command_recognition = None
        control = None
        if type_input == self.VideoDrone:
            stream = self.sf.create(StreamFactory.VideoDrone, drone)
            command_recognition = self.crf.create(CommandRecognitionFactory.Video)
            control = ControlModule.ControlModule(drone)
        if type_input == self.VideoPC:
            stream = self.sf.create(StreamFactory.VideoPC, CaptureAPI)
            command_recognition = self.crf.create(CommandRecognitionFactory.Video)
            control = ControlModule.ControlModule(drone)
        if type_input == self.AudioPC:
            stream = self.sf.create(StreamFactory.AudioPC)
            command_recognition = self.crf.create(CommandRecognitionFactory.Audio)
            control = ControlModule.ControlModule(drone)

        return stream, command_recognition, control


if __name__ == "__main__":
    import cv2

    gf = GlobalFactory()
    stream, command_recognition, control = gf.create(
        GlobalFactory.VideoPC,
        CaptureAPI=cv2.CAP_DSHOW) # cv2.CAP_DSHOW, None

    try:
        while True:
            frame = stream.get_stream_frame()
            command = command_recognition.get_command(frame)

            cv2.imshow("Image", frame)
            key = cv2.waitKey(1)
            if key == 27: # ESC
                break
    finally:
        stream.release_stream()
        cv2.destroyAllWindows()
    pass