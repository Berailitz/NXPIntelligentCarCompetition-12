import matplotlib.pyplot as plt
import numpy as np
import argparse
import imutils
import cv2
import math

def center(image, a, b, c):
          #cv2.imshow("original", image)
          gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#灰度化
          #blurred = cv2.GaussianBlur(gray, (5, 5), 0)
          thresh = cv2.threshold(gray, 150, 128, cv2.THRESH_TRUNC)[1]
          cnts = cv2.findContours(thresh, cv2.RETR_LIST,
                  cv2.CHAIN_APPROX_NONE )
          x, y, w, h = cv2.boundingRect(cnts[0])
          gray = cv2.rectangle(gray, (x, y), (x + w, y + h), (255, 255, 255), -1)
          # x, y, w, h, angle = cv2.minAreaRect(cnts[0])
          cnts = cnts[0] if imutils.is_cv2() else cnts[1]
          cnts = cv2.findContours(gray, cv2.RETR_LIST,
                                  cv2.CHAIN_APPROX_NONE)
          # loop over the contours
          # compute the center of the contour
          M = cv2.moments(cnts[0])
          cX = int(M["m10"] / M["m00"])
          cY = int(M["m01"] / M["m00"])
          # draw the contour and center of the shape on the image
          # cv2.drawContours(gray, [cnts[0]], -1, (255, 255, 0), 2)
          # cv2.circle(image, (cX, cY), 7, (255, 0, 0), -1)
          # cv2.putText(image, "center", (cX - 20, cY - 20),
          #         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
          #print(cX,cY)
          P = [cX, cY, a, b, c]
          P[1] = math.sqrt((P[1] * P[1] + P[0] * P[0]) / (math.cos(P[2]) * math.cos(P[2])) - P[0] * P[0])
          X = cX
          Y = P[1]
          point = [cX, cY]
          return point
          #s[c]=str(cY)
          #cv2.imshow("Image", image)
          #k = cv2.waitKey(0)
          #if k == 27:  # wait for ESC key to exitcv2.destroyAllWindows
           #       cv2.destroyAllWindows


