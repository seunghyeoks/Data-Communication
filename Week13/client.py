import socket
import struct

FLAGS = _ = None
DEBUG = False

# ipaddress = 'localhost'
ipaddress = '34.168.194.7'
port = 3034
chunk_maxsize = 2 ** 16


def calculate_checksum(data):
    checksum = 0

    if len(data) % 2 == 1:
        data += b'\x00'  # 데이터 길이가 홀수인 경우 패딩 바이트 추가

    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]  # 16비트 만큼 자른 뒤 얻기
        checksum += word
        checksum = (checksum & 0xffff) + (checksum >> 16)  # 오버플로우 처리, 기본 16자리 + 오버플로우 1

    checksum = ~checksum & 0xffff  # 1의 보수 취하기, 16이후는 0으로
    return checksum


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(4.0)
    print(f'Ready to send using {sock}')

    while True:
        remain = 0
        try:
            filename = input('Filename: ').strip()
            request = f'INFO {filename}'
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))

            response, server = sock.recvfrom(FLAGS.chunk_maxsize)
            response = response.decode('utf-8')
            if response == '404 Not Found':
                print(f'{response}\n')
                continue
            size = int(response)

            request = f'DOWNLOAD {filename}'
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))
            print(f'[Request] {filename} to ({FLAGS.address}, {FLAGS.port})')

            remain = size
            prevseq = 1
            with open(filename, 'wb') as f:
                while remain > 0:
                    chunk, server = sock.recvfrom(FLAGS.chunk_maxsize)

                    # data가 비어있을 경우, 종료
                    chunk_size = len(chunk[4:])
                    if chunk_size == 0:
                        break

                    # seq 확인
                    seq = struct.unpack('>H', chunk[:2])[0]
                    if prevseq == seq:
                        print(f'[FAIL] invalid Seq received. RETRY')
                        sock.sendto(struct.pack('>H', (seq + 1) % 2), (FLAGS.address, FLAGS.port))
                        continue

                    #print(calculate_checksum(chunk[4:]))  # 데이터만으로 계산해낸 체크섬
                    #print(struct.unpack('>H', chunk[2:4])[0]) # 입력된 값의 체크섬 부분 추출 및 정수화
                    #print(calculate_checksum(struct.pack('>H', calculate_checksum(chunk[4:])) + chunk[4:]))  # 함수 확인용 1
                    #print(calculate_checksum(struct.pack('>H', calculate_checksum(b'\x00\x00\x00\x01')) + b'\x00\x01'))  # 함수 확인용 2

                    # checksum 확인
                    checksum = calculate_checksum(chunk[2:])
                    if checksum == 0:
                        print(f'[FAIL] invalid Checksum received. RETRY')
                        continue

                    # data 저장
                    data = chunk[4:]
                    remain -= len(data)
                    print(f'[pass] Seq:{seq}\tChecksum:{checksum}\tProgress:{size - remain}/{size}')

                    f.write(data)
                    prevseq = seq
                    sock.sendto(struct.pack('>H', (seq + 1) % 2), (FLAGS.address, FLAGS.port))

                    if DEBUG:
                        print("receive from server")
            print(f'[SUCCESS] {filename} download SUCCESS\n')

        except socket.timeout:
            print(f'[Timed out] loss size {remain}\n')
            continue

        except KeyboardInterrupt:
            print(f'[Shutting down] {sock}')
            break


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--address', type=str, default=ipaddress)
    parser.add_argument('--port', type=int, default=port)
    parser.add_argument('--chunk_maxsize', type=int, default=chunk_maxsize)

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()
