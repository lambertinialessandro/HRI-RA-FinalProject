
# TODO
# only for debug, to be deleted
import sys
sys.path.append('../')

from modules.command_recognition.FaceCommandRecognition import PIDFaceCommandRecognition
from modules.command_recognition.HandCommandRecognition import HandCommandRecognition
from modules.command_recognition.HolisticCommandRecognition import HolisticCommandRecognition


class VideoCommandRecognitionFactory:
    Face = "Face"
    Hand = "Hand"
    Holistic = "Holistic"

    def __init__(self):
        pass

    @staticmethod
    def create(type_input):
        tracking = None
        if type_input == VideoCommandRecognitionFactory.Face:
            tracking = PIDFaceCommandRecognition(min_detection_confidence=0.6)
        elif type_input == VideoCommandRecognitionFactory.Hand:
            tracking = HandCommandRecognition(detection_con=.8, track_con=.8, flip_type=True)
        elif type_input == VideoCommandRecognitionFactory.Holistic:
            tracking = HolisticCommandRecognition(enable_segmentation=False, refine_face_landmarks=False,
                                                  min_tracking_confidence=.8, min_detection_confidence=.8,
                                                  flip_type=True)

        return tracking


if __name__ == "__main__":
    import cv2
    from modules.stream.StreamFactory import StreamFactory

    stream = StreamFactory.create(StreamFactory.VideoPC, capture_api=cv2.CAP_DSHOW)  # cv2.CAP_DSHOW, None

    detector = VideoCommandRecognitionFactory.create(VideoCommandRecognitionFactory.Hand)

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
