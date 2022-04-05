
# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

from modules.command_recognition.CommandRecognitionModule \
    import VideoCommandRecognition, AudioCommandRecognition


class CommandRecognitionFactory:
    Video = "Video"
    Audio = "Audio"

    def __init__(self):
        pass

    @staticmethod
    def create(type_input):
        command_recognition = None
        if type_input == CommandRecognitionFactory.Video:
            command_recognition = VideoCommandRecognition()
        elif type_input == CommandRecognitionFactory.Audio:
            command_recognition = AudioCommandRecognition()

        return command_recognition


# TODO
# only for debug, to be deleted
if __name__ == "__main__":
    import cv2
    from modules.stream.StreamFactory import StreamFactory

    stream = StreamFactory.create(StreamFactory.VideoPC, capture_api=cv2.CAP_DSHOW)  # cv2.CAP_DSHOW, None
    command_recognition = CommandRecognitionFactory.create(CommandRecognitionFactory.Video)

    try:
        while True:
            frame = stream.get_stream_frame()
            command = command_recognition.get_command(frame)

            cv2.imshow("Image", frame)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
    finally:
        stream.release_stream()
        cv2.destroyAllWindows()


