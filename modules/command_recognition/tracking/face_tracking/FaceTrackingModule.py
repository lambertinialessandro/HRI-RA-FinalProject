import dataclasses
from abc import abstractmethod
import mediapipe as mp
from simple_pid import PID

# TODO: only for debug, to be deleted
import sys
sys.path.append('../../../')

from modules.command_recognition.tracking.AbstractModuleTracking import AbstractModuleTracking

# TODO: link between 2 files from different hierarchy maybe to be fixed
from modules.control.ControlModule import Command


class AbstractFaceTracking(AbstractModuleTracking):
    def __init__(self, model_selection=1, min_detection_confidence=0.5):
        super().__init__()

        self.bboxes = []
        self.face_detection = mp.solutions.face_detection.FaceDetection(
                model_selection=model_selection,
                min_detection_confidence=min_detection_confidence)

    @dataclasses.dataclass
    class _FaceBBox:
        x: float
        y: float
        w: float
        h: float
        detection: float

        @property
        def center(self) -> tuple:
            return self.x + self.w / 2, self.y + self.h / 2

        def unnormalized_center(self, shape) -> tuple:
            normalized_center = self.center
            return int(normalized_center[0] * shape[0]), int(normalized_center[1] * shape[1])

        def to_tuple(self) -> tuple:
            return self.x, self.y, self.w, self.h

        def to_unnormalized_tuple(self, shape) -> tuple:
            return int(self.x * shape[0]), int(self.y * shape[1]), \
                int(self.w * shape[0]), int(self.h * shape[1]),

        def normalize(self, width, height):
            self.x /= width
            self.w /= width

            self.y /= height
            self.h /= height

    def _analyze_frame(self, frame):
        h, w, _ = frame.shape
        results = self.face_detection.process(frame)

        self.bboxes = []
        if not results.detections:
            return

        # collecting infos
        for id, detection in enumerate(results.detections):
            bbox_c = detection.location_data.relative_bounding_box
            bbox = self._FaceBBox(x=bbox_c.xmin,
                                  y=bbox_c.ymin,
                                  w=bbox_c.width,
                                  h=bbox_c.height,
                                  detection=detection.score[0])
            self.bboxes.append(bbox)

    @abstractmethod
    def _execute(self) -> tuple:
        pass

    @abstractmethod
    def edit_frame(self, frame):
        pass

    def end(self):
        pass


import cv2

class PIDFaceTracking(AbstractFaceTracking):
    def __init__(self, model_selection=1, min_detection_confidence=0.5, sample_time=0.01):
        super().__init__(model_selection=model_selection, min_detection_confidence=min_detection_confidence)

        # 0.7, 0.01, 0.05
        self._pid_x = PID(0.7, 0.1, 0.05, sample_time=sample_time, setpoint=0.5)
        self._pid_y = PID(0.7, 0.1, 0.05, sample_time=sample_time, setpoint=0.5)
        self._pid_z = PID(0.7, 0.1, 0.05, sample_time=sample_time, setpoint=0.2)

        self.old_control_x = None
        self.old_control_y = None
        self.old_control_z = None

    def _execute(self) -> tuple:
        control = (0, 0, 0, 0)
        if len(self.bboxes) > 0:
            face = self.bboxes[0]
            face_center = face.center

            control_x = self._pid_x(face_center[0])
            print(face_center[1])
            control_y = self._pid_y(face_center[1])
            control_z = self._pid_z(face.w)

            if control_x == self.old_control_x and \
                    control_y == self.old_control_y and\
                    control_z == self.old_control_z:
                return Command.NONE, None

            if control_x != self.old_control_x:
                self.old_control_x = control_x
            if control_y != self.old_control_y:
                self.old_control_y = control_y
            if control_z != self.old_control_z:
                self.old_control_z = control_z

            control_x *= -100
            control_y *= 100
            control_z *= -100

            control_z = control_z if 0.1 < face.w and face.w < 0.3 else 0

            control = (0, int(control_z), int(control_y), int(control_x))
            print(control)

        return Command.SET_RC, control

    def edit_frame(self, frame):
        h, w, _ = frame.shape
        shape = (w, h)
        center = w//2, h//2

        for bbox in self.bboxes:
            cv2.circle(frame, bbox.unnormalized_center(shape),
                       2, (0, 255, 0), cv2.FILLED)
            cv2.rectangle(frame, bbox.to_unnormalized_tuple(shape), (255, 0, 255), 2)
            cv2.putText(frame, f'{int(bbox.detection*100)}%',
                        (int(bbox.x*w), int(bbox.y*h-20)), cv2.FONT_HERSHEY_PLAIN,
                        2, (255, 0, 255), 2)
            cv2.putText(frame, f'{bbox.w}',
                        (int(bbox.x*w), int(bbox.y*h-35)), cv2.FONT_HERSHEY_PLAIN,
                        2, (255, 0, 255), 2)

        if len(self.bboxes) > 0:
            cv2.line(frame, center, self.bboxes[0].unnormalized_center(shape),
                     (0, 0, 0), thickness=1)
            cv2.line(frame, center,(
                            int(center[0] - self.old_control_x*360),
                            int(center[1] - self.old_control_y*360)
                        ), (255, 0, 0), thickness=2)

        cv2.circle(frame, center, 5, (0, 0, 255), cv2.FILLED)
        return frame

def main():
    import cv2

    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, 1280//2)
        cap.set(4, 720//2)
        detector = PIDFaceTracking(min_detection_confidence=.8)

        while True:
            success, img = cap.read()
            _ = detector.execute(img)

            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == 27: # ESC
                break

        cap.release()
        cv2.destroyAllWindows()
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

