import math
import struct
import wave

import pyaudio

INTMAX = 2 ** (32 - 1) - 1
channels = 1
unit = 0.1
samplerate = 48000

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

text = '🧡💛💚💙💜'
string_hex = text.encode('utf-8').hex().upper()

audio = []
for i in range(int(unit * samplerate * 2)):
    audio.append(int(INTMAX * math.sin(2 * math.pi * rules['START'] * i / samplerate)))
for s in string_hex:
    for i in range(int(unit * samplerate * 1)):
        audio.append(int(INTMAX * math.sin(2 * math.pi * rules[s] * i / samplerate)))
for i in range(int(unit * samplerate * 2)):
    audio.append(int(INTMAX * math.sin(2 * math.pi * rules['END'] * i / samplerate)))

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt32,
                channels=channels,
                rate=samplerate,
                output=True)

chunk_size = 1024
for i in range(0, len(audio), chunk_size):
    chunk = audio[i:i + chunk_size]
    stream.write(struct.pack('<' + ('l' * len(chunk)), *chunk))
