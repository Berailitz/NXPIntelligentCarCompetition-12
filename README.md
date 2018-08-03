## 数字识别&定位模块

#### 文件结构
├───.vscode VS Code 配置文件
├───camera_calibration 摄像头标定工具
├───img_data 图片样本
│   └───v5
│       └───dataset_30
├───log 运行日志
│───monitor 主程序模块
│   ├───static 网页附件
│   │   ├───css
│   │   └───js
│   ├───templates 网页模板
│   ├───`app.py` 主程序入口
│   ├───`camera_handler.py` 图像输入接口
│   ├───`config.py` 设置项
│   ├───`credentials.py` 机密设置项
│   ├───`handler.py` HTTP 后端
│   ├───`mess.py` 杂物
│   ├───`ocr.py` 图像处理及文字识别模块
│   ├───`protocol.md` 协议文本
│   └───`serial_client.py` 串口客户端
├───`run.py` 入口程序
└───`run.sh` Linux 下的入口程序


#### 运行逻辑
1. `app.py`定义服务器逻辑
1. HTTP请求被传递给`handler.py`处理
1. `camera_handler.py`从摄像头获取图像
1. `ocr.py`加载特征库并处理opencv图像


#### 图像输入流程
1. `CameraHandler`管理摄像头，出现新摄像头调用时构造一个`CameraUnit`对象
1. `CameraUnit`获取一张图像，并调用`OCRHandle`处理
1. `CameraUnit`序列化处理结果

#### 图像处理流程
1. 灰度化
1. 二值化
1. 逆透视
1. 调整长宽比
1. 泛洪法剔除棋盘方框
1. 获取凸包，构成矩形，并排序
1. 顺序遍历寻找数字
1. 识别数字，重心位置纠偏

#### 安装
1. 使用 Python 3.5.3 编译 opencv
1. 顺序安装 Cython, matplotlib, scipy, scikit-image
1. 安装 requirements.txt 中的其他库
1. 安装 tesseract

#### 运行
1. 建立 `config.py`, `credentials.py`
1. 运行 `run.py`

#### 调优
1. 降噪相关
    1. SHORTEST_BOARDER
    1. LONGEST_BOARDER
    1. MAX_RATIO
1. 定位相关
    1. MAIN_CENTER
    1. ANGLE_BASE
1. OCR 相关
    1. STANDARD_SIZE
    1. THRESHHOLD_CONFIDENCE
1. 排序凸包矩形相关
    1. K_SIZE
    1. K_Y

#### TODO
1. 空白（无数字）图片检测
1. SSIM预计算
1. 多线程（图片分块）计算
1. 特性学习记录模式
1. 串口客户端解析数据
