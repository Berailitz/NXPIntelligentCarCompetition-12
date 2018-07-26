import time
import datetime
import math
from matplotlib import pyplot as plt
import cv2
import numpy as np
import pytesseract


class OCRHandle(object):
    def __init__(self):
        self.orig = None
        self.index = 0

    def cut_window(self, img):
        threshold1 = 0
        threshold2 = 60
        height = round(img.shape[0])
        width = round(img.shape[1])
        _, thresh = cv2.threshold(img, threshold1, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
        contours = sorted(contours, key=lambda cont: cv2.contourArea(cont), reverse=True)
        rect = cv2.minAreaRect(contours[0])
        box = cv2.boxPoints(rect)
        cv2.drawContours(self.orig, [np.int0(box)], 0, (0,0,255), 10)
        box_f = np.float32(box)
        canvas = np.float32([[width,height], [0,height], [0,0], [width,0]])
        M = cv2.getPerspectiveTransform(box_f, canvas)
        result = cv2.warpPerspective(img, M, (0, 0))
        retval, result_b = cv2.threshold(result, threshold2, 255, cv2.THRESH_BINARY)
        return result_b


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
        im2, contours_word, hierarchy = cv2.findContours(np.invert(raw_word_img), cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
        contours_word = sorted(contours_word, key=lambda cont: cv2.contourArea(cont), reverse=True)
        x, y, w, h = cv2.boundingRect(contours_word[0])
        return raw_word_img[y:y+h, x:x+w]


    def recognize_number(self, img):
        img_m = cv2.resize(img, (100, 120))
        number = pytesseract.image_to_string(img_m, config='-c tessedit_char_whitelist=0123456789 -psm 10')
        return number


    def analyse_img(self, orig):
        self.orig = orig
        self.index += 1
        begin = datetime.datetime.now()
        print(f"to gray: {datetime.datetime.now()}")
        img = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
        img = np.invert(img)
        print(f"cut_window: {datetime.datetime.now()}")
        img_cut = self.cut_window(img)
        cv2.imwrite(f"img_cut_{self.index}.jpg", img_cut)
        print(f"find_mid: {datetime.datetime.now()}")
        mid = self.find_mid(img_cut)
        half_imgs = [img_cut[:, :mid], img_cut[:, mid:]]
        print(f"cut2: {datetime.datetime.now()}")
        num_imgs = [self.cut_single_word(half_img) for half_img in half_imgs]
        print(f"ocr: {datetime.datetime.now()}")
        data = [self.recognize_number(num_img) for num_img in num_imgs]
        end = datetime.datetime.now()
        print(f"end: {datetime.datetime.now()}")
        print(end - begin)
        return "".join(data)

