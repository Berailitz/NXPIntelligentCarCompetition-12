"""start main app"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
import os
from monitor.app import WebProcess
from monitor.bus import queues
from monitor.camera_handler import CameraProcess
from monitor.config import IS_CHESS_ENABLED, IS_CROSS_ENABLED, IS_DIGIT_ENABLED, IS_WEB_ENABLED, IS_SERIAL_ENABLED, LOG_PATH, MAIN_CAMERA_ID
from monitor.cross_finder import Crossfinder, Chessfinder
from monitor.mess import get_current_time, set_logger
from monitor.serial_handler import SerialHandler
from monitor.ocr import OCRHandle


def main():
    """main func"""
    try:
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)
        set_logger('{}/log_{}_{}.txt'.format(LOG_PATH, get_current_time(), os.getpid()))
        logging.warning("Start `{}` process at PID `{}`.".format("main", os.getpid()))
        if IS_SERIAL_ENABLED:
            serial_process = SerialHandler(queues)
            serial_process.start()
        camera_process = CameraProcess(queues)
        camera_process.start()
        if IS_CROSS_ENABLED:
            cross_finder = Crossfinder(queues)
            cross_finder.start()
        if IS_CHESS_ENABLED:
            chess_finder = Chessfinder(queues)
            chess_finder.start()
        if IS_DIGIT_ENABLED:
            ocr = OCRHandle(queues)
            ocr.initialize()
            ocr.start()
        if IS_WEB_ENABLED:
            web_process = WebProcess()
            web_process.run()
        else:
            web_process = None
            queues['id_queue'].put(MAIN_CAMERA_ID)
        camera_process.join()
        if IS_CROSS_ENABLED:
            cross_finder.join()
        if IS_CHESS_ENABLED:
            chess_finder.join()
        if IS_DIGIT_ENABLED:
            ocr.join()
        queues['bytes_queue'].put(None)
        serial_process.join()
        web_process.join()
    except Exception as e:
        logging.exception(e)
        if IS_WEB_ENABLED:
            web_process.terminate()
        if IS_SERIAL_ENABLED:
            serial_process.terminate()
        camera_process.terminate()
        if IS_CROSS_ENABLED:
            cross_finder.terminate()
        if IS_CHESS_ENABLED:
            chess_finder.terminate()
        if IS_DIGIT_ENABLED:
            ocr.terminate()


if __name__ == '__main__':
    main()
