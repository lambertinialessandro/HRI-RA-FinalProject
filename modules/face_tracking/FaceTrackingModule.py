import dataclasses

import cv2
import mediapipe as mp


class FaceTrackingModule:
    pass


class FaceDetector:
    def __init__(self, model_selection=1, min_detection_confidence=.5):
        self.face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection=model_selection,
            min_detection_confidence=min_detection_confidence)

    def analyze_frame(self, frame):
        results = self.face_detection.process(frame)

        all_bboxes = []
        if not results.detections:
            return all_bboxes

        # collecting infos
        h, w, c = frame.shape
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

