import dataclasses

import cv2
import mediapipe as mp


class FaceDetector:
    def __init__(self, model_selection=1, min_detection_confidence=.5):

        self.mp_draw = mp.solutions.drawing_utils
        self.mp_face_detection = mp.solutions.face_detection

        self.faceDetection = self.mp_face_detection.FaceDetection(
            model_selection=model_selection,
            min_detection_confidence=min_detection_confidence)

        self.all_bboxes = []
        self.results_data = False
        self.results = None

    def analyze_frame(self, frame):
        self.results = self.faceDetection.process(frame)

        self.all_bboxes = []
        if not self.results.detections:
            self.results_data = False
            return frame
        self.results_data = True

        # collecting infos
        h, w, c = frame.shape
        center = w//2, h//2
        for id, detection in enumerate(self.results.detections):
            bbox_c = detection.location_data.relative_bounding_box
            bbox = FaceDetector.BBox(x=int(bbox_c.xmin * w),
                                     y=int(bbox_c.ymin * h),
                                     w=int(bbox_c.width * w),
                                     h=int(bbox_c.height * h))
            self.all_bboxes.append(bbox)

            cv2.circle(frame, bbox.center, 2, (0, 255, 0), cv2.FILLED)
            cv2.rectangle(frame, bbox.to_tuple, (255, 0, 255), 2)
            cv2.putText(frame, f'{int(detection.score[0]*100)}%',
                        (bbox.x, bbox.y-20), cv2.FONT_HERSHEY_PLAIN,
                        2, (255, 0, 255), 2)
        cv2.circle(frame, center, 2, (0, 0, 255), cv2.FILLED)
        return frame

    def execute(self, frame):
        pass

    @dataclasses.dataclass
    class BBox:
        x: int
        y: int
        w: int
        h: int

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
            img = detector.analyze_frame(img)
            print(detector.all_bboxes)

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

