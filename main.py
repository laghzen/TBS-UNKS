# здесь подключаются модули
import time

from client2server import server, Tracker
from show import Screen
from transfer_data import TransferData

from time_class import Timer

from input_files.encoder import encoder
from input_files.decoder import decoder


def start_core():
    filein = open('input_files/input.txt', 'rb')
    fileout = open('input_files/send_data.txt', 'wb')
    encoder(filein, fileout)

    timer.start()

    screen.start()
    radar.start()
    sputnik.start()

    try:
        tracker.start()
    except Exception as e:
        print(e)


def stop_core():
    timer.join()

    screen.join()
    radar.join()
    sputnik.join()

    tracker.join()

    transfer.compile_transfer()
    transfer.close_transfer()
    transfer.join()

    filein = open('input_files/input.txt', 'rb')
    fileout = open('input_files/send_data.txt', 'wb')
    decoder(filein, fileout)


timer = Timer(4.5 * 60)

c2s = server()

screen = Screen()
c2s.set_size(*screen.get_size())

radar, sputnik = c2s.get_obj()
radar.set_timer(timer.get_time)
sputnik.set_timer(timer.get_time)
screen.set_obj(radar, sputnik)

tracker = Tracker(radar, sputnik)

transfer = TransferData(radar, stop_core)
transfer.prepare_data()


if __name__ == '__main__':
    start_core()
    stop_core()
