import math
import struct
import time
import cv2
import numpy as np
from .image_processer import ImageProcesser

def get_H(src_list):
    left_up=src_list[0]
    left_down=src_list[1]
    right_up=src_list[2]
    right_down=src_list[3]

    dst=list()
    '''
    dst.append([left_down[0],right_up[1]])
    dst.append([left_down[0],left_down[1]])
    dst.append([right_up[0],right_up[1]])
    dst.append([right_up[0],left_down[1]])
    '''

    dst.append([left_up[0], right_up[1]])
    dst.append([left_up[0], left_down[1]])
    dst.append([right_up[0], right_up[1]])
    dst.append([right_up[0], left_down[1]])

    dst=np.array(dst)
    return cv2.getPerspectiveTransform(src_list,dst)

class Chess:
    def __init__(self,x,y,r):
        self.x=x
        self.y=y
        self.r=r


def get_chess(image,minR=230,maxR=250,hough_pram2=10,getImg=True):
    chess_list=[]
    image=cv2.GaussianBlur(image,(3,3),7)
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    kernel = np.ones((5, 5), np.uint8)
    gray = cv2.erode(gray, kernel, iterations=10)    #腐蚀


    gray = cv2.Laplacian(gray, cv2.CV_8U, gray, 3)
    #ret, gray = cv2.threshold(gray, 140, 255, 0)

    gray = cv2.dilate(gray, kernel, iterations=5) # 膨胀
    circles=cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,60,param1=400,param2=hough_pram2,minRadius=minR,maxRadius=maxR)
    if circles is None:
        return None
    circles=np.uint16(np.around(circles))

    cimg=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)  # 转RGB

    for i in circles[0,:]:
        x=int(i[0])
        y=int(i[1])
        r=int(i[2])
        chess=Chess(x,y,r)
        chess_list.append(chess)
    biggest=chess_list[0]
    for i in chess_list:
        if i.r>biggest.r:
            biggest=i
    if biggest.r > 200:
        cv2.circle(cimg,(biggest.x,biggest.y),biggest.r,(0,0,255),2)
        cv2.circle(cimg, (biggest.x, biggest.y), 2, (255,0,0), 2)
    if getImg==True:
        return cimg
    else:
        if biggest.r>200:
            return (biggest.x,biggest.y,biggest.r)
        else:
            return None

class Line:
    def __init__(self,x1=0,y1=0,x2=0,y2=0,k=None,b=None):
        self.start=(x1,y1)
        self.end=(x2,y2)
        if k is None:
            self.k=(y2-y1)/(x2-x1)
        else:
            self.k=k
        if b is None:
            self.b=-self.k*x1+y1
        else:
            self.b=b
        if abs(self.k)<1:
            self.isrow=True
        else:
            self.isrow=False

        if self.isrow:
            self.lengh=abs(self.end[0]-self.start[0])
        else:
            self.lengh=abs(self.end[1]-self.start[1])


