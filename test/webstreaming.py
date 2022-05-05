# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 11:32:53 2022

@author: lambe
"""



# import the necessary packages
#from pyimagesearch.motion_detection import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2

local_ip = "0.0.0.0"
local_port = 8080

outputFrame = None
lock = threading.Lock()
app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/video_feed")
def video_feed():
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

def detect_motion(frameCount):
	global vs, outputFrame, lock

	while True:
		frame = vs.read()
		frame = imutils.resize(frame, width=400)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
		with lock:
			outputFrame = frame.copy()

def generate():
    global outputFrame, lock

    while True:
        with lock:
            if outputFrame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not flag:
                continue

        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
			bytearray(encodedImage) + b'\r\n')

def startWebServer():
     app.run(host=local_ip, port=9999, debug=True,
	 	threaded=True, use_reloader=False)


if __name__ == '__main__':
    vs = VideoStream(src=0).start()
    time.sleep(2.0)
    try:
        #app.run(host=local_ip, port=9999, debug=True, threaded=True, use_reloader=False)

        webThread = threading.Thread(target=startWebServer)
        webThread.daemon = True
        webThread.start()


        # t = threading.Thread(target=detect_motion, args=(32,))
        # t.daemon = True
        # t.start()

        detect_motion(32)

        while True:
            time.sleep(1)
    finally:
        vs.end()