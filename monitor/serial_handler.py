import binascii
import logging
import os
import time
import serial
from multiprocessing import Process
from .config import IS_SERIAL_ENABLED, SERIAL_BAUDRATE, SERIAL_PORT, STANDARD_BASE_INTERVAL, SERIAL_ALWAYS_HAS_TASK


class SerialHandler(Process):
    def __init__(self, queues):
        super().__init__()
        self.ser = None
        self.queues = queues

    def has_task(self):
        return SERIAL_ALWAYS_HAS_TASK

    def run(self):
        logging.warning("Start `{}` process at PID `{}`.".format(self.__class__.__name__, os.getpid()))
        logging.warning("Open serial port `{}` at baudrate `{}`.".format(SERIAL_PORT, SERIAL_BAUDRATE))
        if IS_SERIAL_ENABLED:
            self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
            while True:
                time.sleep(STANDARD_BASE_INTERVAL)
                if self.has_task() and self.queues['task_queue'].qsize() <= 1:
                    self.queues['task_queue'].put(-1)
                while not self.queues['bytes_queue'].empty():
                    new_bytes = self.queues['bytes_queue'].get()
                    if new_bytes is None:
                        break
                    else:
                        logging.info("Serial: `{}`".format(binascii.hexlify(new_bytes)))
                        self.ser.write(new_bytes)
            logging.warning("Closing serial port `{}`.".format(SERIAL_PORT))
            self.ser.close()
