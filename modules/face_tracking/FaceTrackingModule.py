import dataclasses

import cv2
import mediapipe as mp

from simple_pid import PID

from modules.control.ControlModule import Command


class FaceTrackingModule:
    def __init__(self):
        self._detector = FaceDetector(min_detection_confidence=0.6)
        self._pid_x = PID(0.7, 0.01, 0.05, sample_time=0.01)
        self._pid_y = PID(0.7, 0.01, 0.05, sample_time=0.01)

        self.old_control_x = None
        self.old_control_y = None

    # TODO
    def execute(self, frame) -> tuple:
        goal_y = frame.shape[0] // 2
        goal_x = frame.shape[1] // 2

        self._pid_x.setpoint = goal_x
        self._pid_y.setpoint = goal_y

        bboxes = self._detector.analyze_frame(frame)

        if len(bboxes) > 0:
            face = bboxes[0]
            face_center = face.center

            control_x = self._pid_x(face_center[0])
            control_y = self._pid_y(face_center[1])

            if control_x == self.old_control_x and control_y == self.old_control_y:
                return Command.NONE, None

            if control_x != self.old_control_x:
                self.old_control_x = control_x
            if control_y != self.old_control_y:
                self.old_control_y = control_y

            control_x /= goal_x
            control_x *= -100

            control_y /= goal_y
            control_y *= 100

            control = (0, 0, int(control_y), int(control_x))

            return Command.SET_RC, control
        else:
            return Command.SET_RC, (0, 0, 0, 0)


class FaceDetector:
    def __init__(self, model_selection=1, min_detection_confidence=.5):
        self.face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection=model_selection,
            min_detection_confidence=min_detection_confidence)

    def analyze_frame(self, frame):
        h, w, c = frame.shape
        center = w//2, h//2
        results = self.face_detection.process(frame)

        all_bboxes = []
        if not results.detections:
            return all_bboxes

        # collecting infos
        for id, detection in enumerate(results.detections):
            bbox_c = detection.location_data.relative_bounding_box
            bbox = FaceDetector.BBox(x=int(bbox_c.xmin * w),
                                     y=int(bbox_c.ymin * h),
                                     w=int(bbox_c.width * w),
                                     h=int(bbox_c.height * h))
            all_bboxes.append(bbox)

            cv2.circle(frame, bbox.center, 2, (0, 255, 0), cv2.FILLED)
            cv2.rectangle(frame, bbox.to_tuple, (255, 0, 255), 2)
            cv2.putText(frame, f'{int(detection.score[0]*100)}%',
                        (bbox.x, bbox.y-20), cv2.FONT_HERSHEY_PLAIN,
                        2, (255, 0, 255), 2)

        cv2.circle(frame, center, 5, (0, 0, 255), cv2.FILLED)
        return all_bboxes

    @dataclasses.dataclass
    class BBox:
        x: int
        y: int
        w: int
        h: int

        @property
        def center(self) -> tuple:
            return int(self.x + self.w // 2), int(self.y + self.h // 2)

        @property
        def to_tuple(self) -> tuple:
            return self.x, self.y, self.w, self.h


def main():
    try:
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280//2)
        cap.set(4, 720//2)
        detector = FaceDetector(min_detection_confidence=.8)

        while True:
            success, img = cap.read()
            bboxes = detector.analyze_frame(img)
            print(bboxes)

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

