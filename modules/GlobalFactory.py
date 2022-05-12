# TODO
# only for debug, to be deleted
import sys
sys.path.append('../')

from modules.drone.DroneFactory import DroneFactory

from modules.stream.StreamFactory import StreamFactory
from modules.command_recognition.CommandRecognitionFactory import CommandRecognitionFactory
from modules.control import ControlModule
from modules.TemplatePatternModule import TemplatePattern, VideoTemplatePattern, AudioTemplatePattern


class GlobalFactory:
    DJITello = "DJITello"
    FakeDrone = "FakeDrone"

    VideoDrone = "VideoDrone"
    VideoPC = "VideoPC"
    AudioPC = "AudioPC"

    def __init__(self):
        pass

    @staticmethod
    def create(type_drone, type_input, input_idx=0, capture_api=None):
        if type_drone == GlobalFactory.DJITello:
            drone, drone_edit_frame = DroneFactory.create(DroneFactory.DJITello, capture_api=capture_api)
        elif type_drone == GlobalFactory.FakeDrone:
            drone, drone_edit_frame = DroneFactory.create(DroneFactory.FakeDrone,
                                                          input_idx=input_idx, capture_api=capture_api)
        else:
            raise ValueError(f"Type drone '{type_drone}' not accepted")


        control_module = ControlModule.ControlModule(drone)

        if type_input == GlobalFactory.VideoDrone:
            stream_module = StreamFactory.create(StreamFactory.VideoDrone, drone=drone)
            command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.VideoHolistic)
            template_pattern = TemplatePattern(drone,
                                                    stream_module,
                                                    command_recognition,
                                                    control_module,
                                                    drone_edit_frame)
        elif type_input == GlobalFactory.VideoPC:
            stream_module = StreamFactory.create(StreamFactory.VideoPC, input_idx=input_idx,
                                                 capture_api=capture_api)
            command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.VideoHolistic)
            template_pattern = TemplatePattern(drone,
                                                    stream_module,
                                                    command_recognition,
                                                    control_module,
                                                    drone_edit_frame)
        elif type_input == GlobalFactory.AudioPC:
            stream_module = StreamFactory.create(StreamFactory.AudioPC)
            command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.Audio)
            template_pattern = AudioTemplatePattern(stream_module,
                                                    command_recognition,
                                                    control_module,
                                                    drone_edit_frame)
        else:
            raise ValueError(f"Type input '{type_input}' not accepted")

        return template_pattern


if __name__ == "__main__":
    import cv2

    import platform
    capture_api = None
    if platform.system() == 'Windows':
        capture_api = cv2.CAP_DSHOW

    templatye_pattern = GlobalFactory.create(GlobalFactory.VideoDrone, capture_api=capture_api)

    templatye_pattern.execute()
