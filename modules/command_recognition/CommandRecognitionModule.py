from abc import ABC, abstractmethod
import pyttsx3

# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

from modules.command_recognition.tracking.TrackingFactory import VideoTrackingFactory

# TODO
# link between 2 files from different hierarchy maybe to be fixed
from modules.control.ControlModule import Command


class AbstractCommandRecognition(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_command(self, frame) -> tuple:
        pass


class VideoCommandRecognition(AbstractCommandRecognition):
    def __init__(self):
        super().__init__()

        self.current_tracking_type = VideoTrackingFactory.Face
        self.detector = None

        self._build_detector()

    def _build_detector(self):
        self.detector = VideoTrackingFactory.create(self.current_tracking_type)

    def update_detector(self, tracking_type):
        self.current_tracking_type = tracking_type
        self._build_detector()

    def get_command(self, frame) -> tuple:
        command, value = self.detector.execute(frame)
        return command, value


class AudioCommandRecognition(AbstractCommandRecognition):
    def __init__(self):
        super().__init__()

        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)

        self.done = False

    def _talk(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def get_command(self, text) -> tuple:
        print("Executing: "+text)
        # if 'start video' in command:
        #     self._talk("Video started!")
        #     return Command.STREAM_ON
        # elif 'stop video' in command:
        #     self._talk("Video stopped!")
        #     return Command.STREAM_OFF
        # el
        if self.done or 'turn off' in text:
            self._talk("Stop execution")
            return Command.STOP_EXECUTION, None
        elif 'take off' in text:
            self._talk("Starting drone! wrwrwr")
            return Command.TAKE_OFF, None
        elif 'land' in text:
            self._talk("Stopping drone! wrwrwr")
            return Command.LAND, None
        elif 'follow me' in text:
            self._talk("i'm following")
            return Command.FOLLOW_ME, None
        else:
            self._talk('Please say the command again.')

        return Command.NONE, None


# TODO
# only for debug, to be deleted
def main():
    import cv2

    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, 1280//2)
        cap.set(4, 720//2)
        vcr = VideoCommandRecognition()

        while True:
            success, frame = cap.read()
            command = vcr.get_command(frame)
            # print(command)

            cv2.imshow("Image", frame)
            key = cv2.waitKey(1)
            if key == 27: # ESC
                vcr.end()
                break
    except:
        pass
    finally:
        vcr.end()
        cap.release()
        cv2.destroyAllWindows()

def main2():
    from modules.stream.StreamFactory import StreamFactory

    stream = StreamFactory.create(StreamFactory.AudioPC)
    acr = AudioCommandRecognition()

    state = True
    while state:
        text = stream.get_stream_word()
        command, value = acr.get_command(text)
        print(f"Command: {command}")

        if command == Command.STOP_EXECUTION:
            state = False

if __name__ == "__main__":
    main()


