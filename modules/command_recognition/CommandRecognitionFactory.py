
from enum import Enum

# TODO
# only for debug, to be deleted
import sys
sys.path.append('../')

from modules.command_recognition.AbstractCommandRecognitionModule import EmptyCommandRecognition
from modules.command_recognition.FaceCommandRecognition import PIDFaceCommandRecognition
from modules.command_recognition.HandCommandRecognition import MediaPipeHandCommandRecognition
from modules.command_recognition.HolisticCommandRecognition import \
    HolisticCommandRecognition, HolisticRACommandRecognition


class VCREnum(Enum):
    Empty = "Empty"
    Face = "Face"
    Hand = "Hand"
    Holistic = "Holistic"
    Holistic_RA = "Holistic_RA"


class VideoCommandRecognitionFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(type_input):
        command_recognition = None
        if type_input == VCREnum.Empty:
            command_recognition = EmptyCommandRecognition()
        elif type_input == VCREnum.Face:
            command_recognition = PIDFaceCommandRecognition(min_detection_confidence=0.6)
        elif type_input == VCREnum.Hand:
            command_recognition = MediaPipeHandCommandRecognition(detection_con=.8, track_con=.8, flip_type=True)
        elif type_input == VCREnum.Holistic:
            command_recognition = HolisticCommandRecognition(enable_segmentation=False, refine_face_landmarks=False,
                                                  min_tracking_confidence=.8, min_detection_confidence=.8,
                                                  flip_type=True)
        elif type_input == VCREnum.Holistic_RA:
            command_recognition = HolisticRACommandRecognition(enable_segmentation=False, refine_face_landmarks=False,
                                                  min_tracking_confidence=.8, min_detection_confidence=.8,
                                                  flip_type=True)
        else:
            raise ValueError(f"Type input '{type_input}' not accepted")

        return command_recognition
