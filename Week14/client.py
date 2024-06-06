import socket
import struct

FLAGS = _ = None
DEBUG = False

ipaddress = '34.168.194.7'  # 'localhost' or '172.16.98.134'
port = 3034
chunk_maxsize = 1500


def calculate_checksum(data):
    checksum = 0

    # 데이터의 길이가 홀수인 경우, 마지막에 바이트 앞에 값이 0인 바이트 추가
    if len(data) % 2 == 1:
        data = data[:-1] + b'\x00' + data[-1:]

    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]  # 16비트 만큼 자르기
        checksum += word
        checksum = (checksum & 0xffff) + (checksum >> 16)  # 오버플로우 처리, 기본 16비트 + 오버플로우 값

    checksum = ~checksum & 0xffff  # 1의 보수 취하기, 16이후는 0으로
    return checksum



def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(7.0)
    print(f'Ready to send using {sock}')

    while True:
        remain = 0
        filename = ""
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
            recentseq = 15
            with open(filename, 'wb') as f:
                while remain >= 0:
                    chunk, server = sock.recvfrom(FLAGS.chunk_maxsize)

                    # seq 확인, H: unsigned Short
                    seq = struct.unpack('>H', chunk[:2])[0]
                    if (recentseq+1) % 16 != seq:
                        print(f'[FAIL] invalid Seq {seq} received. RETRY')
                        # 이전에 보낸 응답이 누락, 이전 seq로 다시 응답
                        sock.sendto(struct.pack('>H', recentseq), (FLAGS.address, FLAGS.port))
                        continue

                    # checksum 확인
                    checksum = calculate_checksum(chunk)
                    if checksum != 0:
                        print(f'[FAIL] invalid Checksum {checksum} received. RETRY')
                        # 받은 데이터의 오염, 이번 seq를 다시 보내 재전송 요청
                        sock.sendto(struct.pack('>H', recentseq), (FLAGS.address, FLAGS.port))
                        continue

                    # data 저장 및 서버에 응답
                    data = chunk[4:]
                    remain -= len(data)
                    print(f'[pass] Seq:{seq}\tChecksum:{checksum}\t  Progress:{size - remain}/{size}')

                    f.write(data)
                    recentseq = (seq+1) % 16
                    sock.sendto(struct.pack('>H', recentseq), (FLAGS.address, FLAGS.port))

                    if DEBUG:
                        print("receive from server")


        except socket.timeout:
            if (remain != 0) | (filename == ""):
                print(f'[Timed out] lost size {remain}\n')
            else:
                print(f'[SUCCESS] {filename} download SUCCESS\n')
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
