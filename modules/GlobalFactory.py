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
        control_module = ControlModule.ControlModule(drone)

        if type_input == GlobalFactory.VideoDrone:
            stream_module = StreamFactory.create(StreamFactory.VideoDrone, drone)
            command_recognition_module = CommandRecognitionFactory.create(CommandRecognitionFactory.Video)
            template_pattern = VideoTemplatePattern(stream_module,
                                                    command_recognition_module,
                                                    control_module,
                                                    drone)
        elif type_input == GlobalFactory.VideoPC:
            stream_module = StreamFactory.create(StreamFactory.VideoPC, capture_api)
            command_recognition_module = CommandRecognitionFactory.create(CommandRecognitionFactory.Video)
            template_pattern = VideoTemplatePattern(stream_module,
                                                    command_recognition_module,
                                                    control_module,
                                                    drone)
        elif type_input == GlobalFactory.AudioPC:
            stream_module = StreamFactory.create(StreamFactory.AudioPC)
            command_recognition_module = CommandRecognitionFactory.create(CommandRecognitionFactory.Audio)
            template_pattern = AudioTemplatePattern(stream_module,
                                                    command_recognition_module,
                                                    control_module,
                                                    drone)
        else:
            raise ValueError(f"Type input '{type_input}' not accepted")

        return template_pattern


if __name__ == "__main__":
    import cv2

    import platform
    capture_api = None
    if platform.system() == '':
        capture_api = cv2.CAP_DSHOW

    templatye_pattern = GlobalFactory.create(GlobalFactory.VideoDrone, capture_api=capture_api)

    templatye_pattern.execute()
