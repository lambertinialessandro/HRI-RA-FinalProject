# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 16:01:48 2022

@author: lambe
"""

import time
import cv2
import math

from HandEnum import HandEnum


# Draw FPS on the top left corner
def drawFps(obj):
    obj.pTime = 0
    obj.cTime = 0

    def f(self, img, drawFps=False, drawFpsColor=(255, 0, 255)):#, **kwargs):
        if drawFps:
            self.cTime = time.time()
            fps = 1/(self.cTime - self.pTime)
            self.pTime = self.cTime

            cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                        drawFpsColor, 3)
        return img
    return f

# Draw hand connections
def drawHand(obj):
    def f(self, img, drawHand=False):#, **kwargs):
        if self.resultsData and drawHand:
            for handLms in self.results.multi_hand_landmarks:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img
    return f

# Draw Bbox
def drawBbox(obj):
    def f(self, img, drawBbox=False, drawBboxColor=(255, 0, 255)):#, **kwargs):
        if self.resultsData and drawBbox:
            for hand in self.allHands:
                bbox = hand["bbox"]
                cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                              (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                              drawBboxColor, 2)
                cv2.putText(img, hand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                            2, drawBboxColor, 2)
        return img
    return f

# Draw finger tip
def drawFingerTip(obj):
    def f(self, img, drawFingerTip=False, drawFingerTipRadius=15,
          drawFingerTipColor=(255, 0, 255)):#, **kwargs):
        if self.resultsData and drawFingerTip:
            for hand in self.allHands:
                lmList = hand["lmList"]
                for idlm in HandEnum.tips():
                    (cx, cy, cz) = lmList[idlm]
                    cv2.circle(img, (cx, cy),
                                drawFingerTipRadius,
                                drawFingerTipColor, cv2.FILLED)
                    # if cz < 0:
                        # cv2.putText(img, str(cz), (cx - 30, cy - 30), cv2.FONT_HERSHEY_PLAIN,
                        #             2, drawBboxColor, 2)
        return img
    return f

def drawCommands(obj):
    def f(self, img, drawCommand=False, drawCommandLine=3):#, **kwargs):
        if self.resultsData and drawCommand:
            rHand = self.getHandsInfo(handNo="Right")
            if rHand:
                #(cx, cy) = rHand["center"]
                (wx, wy, wz) = rHand["lmList"][HandEnum.WRIST.value]
                (pmx, pmy, pmz) = rHand["lmList"][HandEnum.PINKY_MCP.value]
                (imx, imy, imz) = rHand["lmList"][HandEnum.INDEX_FINGER_MCP.value]
                (itx, ity, itz) = rHand["lmList"][HandEnum.INDEX_FINGER_TIP.value]

                minDist = max(math.dist((wx, wy), (pmx, pmy)), math.dist((imx, imy), (pmx, pmy)))*0.75

                distance = math.dist((imx, imy), (itx, ity))
                angle = math.degrees(math.atan2(ity-imy, itx-imx))
                #print(angle)
                drawCommandColor = (0, 0, 0)
                delta = 25 # max 45
                action = ""

                (mtx, mty, mtz) = rHand["lmList"][HandEnum.MIDDLE_FINGER_TIP.value]
                (rtx, rty, rtz) = rHand["lmList"][HandEnum.RING_FINGER_TIP.value]
                (ptx, pty, ptz) = rHand["lmList"][HandEnum.PINKY_TIP.value]
                (rmx, rmy, rmz) = rHand["lmList"][HandEnum.RING_FINGER_MCP.value]

                otherFingersDist = max(math.dist((mtx, mty), (rmx, rmy)),
                                       math.dist((rtx, rty), (rmx, rmy)),
                                       math.dist((ptx, pty), (rmx, rmy)))
                if otherFingersDist > minDist:
                    return img

                if distance > minDist:
                    if (-45+delta) < angle and angle < (45-delta):
                        drawCommandColor = (255, 0, 0) # Blue -> left
                        action = "left"
                    elif (45+delta) < angle and angle < (135-delta):
                        drawCommandColor = (0, 255, 0) # Green -> bottom
                        action = "down"
                    elif (-135+delta) < angle and angle < (-45-delta):
                        drawCommandColor = (0, 0, 255) # Red -> top
                        action = "up"
                    elif (135+delta) < angle or angle < (-135-delta):
                        drawCommandColor = (255, 0, 255) # magenta -> right
                        action = "right"

                cv2.line(img, (imx, imy), (itx, ity), drawCommandColor, drawCommandLine)
                cv2.putText(img, action, (itx, ity), cv2.FONT_HERSHEY_PLAIN, 3,
                            drawCommandColor, 3)

        return img
    return f


# def __(obj):
#     def f(self, img, **kwargs):
#         return img
#     return f


    # def drawHands(self, img,
    #               drawFps=False, drawFpsColor=(255, 0, 255), # BGR
    #               drawHand=False,
    #               drawBbox=False, drawBboxColor=(255, 0, 255), # BGR
    #               drawFingerTip=False, drawFingerTipRadius=15,
    #               drawFingerTipColor=(255, 0, 255), # BGR
    #               ):

    #     if drawFps:
    #         self.cTime = time.time();
    #         fps = 1/(self.cTime - self.pTime)
    #         self.pTime = self.cTime

    #         cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
    #                     drawFpsColor, 3)

    #     if self.results.multi_hand_landmarks:
    #         # Draw hand connections
    #         if drawHand:
    #             for handLms in self.results.multi_hand_landmarks:
    #                     self.mpDraw.draw_landmarks(img, handLms,
    #                                                self.mpHands.HAND_CONNECTIONS)

    #         # Draw Bbox
    #         if drawBbox:
    #             for hand in self.allHands:
    #                 bbox = hand["bbox"]
    #                 cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
    #                               (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
    #                               drawBboxColor, 2)
    #                 cv2.putText(img, hand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
    #                             2, drawBboxColor, 2)

    #         # Draw finger tip
    #         if drawFingerTip:
    #             for hand in self.allHands:
    #                 lmList = hand["lmList"]
    #                 for idlm in HandEnum.tips():
    #                     (cx, cy, cz) = lmList[idlm]
    #                     if cz < 0:
    #                         cv2.circle(img, (cx, cy),
    #                                    drawFingerTipRadius,
    #                                    drawFingerTipColor, cv2.FILLED)

    #                         # cv2.putText(img, str(cz), (cx - 30, cy - 30), cv2.FONT_HERSHEY_PLAIN,
    #                         #             2, drawBboxColor, 2)
    #     return img

