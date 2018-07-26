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
        gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
        threshold = 170
        retval, gray_b = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLines(edges,1,np.pi/180, 150)
        if lines is not None:
            for line in lines:
                r,theta = line[0]
                # Stores the value of cos(theta) in a
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
                cv2.line(orig,(x1,y1), (x2,y2), (0,0,255),10)
            return len(lines)
        else:
            return -1

