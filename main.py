# здесь подключаются модули
import sys
import time

from client2server import server, Tracker
from objects import Barrier
from show import Screen
from transfer_data import TransferData

from time_class import Timer

from input_files.encoder import encoder
from input_files.decoder import decoder


def start_core():
    timer.start()

    screen.start()
    radar.start()
    sputnik.start()

    try:
        tracker.start()
        transfer.start()
    except Exception as e:
        print(e)


def stop_core():
    timer.stop()
    timer.join()

    screen.stop()
    screen.join()

    radar.stop()
    radar.join()

    sputnik.stop()
    sputnik.join()

    # tracker.join()

    transfer.compile_transfer()
    transfer.close_transfer()

    print('Декодируем...')
    filein = open('input_files/send_data.txt', 'rb')
    fileout = open('input_files/output.txt', 'wb')
    decoder(filein, fileout)
    filein.close()
    fileout.close()
    print('Готово!')

    sys.exit()


f1 = open('input_files/send_data.txt', 'wb')
f1.seek(0)
f1.close()
f2 = open('input_files/output.txt', 'wb')
f2.seek(0)
f2.close()

timer = Timer(4.5 * 60)

c2s = server()

screen = Screen()
c2s.set_size(*screen.get_size())

barrier = Barrier
radar, sputnik = c2s.get_obj()
radar.set_timer(timer.get_time)
sputnik.set_timer(timer.get_time)
screen.set_obj(radar, sputnik, barrier)

screen.run()

tracker = Tracker(radar, sputnik)


filein = open('input_files/input.txt', 'rb')
fileout = open('input_files/send_data.txt', 'wb')
encoder(filein, fileout)
filein.close()
fileout.close()

transfer = TransferData(sputnik, stop_core)
timer.set_transfer(transfer)


if __name__ == '__main__':
    start_core()
