"""start main app"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

from tornado import ioloop
from monitor.app import create_app

application = create_app(log_path='log')


def main():
    """main func"""
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
