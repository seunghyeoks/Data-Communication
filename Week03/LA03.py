import sys
import math
import wave
import struct
import statistics

# 변수 설정
INTMAX = 2 ** (32 - 1) - 1
t = 0.1
fs = 48000
f = 523.251  # c5

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

symbol = {' ': '$'}


def text2morse(text):
    text = text.upper()
    morse = ''

    # space도 하나의 글자로 취급, 글자 마다 short gap 추가
    for letter in text:
        for key, value in english.items():
            if letter == key:
                morse = morse + value + ' '
        for key, value in number.items():
            if letter == key:
                morse = morse + value + ' '
        for key, value in symbol.items():
            if letter == key:
                morse = morse + value + ' '

    return morse


def morse2audio(morse):
    audio = []

    for m in morse:
        if m == '.':  # dits, 1unit
            for i in range(int(t * fs * 1)):
                audio.append(int(INTMAX * math.sin(2 * math.pi * f * (i / fs))))
        elif m == '-':  # dahs, 3units
            for i in range(int(t * fs * 3)):
                audio.append(int(INTMAX * math.sin(2 * math.pi * f * (i / fs))))
        elif m == '$':  # medium gap
            for i in range(int(t * fs * 1)):
                audio.append(int(0))
        elif m == ' ':  # short gap
            for i in range(int(t * fs * 2)):
                audio.append(int(0))

        for i in range(int(t * fs * 1)):  # inter gap 1units
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
        unit = int(t * fs)
        for i in range(1, math.ceil(len(audio) / unit) + 1):
            stdev = statistics.stdev(audio[(i - 1) * unit:i * unit])
            if stdev > 10000:
                morse = morse + '.'
            else:
                morse = morse + ' '

        morse = morse.strip()
        morse = morse.replace('...', '-')        # 3 straights to dash
        morse = morse.replace('       ', '#$#')  # temp medium gap (7 units)
        morse = morse.replace('   ', '#')        # temp short gap  (3 units)
        morse = morse.replace(' ', '')           # inter gap  (1 unit)
        morse = morse.replace('#', ' ')          # restore short gap

    return morse


def morse2text(morse):
    text = ''
    morse = morse.split()

    for m_letter in morse:
        for key, value in english.items():
            if m_letter == value:
                text = text + key
        for key, value in number.items():
            if m_letter == value:
                text = text + key
        for key, value in symbol.items():
            if m_letter == value:
                text = text + key

    return text
