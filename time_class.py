import threading

import sys
import time


class Timer(threading.Thread):
    def __init__(self, time_slow):
        super().__init__()
        self.time_slow = time_slow
        self.stop_err = False
        self.start_time = 0

    def get_time(self):
        return time.time() - self.start_time

    def run(self):
        self.start_time = time.time()
        while time.time() - self.start_time < self.time_slow and not self.stop_err:
            time.sleep(5)
        if not self.stop_err:
            print("Скрипт слишком медленный!")
            sys.exit()
        else:
            print('Все ок!')


def time_break(func):
    def wrapper(*args, **kwargs):
        th = Timer(4.5 * 60)
        th.start()
        result = func(*args, **kwargs)
        th.stop()
        return result

    return wrapper
