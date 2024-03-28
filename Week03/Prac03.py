import sys
import math
import wave
import struct
import statistics

# making sound file via Python3

INTMAX = 2**(32-1)-1
t = 1.0
fs = 48000
f = 261.626 # C4
audio = []
for i in range(int(t*fs)):
    audio.append(int(INTMAX*math.sin(2*math.pi*f*(i/fs))))

filename = 't.wav'
with wave.open(filename, 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(4)
    w.setframerate(48000)
    for a in audio:
        w.writeframes(struct.pack('<l', a))


english = {'A': '.-', 'B': '-...', 'C': '-.-.',
           'D': '-..', 'E': '.', 'F': '..-.',
           'G': '--.', 'H': '....', 'I': '..',
           'J': '.---', 'K': '-.-', 'L': '.-..',
           'M': '--', 'N': '-.', 'O': '---',
           'P': '.--.', 'Q': '--.-', 'R': '.-.',
           'S': '...', 'T': '-', 'U': '..-',
           'V': '...-', 'W': '.--', 'X': '-..-_',
           'Y': '-.--', 'Z': '--..'}

number = {'1': '.----', '2': '..---', '3': '...--',
          '4': '....-', '5': '.....', '6': '-....',
          '7': '--...', '8': '---..', '9': '----.',
          '0': '-----'}


def text2morse(text):
    text = text.upper()
    morse = ''

    for t in text:
        for key, value in english.items():
            if t == key:
                morse = morse + value
        for key, value in number.items():
            if t == key:
                morse = morse + value

    return morse


def morse2audio(morse):
    t = 0.5
    fs = 48000
    f = 261.626
    audio = []
    for m in morse:
        if m == '.':
            for i in range(int(t*fs*1)):
                audio.append(int(INTMAX*math.sin(2*math.pi*f*(i/fs))))
        elif m == '-':
            for i in range(int(t*fs*3)):
                audio.append(int(INTMAX*math.sin(2*math.pi*f*(i/fs))))
        for i in range(int(t*fs*1)):
            audio.append(int(0))
    return audio


def audio2file(audio, filename):
    with wave.open(filename, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(4)
        w.setframerate(48000)
        for a in audio:
            w.writeframes(struct.pack('<l', a))


def file2morse(filename):
    with wave.open(filename, 'rb') as w:
        audio = []
        framerate = w.getframerate()
        frames = w.getnframes()
        for i in range(frames):
            frame = w.readframes(1)
            audio.append(struct.unpack('<i', frame)[0])
        morse = ''
        unit = int(0.5 * 48000)
        for i in range(1, math.ceil(len(audio)/unit)+1):
            stdev = statistics.stdev(audio[(i-1)*unit:i*unit])
            if stdev > 10000:
                morse = morse + '.'
            else:
                morse = morse + ' '
        morse = morse.replace('...', '-')
    return morse
