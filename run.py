"""start main app"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
from tornado import ioloop
from monitor import app, credentials

application = app.create_app(log_path='log')


def main():
    """main func"""
    logging.info('start...')
    application.listen(port=credentials.PORT, address='::')
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
