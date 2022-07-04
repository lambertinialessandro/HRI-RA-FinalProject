#!/usr/local/bin/python3

import cv2

from modules.GlobalFactory import GlobalFactory


import platform
input_idx = 0
capture_api = None
if platform.system() == 'Windows':
    input_idx = 1
    capture_api = cv2.CAP_DSHOW


# 1. Creating the sequence
pipeline_pattern = GlobalFactory.create(
    GlobalFactory.DroneEnum.DJITello,
    GlobalFactory.StreamEnum.VideoDrone,
    GlobalFactory.VCREnum.Holistic,
    GlobalFactory.PipelineEnum.BasePipeline,
    input_idx=input_idx,
    capture_api=capture_api,
)

# 2. start web streaming
#pipeline_pattern.start_web_streaming()

# 3. Starting sequence
pipeline_pattern.execute()
