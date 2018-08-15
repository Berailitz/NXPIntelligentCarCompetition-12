#!/usr/env/python3
# -*- coding: UTF-8 -*-

import functools
import logging
import math
import operator
import os
import struct
import cv2
import numpy as np
import pytesseract
from skimage.measure import compare_ssim as ssim
from .config import IMAGE_SAMPLE_FOLDER, IS_WEB_VIDEO_ENABLED, DO_SAVE_IMAGE_SAMPLES, DATASET_STANDARD_FOLDER
from .credentials import NETWORK_IMAGE_DIMENSIONS
from .mess import get_current_time


class OCRHandle(object):
    def __init__(self):
        self.orig = None
        self.cut = None
        self.index = 0
        self.status = {}
        self.num_samples = []
        self.serial_data = b''
        for i in range(10):
            self.num_samples.append(cv2.imread(
                os.path.join(DATASET_STANDARD_FOLDER, "{}.jpg".format(i)), cv2.IMREAD_GRAYSCALE))

    def recognize_number(self, imgs: list):
        resized_images = [cv2.resize(
            img, NETWORK_IMAGE_DIMENSIONS, cv2.INTER_LINEAR) for img in imgs]
        infer_probabilities = []
        for resized_image in resized_images:
            similarities = []
            for i, sample_img in enumerate(self.num_samples):
                similarities.append(ssim(sample_img, resized_image))
            infer_probabilities.append(similarities)
        result = [max(enumerate(
            infer_probabilitie), key=operator.itemgetter(1)) for infer_probabilitie in infer_probabilities]
        if DO_SAVE_IMAGE_SAMPLES:
            for i, resized_image in enumerate(resized_images):
                cv2.imwrite(os.path.join(IMAGE_SAMPLE_FOLDER, "{}_{}.jpg".format(
                    get_current_time(), result[i][0])), resized_image)
        return result

    @staticmethod
    def is_rect_valid(dot_list: list) -> bool:
        """ dot_list: sorted [(x, y)]
        ***WARNING: ASSUME THE CAMERA HEIGHT IS 1080.***
        """
        y = dot_list[0][1]
        if y < 810:
            SHORTEST_BOARDER = 200 - (810 - dot_list[0][1]) * (150 / 810)
            LONGEST_BOARDER = 930 - (810 - dot_list[0][1]) * (300 / 810)
            MAX_RATIO = 2 + (810 - dot_list[0][1]) * (3 / 810)
        else:
            SHORTEST_BOARDER = 200
            LONGEST_BOARDER = 930
            MAX_RATIO = 2
        result = False
        x_list = [dot[0] for dot in dot_list]
        y_list = [dot[1] for dot in dot_list]
        width = max(x_list) - min(x_list)
        height = max(y_list) - min(y_list)
        long_border = max(width, height)
        short_border = min(width, height)
        if short_border > 0:
            ratio = round(1.0 * long_border / short_border, 3)
            if ratio < MAX_RATIO and short_border > SHORTEST_BOARDER and long_border < LONGEST_BOARDER:
                # self.status['ratio'] = ratio
                result = True
        return result

    @staticmethod
    def order_points(rect_points: list) -> None:
        rect_points_np = np.array(rect_points, dtype=np.int)

        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = rect_points_np.sum(axis=1)
        rect_points[0] = rect_points_np[np.argmin(s)]  # top-left
        rect_points[2] = rect_points_np[np.argmax(s)]  # bottom-right

        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(rect_points_np, axis=1)
        rect_points[1] = rect_points_np[np.argmin(diff)]  # top-right
        rect_points[3] = rect_points_np[np.argmax(diff)]  # bottom-left

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
        return OCRHandle.order_points([(x, y), (x + w, y), (x, y + h), (x + w, y + h)])

    @staticmethod
    def iterate_rect_pairs(rect_list: list) -> tuple:
        for right_index, right_value in enumerate(rect_list[1:]):
            for left_index, left_value in enumerate(rect_list[:right_index + 1]):
                yield (left_value, right_value)

    def sweap_map(self, img_bin):
        THRESHHOLD_GRAY_BLUR = 200
        LINE_WIDTH = 5
        map_height = img_bin.shape[0]
        map_width = img_bin.shape[1]
        flood_mask = np.zeros(
            (map_height + 2, map_width + 2), np.uint8)

        triangle_1 = np.array([(round(0.35 * map_width), 0),
                               (map_width - 1, map_height - 1), (map_width - 1, 0)], dtype=np.int32)
        triangle_2 = np.array(
            [(round(0.4 * map_width), 0), (0, round(0.35 * map_height)), (0, 0)], dtype=np.int32)
        triangle_3 = np.array(
            [(0, 900), (0, map_height - 1), (500, map_height - 1)], dtype=np.int32)
        triangle_4 = np.array(
            [(map_width - 1, 600), (0, map_height - 1), (map_width - 1, map_height - 1)], dtype=np.int32)
        cv2.fillConvexPoly(img_bin, triangle_1, 255)
        cv2.fillConvexPoly(img_bin, triangle_2, 255)
        cv2.fillConvexPoly(img_bin, triangle_3, 255)
        cv2.fillConvexPoly(img_bin, triangle_4, 255)
        cv2.line(img_bin, (1, map_height - LINE_WIDTH), (map_width - 1, map_height - LINE_WIDTH), 255, LINE_WIDTH)
        cv2.line(img_bin, (1, LINE_WIDTH), (map_width - 1, LINE_WIDTH), 255, LINE_WIDTH)
        cv2.line(img_bin, (1, round(0.5 * LINE_WIDTH)), (1, map_height - 1), 255, LINE_WIDTH)
        cv2.line(img_bin, (map_width - 1, map_height - 1), (map_width - 1, map_height - 1), 255, LINE_WIDTH)

        if IS_WEB_VIDEO_ENABLED:
            self.videos['video-bin'] = img_bin.copy()

        cv2.floodFill(img_bin, flood_mask, (1, round(0.5 * LINE_WIDTH)), 0)
        img_bin_blur = cv2.blur(img_bin, (5, 5))
        retval, img_blur_bin = cv2.threshold(
            img_bin_blur, THRESHHOLD_GRAY_BLUR, 255, cv2.THRESH_BINARY)
        return img_blur_bin

    def find_text_center(self, main_area, num_rects):
        centers = list(map(self.get_center, num_rects))
        return (round((centers[0][0] + centers[1][0]) / 2), round((centers[0][1] + centers[1][1]) / 2))

    @staticmethod
    def keep_int_in_range(value: int, max_value: int) -> int:
        if value < 0:
            value = 0
        elif value >= max_value:
            value = max_value - 1
        return value

    def keep_dot_in_image(self, dot: tuple, shape) -> tuple:
        width = shape[1]
        height = shape[0]
        real_x = self.keep_int_in_range(dot[0], width)
        real_y = self.keep_int_in_range(dot[1], height)
        return (real_x, real_y)

    @staticmethod
    def add_tuple(a: tuple, b: tuple) -> tuple:
        return (a[0] + b[0], a[1] + b[1])

    @staticmethod
    def get_distance(dot_a: tuple, dot_b: tuple) -> int:
        return math.sqrt(pow(dot_a[0] - dot_b[0], 2) + pow(dot_a[1] - dot_b[1], 2))

    def add_rect_padding(self, dot_list: list, padding: int, shape: tuple) -> list:
        """dot_list: ordered dot list
        """
        new_rect = dot_list.copy()
        real_top_left = self.add_tuple(dot_list[0], (-padding, -padding))
        real_buttom_right = self.add_tuple(dot_list[2], (padding, padding))
        new_rect[0] = self.keep_dot_in_image(real_top_left, shape)
        new_rect[2] = self.keep_dot_in_image(real_buttom_right, shape)
        return new_rect

    def cut_rectangle(self, img, dot_list: list, padding: int):
        rect_with_padding = self.add_rect_padding(dot_list, padding, img.shape)
        x_min, y_min = rect_with_padding[0]
        x_max, y_max = rect_with_padding[2]
        return img[y_min:y_max, x_min:x_max]

    def pre_process_img(self, raw_img):
        if IS_WEB_VIDEO_ENABLED:
            self.videos['video-raw'] = raw_img.copy()
        THRESHHOLD_GRAY_MAIN = 180
        gray = cv2.cvtColor(raw_img, cv2.COLOR_BGR2GRAY)
        retval, img_bin = cv2.threshold(
            gray, THRESHHOLD_GRAY_MAIN, 255, cv2.THRESH_BINARY)
        src = np.float32([[237, 376], [39, 873], [1158, 312], [1914, 479]])
        dst = np.float32([[39, 254], [39, 873], [1158, 254], [1158, 873]])
        H = cv2.getPerspectiveTransform(src, dst)
        perspective_result = cv2.warpPerspective(img_bin, H, (0, 0))
        main_area = self.sweap_map(perspective_result)
        return main_area

    @staticmethod
    def get_rect_size(dot_list: list):
        width = dot_list[1][0] - dot_list[0][0]
        height = dot_list[3][1] - dot_list[0][1]
        return width * height

    @staticmethod
    def rank_rect(dot_list: list):
        K_SIZE = 1
        K_Y = 100
        return OCRHandle.get_center(dot_list)[1] * K_Y + OCRHandle.get_rect_size(dot_list) * K_SIZE

    def get_sorted_rects(self, main_area):
        _main_area, all_contours, hierarchy = cv2.findContours(
            main_area, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS)
        non_hole_contours = [cont for i, cont in enumerate(
            all_contours) if hierarchy[0][i][3] == -1]
        possible_rects = list(filter(self.is_rect_valid, map(
            self.contour_to_rect, non_hole_contours)))
        sorted_rects = sorted(possible_rects, key=self.rank_rect, reverse=True)
        if IS_WEB_VIDEO_ENABLED:
            for possible_rect in sorted_rects:
                self.draw_box(self.videos['video-cut'], possible_rect)
        return sorted_rects

    def analyse_img(self, raw_img):
        self.status = {}
        self.videos = {}
        self.index += 1

        CUT_PADDING = 10
        MAX_RECT_DISTANCE = 200

        main_area = self.pre_process_img(raw_img)
        main_height = main_area.shape[0]
        main_width = main_area.shape[1]
        MAIN_CENTER = (round(main_width * 0.5), 796)
        ANGLE_BASE = (MAIN_CENTER[0], main_height - 1)
        if IS_WEB_VIDEO_ENABLED:
            self.videos['video-cut'] = main_area.copy()

        sorted_rects = self.get_sorted_rects(main_area)
        is_text_found = False

        for (rect_a, rect_b) in self.iterate_rect_pairs(sorted_rects):
            rect_distance = min(self.get_distance(
                rect_a[0], rect_b[1]), self.get_distance(rect_a[1], rect_b[0]))
            if rect_distance < MAX_RECT_DISTANCE:
                is_text_found = True
                # self.status['rect_distance'] = round(rect_distance, 3)

                num_rects = sorted(
                    [rect_a, rect_b], key=lambda num_rect: num_rect[0][0])
                num_imgs = [self.cut_rectangle(
                    main_area, num_rect, CUT_PADDING) for num_rect in num_rects]
                num_list = self.recognize_number(num_imgs)
                self.status['confidence'] = min(num_list[0][1], num_list[1][1])

                if num_list[0][0] == 1:
                    rect_width_left = num_rects[0][1][0] - num_rects[0][0][0]
                    num_rects[0][0] = (num_rects[0][0][0] - rect_width_left, num_rects[0][0][1])
                    num_rects[0][3] = (num_rects[0][3][0] - rect_width_left, num_rects[0][3][1])
                if num_list[1][0] == 1:
                    rect_width_right = num_rects[1][1][0] - num_rects[1][0][0]
                    num_rects[1][1] = (num_rects[1][1][0] + rect_width_right, num_rects[1][1][1])
                    num_rects[1][2] = (num_rects[1][2][0] + rect_width_right, num_rects[1][2][1])

                text_center = self.find_text_center(main_area, num_rects)
                if IS_WEB_VIDEO_ENABLED:
                    cv2.line(self.videos['video-cut'],
                            rect_a[0], rect_b[1], 200, 10)
                    cv2.line(self.videos['video-cut'],
                            rect_a[1], rect_b[0], 200, 10)
                    for num_rect in num_rects:
                        self.draw_box(self.videos['video-cut'], num_rect)
                    self.videos['video-num-l'] = num_imgs[0]
                    self.videos['video-num-r'] = num_imgs[1]
                # cv2.imwrite("img_data//v5//{}_l_{}.jpg".format(self.index, self.status['text'][:1]), num_imgs[0])
                # cv2.imwrite("img_data//v5//{}_r_{}.jpg".format(self.index, self.status['text'][1:]), num_imgs[1])
                break

        if not is_text_found and sorted_rects:
            is_text_found = True
            rect_a = sorted_rects[0]
            if IS_WEB_VIDEO_ENABLED:
                self.draw_box(self.videos['video-cut'], rect_a)
                cv2.line(self.videos['video-cut'], rect_a[0], rect_a[1], 200, 10)
            text_center = self.get_center(rect_a)
            num_img = self.cut_rectangle(main_area, rect_a, CUT_PADDING)
            num_list = self.recognize_number([num_img])
            self.status['confidence'] = num_list[0][1]
            # cv2.imwrite("img_data//v5//{}_c_{}.jpg".format(self.index, self.status['text']), num_img)
            if IS_WEB_VIDEO_ENABLED:
                self.videos['video-num-l'] = num_img

        if is_text_found:
            self.status['number'] = functools.reduce(lambda x, y: 10 * x + y[0], num_list, 0)
            # self.status['center'] = text_center
            center_diff = (text_center[0] - MAIN_CENTER[0],
                           text_center[1] - MAIN_CENTER[1])
            self.status['x'] = int(center_diff[0])
            self.status['y'] = int(center_diff[1])
            self.status['angle'] = round(180 / np.pi * math.atan(
                (text_center[0] - ANGLE_BASE[0]) / (text_center[1] - ANGLE_BASE[1])))
            if IS_WEB_VIDEO_ENABLED:
                cv2.line(self.videos['video-cut'],
                        text_center, MAIN_CENTER, 200, 10)
                cv2.line(self.videos['video-cut'],
                        text_center, ANGLE_BASE, 200, 10)
            SERIAL_START_OF_LINE = "by"
            SERIAL_PORT_LENGTH = 10
            SERIAL_PORT_TYPE = 0x0A
            SERIAL_END_OF_LINE = "\r\n"
            self.serial_data = SERIAL_START_OF_LINE.encode("ASCII")
            self.serial_data += struct.pack('B', SERIAL_PORT_LENGTH)
            self.serial_data += struct.pack('B', SERIAL_PORT_TYPE)
            self.serial_data += struct.pack('B', self.status['number'])
            self.serial_data += struct.pack('h', self.status['x'])
            self.serial_data += struct.pack('h', self.status['y'])
            self.serial_data += SERIAL_END_OF_LINE.encode('ASCII')
        logging.info("Result: {}".format(self.status))
