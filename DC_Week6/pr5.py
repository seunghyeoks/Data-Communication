import wave
import struct

import scipy.fftpack
import numpy as np

unit = 0.1
samplerate = 48000
padding = 5

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
