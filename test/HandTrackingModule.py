# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 12:11:55 2021

@author: lambe
"""

import cv2
import mediapipe as mp
import time


class HandDetector():
    def __init__(self, mode=False, maxHands=2,
                 detectionCon=.5, trackCon=.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode, max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.trackCon)

    def findHands(self, img, drawHand=True, drawFingerTip=True, fingerTipRadius=15):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if drawHand and self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)

        if drawFingerTip and self.results.multi_hand_landmarks:
            h, w, c = img.shape
            for handLms in self.results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    cx, cy = int(lm.x*w), int(lm.y*h)
                    if id in [4, 8, 12, 16, 20]:
                        cv2.circle(img, (cx, cy), fingerTipRadius, (255, 0, 255), cv2.FILLED)
        return img

    def getHands(self, img, handNo=-1):
        assert handNo < self.maxHands

        lmList = []
        h, w, c = img.shape

        if handNo < 0:
            if self.results.multi_hand_landmarks:
                for hand in self.results.multi_hand_landmarks:
                    for id, lm in enumerate(hand.landmark):
                        cx, cy = int(lm.x*w), int(lm.y*h)
                        lmList.append([id, cx, cy, lm.z])
        else:
            if self.results.multi_hand_landmarks:
                myHand = self.results.multi_hand_landmarks[handNo]
                for id, lm in enumerate(myHand.landmark):
                    cx, cy = int(lm.x*w), int(lm.y*h)
                    lmList.append([id, cx, cy])
        return lmList



def main():
    cap = cv2.VideoCapture(0)
    detector = HandDetector()

    pTime = 0
    cTime = 0

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.getHands(img)

        cTime = time.time();
        fps = 1/(cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()