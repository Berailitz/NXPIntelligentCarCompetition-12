#!/usr/env/python3
# -*- coding: UTF-8 -*-

import cProfile
import os
import pstats
import cv2
from monitor.config import STANDARD_VIDEO_PATH
from monitor.mess import get_current_time
from monitor.ocr import OCRHandle


cap = cv2.VideoCapture(STANDARD_VIDEO_PATH)
res, frame = cap.read()
if res:
    ocr = OCRHandle()
    ocr.initialize()
    filename = os.path.join('test_result', 'OCRHandle.analyse_img_{}'.format(get_current_time()))
    cProfile.run('ocr.analyse_img(frame)', filename)
    ocr.close()
    p = pstats.Stats(filename)
    p.sort_stats('cumulative').print_stats(20)
else:
    print("Cannot run target function.")
