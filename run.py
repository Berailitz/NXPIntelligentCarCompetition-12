"""start main app"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

from tornado import ioloop
from monitor.app import create_app
from monitor.camera_handler import CameraUnit
from monitor.config import IS_WEB_ENABLED, IS_SERIAL_ENABLED 

application = create_app(log_path='log')


def main():
    """main func"""
    if IS_WEB_ENABLED:
        ioloop.IOLoop.instance().start()
    else:
        IS_SERIAL_ENABLED = True
        camera_unit = CameraUnit(0)
        while True:
            camera_unit.detect_video()


if __name__ == '__main__':
    main()
