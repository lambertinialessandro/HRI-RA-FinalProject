import dataclasses
import cv2
from abc import abstractmethod
import mediapipe as mp
from simple_pid import PID

import time
import numpy as np

import sys
sys.path.append('../')

from modules.command_recognition.FaceGestureModule import Face
from modules.command_recognition.AbstractCommandRecognitionModule import AbstractCommandRecognitionModule

from modules.control.ControlModule import Command


class AbstractMediaPipeFaceCommandRecognition(AbstractCommandRecognitionModule):
    def __init__(self, model_selection=1, min_detection_confidence=0.5):
        super().__init__()

        self.face_detection = mp.solutions.face_detection.FaceDetection(
                model_selection=model_selection,
                min_detection_confidence=min_detection_confidence)

        self.all_faces = []

    def _analyze_frame(self, frame):
        self.all_faces = []

        h, w, _ = frame.shape
        results = self.face_detection.process(frame)

        if not results.detections:
            return

        # collecting infos
        for id, detection in enumerate(results.detections):
            bbox_c = detection.location_data.relative_bounding_box

            keypoints = [[lm.x, lm.y]for lm in detection.location_data.relative_keypoints]
            bbox = Face(x=bbox_c.xmin,
                        y=bbox_c.ymin,
                        w=bbox_c.width,
                        h=bbox_c.height,
                        detection=detection.score[0],
                        keypoints=keypoints)

            self.all_faces.append(bbox)

    @abstractmethod
    def _execute(self) -> tuple:
        pass

    @abstractmethod
    def edit_frame(self, frame):
        pass

    def end(self):
        pass


class PIDFaceCommandRecognition(AbstractMediaPipeFaceCommandRecognition):
    def __init__(self, model_selection=1, min_detection_confidence=0.5, sample_time=0.01):
        super().__init__(model_selection=model_selection, min_detection_confidence=min_detection_confidence)

        p = 0.7
        i = 0.
        d = 0.
        self._pid_x = PID(p, i, d, sample_time=sample_time, setpoint=0.5)
        self._pid_y = PID(p, i, d, sample_time=sample_time, setpoint=0.5)
        self._pid_z = PID(p, i, d, sample_time=sample_time, setpoint=0.2)

        self.old_control_x = 0
        self.old_control_y = 0
        self.old_control_z = 0

        self.old_value = (1, 0, 0, 0)

        self.face_state = "None"
        self.face_last_T = 0
        self.face_old = None
        self.face_old_ratio = 0

    def _execute(self) -> tuple:
        command = Command.SET_RC
        value = (0, 0, 0, 0)

        pos = self._get_face_min_dist()
        if pos != -1:
            face = self.all_faces[pos]
            self.face_old = face
            self.face_old_ratio = face.get_ratio()
            face_center = face.center

            if self.face_state == "None":
                self.face_state = "Detected"
                self.face_last_T = time.time()

            elif self.face_state == "Detected":
                face_elapsed_T = time.time() - self.face_last_T
                if face_elapsed_T > 2:
                    print("Locked")
                    self.face_state = "Locked"
                    self.face_last_T = time.time()

            elif self.face_state == "Lost":
                face_elapsed_T = time.time() - self.face_last_T
                if face_elapsed_T > 1:
                    print("locked")
                    self.face_state = "Locked"

            elif self.face_state == "Locked":
                self.face_last_T = time.time()

                control_x = self._pid_x(face_center[0])
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
                control_z *= 100 * 3

                value = (0, int(control_z), int(control_y), int(control_x))

        else:
            if self.face_state == "Detected":
                self.face_state = "None"
                print("none")

            elif self.face_state == "Locked":
                face_elapsed_T = time.time() - self.face_last_T
                if face_elapsed_T > 0.5:
                    print("lost")
                    self.face_state = "Lost"
                    self.face_last_T = time.time()
                else:
                    value = (0, 0,
                               int(self.old_control_y),
                               int(self.old_control_x))

            elif self.face_state == "Lost":
                print("none")
                face_elapsed_T = time.time() - self.face_last_T
                if face_elapsed_T > 2:
                    self.face_state = "None"


        if self.old_value == (0, 0, 0, 0):
            command = Command.KEEP_ALIVE

        self.old_value = value
        return command, value

    def _get_face_min_dist(self):
        pos = -1
        len_bboxes = len(self.all_faces)
        if len_bboxes > 0:
            if self.face_state == "None":
                pos = 0

            else:
                base_x, base_y, _, _ = self.face_old.to_tuple()

                mse = [round(np.sum(np.power([base_x-bbox.x, base_y-bbox.y], 2)), 3) for bbox in self.all_faces]
                pos_mse = np.argmin(mse)
                if mse[pos_mse] < 0.025:
                    pos = pos_mse

        return pos

    def edit_frame(self, frame):
        h, w, _ = frame.shape
        shape = (w, h)
        center = w//2, h//2

        i = 0
        for bbox in self.all_faces:
            cv2.rectangle(frame, bbox.to_unnormalized_tuple(shape), (255, 0, 255), 2)

            cv2.putText(frame, f'{i}. {round(bbox.x, 3)}, {round(bbox.y, 3)}%',
                        (int(bbox.x*w), int(bbox.y*h-20)), cv2.FONT_HERSHEY_PLAIN,
                        2, (255, 0, 255), 2)
            i = i + 1

            cv2.putText(frame, f'{bbox.w}',
                        (int(bbox.x*w), int(bbox.y*h-40)), cv2.FONT_HERSHEY_PLAIN,
                        2, (255, 0, 255), 2)

            cv2.circle(frame, (int(bbox.x*w), int(bbox.y*h)),
                       4, (0, 255, 0), cv2.FILLED)

            for lm in bbox.unnormalized_keypoints(shape):
                cv2.circle(frame, (lm[0], lm[1]),
                           2, (0, 255, 255), cv2.FILLED)

        if self.face_old is not None:
            base_x, base_y, _, _ = self.face_old.to_tuple()
            cv2.circle(frame, (int(base_x*w), int(base_y*h)),
                       4, (255, 0, 0), cv2.FILLED)

        pos = self._get_face_min_dist()
        if pos != -1:
            face = self.all_faces[pos]

            cv2.putText(frame, f"{self.face_state}",
                        (int(face.x*w), int(face.y*h-60)), cv2.FONT_HERSHEY_PLAIN,
                        2, (255, 0, 0), 2)

            if self.face_state == "Locked" or self.face_state == "Lost":
                cv2.circle(frame, face.unnormalized_center(shape),
                           2, (0, 255, 0), cv2.FILLED)

                cv2.line(frame, center, face.unnormalized_center(shape),
                         (0, 0, 0), thickness=1)
                cv2.line(frame, center, (
                                int(center[0] - self.old_control_x*360),
                                int(center[1] - self.old_control_y*360)
                            ), (255, 0, 0), thickness=2)

            cv2.circle(frame, self.face_old.unnormalized_center(shape),
                       2, (255, 0, 255), cv2.FILLED)

        cv2.circle(frame, center, 5, (0, 0, 255), cv2.FILLED)
        return frame
