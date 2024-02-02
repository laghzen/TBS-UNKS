import sys
import threading

from random import uniform, randint, choice
import time


def noiseGenerate(dataAndP, MAX_COUNT_ERR=None, MIN_DISTANCE_ERR=None, MIN_LEN_ERR=None, MAX_LEN_ERR=None, permission_position_err=None):
    data = sum([i[1:] for i in dataAndP], [])
    indexAndP = [i[0] * 100 for i in dataAndP for j in range(len(i)-1)]

    if MAX_COUNT_ERR is None:
        MAX_COUNT_ERR = 1

    if MIN_DISTANCE_ERR is None:
        MIN_DISTANCE_ERR = 0

    if MIN_LEN_ERR is None:
        MIN_LEN_ERR = 1

    if MAX_LEN_ERR is None:
        MAX_LEN_ERR = 1

    if permission_position_err is None:
        permission_position_err = [i for i in range(0, len(data))]
    else:
        permission_position_err = [i for i in range(permission_position_err[0], permission_position_err[1])]

    free_index = [i for i in range(0, len(data))]

    while MAX_COUNT_ERR > 0 and free_index:
        if permission_position_err:
            random_index_err = choice(permission_position_err)
        else:
            random_index_err = choice(free_index)
        random_len_err = randint(MIN_LEN_ERR, MAX_LEN_ERR)

        lost_bits = uniform(0, 100) <= indexAndP[random_index_err]
        for i in range(0, random_len_err):
            index = random_index_err + i
            if index >= len(data): break
            if index in free_index and MAX_COUNT_ERR > 0:
                MAX_COUNT_ERR -= 1
                if lost_bits: data[index] = 1 - data[index]
                free_index.remove(index)
                if permission_position_err: permission_position_err.remove(index)
            else:
                break

        for i in range(1, MIN_DISTANCE_ERR + 1):
            index1 = max(random_index_err - i, -1)
            index2 = min(random_index_err + random_len_err - 1 + i, len(data))

            if index1 != -1: free_index.remove(index1)
            if index2 != len(data): free_index.remove(index2)
            if permission_position_err:
                if index1 != -1: permission_position_err.remove(index1)
                if index2 != len(data): permission_position_err.remove(index2)

    return ''.join([str(i) for i in data])


def getBits(fin):
    newData = ''
    data = fin.read()
    if data:
        for i in data:
            byte = str(bin(i))[2:].zfill(8)
            newData += byte

    return newData


def fromBits(fout, data):
    newData = b''
    if data:
        for i in range(len(data) // 8):
            byte = data[i * 8:i * 8 + 8]
            char = bytes(int(byte, 2))
            newData += char

    fout.write(newData)


class TransferData(threading.Thread):
    def __init__(self, sputnik, stop_core, chank=None):
        super().__init__()

        self.sputnik = sputnik

        self.stop_core = stop_core

        self.fin = open('input_files/send_data.txt', 'rb')
        self.data_in = getBits(self.fin)
        self.data_in = [int(i) for i in list(self.data_in)]

        self.data_out = ''
        self.transfer_data = []
        self.fout = open('input_files/output.txt', 'wb')

        self.volume_input_data = 256000 * 8
        if chank is None:
            self.chank = len(self.data_in)
        else:
            self.chank = chank
        self.speed = (1750 * 1024 * 8) / (5 * 60)

        self.MAX_COUNT_ERR = None
        self.MIN_DISTANCE_ERR = None
        self.MIN_LEN_ERR = None
        self.MAX_LEN_ERR = None
        self.permission_position_err = None

        self.stop_flag = False

    def compile_transfer(self):
        print('Добавляем ШУМ!')
        for i in self.transfer_data:
            self.data_out += noiseGenerate(i, self.MAX_COUNT_ERR, self.MIN_DISTANCE_ERR, self.MIN_LEN_ERR, self.MAX_LEN_ERR, self.permission_position_err)
        print('Конвертируем в байты...')
        fromBits(self.fout, self.data_out)

    def close_transfer(self):
        print('Закончили обработку передачи!')
        self.fin.close()
        self.fout.close()

    def stop_transfer(self):
        print('Врямя вышло!')
        self.stop_flag = True

    def run(self):
        chank_speed = round(self.speed/1000)
        for i in range(len(self.data_in) // self.chank + [0, 1][len(self.data_in) % self.chank != 0]):
            chank_data = self.data_in[i * self.chank : min((i + 1) * self.chank, len(self.data_in))]
            if not chank_data: break

            self.transfer_data.append([])

            for j in range(len(chank_data) // chank_speed + [0, 1][len(chank_data) % chank_speed != 0]):
                d_data = chank_data[j * chank_speed : min((j + 1) * chank_speed, len(chank_data))]

                status = self.sputnik.get_info()
                dx = int(status) & 0x0fff
                if dx > 2048:
                    dx = dx - 4096

                if abs(dx) <= 25: P = 0
                elif abs(dx) <= 100: P = abs(dx) / 100
                else: P = 1

                if dx + 4096 != 3423:
                    if self.transfer_data[-1] and self.transfer_data[-1][-1][0] == P:
                        self.transfer_data[-1][-1] += d_data
                    else:
                        self.transfer_data[-1].append([P, *d_data])
                elif self.chank < len(self.data_in):
                    self.transfer_data.pop(-1)
                    break

                time.sleep(0.001)

                print((chank_speed * j + chank_speed * i * (len(chank_data) // chank_speed)) / len(self.data_in) * 100)

                if self.stop_flag: break
            if self.stop_flag: break
        print('Передача закончена!')

        self.stop_core()
