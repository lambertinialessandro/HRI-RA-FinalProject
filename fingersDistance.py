# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 17:58:55 2021

@author: lambe
"""

import cv2
import time
import math
from HandTrakingModule import HandDetector
from win32api import GetSystemMetrics

cap = cv2.VideoCapture(1)
detector = HandDetector(maxHands=2, detectionCon=.75, trackCon=.75)

def getMano(lmList, num):
    return lmList[4+21*num], [lmList[8+21*num], lmList[12+21*num], lmList[16+21*num], lmList[20+21*num]]
def pltDistance(p, d):
    colors = [(255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]
    for id, lm in enumerate(d):
        curColor = colors[-1]
        dist = math.sqrt(pow(p[1]-lm[1], 2) + pow(p[2]-lm[2], 2))
        k = int(dist/50);
        if k == 0:
            curColor = colors[0]
        elif k == 1:
            curColor = colors[1]
        elif k == 2:
            curColor = colors[2]
        elif k == 3:
            curColor = colors[3]
        cv2.line(img, (p[1], p[2]), (lm[1], lm[2]), curColor, 3)
        cv2.putText(img, str(k), (lm[1], lm[2]), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

pTime = 0
cTime = 0

dim = (GetSystemMetrics(0), GetSystemMetrics(1))

while True:
    success, img = cap.read()
    img = detector.findHands(img, fingerTipRadius=5)
    lmList = detector.getHands(img)

    if lmList:
        if len(lmList) > 21:
            p1, d1 = getMano(lmList, 0)
            p2, d2 = getMano(lmList, 1)
            pltDistance(p1, d1)
            pltDistance(p2, d2)
        else:
            p1, d1 = getMano(lmList, 0)
            pltDistance(p1, d1)

    cTime = time.time();
    fps = 1/(cTime - pTime)
    pTime = cTime

    # img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 255), 3)

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()