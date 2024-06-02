import math
import struct
import wave

import pyaudio

INTMAX = 2 ** (32 - 1) - 1
channels = 1
unit = 0.1
samplerate = 48000


def audio2file(audio_sample, filename):
    with wave.open(filename, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(4)
        w.setframerate(48000)
        for a in audio_sample:
            w.writeframes(struct.pack('<l', a))


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

text = '🧡💛💚💙💜'
string_hex = text.encode('utf-8').hex().upper()

audio = []
for i in range(int(unit * samplerate * 2)):  # start signal, 1unit
    audio.append(int(INTMAX * math.sin(2 * math.pi * rules['START'] * i / samplerate)))
for s in string_hex:  # text
    for i in range(int(unit * samplerate * 1)):
        audio.append(int(INTMAX * math.sin(2 * math.pi * rules[s] * i / samplerate)))
for i in range(int(unit * samplerate * 2)):  # end signal, 2unit
    audio.append(int(INTMAX * math.sin(2 * math.pi * rules['END'] * i / samplerate)))

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt32,
                channels=channels,
                rate=samplerate,
                output=True)

chunk_size = 1200
for i in range(0, len(audio), chunk_size):
    chunk = audio[i:i + chunk_size]
    stream.write(struct.pack('<' + ('l' * len(chunk)), *chunk))

audio2file(audio, "sample_week06.wav")
