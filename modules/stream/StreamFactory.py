
# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

from modules.stream.VideoStreamModule import VideoDroneStream, WebcamStream
from modules.stream.AudioStreamModule import ComputerMicrophoneStream


class StreamFactory:
    VideoDrone = "VideoDrone"
    VideoPC = "VideoPC"
    AudioPC = "AudioPC"

    def __init__(self):
        pass

    @staticmethod
    def create(type_input, drone=None, input_idx=0, capture_api=None):
        stream = None
        if type_input == StreamFactory.VideoDrone:
            assert drone is not None
            stream = VideoDroneStream(drone)
        elif type_input == StreamFactory.VideoPC:
            stream = WebcamStream(input_idx=input_idx, capture_api=capture_api)
        elif type_input == StreamFactory.AudioPC:
            stream = ComputerMicrophoneStream()

        return stream


# TODO
# only for debug, to be deleted
if __name__ == "__main__":
    import cv2

    import platform
    capture_api = None
    if platform.system() == '':
        capture_api = cv2.CAP_DSHOW

    stream = StreamFactory.create(StreamFactory.VideoPC, capture_api=capture_api)

    try:
        while True:
            img = stream.get_stream_frame()
            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
    finally:
        stream.release_stream()
        cv2.destroyAllWindows()


