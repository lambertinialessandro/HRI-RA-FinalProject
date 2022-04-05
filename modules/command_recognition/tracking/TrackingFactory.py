
# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

from modules.command_recognition.tracking.AbstractModuleTracking import AbstractModuleTracking
from modules.command_recognition.tracking.face_tracking.FaceTrackingModule import FaceTracking
from modules.command_recognition.tracking.hand_tracking.HandTrackingModule import HandTracking
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
        detector = None
        if type_input == TrackingFactory.Face:
            detector = FaceTracking(min_detection_confidence=0.6)
        elif type_input == TrackingFactory.Hand:
            detector = HandTracking(detection_con=.8, track_con=.8, flip_type=True)
        # elif type_input == TrackingFactory.Holistic:
        #     detector = HolisticTracking()
        else:
            detector = EmptyTracking()

        return detector


# TODO
# only for debug, to be deleted
if __name__ == "__main__":
    import cv2
    from modules.stream.StreamFactory import StreamFactory

    stream = StreamFactory.create(StreamFactory.VideoPC, capture_api=cv2.CAP_DSHOW)  # cv2.CAP_DSHOW, None

    detector = TrackingFactory.create(TrackingFactory.Hand)

    try:
        while True:
            frame = stream.get_stream_frame()

            detector._analyze_frame(frame)
            command = detector.execute(frame)

            cv2.imshow("Image", frame)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
    finally:
        stream.release_stream()
        cv2.destroyAllWindows()


