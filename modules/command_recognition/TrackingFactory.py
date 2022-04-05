
# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

from modules.command_recognition.AbstractModuleTracking import AbstractModuleTracking
from modules.command_recognition.face_tracking.FaceTrackingModule import FaceTracking
from modules.command_recognition.hand_tracking.HandTrackingModule import HandTracking
#from modules.command_recognition.holistic_tracking.HolisticModule import HolisticTracking


class EmptyTracking(AbstractModuleTracking):
    def _analyze_frame(self, frame):
        return

    def execute(self, frame) -> tuple:
        return None, None

class TrackingFactory:
    Face = "Face"
    Hand = "Hand"
    Holistic = "Holistic"

    def __init__(self):
        pass

    @staticmethod
    def create(type_input):
        command_recognition =  EmptyTracking()
        if type_input == TrackingFactory.Face:
            command_recognition = FaceTracking(min_detection_confidence=0.6)
        # elif type_input == TrackingFactory.Hand:
        #     command_recognition = HandTracking()
        # elif type_input == TrackingFactory.Holistic:
        #     command_recognition = HolisticTracking()

        return command_recognition


# TODO
# only for debug, to be deleted
if __name__ == "__main__":
    import cv2
    from modules.stream.StreamFactory import StreamFactory
    from modules.command_recognition.CommandRecognitionFactory import CommandRecognitionFactory

    stream = StreamFactory.create(StreamFactory.VideoPC, capture_api=cv2.CAP_DSHOW)  # cv2.CAP_DSHOW, None
    command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.Video)

    try:
        while True:
            frame = stream.get_stream_frame()
            command = command_recognition.get_command(frame)

            cv2.imshow("Image", frame)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
    finally:
        stream.release_stream()
        cv2.destroyAllWindows()


