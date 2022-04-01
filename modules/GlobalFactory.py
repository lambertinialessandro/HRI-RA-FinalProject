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
from modules.TemplatePatternModule import VideoTemplatePattern, AudioTemplatePattern


class GlobalFactory:
    VideoDrone = "VideoDrone"
    VideoPC = "VideoPC"
    AudioPC = "AudioPC"

    def __init__(self):
        self.sf = StreamFactory()
        self.crf = CommandRecognitionFactory()

    def create(self, drone=None, capture_api=None):
        stream_module = None
        command_recognition = None
        control_module = None
        templatye_pattern = None

        print("Which Input? \n"+
              "    1) VideoDrone \n"+
              "    2) VideoPC \n"+
              "    3) AudioPC \n")
        type_input = input('Input: ');

        if type_input == "1": #☻ VideoDrone
            stream_module = self.sf.create(StreamFactory.VideoDrone, drone=drone)
            command_recognition = self.crf.create(CommandRecognitionFactory.Video)
            control_module = ControlModule.ControlModule(drone)
            templatye_pattern = VideoTemplatePattern(stream_module, command_recognition, control_module)

        elif type_input == "2": # VideoPC
            stream_module = self.sf.create(StreamFactory.VideoPC, capture_api=capture_api)
            command_recognition = self.crf.create(CommandRecognitionFactory.Video)
            control_module = ControlModule.ControlModule(drone)
            templatye_pattern = VideoTemplatePattern(stream_module, command_recognition, control_module)

        elif type_input == "3": # AudioPC
            stream_module = self.sf.create(StreamFactory.AudioPC)
            command_recognition = self.crf.create(CommandRecognitionFactory.Audio)
            control_module = ControlModule.ControlModule(drone)
            templatye_pattern = AudioTemplatePattern(stream_module, command_recognition, control_module)

        return templatye_pattern


if __name__ == "__main__":
    import cv2

    import platform
    capture_api = None
    if platform.system() == '':
        capture_api = cv2.CAP_DSHOW

    gf = GlobalFactory()
    templatye_pattern = gf.create(capture_api=capture_api)

    templatye_pattern.execute()
