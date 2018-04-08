import random
import cv2
import numpy as np


class CameraHandler(object):
    """An Event-like class that signals all active clients when a new frame is
    available."""

    def update_image(self):
        img_q = np.random.randint(222, size=(90, 120, 3))
        img_h = np.concatenate((img_q,) * 4, axis=0)
        img_f = np.concatenate((img_h,) * 4, axis=1)
        gen = np.array(img_f, dtype=np.uint8)
        return gen

    def update_status(self):
        return {'picture': '/video_feed', 'status': {'速度': f'{random.randint(0, 3000) / 100}m/s', '长宽比': f'{random.randrange(0, 1000) / 1000}', '是否发生事故': '否'}}
