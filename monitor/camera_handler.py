import random
import cv2
import numpy as np


class CameraHandler(object):
    """An Event-like class that signals all active clients when a new frame is
    available."""

    def update_image(self):
        img = np.random.randint(222, size=(360, 480, 3))
        gen = np.array(img, dtype=np.uint8)
        return gen

    def update_status(self):
        return {'picture': '/video_feed', 'status': {'速度': f'{random.randint(0, 3000) / 100}m/s', '长宽比': f'{random.randrange(0, 1000) / 1000}', '是否发生事故': '否'}}
