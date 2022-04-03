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
        pass

    @staticmethod
    def create(type_input, drone=None, capture_api=None):
        stream = None
        command_recognition = None
        control = None
        if type_input == GlobalFactory.VideoDrone:
            stream = StreamFactory.create(StreamFactory.VideoDrone, drone)
            command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.Video)
            control = ControlModule.ControlModule(drone)
        elif type_input == self.VideoPC:
            stream = self.sf.create(StreamFactory.VideoPC, capture_api)
            command_recognition = self.crf.create(CommandRecognitionFactory.Video)
            control = ControlModule.ControlModule(drone)
        elif type_input == self.AudioPC:
            stream = self.sf.create(StreamFactory.AudioPC)
            command_recognition = self.crf.create(CommandRecognitionFactory.Audio)
            control = ControlModule.ControlModule(drone)

        return stream, command_recognition, control






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
