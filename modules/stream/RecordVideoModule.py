
import cv2
import os


class RecordVideoModule:
    def __init__(self, filename, size=(1920, 1080)):
        self._writer = cv2.VideoWriter(
            os.path.join("video_out", filename),
            cv2.VideoWriter_fourcc(*'mp4v'),
            24,
            (size[0], size[1])
        )

        self.is_running = True

    def write_frame(self, frame):
        self._writer.write(frame)

    def end(self):
        if self.is_running:
            self.is_running = False
            self._writer.release()
