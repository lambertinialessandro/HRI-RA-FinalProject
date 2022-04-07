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

        self.face_detection = mp.solutions.face_detection.FaceDetection(
                model_selection=model_selection,
                min_detection_confidence=min_detection_confidence)

    def _analyze_frame(self, frame):
        h, w, c = frame.shape
        center = w//2, h//2
        results = self.face_detection.process(frame)

        all_bboxes = []
        if not results.detections:
            return all_bboxes

        # collecting infos
        for id, detection in enumerate(results.detections):
            bbox_c = detection.location_data.relative_bounding_box
            bbox = self._FaceBBox(x=int(bbox_c.xmin * w),
                                  y=int(bbox_c.ymin * h),
                                  w=int(bbox_c.width * w),
                                  h=int(bbox_c.height * h))

            # Window.instance.draw_circle(bbox.center, 2, (0, 255, 0))
            # Window.instance.draw_rectangle(*bbox.to_tuple(), color=(255, 0, 255), thickness=2)
            # Window.instance.write(f"{int(detection.score[0]*100)}%", position=(bbox.x, bbox.y-20), font_scale=2,
            #                       color=(255, 0, 255), thickness=2)

            bbox.normalize(frame.shape[0], frame.shape[1])
            all_bboxes.append(bbox)

        # Window.instance.draw_circle(center, 5, (0, 0, 255))
        return all_bboxes

    @abstractmethod
    def _execute(self, frame) -> tuple:
        pass

    @dataclasses.dataclass
    class _FaceBBox:
        x: float
        y: float
        w: float
        h: float

        @property
        def center(self) -> tuple:
            center_x = self.x + self.w // 2
            center_y = self.y + self.h // 2
            if center_x < 0:
                center_x = int(center_x)
            if center_y < 0:
                center_y = int(center_y)
            return center_x, center_y

        def to_tuple(self) -> tuple:
            return self.x, self.y, self.w, self.h

        def normalize(self, width, height):
            self.x /= width
            self.w /= width

            self.y /= height
            self.h /= height


class PIDFaceTracking(AbstractFaceTracking):
    def __init__(self, model_selection=1, min_detection_confidence=0.5, sample_time=0.01, box_width=100):
        super().__init__(model_selection=model_selection, min_detection_confidence=min_detection_confidence)

        self._pid_x = PID(0.7, 0.01, 0.05, sample_time=sample_time, setpoint=0.5)
        self._pid_y = PID(0.7, 0.01, 0.05, sample_time=sample_time, setpoint=0.5)

        self.box_width = box_width
        self._pid_z = PID(0.7, 0.01, 0.05, sample_time=sample_time)

        self.old_control_x = None
        self.old_control_y = None
        self.old_control_z = None

    def _execute(self, bboxes) -> tuple:
        goal_z = self.box_width  # TODO

        if len(bboxes) > 0:
            face = bboxes[0]
            face_center = face.center
            print(face_center)

            control_x = self._pid_x(face_center[0])
            control_y = self._pid_y(face_center[1])
            control_z = self._pid_y(face.w)

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

            # control_z /= goal_z
            control_z *= 100

            control = (0, int(control_z), int(control_y), int(control_x))

            return Command.SET_RC, control
        else:
            return Command.SET_RC, (0, 0, 0, 0)


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

