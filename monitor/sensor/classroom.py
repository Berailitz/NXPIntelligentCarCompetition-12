class target(object):
    def __init__(self,lwrate,x,y,zhentime):
        self.speed=[]#速度
        self.lwrate=[lwrate]#长宽比
        self.maxspeed=0#最大速度
        self.xroc=[] #x上变化率
        self.acspeed=[]#加速度
        self.x=[x]#x的值
        self.y=[y]#y的值#二维的x,y?还是三维的x,y?
        self.time=zhentime#每帧时长
        self.counter=5
    def update(self,lwrate,x,y):
        self.x.append(x)
        self.y.append(y)
        self.lwrate.append(lwrate)
        self.speed.append(pow(pow(self.x[-1]-self.x[-2],2)+pow(self.y[-1]-self.y[-2],2),1/2)/self.time)#要求三维，速度大小
        self.maxspeed=max(self.speed)
        if len(self.x)>2:
            self.xroc.append(self.x[-1]-self.x[-2])#要求三维，正则是向右移动，负则是向左移动
        if len(self.speed)>2:
            self.acspeed.append(self.speed[-1]-self.speed[-2])#正则是变大，负则是变小
        #print(self.x,self.y,self.lwrate,self.speed,self.maxspeed,self.xroc,self.acspeed)
    def dictionary(self,img,x,y):
        if  self.counter!=0:#输出图片
            self.counter=self.counter-1
            #data=[self.speed[-1],self.lwrate[-1],self.maxspeed,self.xroc[-1],self.acspeed[-1]]
            diction={'picture':img, 'data': {'速度':'','长宽比':'','最大速度':'','x方向变化量':'','加速度':''}}
            #print(diction['data'])
            return diction
        else:#输出数据+图片
            self.counter=5
            if (x==0 )&(y==0):
                diction={'picture':img,'data': {'速度':0,'长宽比':0,'最大速度':0,'x方向变化量':0,'加速度':0}}
                #print(diction['data'])
                return diction
            else:      
                diction={'picture':img,'data':{'速度':int(self.speed[-1]),'长宽比':int(self.lwrate[-1]),'最大速度':int(self.maxspeed),'x方向变化量':int(self.xroc[-1]),'加速度':int(self.acspeed[-1])}}
                return diction
