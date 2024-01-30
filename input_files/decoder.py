from collections import deque
from math import ceil, log2, floor
from time import time


def dehamming(data):
    CHUNK_LENGTH = 57
    CHECK_BITS = [0, 1, 3, 7, 15, 31]
    NOT_CHECK_BITS = [2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62]

    output = ''

    for index in range(0, ceil(len(data) / (CHUNK_LENGTH + 7))):

        start = index * (CHUNK_LENGTH + 7)
        end = (index + 1) * (CHUNK_LENGTH + 7)

        chunk = data[start:end]
        control_bits = [0, 0, 0, 0, 0, 0]
        data_chunk = ''
        err_bits = []

        for target_index in NOT_CHECK_BITS:
            for itr, bit in enumerate(bin(target_index + 1)[2:].zfill(6)[::-1]):
                if bit == '1':
                    control_bits[itr] ^= int(chunk[target_index])

        for itr, bit in enumerate(CHECK_BITS):
            if chunk[bit] != str(control_bits[itr]):
                err_bits.append(bit + 1)

        if not len(err_bits):
            chunk_valid = chunk
        else:
            err_bit = sum(err_bits) - 1
            chunk_valid = f'{chunk[:err_bit]}{str(1 - int(chunk[err_bit]))}{chunk[err_bit + 1:]}'

        for target_index in NOT_CHECK_BITS:
            data_chunk += chunk_valid[target_index]

        output += data_chunk

    return output


def main(filein, fileout):
    blocksize = 1024
    packets = {}
    maxNum = 0

    while True:
        s = filein.read(blocksize)
        if not s: break

        s1 = bin(int.from_bytes(s, byteorder='big'))[2:].zfill(1024 * 8)
        s1 = dehamming(s1)
        s = int(s1, 2).to_bytes(913, byteorder='big')

        number = int.from_bytes(s[1:3], byteorder='big')
        maxNum = max(maxNum, number)

        s = s[3:].replace(b';', b'')

        packets[number] = s

    for i in range(0, maxNum+1):
        if i in list(packets):
            fileout.write(packets[i])
        else:
            fileout.write(packets[list(packets)[0]])

def decoder(filein, fileout):
    try:
        main(filein, fileout)
    except Exception as e:
        import traceback

        exc = traceback.format_exc().encode()

        fileout.write(exc)

if __name__ == '__main__':
    filein = open('send_data.txt', 'rb')
    fileout = open('output.txt', 'wb')

    start = time()
    decoder(filein, fileout)
    print(time() - start)

    filein.close()
    fileout.close()
