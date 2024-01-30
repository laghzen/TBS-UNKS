# здесь подключаются модули
import time

from client2server import server, Tracker, Encoder, Decoder
from show import Screen

from time_class import Timer


timer = Timer(4.5 * 60)

c2s = server()

screen = Screen()
c2s.set_size(*screen.get_size())

radar, sputnik = c2s.get_obj()
radar.set_timer(timer.get_time)
sputnik.set_timer(timer.get_time)
screen.set_obj(radar, sputnik)

tracker = Tracker(radar, sputnik)
encoder = Encoder()
decoder = Decoder()


def start_core():
    timer.start()

    screen.start()
    radar.start()
    sputnik.start()

    try:
        tracker.start()
        # encoder.start()

    except Exception as e:
        print(e)


def stop_core():
    timer.join()

    screen.join()
    radar.join()
    sputnik.join()

    tracker.join()
    # encoder.join()


if __name__ == '__main__':
    start_core()
    stop_core()
