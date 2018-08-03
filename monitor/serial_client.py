"""Client receiving camera data."""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import serial
from .credentials import SERIAL_BAUDRATE, SERIAL_PORT


def main():
    END_OF_LINE = '\n'.encode('utf8')
    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE) as ser:
        bin_text = b''
        while True:
            bin_word = ser.read()
            bin_text += bin_word
            if bin_word == END_OF_LINE:
                print(bin_text[:2].decode('utf8'), end='')
                print(bin_text[2:])

if __name__ == '__main__':
    main()
