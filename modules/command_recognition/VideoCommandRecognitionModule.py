
# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

from abc import ABC, abstractmethod

from modules.command_recognition.TrackingFactory import TrackingFactory


class AbstractVideoCommandRecognition(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_command(self, frame) -> tuple:
        pass


class VideoCommandRecognition(AbstractVideoCommandRecognition):
    def __init__(self):
        super().__init__()

        self.current_tracking_type = TrackingFactory.Face
        self.detector = TrackingFactory.create(None)

        self._build_detector()

    def _build_detector(self):
        self.detector = TrackingFactory.create(self.current_tracking_type)

    def update_detector(self, tracking_type):
        self.current_tracking_type = tracking_type
        self._build_detector()

    def get_command(self, frame) -> tuple:
        command, value = self.detector.execute(frame)
        return command, value


# TODO
# only for debug, to be deleted
def main():
    import cv2

    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, 1280//2)
        cap.set(4, 720//2)
        vcr = VideoCommandRecognition()

        while True:
            success, frame = cap.read()
            command = vcr.get_command(frame)
            print(command)

            cv2.imshow("Image", frame)
            key = cv2.waitKey(1)
            if key == 27: # ESC
                break

        cap.release()
        cv2.destroyAllWindows()
    except:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()


