import logging
import time
import serial
from multiprocessing import Process
from .config import IS_SERIAL_ENABLED, SERIAL_BAUDRATE, SERIAL_PORT, SCAN_INTERVAL


class SerialHandler(Process):
    def __init__(self, queues):
        super().__init__()
        self.ser = None
        self.queues = queues

    def has_task(self):
        return True

    def run(self):
        logging.warning("Open serial port `{}` at baudrate `{}`.".format(SERIAL_PORT, SERIAL_BAUDRATE))
        if IS_SERIAL_ENABLED:
            self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
            while True:
                time.sleep(SCAN_INTERVAL)
                if self.has_task():
                    self.queues['task_queue'].put(-1)
                while not self.queues['bytes_queue'].empty():
                    new_bytes = self.queues['bytes_queue'].get()
                    if new_bytes is None:
                        break
                    else:
                        self.ser.write(new_bytes)
            logging.warning("Closing serial port `{}`.".format(SERIAL_PORT))
            self.ser.close()
