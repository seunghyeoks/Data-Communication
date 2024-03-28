import math
import statistics
import struct
import time
import wave

import pyaudio
import re

# 변수 설정
INTMAX = 2 ** (32 - 1) - 1
t = 0.1
fs = 48000
f = 523.251  # c5
chunk_size = 1200
threshold = 100000000

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


def send_data():
    # text 입력 부분, alphanumeric + space
    while True:
        print('Type some text (only English and Number)')
        text = input('User input: ').strip()
        if re.match(r'[A-Za-z0-9 ]+', text):
            break

    # text를 morse code로 변환한 뒤 화면에 표시
    morse = text2morse(text)
    print("encoded  : " + morse)

    # 오디오 재생 부분
    print("playing...")
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt32,
                    channels=1,
                    rate=fs,
                    output=True)

    audio = morse2audio(morse)  # 오디오로 변환된 morse

    for i in range(0, len(audio), chunk_size):  # 청크 사이즈 마다 잘라서 재생
        chunk = audio[i:i + chunk_size]
        stream.write(struct.pack('<' + ('l' * len(chunk)), *chunk))

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("done.")

    pass


def receive_data():
    # 준비 부분
    print("listening...")

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt32,
                    channels=1,
                    rate=fs,
                    input=True)

    morse = ''
    empty = 0
    temp = 0

    # fs(48000)/chunk_size(1200) = 40
    # -> 1초에 40번 측정, 4번의 측정 데이터로 1unit 측정 가능

    # 녹음 시작, threshold가 넘어건 소리가 1unit 이상 측정 될때 탈출.
    while True:
        data = struct.unpack('<' + ('l' * chunk_size), stream.read(chunk_size))  # 반복 측정
        if statistics.stdev(data) > threshold:
            for _ in range(0, math.ceil((fs / chunk_size) * t) - 1):  # 현재 변수 조건에선 3번 반복됨
                data = struct.unpack('<' + ('l' * chunk_size), stream.read(chunk_size))
                if statistics.stdev(data) > threshold:
                    temp += 1

            if temp > 3:  # threshold를 넘어선 소리가 4번 이어질 경우, 1unit '.'으로 판단
                morse += '.'
                break
            else:         # 아닐 경우, 잡음으로 판단하고 계속 대기
                continue

    # 측정 부분
    while True:
        for _ in range(0, math.ceil((fs / chunk_size) * t)):  # 현재 변수 조건에선 4번 반복됨.
            data = struct.unpack('<' + ('l' * chunk_size), stream.read(chunk_size))
            if statistics.stdev(data) > threshold:
                temp += 1

        if temp > 3:    # 4번의 측정에서 전부 threshold를 넘겼을 경우, 유효한 신호로 판단
            morse += '.'
            empty = 0
        else:           # 아닐 경우, 공백
            morse += ' '
            empty += 1

        print(morse)
        temp = 0

        if empty > 50:  # 공백이 50이상일 경우 -> 5초이상 무음으로 판단, 녹음 종료
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    morse = morse.strip()   # 양쪽 여백 제거
    morse = morse.replace('...', '-')  # 3 straights to dash
    morse = morse.replace('       ', '#$#')  # temp medium gap (7 units)
    morse = morse.replace('   ', '#')  # temp short gap  (3 units)
    morse = morse.replace(' ', '')  # inter gap  (1 unit)
    morse = morse.replace('#', ' ')  # restore short gap

    print("received : " + morse)
    print("decoded  : " + morse2text(morse))
    print("done")

    pass


def main():
    while True:
        print('Morse Code over Sound with Noise')
        print('2024 Spring Data Communication at CNU')
        print('[1] Send morse code over sound (play)')
        print('[2] Receive morse code over sound (record)')
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
