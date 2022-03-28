# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 13:02:58 2022

@author: lambe
"""

# pip install speechRecognition
# pip install pyttsx3

# pip install pipwin
# pipwin install pyaudio

import speech_recognition as sr
import pyttsx3

import HandTrakingModule

name = "alexa"

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def talk(text):
    engine.say(text)
    engine.runAndWait()

def take_command():
    command = ''
    try:
        with sr.Microphone() as source:
            print('listening...')
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            print(command)
            if name in command:
                command = command.replace(name, '')
    except:
        pass
    return command

proc = None
def run_alexa():
    command = take_command()
    print("Executing: "+command)
    if 'start video' in command:
        talk("Starting video!")
        HandTrakingModule.main()

    elif 'stop video' in command:
        talk("Video stopped!")

    elif 'take off' in command:
        talk("Starting drone! wrwrwr")

    elif 'land' in command:
        talk("Stopping drone! wrwrwr")

    elif 'follow me' in command:
        talk("i'm following")

    elif 'turn off' in command:
        talk("Stop execution")
        return False

    else:
        talk('Please say the command again.')

    return True

state = True
while state:
    state = run_alexa()