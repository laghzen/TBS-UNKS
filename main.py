# здесь подключаются модули
from client2server import server, Tracker
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


def start_core():
    timer.start()

    screen.start()
    radar.start()
    sputnik.start()

    tracker.start()


def stop_core():
    timer.join()

    screen.join()
    radar.join()
    sputnik.join()

    tracker.join()


if __name__ == '__main__':
    start_core()
    # stop_core()
