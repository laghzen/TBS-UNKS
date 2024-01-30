from math import ceil, log2, floor
from time import time


def hamming(data):
    CHUNK_LENGTH = 57
    CHECK_BITS = [0, 1, 3, 7, 15, 31]

    output = ''

    for index in range(0, ceil(len(data) / CHUNK_LENGTH)):
        start = index * CHUNK_LENGTH
        end = (index + 1) * CHUNK_LENGTH

        chunk = data[start:end]
        control_bits = [0, 0, 0, 0, 0, 0]

        for target_index in CHECK_BITS:
            chunk = f'{chunk[:target_index]}0{chunk[target_index:]}'

        for target_index in range(0, CHUNK_LENGTH + 6):
            if target_index not in CHECK_BITS:
                for itr, bit in enumerate(bin(target_index + 1)[2:].zfill(6)[::-1]):
                    if bit == '1':
                        control_bits[itr] ^= int(chunk[target_index])

        for itr, target_index in enumerate(CHECK_BITS):
            chunk = f'{chunk[:target_index]}{control_bits[itr]}{chunk[target_index+1:]}'

        output += chunk + '0'

    return output


def encoder(filein, fileout):
    blocksize= 910
    num = 0
    packets = []

    while True:
        s = filein.read(blocksize)
        if not s: break
        s = num.to_bytes(2, byteorder='big') + s
        num += 1

        s += b';'*(912-len(s))

        s1 = bin(int.from_bytes(s, byteorder='big'))[2:].zfill(912*8)
        s1 = hamming(s1)
        s = int(s1, 2).to_bytes(1024, byteorder='big')

        packets.append(s)

    for _ in range(10):
        for i in packets:
            fileout.write(i)



if __name__ == '__main__':
    filein = open('input.txt', 'rb')
    fileout = open('send_data.txt', 'wb')

    start = time()
    encoder(filein, fileout)
    print(time() - start)

    filein.close()
    fileout.close()
