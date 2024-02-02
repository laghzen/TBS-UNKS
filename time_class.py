import threading

import sys
import time


class Timer(threading.Thread):
    def __init__(self, time_slow):
        super().__init__()
        self.time_slow = time_slow
        self.stop_flag = False
        self.start_time = 0

    def set_transfer(self, transfer):
        self.transfer = transfer

    def get_time(self):
        return time.time() - self.start_time

    def stop(self):
        self.stop_flag = True

    def run(self):
        self.start_time = time.time()
        while time.time() - self.start_time < self.time_slow and not self.stop_flag:
            time.sleep(5)

        if not self.stop_flag:
            self.transfer.stop_transfer()
