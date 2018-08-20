#!/usr/env/python3
# -*- coding: UTF-8 -*-

import cProfile
import os
import pstats
import cv2
from multiprocessing import Queue
from monitor.config import STANDARD_VIDEO_PATH
from monitor.mess import get_current_time
from monitor.ocr import OCRHandle


cap = cv2.VideoCapture(STANDARD_VIDEO_PATH)
res, frame = cap.read()
if res:
    ocr = OCRHandle({'bytes_queue': Queue(), 'ws_queue': Queue()})
    ocr.initialize()
    filename = os.path.join('test_result', 'OCRHandle.analyse_img_{}'.format(get_current_time()))
    cProfile.run('ocr.analyse(frame)', filename)
    ocr.close()
    p = pstats.Stats(filename)
    p.sort_stats('cumulative').print_stats(20)
else:
    print("Cannot run target function.")
