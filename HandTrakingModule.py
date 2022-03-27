# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 12:11:55 2021

@author: lambe
"""

import cv2
import mediapipe as mp

import DrawModule

"""
STATIC_IMAGE_MODE
If set to false, the solution treats the input images as a video stream. It will try to detect hands in the first input images, and upon a successful detection further localizes the hand landmarks. In subsequent images, once all max_num_hands hands are detected and the corresponding hand landmarks are localized, it simply tracks those landmarks without invoking another detection until it loses track of any of the hands. This reduces latency and is ideal for processing video frames. If set to true, hand detection runs on every input image, ideal for processing a batch of static, possibly unrelated, images. Default to false.

MAX_NUM_HANDS
Maximum number of hands to detect. Default to 2.

MODEL_COMPLEXITY
Complexity of the hand landmark model: 0 or 1. Landmark accuracy as well as inference latency generally go up with the model complexity. Default to 1.

MIN_DETECTION_CONFIDENCE
Minimum confidence value ([0.0, 1.0]) from the hand detection model for the detection to be considered successful. Default to 0.5.

MIN_TRACKING_CONFIDENCE:
Minimum confidence value ([0.0, 1.0]) from the landmark-tracking model for the hand landmarks to be considered tracked successfully, or otherwise hand detection will be invoked automatically on the next input image. Setting it to a higher value can increase robustness of the solution, at the expense of a higher latency. Ignored if static_image_mode is true, where hand detection simply runs on every image. Default to 0.5.
"""

class HandDetector():
    def __init__(self, mode=False, maxHands=2,
                 detectionCon=.5, trackCon=.5,
                 drawFunList=[]):
        self.mode = mode # STATIC_IMAGE_MODE
        self.maxHands = maxHands # MAX_NUM_HANDS
        self.detectionCon = detectionCon # MIN_DETECTION_CONFIDENCE
        self.trackCon = trackCon # MIN_TRACKING_CONFIDENCE

        self.mpDraw = mp.solutions.drawing_utils
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode,
                                        max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.trackCon)

        self.drawFunList = []
        for drawFun in drawFunList:
            self.drawFunList.append(drawFun(self))

        self.resultsData = False

    def analizeImage(self, img, flipType=True):
        """
        Parameters
        ----------
        img : 3-dimensional array

        flipType : boolean, optional
            The default is True.
            flip hands lable between left and right
        Returns
        -------
        None.

        save data in allHands.
        to get this data use: getHandsInfo

        """
        self.allHands = []
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self.results = self.hands.process(imgRGB)
        self.resultsData = False

        # collecting infos
        if self.results.multi_hand_landmarks:
            self.resultsData = True
            h, w, c = img.shape
            for handType, handLms in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
                myHand = {}
                mylmList = []
                xList = []
                yList = []

                # data = handType.classification[0]
                # print("{}, {:.2f}, {}".format(data.index,
                #                              data.score,
                #                              data.label))

                for id, lm in enumerate(handLms.landmark):
                    px, py, pz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                    mylmList.append([px, py, pz])
                    xList.append(px)
                    yList.append(py)

                ## bbox
                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                boxW = xmax - xmin
                boxH = ymax - ymin
                bbox = xmin, ymin, boxW, boxH
                cx = bbox[0] + (bbox[2] // 2)
                cy = bbox[1] + (bbox[3] // 2)

                myHand["lmList"] = mylmList
                myHand["bbox"] = bbox
                myHand["center"] = (cx, cy)

                if flipType:
                    if handType.classification[0].label == "Right":
                        myHand["type"] = "Left"
                    else:
                        myHand["type"] = "Right"
                else:
                    myHand["type"] = handType.classification[0].label
                self.allHands.append(myHand)

    def drawHands(self, img, **kwargs):
        for drawFun in self.drawFunList:
            if self.resultsData:
                img = drawFun(self, img, **kwargs)
        return img

    def getHandsInfo(self, handNo=-1):
        """
        Parameters
        ----------
        handNo : int | str, optional
            The default is -1.
            int:
                -1: return data of all hands

                N: return data of N-th hand
                    N belongs to [0, maxHands]

            str:
                "left" or "right"
        Returns
        -------
        lmList : TYPE
            DESCRIPTION.

        """
        if isinstance(handNo, (int)):
            assert handNo < self.maxHands

            if handNo < 0:
                return self.allHands
            else:
                if handNo <= len(self.allHands):
                    return self.allHands[handNo]
        elif isinstance(handNo, (str)):
            if handNo.lower() == "left":
                for hand in self.allHands:
                    if hand["type"].lower() == "left":
                        return hand
            elif handNo.lower() == "right":
                for hand in self.allHands:
                    if hand["type"].lower() == "right":
                        return hand
        return []




def main():
    try:
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280//2)
        cap.set(4, 720//2)
        detector = HandDetector(detectionCon=.8, trackCon=.8,
                                drawFunList=[
                                    DrawModule.drawFps,
                                            DrawModule.drawHand,
                                            DrawModule.drawBbox,
                                            DrawModule.drawFingerTip,
                                            DrawModule.drawCommands])

        while True:
            success, img = cap.read()
            detector.analizeImage(img, flipType=True)
            img = detector.drawHands(img,
                                     drawFps=True, drawFpsColor=(255, 0, 0), # BGR
                                     drawHand=False,
                                     drawBbox=True, drawBboxColor=(0, 0, 255), # BGR
                                     drawFingerTip=True, drawFingerTipRadius=5,
                                     drawFingerTipColor=(0, 255, 255), # BGR
                                     drawCommand=True,
                                     drawCommandLine=2
                                     )
            #lmList = detector.getHandsInfo(handNo=-1)
            #lmList = detector.getHandsInfo(handNo="Left")

            cv2.imshow("Image", img)
            key = cv2.waitKey(1)
            if key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
    except:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


