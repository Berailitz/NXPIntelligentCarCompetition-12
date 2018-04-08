# coding:utf8
import cv2
from .center import center
from .classroom import target
import time
def produce():
        camera = cv2.VideoCapture(0)
        history = 20    # 训练帧数
    
        bs = cv2.createBackgroundSubtractorKNN(detectShadows=False)  # 背景减除器，设置阴影检测
        bs.setHistory(history)
        rem=0    
        targ=target(100,0,0,1)#先定义出targ
        frames = 0
        a=0
        while True:
            res, frame = camera.read()
            a+=1
            if not res:
                break

            fg_mask = bs.apply(frame)   # 获取 foreground mask

            if frames < history:
                frames += 1
                continue

        # 对原始帧进行膨胀去噪
            th = cv2.threshold(fg_mask.copy(), 244, 255, cv2.THRESH_BINARY)[1]
            th = cv2.erode(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=2)
            dilated = cv2.dilate(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 3)), iterations=2)
        # 获取所有检测框
            image, contours, hier = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for c in contours:
            # 获取矩形框边界坐标
                x, y, w, h = cv2.boundingRect(c)
            # 计算矩形框的面积
                area = cv2.contourArea(c)
                if 500 < area < 3000:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            dilated=cv2.cvtColor(dilated,cv2.COLOR_GRAY2RGB)
            pointx,pointy=center(dilated, 0.785, 1000, 3.09)
            #print(pointx,pointy)
            if (pointx!=0)&(pointy!=0)& (rem==1):
                targ.update(100,pointx,pointy)
            elif (pointx!=0)&(pointy!=0) & (rem==0):
            #print(1)
                targ=target(100,pointx,pointy,1)#第一个数据是长宽比，最后一个是帧长
                rem=1
            elif (pointx==0)&(pointy==0) :
                rem=0
            #print(0)
            diction= targ.dictionary(frame,pointx,pointy)
            #cv2.imshow("detection", frame)
            yield diction
        #cv2.imshow("back", dilated)
class result(object):
    def __init__(self):
       self.c = produce()
    def detect_video(self):
        self.dict = next(self.c)
        return self.dict
    

    
