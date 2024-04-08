import math

import scipy.fftpack
import numpy as np

INTMAX = 2**(32-1)-1
channels = 1
length = 5.0
samplerate = 48000
frequencies = [261.625, 523.251, 1046.502]  # C4, C5, C6
volumes = [1.0, 0.75, 0.5]
waves = []

for frequency, volume in zip(frequencies, volumes):
    audio = []
    for i in range(int(length*samplerate)):
        audio.append(volume*INTMAX*math.sin(2*math.pi*frequency*i/samplerate))
    waves.append(audio)

track = [0]*int(length*samplerate)
for i in range(len(track)):
    for w, v in zip(waves, volumes):
        track[i] = track[i] + w[i]
    track[i] = track[i] / len(waves)

# 실제 푸리에 처리 부분
freq = scipy.fftpack.fftfreq(len(track), d=1/samplerate)
fourier = scipy.fftpack.fft(track)
print(freq[np.argmax(abs(fourier))])

for i in range(len(freq)):
    if 261.125 <= freq[i] <= 262.125:
        print(f'{i} => {freq[i]}')
    elif 522.751 <= freq[i] <= 523.751:
        print(f'{i} => {freq[i]}')
    elif 1046.002 <= freq[i] <= 1047.002:
        print(f'{i} => {freq[i]}')
