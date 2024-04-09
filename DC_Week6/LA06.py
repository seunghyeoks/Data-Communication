import math
import statistics
import struct
import time
import wave

import pyaudio
import scipy.fftpack
import numpy

INTMAX = 2 ** (32 - 1) - 1
unit = 0.1
samplerate = 48000
padding = 10
chunk_size = 1200
threshold = 100000000

rules = {'START': 520,
         '0': 760,
         '1': 880,
         '2': 1000,
         '3': 1120,
         '4': 1240,
         '5': 1360,
         '6': 1480,
         '7': 1600,
         '8': 1720,
         '9': 1840,
         'A': 1960,
         'B': 2080,
         'C': 2200,
         'D': 2320,
         'E': 2440,
         'F': 2560,
         'END': 2800}


def send_data():
    print('\nType some text! ')
    text = input('User input\t : ').strip()
    string_hex = text.encode('utf-8').hex().upper()

    print("converted to : " + string_hex)
    print("\nplaying...")

    audio = []
    for i in range(int(unit * samplerate * 2)):  # start signal, 2unit
        audio.append(int(INTMAX * math.sin(2 * math.pi * rules['START'] * i / samplerate)))
    for s in string_hex:  # text
        for i in range(int(unit * samplerate * 1)):
            audio.append(int(INTMAX * math.sin(2 * math.pi * rules[s] * i / samplerate)))
    for i in range(int(unit * samplerate * 2)):  # end signal, 2unit
        audio.append(int(INTMAX * math.sin(2 * math.pi * rules['END'] * i / samplerate)))

    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt32,
                    channels=1,
                    rate=samplerate,
                    output=True)

    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i + chunk_size]
        stream.write(struct.pack('<' + ('l' * len(chunk)), *chunk))

    print("done.")
    print("\n")

    pass


def receive_data():
    print("\nlistening...\n")

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt32,
                    channels=1,
                    rate=samplerate,
                    input=True)
    started = False
    checker = False
    counter = 0
    text = ''
    temp = []

    while True:
        data = struct.unpack('<' + ('l' * chunk_size), stream.read(chunk_size))  # 반복 측정

        freq = scipy.fftpack.fftfreq(len(data), d=1 / samplerate)
        fourier = scipy.fftpack.fft(data)
        top = freq[numpy.argmax(abs(fourier))]  # 가장 큰 진폭의 주파수을 가져오기 위해 -> 입력된 주파수

        for k, v in rules.items():
            if v - padding <= top <= v + padding:
                data = k

        if len(data) > 6:
            data = '$'

        # print(top)

        if not started:
            if data == 'START':
                counter += 1
            else:
                counter = 0

            if counter == 8:
                started = True
                counter = 0
                print("[START] " + data)

            continue

        if started:
            counter += 1
            temp.append(data)
            if counter != 4:
                continue
            else:
                temp.reverse()
                data = max(set(temp), key=temp.count)
                temp.clear()
                counter = 0

            if data == 'END':
                print("[END] " + data)
                break
            if data != 'START' and data != 'END':
                #print(data)
                text += data
                print("[DATA] " + text)
            if data == 'START':
                print("[START] " + data)

    print()
    print(f'Decoded: {bytes.fromhex(text).decode("utf-8")}')
    print()

    stream.stop_stream()
    stream.close()
    p.terminate()

    pass


def main():
    while True:
        print('Unicode over Sound with Noise')
        print('2024 Spring Data Communication at CNU')
        print('[1] Send Unicode over sound (play)')
        print('[2] Receive Unicode over sound (record)')
        print('[q] Exit')
        select = input('Select menu: ').strip().upper()
        if select == '1':
            send_data()
        elif select == '2':
            receive_data()
        elif select == 'Q':
            print('Terminating...')
            break


if __name__ == '__main__':
    main()
