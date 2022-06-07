# -*- coding: utf-8 -*-
"""
Created on Fri May 20 11:37:18 2022

@author: lambe
"""

import os
import cv2
import matplotlib.pyplot as plt


from deepface import DeepFace
from deepface.detectors import MediapipeWrapper


import platform
input_idx = 0
capture_api = None
if platform.system() == 'Windows':
    input_idx = 1
    capture_api = cv2.CAP_DSHOW

models_name = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib", "SFace"]
m_ver = DeepFace.build_model('VGG-Face')
m_emo = DeepFace.build_model('Emotion')

# m = MediapipeWrapper.build_model()
cap = cv2.VideoCapture(input_idx, capture_api)
success, frame = cap.read()
plt.imshow(frame)
plt.show()
# resp = MediapipeWrapper.detect_face(m, frame, align = True)
cap.release()

# img1_path = [[os.path.join("./dataset/", ss), frame] for ss in os.listdir("./dataset/")]

# res = DeepFace.verify(img1_path, img2_path='', model_name='VGG-Face',
#                 distance_metric='cosine', model=m_ver, enforce_detection=False,
#                 detector_backend='opencv', align=True, prog_bar=True,
#                 normalization='base')
# for k in res.keys():
#     vv = res[k]
#     print(vv)

res = DeepFace.analyze(frame, actions=('emotion', ), models=None,#('emotion') {'emotion':m_emo},
                       enforce_detection=False, detector_backend='opencv',
                       prog_bar=False)
print(res)

# DeepFace.stream("dataset") #opencv
# #DeepFace.stream("dataset", detector_backend = 'opencv')
# #DeepFace.stream("dataset", detector_backend = 'ssd')
# #DeepFace.stream("dataset", detector_backend = 'mtcnn')
# #DeepFace.stream("dataset", detector_backend = 'dlib')
# #DeepFace.stream("dataset", detector_backend = 'retinaface')



# DeepFace.stream(db_path = "C:/User/lambe/Desktop/database")




# #face verification
# result = DeepFace.verify(img1_path = "img1.jpg", img2_path = "img2.jpg", model_name = models[1])

# #face recognition
# df = DeepFace.find(img_path = "img1.jpg", db_path = "C:/workspace/my_db", model_name = models[1])



