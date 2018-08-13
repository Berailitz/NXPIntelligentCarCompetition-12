"""start main app"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import os
from monitor import config
from monitor.camera_handler import CameraUnit
from monitor.mess import get_current_time, set_logger


def main():
    """main func"""
    log_path = 'log'
    config.IS_SERIAL_ENABLED = True
    config.IS_WEB_ENABLED = False
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    set_logger('{}/log_{}_{}.txt'.format(log_path, get_current_time(), os.getpid()))
    camera_unit = CameraUnit(0)
    while True:
        camera_unit.detect_video()


if __name__ == '__main__':
    main()
