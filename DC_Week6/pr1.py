import pyaudio
import math
import struct
import time

INTMAX = 2 ** (32 - 1) - 1
channels = 1
length = 5.0
samplerate = 48000
frequencies = [261.625, 523.251, 1046.502]  # C4, C5, C6
volumes = [1.0, 0.75, 0.5]
waves = []

for frequency, volume in zip(frequencies, volumes):
    audio = []
    for i in range(int(length * samplerate)):
        audio.append(volume * INTMAX * math.sin(2 * math.pi * frequency * i / samplerate))
    waves.append(audio)

track = [0] * int(length * samplerate)
for i in range(len(track)):
    for w, v in zip(waves, volumes):
        track[i] = track[i] + w[i]
    track[i] = round(track[i] / len(waves))

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt32,
                channels=channels,
                rate=samplerate,
                output=True)
chunk_size = 1024
for i in range(0, len(track), chunk_size):
    chunk = track[i:i + chunk_size]
    stream.write(struct.pack('<' + ('l' * len(chunk)), *chunk))

stream.stop_stream()
stream.close()
p.terminate()
