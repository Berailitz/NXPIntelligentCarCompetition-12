#!/usr/env/python3
# -*- coding: UTF-8 -*-

import functools
import logging
import time
import math
import operator
import os
import struct
import cv2
import numpy as np
import pytesseract
from .config import CAMERA_HEIGHT, CAMERA_WIDTH, IS_WEB_VIDEO_ENABLED, DO_SAVE_IMAGE_SAMPLES, OCR_DO_USE_NCS, STANDARD_LINE_WIDTH
from .credentials import NETWORK_IMAGE_DIMENSIONS
from .mess import get_current_time


blur_ksize = 5  # Gaussian blur kernel size
canny_lthreshold = 50  # Canny edge detection low threshold
canny_hthreshold = 150  # Canny edge detection high threshold

# Hough transform parameters
rho = 1  # rho的步长，即直线到图像原点(0,0)点的距离
theta = np.pi / 180  # theta的范围
threshold = 15  # 累加器中的值高于它时才认为是一条直线
min_line_length = 40  # 线的最短长度，比这个短的都被忽略
max_line_gap = 20  # 两条直线之间的最大间隔，小于此值，认为是一条直线


class OCRHandle(object):
    def __init__(self):
        self.index = 0
        self.status = {}
        self.videos = {}
        self.serial_data = b''

    def initialize(self):
        pass

    def close(self):
        pass


    def get_line_tuple(self, r, theta) -> tuple:
        a = np.cos(theta)
        # Stores the value of sin(theta) in b
        b = np.sin(theta)
        # x0 stores the value rcos(theta)
        x0 = a*r
        # y0 stores the value rsin(theta)
        y0 = b*r
        # x1 stores the rounded off value of (rcos(theta)-1000sin(theta))
        x1 = int(x0 + 1000*(-b))
        # y1 stores the rounded off value of (rsin(theta)+1000cos(theta))
        y1 = int(y0 + 1000*(a))
        # x2 stores the rounded off value of (rcos(theta)+1000sin(theta))
        x2 = int(x0 - 1000*(-b))
        # y2 stores the rounded off value of (rsin(theta)-1000cos(theta))
        y2 = int(y0 - 1000*(a))
        # cv2.line draws a line in img from the point(x1,y1) to (x2,y2).
        # (0,0,255) denotes the colour of the line to be
        #drawn. In this case, it is red.
        return ((x1, y1), (x2, y2))


    def check_line_duplication(self, current_list: list, new_r, new_theta) -> bool:
        is_duplicate = False
        min_gap_r = 80
        min_gap_theta = 0.2
        for current_line in current_list:
            current_r, current_theta = current_line
            if abs(current_r - new_r) < min_gap_r and abs(new_theta - current_theta) < min_gap_theta:
                is_duplicate = True
                break
        return is_duplicate


    @staticmethod
    def get_line_in_ab(r, theta) -> tuple():
        result = None
        if theta == 0:
            result = (0, 0)
        else:
            result = (- 1.0 / math.tan(theta), r / math.sin(theta))
        return result


    @staticmethod
    def get_line_angle(line: tuple) -> float:
        r, theta = line
        if theta < np.pi * 0.5:
            return theta + np.pi * 0.5
        else:
            return theta - np.pi * 0.5


    def filter_lines(self, lines: list) -> tuple:
        vert_lines = []
        hori_lines = []
        for line in lines:
            r, theta = line[0]
            if theta < np.pi * 0.15 or theta > np.pi * 0.85:
                # 竖线
                is_duplicate = self.check_line_duplication(
                    vert_lines, r, theta)
                if not is_duplicate:
                    vert_lines.append((r, theta))
                    a, b = self.get_line_in_ab(r, theta)
                    cv2.line(self.videos['video-cut'], *self.get_line_tuple(r,
                                                             theta), (0, 0, 255), 2)
                    # print(f"Vert: {(r,theta)}, y = {a} * x + {b}")
        return sorted(vert_lines, key=self.get_line_angle)


    def analyse_img(self, raw_img):
        self.videos = {}
        self.videos['video-raw'] = raw_img
        self.status = {}
        gray = cv2.cvtColor(raw_img, cv2.COLOR_RGB2GRAY)    # 图像转换为灰度图
        kernel = np.ones((5, 5), np.uint8)
        closing_1 = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        blur_gray = cv2.GaussianBlur(
            closing_1, (5, 55), 0, 0)    # 使用高斯模糊去噪声
        self.videos['video-cut'] = blur_gray.copy()
        edges = cv2.Canny(blur_gray, 50, 150)    # 使用Canny进行边缘检测
        self.videos['video-bin'] = edges.copy()
        lines = cv2.HoughLines(edges, 1, np.pi/180, 90)
        if lines is not None:
            real_lines = self.filter_lines(lines)
            if real_lines is not None:
                print("{}->{}".format(len(lines), len(real_lines)))
                for real_line in real_lines:
                    line_points = self.get_line_tuple(real_line[0], real_line[1])
                    # print(line_points)
                    cv2.line(self.videos['video-raw'], *line_points, (0, 0, 255), 20)
