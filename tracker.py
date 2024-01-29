import time

from client2server import client2server
from math import ceil


class tracker:
    def __init__(self, radar, sputnik):
        self.radar = radar
        self.sputnik = sputnik

    def run(self, tracklog):
        c2s = client2server(self.radar, self.sputnik)
        i = 0

        P = 1
        I = 0.2
        D = 0.1
        err = 0
        integral = 0
        prev_err = 0
        PID = lambda P, I, D, err, integral, prev_err: P * err + integral * I * 0.1 + (err - prev_err) * D * 10

        status = c2s.getStatus()
        dx = int(status) & 0x0fff
        if dx > 2048:
            dx = dx - 4096
        tracklog.write(f"{status}\n".encode())

        err = dx
        rez = PID(P, I, D, err, integral, prev_err)

        integral += err
        prev_err = err
        # print(rez)

        if rez > 0:
            c2s.moveLeft(abs(rez))
        else:
            c2s.moveRight(abs(rez))
        # print(dx)

        # if abs(dx) < 500:
        #     if abs(dx) < 10:
        #         c2s.moveStop()
        #     else:
        #         if dx > 0:
        #             c2s.moveLeft(5)
        #         else:
        #             c2s.moveRight(5)
        time.sleep(0.001)
