import math
import struct
import time
import cv2
import numpy as np
from .image_processer import ImageProcesser
from .opencv_hcm import get_chess, get_cross5


def pack_cross_data(x,y,angle):
    head=b'by'
    length=struct.pack('b',8)
    type=struct.pack('b',15)
    try:
        s_x=struct.pack('h',x)
        s_y=struct.pack('h',y)
        s_a=struct.pack('f',angle)
        s=head+length+type+s_x+s_y+s_a+b'\r\n'
        return s
    except:
        print("error!\r\n")
        print(s)
        return None

def pack_chess_data(x,y,r):
    head=b'by'
    length=struct.pack('b',6)
    type=struct.pack('b',14)
    try:
        s_x=struct.pack('h',x)
        s_y=struct.pack('h',y)
        s_r=struct.pack('h',r)
        s=head+length+type+s_x+s_y+s_r+b'\r\n'
        return s
    except:
        print("error!\r\n")
        print(s)
        return None


def get_cross_data(frame):
    cross=get_cross5(frame,getImg=False)
    if cross is not None:
        return pack_cross_data(cross[0],cross[1],cross[2])
    else:
        return pack_cross_data(0,0,0)


def get_chess_data(frame):
    chess=get_chess(frame,getImg=False)
    if chess is not None:
        return pack_chess_data(chess[0],chess[1],chess[2])
    else:
        print("no chess!\r\n")
        return pack_chess_data(0,0,0)


class Crossfinder(ImageProcesser):
    def __init__(self, queues):
        super().__init__(queues, 'image_queue_b')

    def analyse(self, raw_img):
        result = get_cross_data(raw_img)
        if result is not None:
            self.write_serial(result)


class Chessfinder(ImageProcesser):
    def __init__(self, queues):
        super().__init__(queues, 'image_queue_c')

    def analyse(self, raw_img):
        result = get_chess_data(raw_img)
        if result is not None:
            self.write_serial(result)
