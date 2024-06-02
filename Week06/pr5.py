import wave
import struct

import scipy.fftpack
import numpy as np

unit = 0.1
samplerate = 48000
padding = 5

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


filename = 'sample_week06.wav'

print('Raw hex:')
text = ''
with wave.open(filename, 'rb') as w:
    framerate = w.getframerate()
    frames = w.getnframes()
    audio = []
    for i in range(frames):
        frame = w.readframes(1)
        d = struct.unpack('<l', frame)[0]
        audio.append(d)
        if len(audio) >= unit * framerate:
            freq = scipy.fftpack.fftfreq(len(audio), d=1 / samplerate)
            fourier = scipy.fftpack.fft(audio)
            top = freq[np.argmax(abs(fourier))]  # 가장 큰 진폭의 주파수을 가져오기 위해

            data = ''
            for k, v in rules.items():
                if v - padding <= top <= v + padding:
                    data = k

            if data == 'END':
                print()
                print(data, end='')
            if data != 'START' and data != 'END':
                text = f'{text}{data}'
                print(data, end='')
            if data == 'START':
                print(data)

            audio.clear()
    print()

print(f'Decoded: {bytes.fromhex(text).decode("utf-8")}')
