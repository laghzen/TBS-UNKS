import traceback
import sys
import random
import math


class Radar():
    def __init__(self, stand):
        from main import FPS
        self.FPS = FPS

        self.size_x = 211//2
        self.size_y = 203//2

        self.x = 50//2 + self.size_x//2
        self.y = 620//2 + self.size_y//2

        self.a = 0
        self.speed = 0
        self.k = 1.8

        self.max_a = 24

        self.working_mode = 2
        self.rotation_mode = 0

        self.freez_radar = [0 for _ in range(0, 5)]

    def updata(self):
        for i in range(len(self.freez_radar)-1, 0, -1):
            self.freez_radar[i] = self.freez_radar[i-1]
        self.freez_radar[0] = self.speed

        self.a += self.freez_radar[-1]*self.k/self.FPS
        self.a = max(-self.max_a, min(self.max_a, self.a))

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

    def set_speed(self, value):
        self.speed = value


class Sputnik():
    def __init__(self, stand):
        from main import FPS
        self.FPS = FPS

        self.radar = stand.radar

        self.size_x = 124//2
        self.size_y = 147//2

        self.x = stand.WIDTH - self.size_x + 3
        self.startY = stand.HEIGHT // 2 - self.size_y
        self.y = self.startY

        self.max_way = 228
        self.max_loss = self.size_y * 0.5
        self.centre = self.y + self.size_y*0.75

        self.dy = 0
        self.k = 1
        self.time = 0
        self.status = '0'*128
        self.freez_status = [True] + [False for _ in range(0, 5)]
        self.itr_status = 1

        self.first_step = True
        self.mode = 0
        self.modes = {
            0: [(0, 0, False), 0],
            1: [(self.FPS*0.25, 30/FPS*2, False), 0],
            2: [(self.FPS*0.5, 20/FPS*2, True), 0],
            3: [(self.FPS*1, 35/FPS*2, True), 0],
            4: [(self.FPS*2, 25/FPS*2, False), 0],
            5: [(self.FPS*4, 20/FPS*2, True), 0]
        }

    def updata(self, time):
        if self.mode == 0:
            self.mode = random.randint(1, 5)

            self.modes[self.mode][-1] = self.modes[self.mode][0][0]
            self.dy = self.modes[self.mode][0][1]
            if self.modes[self.mode][0][-1]:
                self.k -= self.k * 2

        if self.modes[self.mode][-1] == 0 or (self.y == self.startY+self.max_way or self.y == self.startY-self.max_way) and (not self.first_step):
            self.mode = 0
            self.first_step = True
            self.dy = 0
        else:
            self.first_step = False
            self.modes[self.mode][-1] -= 1

        self.y += self.dy * self.k
        self.y = min(self.startY+self.max_way, max(self.startY-self.max_way, self.y))

        self.centre = self.y + self.size_y * 0.75
        self.time = round(time*1000)

        self.itr_status -= 1
        if self.freez_status[self.itr_status]:
            self.itr_status = len(self.freez_status)-1
            self.status = self.get_info()

    def get_info(self):
        dx_input = self.startY + self.size_y*0.75 - 512 * math.tan(math.radians(self.radar.a)) - self.centre
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


class TBS_Stand_Server():
    def __init__(self):
        self.WIDTH, self.HEIGHT = 0, 0

    def update_classes(self):
        self.radar = Radar(self)
        self.sputnik = Sputnik(self)

    def set_size(self, WIDTH, HEIGHT):
        self.WIDTH, self.HEIGHT = WIDTH, HEIGHT
        self.update_classes()


def server() -> TBS_Stand_Server:
    return TBS_Stand_Server()


class TBS_Stand_Client():
    def __init__(self):
        from main import c2s

        self.server = c2s
        self.radar = c2s.radar
        self.sputnik = c2s.sputnik

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


def client2server() -> TBS_Stand_Client:
    return TBS_Stand_Client()


if __name__ == '__main__':
    c2s = client2server()
    print(c2s)
    c2s.moveLeft('5')
