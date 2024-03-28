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
    print("\n")
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
    print("\n")

    pass


def receive_data():
    # 준비 부분
    print("\n")
    print("listening...")

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt32,
                    channels=1,
                    rate=fs,
                    input=True)

    morse = ''
    empty = 0
    unit = int((fs / chunk_size) * t)   # unit의 측정 기준, 현재 조건에 경우 4 값을 가짐

    over_t = 0
    unit_counter = 0
    maximum_empty = 50
    started = False

    # fs(48000)/chunk_size(1200) = 40
    # -> 1초에 40번 측정, 4번의 측정 데이터로 1unit 측정 가능

    # 녹음 시작
    while True:
        data = struct.unpack('<' + ('l' * chunk_size), stream.read(chunk_size))  # 반복 측정

        if not started:  # 데이터 입력 전
            if statistics.stdev(data) > threshold:
                over_t += 1
            unit_counter += 1

            if unit_counter == unit:
                if unit_counter == over_t:  # 4번의 측정 동안 모두 threshold 초과 -> 데이터 입력 시작으로 간주
                    morse += '.'
                    started = True
                    print("started...")
                over_t = 0
                unit_counter = 0

        else:  # 데이터 입력 부분
            if statistics.stdev(data) > threshold:
                over_t += 1
            unit_counter += 1

            if unit_counter == unit:    # 4번의 측정 동안 모두 threshold 초과 -> '.' 입력으로 해석
                if unit_counter == over_t:
                    morse += '.'
                    empty = 0
                else:                   # 아닐 경우, ' ' 입력으로 해석
                    morse += ' '
                    empty += 1
                over_t = 0
                unit_counter = 0

            print(morse)

        if empty > maximum_empty:       # 공백이 50 unit 이상 측정될 경우 -> 5초이상 입력 없는 것으로 간주, while문 탈출
            print("ended")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    morse = morse.strip()  # 양쪽 여백 제거
    morse = morse.replace('...', '-')  # 3 straights to dash
    morse = morse.replace('       ', '#$#')  # temp medium gap (7 units)
    morse = morse.replace('   ', '#')  # temp short gap  (3 units)
    morse = morse.replace(' ', '')  # inter gap  (1 unit)
    morse = morse.replace('#', ' ')  # restore short gap

    print("\n")
    print("received : " + morse)
    print("decoded  : " + morse2text(morse))
    print("done")
    print("\n")

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
