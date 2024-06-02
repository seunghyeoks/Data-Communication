import math
import random

import reedsolo

RSC_LEN = 4
HEX = {'0', '1', '2', '3',
       '4', '5', '6', '7',
       '8', '9', 'A', 'B',
       'C', 'D', 'E', 'F'}

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


# 연습 1
# 일반 RS 인코딩 및 디코딩
text = '🐯사용자 입력!💻'
byte_hex = text.encode('utf-8')
string_hex = byte_hex.hex().upper()
rsc = reedsolo.RSCodec(RSC_LEN)
byte_rsc = rsc.encode(byte_hex)
string_rsc = byte_rsc.hex().upper()
print(f'인코딩: {string_rsc}')

client_string_rsc = string_rsc
client_byte_hex = bytes.fromhex(client_string_rsc)
client_rsc = reedsolo.RSCodec(RSC_LEN)
client_byte = client_rsc.decode(client_byte_hex)[0]
client_text = client_byte.decode('utf-8')
print(f'디코딩: {client_text}')

# 데이터 오류 추가
client_string_rsc = string_rsc
client_string_list = list(client_string_rsc)
client_string_list[0] = 'A'
client_string_list[1] = 'A'
client_string_rsc = ''.join(client_string_list)

client_byte_hex = bytes.fromhex(client_string_rsc)
client_rsc = reedsolo.RSCodec(RSC_LEN)
client_byte = client_rsc.decode(client_byte_hex)[0]
client_text = client_byte.decode('utf-8')
print(f'디코딩: {client_text}')

# RS Code 오류 추가
client_string_rsc = string_rsc
client_string_list = list(client_string_rsc)
client_string_list[-2] = 'F'
client_string_list[-1] = 'F'
client_string_rsc = ''.join(client_string_list)

client_byte_hex = bytes.fromhex(client_string_rsc)
client_rsc = reedsolo.RSCodec(RSC_LEN)
client_byte = client_rsc.decode(client_byte_hex)[0]
client_text = client_byte.decode('utf-8')
print(f'디코딩: {client_text}')


print()  # 연습 2
client_rsc = reedsolo.RSCodec(RSC_LEN)
for i in range(0, RSC_LEN):
    client_string_rsc = string_rsc
    client_string_list = list(client_string_rsc)
    for r in random.sample(range(0, len(client_string_list) // 2), k=i):
        m = random.randint(0, 2)
        if m == 0:
            client_string_list[(r - 1) * 2] = random.choice(list(HEX - {client_string_list[(r - 1) * 2]}))
        elif m == 1:
            client_string_list[(r - 1) * 2 + 1] = random.choice(list(HEX - {client_string_list[(r - 1) * 2 + 1]}))
        elif m == 2:
            client_string_list[(r - 1) * 2] = random.choice(list(HEX - {client_string_list[(r - 1) * 2]}))
            client_string_list[(r - 1) * 2 + 1] = random.choice(list(HEX - {client_string_list[(r - 1) * 2 + 1]}))
    client_string_rsc = ''.join(client_string_list)
    client_byte_hex = bytes.fromhex(client_string_rsc)
    try:
        client_byte = client_rsc.decode(client_byte_hex)[0]
        client_text = client_byte.decode('utf-8')
        if client_text == text:
            print(f'{i}개 오류 통과(정정):')
            print(f'> {string_rsc}')
            print(f'> {client_string_rsc}')
    except reedsolo.ReedSolomonError:
        print(f'{i}개 오류 통과(정정) 실패:')
        print(f'> {string_rsc}')
        print(f'> {client_string_rsc}')
        break

print()  # 연습 3
DATA_LEN = 12
RSC_LEN = 4
INTMAX = 2 ** (16 - 1) - 1
UNIT = 0.1
SAMPLERATE = 48000

text = '이것도 되나??'
byte_hex = text.encode('utf-8')
string_hex = byte_hex.hex().upper()
encode_hex = ""
decode_hex = ""

audio = []
for i in range(int(UNIT * SAMPLERATE * 2)):
    audio.append(INTMAX * math.sin(2 * math.pi * rules['START'] * i / SAMPLERATE))


client_rsc = reedsolo.RSCodec(RSC_LEN)
for k in range(0, len(byte_hex), DATA_LEN):
    data = byte_hex[k:k + DATA_LEN]
    encoded_data = client_rsc.encode(data).hex().upper()
    print(f'before_encode : {data.hex().upper()}')
    print(f'encoded_data  : {encoded_data}')
    encode_hex += encoded_data

    decoded_data = client_rsc.decode(bytes.fromhex(encoded_data))[0]
    print(f'decoded_data  : {decoded_data.hex().upper()}\n')
    decode_hex += decoded_data.hex().upper()

    for s in encoded_data:
        for i in range(int(UNIT * SAMPLERATE * 1)):
            audio.append(INTMAX * math.sin(2 * math.pi * rules[s] * i / SAMPLERATE))

for i in range(int(UNIT * SAMPLERATE * 2)):
    audio.append(INTMAX * math.sin(2 * math.pi * rules['END'] * i / SAMPLERATE))


print(bytes.fromhex(decode_hex).decode('utf-8'))
print()

# DATA_LEN = 12, RSC_LEN = 4
text_bytes = bytes.fromhex(encode_hex)

client_rsc = reedsolo.RSCodec(RSC_LEN)
for k in range(0, len(text_bytes), DATA_LEN + RSC_LEN):
    data_temp = text_bytes[k:k + DATA_LEN + RSC_LEN]
    decoded_data = client_rsc.decode(data_temp)[0]
    print("input  [block " + str(k % 15) + "] : " + data_temp.hex().upper())
    print("decode [block " + str(k % 15) + "] : " + decoded_data.hex().upper())
    print()
