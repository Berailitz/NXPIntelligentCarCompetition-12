#!/usr/env/python3
# -*- coding: UTF-8 -*-

import itertools
import logging
import math
import cv2
import numpy as np
import pytesseract
from .mess import get_current_time


class OCRHandle(object):
    def __init__(self):
        self.orig = None
        self.cut = None
        self.index = 0
        self.status = {}

    def possible_mids(self, width):
        mids_left = (x for x in range(round(width * 0.5), 0, -1))
        mids_right = (x for x in range(round(width * 0.5), width))
        while True:
            yield next(mids_left)
            yield next(mids_right)

    def find_mid(self, img):
        width = img.shape[1]
        height = img.shape[0]
        NOISE_THRESHOLD = 10
        mid = round(0.5 * width)
        for x in self.possible_mids(width):
            noise = 0
            for y in range(round(height * 0.25), round(height * 0.75)):
                if img[y, x] == 0:
                    noise += 1
            if noise <= NOISE_THRESHOLD:
                mid = x
                break
        return mid

    def cut_single_word(self, raw_word_img):
        im2, contours_word, hierarchy = cv2.findContours(
            np.invert(raw_word_img), cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
        contours_word = sorted(
            contours_word, key=cv2.contourArea, reverse=True)
        x, y, w, h = cv2.boundingRect(contours_word[0])
        return raw_word_img[y:y+h, x:x+w]

    def recognize_number(self, img):
        # img_m = cv2.resize(img, (100, 120))
        number = pytesseract.image_to_string(
            img, config='-c tessedit_char_whitelist=0123456789 -psm 10')
        return number

    @staticmethod
    def is_rect_valid(dot_list: list) -> bool:
        """ dot_list: sorted [(x, y)]
        """
        MAX_RATIO = 45
        SHORTEST_BOARDER = 60
        result = False
        x_list = [dot[0] for dot in dot_list]
        y_list = [dot[1] for dot in dot_list]
        width = max(x_list) - min(x_list)
        height = max(y_list) - min(y_list)
        long_border = max(width, height)
        short_border = min(width, height)
        # self.status['width'] = width
        # self.status['height'] = height
        if short_border > 0:
            ratio = round(1.0 * long_border / short_border, 3)
            if ratio < MAX_RATIO and short_border > SHORTEST_BOARDER:
                # self.status['ratio'] = ratio
                result = True
        return result

    @staticmethod
    def order_points(rect_points: list) -> None:
        rect_points_np = np.array(rect_points, dtype=np.int)

        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = rect_points_np.sum(axis=1)
        rect_points[0] = rect_points_np[np.argmin(s)] # top-left
        rect_points[2] = rect_points_np[np.argmax(s)] # bottom-right

        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(rect_points_np, axis=1)
        rect_points[1] = rect_points_np[np.argmin(diff)] # top-right
        rect_points[3] = rect_points_np[np.argmax(diff)] # bottom-left

        for i, dot in enumerate(rect_points):
            rect_points[i] = tuple(dot.tolist())
        return rect_points

    @staticmethod
    def get_center(rect: list) -> tuple:
        return (round((rect[0][0] + rect[2][0]) / 2), round((rect[0][1] + rect[2][1]) / 2))

    @staticmethod
    def draw_box(img, dot_list: list) -> None:
        dots = [tuple(dot) for dot in dot_list]
        cv2.line(img, dots[0], dots[1], 200, 5)
        cv2.line(img, dots[1], dots[2], 200, 5)
        cv2.line(img, dots[2], dots[3], 200, 5)
        cv2.line(img, dots[3], dots[0], 200, 5)

    @staticmethod
    def contour_to_rect(contour):
        x, y, w, h = cv2.boundingRect(contour)
        return [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]

    def sweap_map(self, img_bin):
        MARGIN_BUTTOM = 100
        THRESHHOLD_GRAY_BLUR = 200
        flood_mask = np.zeros((self.camera_height + 2, self.camera_width + 2), np.uint8)

        line_1_start = (MARGIN_BUTTOM, self.camera_height - 1)
        line_1_end = (round(0.1 * self.camera_width - 1), 0)
        line_2_start = (self.camera_width - MARGIN_BUTTOM, self.camera_height - 1)
        line_2_end = (round(0.9 * self.camera_width - 1), 0)
        cv2.line(img_bin, line_1_start, line_1_end, 255, 20)
        cv2.line(img_bin, line_2_start, line_2_end, 255, 20)

        self.videos['video-orig'] = img_bin.copy()

        cv2.floodFill(img_bin, flood_mask, (MARGIN_BUTTOM, self.camera_height - 1), 0)
        cv2.floodFill(img_bin, flood_mask, (self.camera_width - MARGIN_BUTTOM, self.camera_height - 1), 0)
        img_bin_blur = cv2.blur(img_bin, (5, 5))
        retval, img_blur_bin = cv2.threshold(img_bin_blur, THRESHHOLD_GRAY_BLUR, 255, cv2.THRESH_BINARY)
        return img_blur_bin

    def cut_main_area(self, img):
        MIN_HEIGHT = 300
        MAX_HEIGHT = 1000
        main_area = img[MIN_HEIGHT:MAX_HEIGHT, :]
        self.videos['video-cut'] = main_area
        return main_area
    
    def find_center(self, main_area, num_rects):
        main_height = main_area.shape[0]
        main_width = main_area.shape[1]
        centers = list(map(self.get_center, num_rects))
        text_center = (round((centers[0][0] + centers[1][0]) / 2), round((centers[0][1] + centers[1][1]) / 2))
        center_diff = (round((text_center[0] - main_width * 0.5)), round((text_center[1] - main_height * 0.5)))
        self.status['x'] = int(center_diff[0])
        self.status['y'] = int(center_diff[1])
    
    @staticmethod
    def cut_rectangle(img, dot_list: list):
        x_min, y_min = dot_list[0]
        x_max, y_max = dot_list[2]
        return img[y_min:y_max, x_min:x_max]

    def analyse_img(self, orig):
        self.status = {}
        self.videos = {}
        self.index += 1

        THRESHHOLD_GRAY_MAIN = 180

        width = orig.shape[1]
        self.camera_width = width
        height = orig.shape[0]
        self.camera_height = height

        # canvas = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
        gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
        retval, img_bin = cv2.threshold(gray, THRESHHOLD_GRAY_MAIN, 255, cv2.THRESH_BINARY)
        img_blur_bin = self.sweap_map(img_bin)
        main_area = self.cut_main_area(img_blur_bin)

        _main_area, contours, _hierarchy = cv2.findContours(main_area, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        num_rects = list(filter(self.is_rect_valid, [self.contour_to_rect(cont) for cont in contours]))[:2]
        if len(num_rects) == 2:
            num_rects = list(map(self.order_points, num_rects))
            num_rects.sort(key=lambda num_rect: num_rect[0][0])
            for num_rect in num_rects:
                self.draw_box(self.videos['video-cut'], num_rect)
            self.find_center(main_area, num_rects)
            # logging.info(f"num_rects: {num_rects}")
            # logging.info(f"centers: {centers}")

            # num_imgs = []
            # for num_rect in num_rects:
            #     box_f = np.float32(num_rect)
            #     canvas = np.float32([[0, 0], [main_width, 0], [main_width, main_height], [0, main_height]])
            #     M = cv2.getPerspectiveTransform(box_f, canvas)
            #     num_imgs.append(cv2.warpPerspective(main_area, M, (0, 0)))
            num_imgs = [self.cut_rectangle(main_area, num_rect) for num_rect in num_rects]

            self.status['text'] = "".join([self.recognize_number(num_img) for num_img in num_imgs])
            self.videos['video-num-l'] = num_imgs[0]
            self.videos['video-num-r'] = num_imgs[1]
            logging.info(f"Result: {self.status}")
