# coding:utf8
import random
import logging
import base64
import cv2
import json
from .center import center
from .classroom import target
import time
def produce(video_id):
    try:
        filename = int(video_id)
    except:
        filename = f'{video_id}'
    camera = cv2.VideoCapture(filename)
    frames = 0
    while True:
        res, frame = camera.read()
        retval, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer)
        yield {'picture': buffer, 'status': {'frame_index': frames}}

class result(object):
    def __init__(self, video_id):
       self.c = produce(video_id)
    def detect_video(self):
        self.dict = next(self.c)
        return self.dict
    

    
