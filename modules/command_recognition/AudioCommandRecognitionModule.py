
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

        self.done = False
        def my_keyboard_hook(keyboard_event):
            #print("Name:", keyboard_event.name)
            #print("Scan code:", keyboard_event.scan_code)
            #print("Time:", keyboard_event.time)

            if keyboard_event.scan_code == 1: # Esc
                print("Esc pressed!")
                self.done = True

        keyboard.hook(my_keyboard_hook)

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
            keyboard.unhook_all()
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


