# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 13:02:58 2022

@author: lambe
"""

import speech_recognition as sr
import pyttsx3

from djitellopy import Tello

import cv2
from threading import Thread

import HandTrakingModule

name = "alexa"
tello = Tello()
tello.connect()

keepRecording = True
tello.streamon()
frame_read = tello.get_frame_read()


def videoShow():
    try:
        while True:
            img = frame_read.frame
            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == 27: # ESC
                break
    finally:
        cv2.destroyAllWindows()

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
        tello.takeoff()

    elif 'land' in command:
        talk("Stopping drone! wrwrwr")
        tello.land()

    elif 'follow me' in command:
        talk("i'm following")
        tello.move_forward(100)

    elif 'turn off' in command:
        talk("Stop execution")
        return False

    else:
        talk('Please say the command again.')

    return True


state = True
while state:
    recorder = Thread(target=videoRecorder)
    recorder.start()

    state = run_alexa()

    recorder.join()