class Cross:
    def __init__(self):
        self.rows=[]
        self.cols=[]

    def add_line(self,line):
        if line.isrow==True:
            if len(self.rows)>=2:
                return None
            for i in self.rows:
                if self.is_same_line(i,line):
                    break
            else:
                self.rows.append(line)
        else:
            if len(self.cols)>=2:
                return None
            for i in self.cols:
                if self.is_same_line(i,line):
                    break
            else:
                self.cols.append(line)

    def get_cross_point(self):
        if len(self.rows)==2:
            row_width=int(abs(self.rows[0].start[1]-self.rows[1].start[1]))
        if len(self.cols)==2:
            col_width=int(abs(self.cols[0].start[0]-self.cols[1].start[0]))

        if len(self.rows)+len(self.cols)==3:
            if len(self.rows)==1:
                new_row=Line(x1=self.rows[0].start[0],
                             y1=self.rows[0].start[1]+col_width,
                             x2=self.rows[0].end[0],
                             y2=self.rows[0].end[1]+col_width)
                self.add_line(new_row)
                row_width=col_width
            else:
                new_col=Line(x1=self.cols[0].start[0]-row_width,
                             y1=self.cols[0].start[1],
                             x2=self.cols[0].end[0]-row_width,
                             y2=self.cols[0].end[1])
                self.add_line(new_col)
                col_width=row_width
        if len(self.rows)!=2 or len(self.cols)!=2:
            raise Exception
        if abs(row_width-col_width)>20:
            # 判断宽度
            raise Exception
        #if self.rows[0].k*self.cols[1].k>-0.8:
            #print(self.rows[0].k)
            #   print(self.rows[0].k*self.cols[1].k)
            #raise Exception
        temp_k=(self.rows[0].k+self.rows[1].k)/2
        temp_b=(self.rows[0].b+self.rows[1].b)/2
        row_line=Line(k=temp_k,b=temp_b)

        inf=float("inf")
        if abs(self.cols[0].k)==inf or abs(self.cols[1].k)==inf: # 处理垂直的直线的情况
            x=(self.cols[0].start[0]+self.cols[1].start[0])/2
            y=row_line.k*x+row_line.b
            x=int(x)
            y=int(y)
        else:
            temp_k = (self.cols[0].k + self.cols[1].k) / 2
            temp_b = (self.cols[0].b + self.cols[1].b) / 2
            col_line = Line(k=temp_k, b=temp_b)
            x,y=self.get_2lines_cross(row_line,col_line)
        angle=math.atan(self.cols[0].k)*180/math.pi
        return (x,y,angle)




    def get_2lines_cross(self,line1,line2):
        x=(line2.b-line1.b)/(line1.k-line2.k)
        y=line1.k*x+line1.b

        x=int(x)
        y=int(y)
        return (x,y)


    def is_same_line(self,line1,line2):
        if line1.isrow==True:
            if abs(line1.b-line2.b)<10:
                return True
            else:
                return False
        else:
            if abs(line1.start[0]-line2.start[0])<10:
                return True
            else:
                return False


SRC = np.float32([[106, 153], [460, 476], [272, 109], [625, 277]])
H = get_H(SRC)
def get_cross5(image,getImg=True):
    height=int(image.shape[0])
    width=int(image.shape[1])
    kernel = np.ones((5, 5), np.uint8)

    #image=image[0:int(height/12)*6,:]  # 切片，不要的扔掉
    image = cv2.warpPerspective(image, H, (640, 480))
    #image=image[:,0:int(width/2)]
    #image=image[0:int(height/12)*6:,int(width/4):width]
    #image=image[int(height/12)*:height,:]
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    gray = cv2.erode(gray, kernel, iterations=5)    #腐蚀
    t,contours,h=cv2.findContours(gray,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)  # 找外轮廓
    #gray = cv2.Laplacian(gray, cv2.CV_8U, gray,5 )
    #ret, gray = cv2.threshold(gray, 140, 255, 0)

    gray=cv2.Canny(gray,300,300)
    cv2.drawContours(gray,contours,-1,(0,0,0),2)  #去掉外轮廓 实际上是为了去掉透视后的黑边

    gray = cv2.dilate(gray, kernel, iterations=1)

    lines = cv2.HoughLinesP(gray, 1, np.pi / 180, 120, minLineLength=100, maxLineGap=100)
    cimg = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    cross = Cross()
    if lines is None:
        if getImg == True:
            return cimg
        else:
            return None
    for j in lines:
        i = j[0]
        x1 = i[0]
        y1 = i[1]
        x2 = i[2]
        y2 = i[3]
        temp = Line(x1, y1, x2, y2)

        cross.add_line(temp)
        cv2.line(cimg, (x1, y1), (x2, y2), (0, 255, 0), 1)
    if len(cross.cols)==0:
        # 如果没找到竖线
        lines=cv2.HoughLinesP(gray, 1, np.pi / 180, 30, minLineLength=0, maxLineGap=1)
        if lines is not None:
            for j in lines:
                i = j[0]
                x1 = i[0]
                y1 = i[1]
                x2 = i[2]
                y2 = i[3]
                temp = Line(x1, y1, x2, y2)
                if abs(temp.k)>5:
                    cross.add_line(temp)
                    cv2.line(cimg, (x1, y1), (x2, y2), (0, 255, 0), 1)
    try:
        (x, y, angle) = cross.get_cross_point()  # 如果没找够4条线，这里会抛出异常
        cv2.circle(cimg, (x, y), 2, (255, 255, 0), 2)
    except:
        if getImg == True:
            return cimg
        else:
            return None
    if getImg == True:
        print(x, y, angle)
        return cimg
    else:
        if x>640 or y>480 or x<0 or y<0:
            return None
        else:
            return (x, y, angle)


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

