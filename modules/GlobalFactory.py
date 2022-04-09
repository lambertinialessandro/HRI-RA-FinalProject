
# TODO
# only for debug, to be deleted
import sys
sys.path.append('../')

from modules.drone.DroneFactory import DroneFactory

from modules.stream.StreamFactory import StreamFactory
from modules.command_recognition.CommandRecognitionFactory import CommandRecognitionFactory
from modules.control import ControlModule
from modules.TemplatePatternModule import TemplatePattern, VideoTemplatePattern, AudioTemplatePattern

import cv2

class Displayer:
    def __init__(self, name="frame"):
        self.name = name

    def show(self, frame):
        cv2.imshow(self.name, frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            return False
        return True

    def end(self):
        cv2.destroyAllWindows()

class GlobalFactory:
    DJITello = "DJITello"
    FakeDrone = "FakeDrone"

    VideoDrone = "VideoDrone"
    VideoPC = "VideoPC"
    AudioPC = "AudioPC"

    def __init__(self):
        pass

    @staticmethod
    def create(type_drone, type_input, capture_api=None):
        if type_drone == GlobalFactory.DJITello:
            drone, drone_edit_frame = DroneFactory.create(DroneFactory.DJITello, capture_api=capture_api)
        elif type_drone == GlobalFactory.FakeDrone:
            drone, drone_edit_frame = DroneFactory.create(DroneFactory.FakeDrone, capture_api=capture_api)
        else:
            raise ValueError(f"Type drone '{type_drone}' not accepted")


        control_module = ControlModule.ControlModule(drone)
        displayer = Displayer()

        if type_input == GlobalFactory.VideoDrone:
            stream_module = StreamFactory.create(StreamFactory.VideoDrone, drone)
            frame_tracker,\
            command_recognition,\
            tracking_edit_frame = CommandRecognitionFactory.create(CommandRecognitionFactory.Video)
            template_pattern = TemplatePattern(stream_module,
                                                    frame_tracker,
                                                    command_recognition,
                                                    control_module,
                                                    tracking_edit_frame,
                                                    drone_edit_frame,
                                                    displayer)
        elif type_input == GlobalFactory.VideoPC:
            stream_module = StreamFactory.create(StreamFactory.VideoPC, capture_api)
            frame_tracker,\
            command_recognition,\
            tracking_edit_frame = CommandRecognitionFactory.create(CommandRecognitionFactory.Video)
            template_pattern = TemplatePattern(stream_module,
                                                    frame_tracker,
                                                    command_recognition,
                                                    control_module,
                                                    tracking_edit_frame,
                                                    drone_edit_frame,
                                                    displayer)
        elif type_input == GlobalFactory.AudioPC:
            stream_module = StreamFactory.create(StreamFactory.AudioPC)
            frame_tracker,\
            command_recognition,\
            tracking_edit_frame = CommandRecognitionFactory.create(CommandRecognitionFactory.Audio)
            template_pattern = AudioTemplatePattern(stream_module,
                                                    frame_tracker,
                                                    command_recognition,
                                                    control_module,
                                                    tracking_edit_frame,
                                                    drone_edit_frame,
                                                    displayer)
        else:
            raise ValueError(f"Type input '{type_input}' not accepted")

        return template_pattern


# TODO
# only for debug, to be deleted
if __name__ == "__main__":
    import cv2

    import platform
    capture_api = None
    if platform.system() == 'Windows':
        capture_api = cv2.CAP_DSHOW

    templatye_pattern = GlobalFactory.create(GlobalFactory.VideoDrone, capture_api=capture_api)

    templatye_pattern.execute()
