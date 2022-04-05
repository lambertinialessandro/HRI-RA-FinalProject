
from abc import ABC, abstractmethod
import pyttsx3
import keyboard

# TODO
# only for debug, to be deleted
import sys
sys.path.append('../../')

from modules.control.ControlModule import Command


class AbstractAudioCommandRecognition(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_command(self, text) -> tuple:
        pass


class AudioCommandRecognition(AbstractAudioCommandRecognition):
    def __init__(self):
        super().__init__()

        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)

    def __talk(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def get_command(self, text) -> tuple:
        print("Executing: "+text)
        # if 'start video' in command:
        #     self.__talk("Video started!")
        #     return Command.STREAM_ON
        # elif 'stop video' in command:
        #     self.__talk("Video stopped!")
        #     return Command.STREAM_OFF
        # el
        if 'take off' in text:
            self.__talk("Starting drone! wrwrwr")
            return Command.TAKE_OFF, None
        elif 'land' in text:
            self.__talk("Stopping drone! wrwrwr")
            return Command.LAND, None
        elif 'follow me' in text:
            self.__talk("i'm following")
            return Command.FOLLOW_ME, None
        elif 'turn off' in text:
            self.__talk("Stop execution")
            return Command.STOP_EXECUTION, None
        else:
            self.__talk('Please say the command again.')

        return None, None


# TODO
# only for debug, to be deleted
def main():
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
    print("Done!")


