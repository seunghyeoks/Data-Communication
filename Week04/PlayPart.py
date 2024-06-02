import math
import struct
import time

import pyaudio

INTMAX = 2 ** (32 - 1) - 1


def main():
    t = 10
    fs = 48000
    f = 261.626  # C4

    # input data
    audio = []
    for i in range(int(t * fs)):
        audio.append(int(INTMAX * math.sin(2 * math.pi * f * (i / fs))))

    # Play sound via pyaudio
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt32,
                    channels=1,
                    rate=fs,
                    output=True)

    chunk_size = 1024
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i + chunk_size]
        stream.write(struct.pack('<' + ('l' * len(chunk)), *chunk))

    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == '__main__':
    main()
