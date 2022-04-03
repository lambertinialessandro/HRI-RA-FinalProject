import sys

from abc import ABC, abstractmethod

from modules.hand_traking.HandTrakingModule import HandDetector

sys.path.append('../../')


class AbstractVideoCommandRecognition(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_command(self, frame):
        pass


class VideoCommandRecognition(AbstractVideoCommandRecognition):
    def __init__(self):
        super().__init__()
        self.detector = HandDetector(detection_con=.8, track_con=.8)

    def get_command(self, frame):
        self.detector.analize_frame(frame, flip_type=True)
        command = self.detector.execute(frame)

        return command


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
