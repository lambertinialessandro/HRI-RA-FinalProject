import cv2


class RecordVideoModule:
    def __init__(self, filename, size=(1920, 1080)):
        self._writer = cv2.VideoWriter(
            filename,
            cv2.VideoWriter_fourcc(*'mp4v'),
            24,
            (size[0], size[1])
        )

    def write_frame(self, frame):
        self._writer.write(frame)

    def end(self):
        self._writer.release()
