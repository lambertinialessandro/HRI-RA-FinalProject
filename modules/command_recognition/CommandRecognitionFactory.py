
from enum import Enum

# TODO
# only for debug, to be deleted
import sys
sys.path.append('../')

from modules.command_recognition.FaceCommandRecognition import PIDFaceCommandRecognition
from modules.command_recognition.HandCommandRecognition import MediaPipeHandCommandRecognition
from modules.command_recognition.HolisticCommandRecognition import HolisticCommandRecognition


class VCREnum(Enum):
    Face = "Face"
    Hand = "Hand"
    Holistic = "Holistic"


class VideoCommandRecognitionFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(type_input):
        command_recognition = None
        if type_input == VCREnum.Face:
            command_recognition = PIDFaceCommandRecognition(min_detection_confidence=0.6)
        elif type_input == VCREnum.Hand:
            command_recognition = MediaPipeHandCommandRecognition(detection_con=.8, track_con=.8, flip_type=True)
        elif type_input == VCREnum.Holistic:
            command_recognition = HolisticCommandRecognition(
                enable_segmentation=False,
                refine_face_landmarks=False,
                min_tracking_confidence=.8,
                min_detection_confidence=.8,
                flip_type=True
            )

        return command_recognition
