import math
import statistics
import struct
import time
import wave

import pyaudio
import scipy.fftpack
import numpy

INTMAX = 2 ** (32 - 1) - 1
t = 0.1  # 타이밍
samplerate = 48000
padding = 10
chunk_size = 1200  # 청크 사이즈
unit_counter = t * samplerate / chunk_size  # 1unit 측정에 필요한 횟수 = 4

# 주파수별 변환코드, 측정 환경에 맞게 새팅
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


def send_data():
    # 사용자 입력 단계
    print('\nType some text! ')
    text = input('User input\t : ').strip()
    string_hex = text.encode('utf-8').hex().upper()

    print("converted to : " + string_hex)
    print("\nplaying...")

    # 오디오 변환 단계
    audio = []
    for i in range(int(t * samplerate * 2)):  # start signal, 2unit
        audio.append(int(INTMAX * math.sin(2 * math.pi * rules['START'] * i / samplerate)))
    for s in string_hex:  # text
        for i in range(int(t * samplerate * 1)):
            audio.append(int(INTMAX * math.sin(2 * math.pi * rules[s] * i / samplerate)))
    for i in range(int(t * samplerate * 2)):  # end signal, 2unit
        audio.append(int(INTMAX * math.sin(2 * math.pi * rules['END'] * i / samplerate)))

    # 스피커 재생 단계
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt32,
                    channels=1,
                    rate=samplerate,
                    output=True)

    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i + chunk_size]
        stream.write(struct.pack('<' + ('l' * len(chunk)), *chunk))

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("done.")
    print("\n")

    pass


def receive_data():
    print("\nlistening...\n")

    # 스트림 준비
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt32,
                    channels=1,
                    rate=samplerate,
                    input=True)
    # 지역변수
    started = False
    counter = 0
    text = ''
    temp = []
    temp_end = ''

    while True:
        data = struct.unpack('<' + ('l' * chunk_size), stream.read(chunk_size))  # 청크 만큼 측정

        freq = scipy.fftpack.fftfreq(len(data), d=1 / samplerate)
        fourier = scipy.fftpack.fft(data)
        top = freq[numpy.argmax(abs(fourier))]  # 가장 큰 진폭의 주파수을 가져오기 위해 -> 입력된 주파수

        # rule에 맞게 변환
        for k, v in rules.items():
            if v - padding <= top <= v + padding:
                data = k
                continue

        # 변환에 실패할 경우 -> 임시 문자 할당
        if len(data) > 5:
            data = '$'

        # 데이터 입력 여부 확인 단계
        if not started:
            if data == 'START':
                counter += 1
            else:
                counter = 0

            if counter == 2 * unit_counter:  # 'START'가 8번 연속(2unit) 입력되었을 경우
                started = True
                counter = 0
                print("[START] " + data)

            continue

        # 입력돤 데이터 실시간 해석 단계
        if started:
            counter += 1
            temp.append(data)  # 각 data를 temp에 저장
            if counter != unit_counter:
                continue

            # temp에 4개의 data가 들어갔을 경우, 가장 빈도 많은 걸 data로 선택
            # 앞에서 침범하는 데이터를 피하기 위해 뒤에서 부터 많은거 계산
            # ex) ..., A, A] [A, A, B, B] [D, D, ... -> 일때, 가운데 경우에는 B가 선택되도록
            temp.reverse()
            data = max(set(temp), key=temp.count)
            temp.clear()
            counter = 0

            # 반환할 text에 해당 data 추가
            if data != 'START' and data != 'END':
                text += data
                print("[DATA] " + text)

            # END가 입력될 경우, 2 연속(2unit)인지 판단, 아니면 무시
            if data == 'END':
                if temp_end == '':
                    temp_end = data
                elif temp_end == data:
                    print("[END] " + data)
                    break
                else:
                    temp_end = ''

    print()
    print(f'Decoded: {bytes.fromhex(text).decode("utf-8")}')  # 일반 문자열로 변환해서 print
    print()

    stream.stop_stream()
    stream.close()
    p.terminate()

    pass


def main():
    while True:
        print('Unicode over Sound with Noise')
        print('2024 Spring Data Communication at CNU')
        print('[1] Send Unicode over sound (play)')
        print('[2] Receive Unicode over sound (record)')
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
