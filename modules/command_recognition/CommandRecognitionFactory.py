# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

from modules.command_recognition.CommandRecognitionModule \
    import VideoCommandRecognition, AudioCommandRecognition

from modules.command_recognition.tracking.TrackingFactory import VideoTrackingFactory

class CommandRecognitionFactory:
    Video = "Video"
    Audio = "Audio"

    def __init__(self):
        pass

    @staticmethod
    def create(type_input):
        command_recognition = None
        if type_input == CommandRecognitionFactory.Video:
            frame_tracker = VideoTrackingFactory.create(VideoTrackingFactory.Face)
            command_recognition = VideoTrackingFactory.create(VideoTrackingFactory.Face)
            tracking_edit_frame = VideoTrackingFactory.create(VideoTrackingFactory.Face)
        elif type_input == CommandRecognitionFactory.Audio:
            frame_tracker,\
            command_recognition,\
            tracking_edit_frame = AudioCommandRecognition()

        return frame_tracker, command_recognition, tracking_edit_frame


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


