import threading
import time
import traceback
import sys
import math


class Radar(threading.Thread):
    def __init__(self, stand):
        super().__init__()

        self.size_x = 147
        self.size_y = 123

        self.x = 33 + self.size_x / 2
        self.y = stand.HEIGHT / 2

        self.a = 0
        self.speed = 0
        self.k = 1.8

        self.max_a = 30

        self.working_mode = 2
        self.rotation_mode = 0

        self.time_prev = 0

        self.stop_flag = False

    def stop(self):
        self.stop_flag = True

    def run(self):
        while not self.stop_flag:
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

    def get_a(self):
        return self.a


class Sputnik(threading.Thread):
    def __init__(self, stand):
        super().__init__()

        self.radar = stand.radar

        self.size_x = 36
        self.size_y = 61

        self.x = stand.WIDTH - self.size_x / 2 - 70
        self.startY = stand.HEIGHT / 2 - self.size_y / 2
        self.y = self.startY

        self.max_way = 415
        self.max_vision = self.max_way * 55/90
        self.centre = self.y + self.size_y / 2

        self.dy = 0
        self.k = 1
        self.time = 0

        self.move = lambda time: 2*math.sin(time) + math.sin(time*4.3+1)
        self.max_move = 3
        # for i in range(1000, 100000000):
        #     if self.move(i/1000) > self.max_move:
        #         self.max_move = i/1000

        self.stop_flag = False

    def stop(self):
        self.stop_flag = True

    def run(self):
        while not self.stop_flag:
            self.y = self.startY - self.move(self.get_time()) * self.max_way / self.max_move
            self.y = min(self.startY + self.max_way, max(self.startY - self.max_way, self.y))

            self.centre = self.y + self.size_y / 2
            self.time = round(self.get_time())

            time.sleep(0.001)

    def get_info(self):
        dx_input = math.cos(math.radians(self.radar.get_a())) * (self.startY + self.size_y / 2 - self.centre - 726 * math.tan(math.radians(self.radar.get_a())))
        if abs(dx_input) > self.max_vision:
            dx = 3423  # !!!
        else:
            dx_convert = (((dx_input + self.max_vision) * (2048 + 2048)) / (self.max_vision + self.max_vision)) - 2048
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

    def get_dx(self):
        dx_input = math.cos(math.radians(self.radar.get_a())) * (
                    self.startY + self.size_y / 2 - self.centre - 726 * math.tan(math.radians(self.radar.get_a())))
        if abs(dx_input) > self.max_vision:
            dx = 3423  # !!!
        else:
            dx_convert = (((dx_input + self.max_vision) * (2048 + 2048)) / (self.max_vision + self.max_vision)) - 2048
            dx = dx_convert if dx_convert >= 0 else 4096 + dx_convert
        return dx

    def set_timer(self, get_time):
        self.get_time = get_time

    def get_xy(self):
        return self.x, self.y


radar_global, sputnik_global = None, None
class Tracker(threading.Thread):
    def __init__(self, radar, sputnik):
        super().__init__()

        global radar_global
        global sputnik_global
        radar_global = radar
        sputnik_global = sputnik

        from input_files.tracker import tracker
        self.tracker = tracker()

        self.tracklog = open('tracklog.log', 'wb')

    def run(self):
        self.tracker.run(self.tracklog)


class TBS_Stand_Server():
    def __init__(self):
        self.WIDTH, self.HEIGHT = 0, 0

    def update_classes(self):
        self.radar = Radar(self)
        self.sputnik = Sputnik(self)

    def set_size(self, WIDTH, HEIGHT):
        self.WIDTH, self.HEIGHT = WIDTH, HEIGHT

    def get_obj(self):
        self.update_classes()
        return self.radar, self.sputnik


def server() -> TBS_Stand_Server:
    return TBS_Stand_Server()


class TBS_Stand_Client():
    def __init__(self):
        global radar_global
        global sputnik_global
        self.radar = radar_global
        self.sputnik = sputnik_global

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
        status = self.sputnik.get_info()
        return status

    @staticmethod
    def __warn_tb(error, warning=False, cut=2):
        level = "Предупреждение" if warning else "Ошибка"
        print("".join(traceback.format_list(traceback.extract_stack()[:-cut])) +
              f"{level}: {error}", file=sys.stderr, flush=True)


def client2server() -> TBS_Stand_Client:
    return TBS_Stand_Client()


if __name__ == '__main__':
    c2s = client2server()
    print(c2s)
    c2s.moveLeft('5')
