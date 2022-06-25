
import os
import imageio


class RecordVideoModule:
    def __init__(self, filename, size=(1920, 1080)):
        self.video = imageio.get_writer(os.path.join("video_out", filename),
                                        fps=24)
        self.is_running = True

    def write_frame(self, frame):
        self.video.append_data(frame)

    def end(self):
        if self.is_running:
            self.is_running = False
            self.video.close()
