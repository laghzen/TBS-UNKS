import threading
import time
import traceback
import sys
import math


class Radar(threading.Thread):
    def __init__(self, stand, FPS):
        super().__init__()
        self.FPS = FPS

        self.size_x = 211 // 2
        self.size_y = 203 // 2

        self.x = 50 // 2 + self.size_x // 2
        self.y = 620 // 2 + self.size_y // 2

        self.a = 0
        self.speed = 0
        self.k = 1.8

        self.max_a = 24

        self.working_mode = 2
        self.rotation_mode = 0

        self.time_prev = 0

    def run(self):
        while True:
            time_now = self.get_time()
            self.a += self.speed * self.k * (time_now - self.time_prev)
            self.a = max(-self.max_a, min(self.max_a, self.a))
            self.time_prev = time_now

            if self.speed == 0:
                self.working_mode = 3
                if self.speed > 0:
                    self.rotation_mode = 1
                else:
                    self.rotation_mode = 2
            else:
                self.working_mode = 2
                self.rotation_mode = 0

            if self.a == self.max_a:
                self.rotation_mode = 3
            if self.a == -self.max_a:
                self.rotation_mode = 4

            time.sleep(0.001)

    def set_speed(self, value):
        self.speed = value

    def set_timer(self, get_time):
        self.get_time = get_time


class Sputnik(threading.Thread):
    def __init__(self, stand, FPS):
        super().__init__()
        self.FPS = FPS

        self.radar = stand.radar

        self.size_x = 124 // 2
        self.size_y = 147 // 2

        self.x = stand.WIDTH - self.size_x + 3
        self.startY = stand.HEIGHT // 2 - self.size_y
        self.y = self.startY

        self.max_way = 228
        self.max_loss = self.size_y * 0.5
        self.centre = self.y + self.size_y * 0.75

        self.dy = 0
        self.k = 1
        self.time = 0
        self.status = '0' * 128
        self.freez_status = [True] + [False for _ in range(0, 5)]
        self.itr_status = 1

        self.move = lambda time: 2*math.sin(time) + math.sin(time*4.3+1)
        self.max_move = 3
        # for i in range(1000, 100000000):
        #     if self.move(i/1000) > self.max_move:
        #         self.max_move = i/1000

    def run(self):
        while True:
            self.y = self.startY + self.move(self.get_time()) * self.max_way / self.max_move
            self.y = min(self.startY + self.max_way, max(self.startY - self.max_way, self.y))

            self.centre = self.y + self.size_y * 0.75
            self.time = round(self.get_time())

            self.itr_status -= 1
            if self.freez_status[self.itr_status]:
                self.itr_status = len(self.freez_status) - 1
                self.status = self.get_info()

            time.sleep(0.001)

    def get_info(self):
        dx_input = self.startY + self.size_y * 0.75 - 512 * math.tan(math.radians(self.radar.a)) - self.centre
        dx_convert = (((dx_input + 456) * (2048 + 2048)) / (456 + 456)) - 2048
        dx = dx_convert if dx_convert >= 0 else 4096 + dx_convert
        info_dict = {
            '0-11': bin(round(dx))[2:].zfill(12),
            '12-15': bin(self.radar.working_mode)[2:].zfill(4),
            '16-19': bin(self.radar.rotation_mode)[2:].zfill(4),
            '20-36': bin(self.time)[2:].zfill(17)
        }

        info = ''
        for name in list(info_dict):
            data = info_dict[name][::-1]
            info += data

        return int(info[::-1].zfill(128), 2)

    def set_timer(self, get_time):
        self.get_time = get_time

    def get_xy(self):
        return self.x, self.y


class Tracker(threading.Thread):
    def __init__(self, radar, sputnik):
        super().__init__()
        from tracker import tracker
        self.tracker = tracker(radar, sputnik)

        self.tracklog = open('tracklog.log', 'wb')

    def run(self):
        self.tracker.run(self.tracklog)


class TBS_Stand_Server():
    def __init__(self):
        self.WIDTH, self.HEIGHT = 0, 0

    def update_classes(self):
        self.radar = Radar(self, self.FPS)
        self.sputnik = Sputnik(self, self.FPS)

    def set_size(self, WIDTH, HEIGHT):
        self.WIDTH, self.HEIGHT = WIDTH, HEIGHT

    def set_FPS(self, FPS):
        self.FPS = FPS

    def get_obj(self):
        self.update_classes()
        return self.radar, self.sputnik


def server() -> TBS_Stand_Server:
    return TBS_Stand_Server()


class TBS_Stand_Client():
    def __init__(self, radar, sputnik):
        self.radar = radar
        self.sputnik = sputnik

    def moveStop(self):
        self.radar.set_speed(0)
        # return self.getStatus()

    def moveLeft(self, n):
        try:
            n = int(n)
            if n < 0:
                self.__warn_tb("Для приказа нужено положительное число. Приказ не принят.")
                return
        except:
            self.__warn_tb("Для приказа нужен int-совместимый тип. Приказ не принят.")
            return

        self.radar.set_speed(n)
        # return self.getStatus()

    def moveRight(self, n):
        try:
            n = int(n)
            if n < 0:
                self.__warn_tb("Для приказа нужено положительное число. Приказ не принят.")
                return
        except:
            self.__warn_tb("Для приказа нужен int-совместимый тип. Приказ не принят.")
            return

        self.radar.set_speed(-n)
        # return self.getStatus()

    def getStatus(self):
        status = self.sputnik.status
        return status

    @staticmethod
    def __warn_tb(error, warning=False, cut=2):
        level = "Предупреждение" if warning else "Ошибка"
        print("".join(traceback.format_list(traceback.extract_stack()[:-cut])) +
              f"{level}: {error}", file=sys.stderr, flush=True)


def client2server(radar, sputnik) -> TBS_Stand_Client:
    return TBS_Stand_Client(radar, sputnik)


if __name__ == '__main__':
    c2s = client2server()
    print(c2s)
    c2s.moveLeft('5')
