# simple example demonstrating how to control a Tello using your keyboard.
# For a more fully featured example see manual-control-pygame.py
#
# Use W, A, S, D for moving, E, Q for rotating and R, F for going up and down.
# When starting the script the Tello will takeoff, pressing ESC makes it land
#  and the script exit.

import cv2
import math
import time

import keyboard
import schedule

from djitellopy import Tello

global state
state = True
tello = Tello()
tello.connect()

battery = tello.get_battery()
height = tello.get_height()
temperature = tello.get_temperature()

def update_battery():
    global tello, battery
    battery = tello.get_battery()
def update_height():
    global tello, height
    height = tello.get_height()
def update_temperature():
    global tello, temperature
    temperature = tello.get_temperature()

schedule.every(10).seconds.do(update_battery)
schedule.every(1).seconds.do(update_height)
schedule.every(5).seconds.do(update_temperature)

tello.streamon()
frame_read = tello.get_frame_read()

def my_keyboard_hook(keyboard_event):
    try:
        global tello
        global state
        print("Name:", keyboard_event.name)
        print("Scan code:", keyboard_event.scan_code)
        print("Time:", keyboard_event.time)

        if keyboard_event.name == "t":
            tello.takeoff()
        elif keyboard_event.name == "esc":
            tello.land()
            state = False
        elif keyboard_event.name == "w":
            tello.move_forward(30)
        elif keyboard_event.name == "s":
            tello.move_back(30)
        elif keyboard_event.name == "a":
            tello.move_left(30)
        elif keyboard_event.name == "d":
            tello.move_right(30)
        elif keyboard_event.name == "e":
            tello.rotate_clockwise(30)
        elif keyboard_event.name == "q":
            tello.rotate_counter_clockwise(30)
        elif keyboard_event.name == "r":
            tello.move_up(30)
        elif keyboard_event.name == "f":
            tello.move_down(30)
    except:
        state = False

keyboard.on_press(my_keyboard_hook)

try:
    time.sleep(2)
    while state:
        schedule.run_pending()
        # In reality you want to display frames in a seperate thread. Otherwise
        #  they will freeze while the drone moves.
        frame = frame_read.frame

        cv2.putText(frame, f"battery: {battery}", (10, 15), cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1, color=(0, 0, 255), thickness=1)
        cv2.putText(frame, f"Height: {height}", (10, 30), cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1, color=(0, 0, 255), thickness=1)
        cv2.putText(frame, f"temperature: {temperature}", (10, 45), cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1, color=(0, 0, 255), thickness=1)

        cv2.imshow("drone", frame)
        key = cv2.waitKey(1)
finally:
    tello.end()
    cv2.destroyAllWindows()
    keyboard.unhook_all()
    schedule.clear()