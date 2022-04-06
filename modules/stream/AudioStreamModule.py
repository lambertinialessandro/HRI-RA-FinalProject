
from abc import ABC, abstractmethod

import speech_recognition as sr


class AbstractAudioStream(ABC):
    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def get_stream_word(self):
        pass

    @classmethod
    @abstractmethod
    def end(self):
        pass


class ComputerMicrophoneStream(AbstractAudioStream):
    def __init__(self, name = "mario"):
        super().__init__()
        self.name = name

        self.listener = sr.Recognizer()

    def get_stream_word(self):
        command = ''
        try:
            with sr.Microphone() as source:
                print("Listening...")
                voice = self.listener.listen(source, timeout=5, phrase_time_limit=5)
                try:
                    command = self.listener.recognize_google(voice)
                    print(command)
                except speech_recognition.UnknownValueError:
                    return ""
                command = command.lower()
                if self.name in command:
                    command = command.replace(self.name, '')
                else:
                    command = ''
        except:
            pass
        return command

    def end(self):
        pass


