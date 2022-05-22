
from enum import Enum

# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

from modules.stream.VideoStreamModule import VideoDroneStream, WebcamStream
from modules.stream.AudioStreamModule import ComputerMicrophoneStream


class StreamEnum(Enum):
    VideoDrone = "VideoDrone"
    VideoPC = "VideoPC"
    AudioPC = "AudioPC"


class StreamFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(type_stream: StreamEnum, drone=None, input_idx=0, capture_api=None):
        stream = None
        if type_stream == StreamEnum.VideoDrone:
            assert drone is not None
            stream = VideoDroneStream(drone)
        elif type_stream == StreamEnum.VideoPC:
            stream = WebcamStream(input_idx=input_idx, capture_api=capture_api)
        elif type_stream == StreamEnum.AudioPC:
            stream = ComputerMicrophoneStream()
        else:
            raise ValueError(f"Type stream '{type_stream}' not accepted")

        return stream


# TODO
# only for debug, to be deleted
if __name__ == "__main__":
    import cv2

    import platform
    capture_api = None
    if platform.system() == '':
        capture_api = cv2.CAP_DSHOW

    stream = StreamFactory.create(StreamEnum.VideoPC, capture_api=capture_api)

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


