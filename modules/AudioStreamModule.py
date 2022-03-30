from abc import ABC, abstractmethod

import speech_recognition
import speech_recognition as sr
# import pyttsx3


class AudioStreamModule(ABC):
    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def get_stream_word(cls):
        pass

    @classmethod
    @abstractmethod
    def release_stream(cls):
        pass


class ComputerMicrophoneStream(AudioStreamModule):
    def __init__(self):
        super().__init__()
        self.name = "mario"

        self.listener = sr.Recognizer()
        # self.engine = pyttsx3.init()
        # self.voices = self.engine.getProperty('voices')
        # self.engine.setProperty('voice', self.voices[1].id)

    # def talk(self, text):
    #     self.engine.say(text)
    #     self.engine.runAndWait()

    def get_stream_word(self):
        with sr.Microphone() as source:
            voice = self.listener.listen(source, timeout=5, phrase_time_limit=5)
            try:
                command = self.listener.recognize_google(voice)
            except speech_recognition.UnknownValueError:
                return ""
            command = command.lower()
            if self.name in command:
                command = command.replace(self.name, '')
        return command

    def release_stream(self):
        pass



