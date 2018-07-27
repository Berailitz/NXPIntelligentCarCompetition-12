import itertools
import logging
import math
import cv2
import numpy as np
import pytesseract


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
        noise_threshold = 20
        mid = round(0.5 * width)
        for x in self.possible_mids(width):
            noise = 0
            for y in range(round(height * 0.25), round(height * 0.75)):
                if img[y, x] == 0:
                    noise += 1
            if noise >= noise_threshold:
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
        img_m = cv2.resize(img, (100, 120))
        number = pytesseract.image_to_string(
            img_m, config='-c tessedit_char_whitelist=0123456789 -psm 10')
        return number

    def check_line_duplication(self, current_list: list, new_r, new_theta) -> bool:
        is_duplicate = False
        min_gap_r = 40
        min_gap_theta = 0.2
        for current_line in current_list:
            current_r, current_theta = current_line
            if abs(current_r - new_r) < min_gap_r and abs(new_theta - current_theta) < min_gap_theta:
                is_duplicate = True
                break
        return is_duplicate

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

    def filter_lines(self, lines: list) -> tuple:
        vert_lines = []
        hori_lines = []
        for line in lines:
            r, theta = line[0]
            if theta < np.pi * 0.25 or theta > np.pi * 0.75:
                # 竖线
                is_duplicate = self.check_line_duplication(vert_lines, r, theta)
                if not is_duplicate:
                    vert_lines.append(line[0])
                    a, b = self.get_line_in_ab(r, theta)
                    cv2.line(self.orig, *self.get_line_tuple(r, theta), (200, 0, 0), 2)
                    # print(f"Vert: {(r,theta)}, y = {a} * x + {b}")
            else:
                # 横线
                is_duplicate = self.check_line_duplication(hori_lines, r, theta)
                if not is_duplicate:
                    hori_lines.append(line[0])
                    a, b = self.get_line_in_ab(r, theta)
                    cv2.line(self.orig, *self.get_line_tuple(r, theta), (200, 0, 0), 2)
                    # print(f"Hori: {(r,theta)}, y = {a} * x + {b}")
        return (sorted(hori_lines, key=lambda line: line[0] / math.cos(line[1])), sorted(vert_lines, key=lambda line: line[0] / math.cos(line[1])))

    @staticmethod
    def iterate_near(iterable) -> tuple:
        iterater = iter(iterable)
        first = next(iterater)
        second = next(iterater)
        while True:
            yield (first, second)
            first = second
            try:
                second = next(iterater)
            except StopIteration:
                break

    @staticmethod
    def get_line_in_ab(r, theta) -> tuple():
        result = None
        if theta == 0:
            result = (0, 0)
        else:
            result = (- 1.0 / math.tan(theta), r / math.sin(theta))
        return result

    def get_line_crossing(self, line_1: tuple, line_2: tuple) -> tuple():
        a_1, b_1 = self.get_line_in_ab(*line_1)
        a_2, b_2 = self.get_line_in_ab(*line_2)
        return (round((b_2 - b_1) / (a_1 - a_2)), round((a_1 * b_2 - a_2 * b_1) / (a_1 - a_2)))

    def is_in_image(self, image, x, y) -> bool:
        width = image.shape[1]
        height = image.shape[0]
        return x > 0 and x < width and y > 0 and y < height

    def get_rec_ratio(self, dot_list: list) -> float:
        min_x = 10000
        max_x = 0
        min_y = 10000
        max_y = 0
        for (x, y) in dot_list:
            if x > max_x:
                max_x = x
            if x < min_x:
                min_x = x
            if y > max_y:
                max_y = y
            if y < min_y:
                min_y = y
        self.status['height'] = max_y - min_y
        self.status['width'] = max_x - min_x
        return max(1.0 * self.status['height'] / self.status['width'], 1.0 * self.status['width'] / self.status['height'])

    def get_max_square(self, hori_lines: list, vert_lines: list) -> tuple:
        max_square_size = 0
        max_square = None
        for hori_line_pair, vert_line_pair in itertools.product(self.iterate_near(hori_lines), self.iterate_near(vert_lines)):
            # print(f"line_pairs: {hori_line_pair}, {vert_line_pair}")
            line_crossings = [] # [(x, y), ..]
            for hori_line, vert_line in itertools.product(iter(hori_line_pair), iter(vert_line_pair)):
                x, y = self.get_line_crossing(hori_line, vert_line)
                if self.is_in_image(self.orig, x, y):
                    line_crossings.append((x, y))
            if len(line_crossings) == 4:
                ratio = self.get_rec_ratio(line_crossings)
                if ratio < 1.5:
                    new_size = cv2.contourArea(np.intp(line_crossings))
                    self.status['ratio'] = round(ratio, 3)
                    # print(f"new size: {new_size}")
                    if new_size > max_square_size:
                        max_square = line_crossings.copy()
                        # cv2.drawContours(orig, np.intp([max_square]), -1, (255, 0, 0), 3)
        if max_square is not None:
            max_square[2], max_square[3] = max_square[3], max_square[2]
        return max_square

    def analyse_img(self, orig):
        self.orig = orig
        self.cut = None
        self.index += 1
        THRESHHOLD_CUT = 150
        width = orig.shape[1]
        height = orig.shape[0]
        canvas = np.float32([[0, height], [width, height], [width, 0], [0, 0]])
        gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi/180, 150)
        if lines is not None:
            hori_lines, vert_lines = self.filter_lines(lines)
            # logging.info(f"hori_lines: {hori_lines}")
            # logging.info(f"vert_lines: {vert_lines}")
            if hori_lines and vert_lines and len(hori_lines) >= 2 and len(vert_lines) >= 2:
                max_square = self.get_max_square(hori_lines, vert_lines)
                if max_square:
                    cv2.drawContours(orig, np.intp([max_square]), -1, (0, 250, 0), 3)
                    M = cv2.getPerspectiveTransform(np.float32([max_square]), canvas)
                    self.cut = cv2.warpPerspective(gray, M, (0, 0))
                    retval, self.cut = cv2.threshold(self.cut, THRESHHOLD_CUT, 255, cv2.THRESH_BINARY)
                    self.status['line_counter'] = len(hori_lines) + len(vert_lines)
                    return
        self.status['line_counter'] = -1
