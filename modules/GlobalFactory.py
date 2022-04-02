# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 12:43:10 2022

@author: lambe
"""

import sys

from modules.stream.StreamFactory import StreamFactory
from modules.command_recognition.CommandRecognitionFactory import CommandRecognitionFactory
from modules.control import ControlModule
from modules.TemplatePatternModule import VideoTemplatePattern, AudioTemplatePattern

sys.path.append('../')


class GlobalFactory:
    VideoDrone = "VideoDrone"
    VideoPC = "VideoPC"
    AudioPC = "AudioPC"

    def __init__(self):
        self.crf = CommandRecognitionFactory()

    @staticmethod
    def create(drone=None, capture_api=None):
        stream_module = None
        command_recognition = None
        control_module = None
        template_pattern = None

        print("Which Input? \n"+
              "    1) VideoDrone \n"+
              "    2) VideoPC \n"+
              "    3) AudioPC \n")
        type_input = input('Input: ')

        if type_input == "1":  # VideoDrone
            stream_module = StreamFactory.create(StreamFactory.VideoDrone, drone=drone)
            command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.Video)
            control_module = ControlModule.ControlModule(drone)
            template_pattern = VideoTemplatePattern(stream_module,
                                                    command_recognition,
                                                    control_module,
                                                    drone)

        elif type_input == "2":  # VideoPC
            stream_module = StreamFactory.create(StreamFactory.VideoPC, capture_api=capture_api)
            command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.Video)
            control_module = ControlModule.ControlModule(drone)
            template_pattern = VideoTemplatePattern(stream_module,
                                                    command_recognition,
                                                    control_module,
                                                    drone)

        elif type_input == "3":  # AudioPC
            stream_module = StreamFactory.create(StreamFactory.AudioPC)
            command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.Audio)
            control_module = ControlModule.ControlModule(drone)
            template_pattern = AudioTemplatePattern(stream_module,
                                                    command_recognition,
                                                    control_module,
                                                    drone)

        return template_pattern


if __name__ == "__main__":
    import cv2

    import platform
    capture_api = None
    if platform.system() == '':
        capture_api = cv2.CAP_DSHOW

    templatye_pattern = GlobalFactory.create(capture_api=capture_api)

    templatye_pattern.execute()
