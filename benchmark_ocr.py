#!/usr/env/python3
# -*- coding: UTF-8 -*-

import cProfile
import os
import pstats
import cv2
from monitor.mess import get_current_time
from monitor.ocr import OCRHandle


cap = cv2.VideoCapture('video_1.mp4')
res, frame = cap.read()
if res:
    ocr = OCRHandle()
    filename = os.path.join('test_result', f'OCRHandle.analyse_img_{get_current_time()}')
    cProfile.run('ocr.analyse_img(frame)', filename)
    p = pstats.Stats(filename)
    p.sort_stats('cumulative').print_stats(20)
else:
    print("Cannot run target function.")
