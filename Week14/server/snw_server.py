import socket
import struct
import os

FLAGS = _ = None
DEBUG = False

ipaddress = 'localhost'  # 'localhost' or '172.16.98.134'
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
    sock.bind((FLAGS.address, FLAGS.port))
    sock.settimeout(1.0)
    print(f'Ready to send using {sock}')

    while True:
        try:
            data, client = sock.recvfrom(FLAGS.chunk_maxsize)
            data = data.decode('utf-8').strip().split()
            print(f'Received {data} from {client}')

            # 명령어와 파일 이름 부분을 분리
            command = str(data[0]).upper()
            filename = data[1]

            # 파일 검색
            if not os.path.isfile(filename):
                sock.sendto("404 Not Found".encode('utf-8'), client)
                print(f'[404] {data[1]} Not Found\n')
                continue

            # 파일 사이즈 전송
            if command == 'INFO':
                file_size = os.path.getsize(filename)
                sock.sendto(str(file_size).encode('utf-8'), client)
                print(f'Send info {file_size} to {client}')

            # 파일 전송
            if command == 'DOWNLOAD':
                file_size = os.path.getsize(filename)
                remain = file_size

                prevseq = 0
                stack = 0

                with open(filename, 'rb') as f:
                    # 첫 패킷 전송, seq는 0으로 설정
                    seq = struct.pack('>H', 0)
                    block = f.read(chunk_maxsize - 4)
                    checksum = struct.pack('>H', calculate_checksum(seq + b'\x00\x00' + block))

                    send_data = seq + checksum + block
                    sock.sendto(send_data, client)

                    while remain >= 0:
                        try:
                            recvseq, client = sock.recvfrom(FLAGS.chunk_maxsize)

                            # seq 확인, H: unsigned Short
                            seq = struct.unpack('>H', recvseq)[0]

                            if prevseq == seq:
                                print(f'[FAIL] invalid Seq {seq} received. RETRY')
                                # 이전에 보낸 응답이 누락, 이전 seq로 다시 응답
                                sock.sendto(send_data, client)
                                continue

                            # 답장을 확인 한 후, 남은 전송량을 반영하도록 작성
                            remain -= len(block)
                            print(f'[Send] Seq:{seq}\tProgress:{file_size - remain}/{file_size}')

                            # 전송할게 없으면 종료 (마지막 패킷에 대한 답장도 이미 받았으므로)
                            if remain == 0:
                                print(f'transfer success')
                                break

                            # 다음 패킷 준비 및 전송
                            seq = struct.pack('>H', seq)
                            block = f.read(chunk_maxsize - 4)
                            checksum = struct.pack('>H', calculate_checksum(seq + b'\x00\x00' + block))

                            send_data = seq + checksum + block
                            sock.sendto(send_data, client)

                            stack = 0
                            prevseq = seq % 2

                        except socket.timeout:
                            # 클라이언트의 응답이 없는 경우, 이전 패킷 재전송.
                            sock.sendto(send_data, client)

                            stack += 1
                            if stack > 4:   # timer의 4배 기다림 ( 마지막 송수신 누락 대비 )
                                print(f'holding stack expired')
                                break
                            else:
                                continue

        except socket.timeout:
            # 단순 대기시 timeout 종료 방지
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
