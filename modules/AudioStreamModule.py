# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 12:07:52 2022

@author: lambe
"""

from abc import ABC, abstractmethod
import speech_recognition as sr
import pyttsx3


class AudioStreamModule(ABC):
    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def get_stream(cls):
        pass

    @classmethod
    @abstractmethod
    def release_stream(cls):
        pass


class AudioPcStream(AudioStreamModule):
    def __init__(self):
        super().__init__()
        self.name = "alexa"

        self.listener = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[1].id)

    def talk(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def take_command(self):
        command = ''
        try:
            with sr.Microphone() as source:
                print('listening...')
                voice = self.listener.listen(source)
                command = self.listener.recognize_google(voice)
                command = command.lower()
                print(command)
                if self.name in command:
                    command = command.replace(self.name, '')
        except:
            pass
        return command

    def get_stream(self):
        return self.take_command()

    def release_stream(self):
        pass



