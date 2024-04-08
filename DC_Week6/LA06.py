import math
import statistics
import struct
import time
import wave

import pyaudio

INTMAX = 2 ** (32 - 1) - 1
unit = 0.1
samplerate = 48000
padding = 5
chunk_size = 1200
threshold = 100000000

rules = {'START': 512,
         '0': 768,
         '1': 896,
         '2': 1024,
         '3': 1152,
         '4': 1280,
         '5': 1408,
         '6': 1536,
         '7': 1664,
         '8': 1792,
         '9': 1920,
         'A': 2048,
         'B': 2176,
         'C': 2304,
         'D': 2432,
         'E': 2560,
         'F': 2688,
         'END': 2944}


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

    print("\nlistening...")

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt32,
                    channels=1,
                    rate=samplerate,
                    input=True)

    while True:
        data = struct.unpack('<' + ('l' * chunk_size), stream.read(chunk_size))  # 반복 측정


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
