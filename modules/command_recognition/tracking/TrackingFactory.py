
# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

from modules.command_recognition.tracking.AbstractModuleTracking import EmptyTracking
from modules.command_recognition.tracking.face_tracking.FaceTrackingModule import PIDFaceTracking
from modules.command_recognition.tracking.hand_tracking.HandTrackingModule import HandTracking
from modules.command_recognition.tracking.holistic_tracking.HolisticModule import HolisticTracking


class VideoTrackingFactory:
    Face = "Face"
    Hand = "Hand"
    Holistic = "Holistic"

    def __init__(self):
        pass

    @staticmethod
    def create(type_input):
        tracking = None
        if type_input == VideoTrackingFactory.Face:
            tracking = PIDFaceTracking(min_detection_confidence=0.6)
        elif type_input == VideoTrackingFactory.Hand:
            tracking = HandTracking(detection_con=.8, track_con=.8, flip_type=True)
        elif type_input == VideoTrackingFactory.Holistic:
            tracking = HolisticTracking(enable_segmentation=False, refine_face_landmarks=False,
                         min_tracking_confidence=.8, min_detection_confidence=.8,
                         flip_type=True)
        else:
            tracking = EmptyTracking()

        return tracking


if __name__ == "__main__":
    import cv2
    from modules.stream.StreamFactory import StreamFactory

    stream = StreamFactory.create(StreamFactory.VideoPC, capture_api=cv2.CAP_DSHOW)  # cv2.CAP_DSHOW, None

    detector = VideoTrackingFactory.create(VideoTrackingFactory.Hand)

    try:
        while True:
            frame = stream.get_stream_frame()

            command = detector.execute(frame)
            frame = detector.edit_frame(frame)

            cv2.imshow("Image", frame)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
    finally:
        stream.release_stream()
        cv2.destroyAllWindows()
