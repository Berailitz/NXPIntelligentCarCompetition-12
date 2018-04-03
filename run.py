"""start main app"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
from monitor import app, credentials

application = app.create_app(log_path='log')

def main():
    """main func"""
    logging.info('start...')
    application.run(port=credentials.PORT)

if __name__ == '__main__':
    main()
