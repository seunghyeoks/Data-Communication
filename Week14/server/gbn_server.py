import socket
import struct
import os

FLAGS = _ = None
DEBUG = False
ipaddress = 'localhost'  # 'localhost' or '172.16.98.134'
port = 3034
chunk_maxsize = 1500
window_size = 2 ** 4 - 1


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


def process_queue(f, pop_count, file_queue):
    # pop count 만큼 pop 및 새로운 data 읽기
    for i in range(pop_count):
        prevseq = struct.unpack('>H', file_queue[len(file_queue)-1][:2])[0]
        seq = struct.pack('>H', (prevseq + 1) % 16)
        block = f.read(chunk_maxsize - 4)
        checksum = struct.pack('>H', calculate_checksum(seq + b'\x00\x00' + block))

        file_queue.pop(0)

        # data가 비어있을 경우, queue에 불필요한 push 방지
        if len(block) == 0:
            continue
        else:
            file_queue.append(seq + checksum + block)

    return file_queue


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))
    sock.settimeout(1.0)
    print(f'Listening on {sock}')

    remain = 0

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

                file_queue = []
                seq_queue = []

                send_mode = True
                count = 0

                with open(filename, 'rb') as f:
                    # 첫번째 전송 준비, window size 만큼 패킷을 큐에 집어넣음
                    for i in range(window_size):
                        seq = struct.pack('>H', i)
                        block = f.read(chunk_maxsize - 4)
                        checksum = struct.pack('>H', calculate_checksum(seq + b'\x00\x00' + block))

                        file_queue.append(seq + checksum + block)

                    while remain > 0:
                        try:
                            if send_mode:
                                # 전송 작업 수행, 파일 큐에 있는 데이터 모두 send
                                sock.sendto(file_queue[count], client)
                                tseq = struct.unpack('>H', file_queue[count][:2])[0]

                                count += 1
                                print(f'[send] count:{count}/{len(file_queue)}, seq:{tseq}')

                                # 전송을 다 했을 경우, count 초기화 및 수신 작업으로 전환
                                if count == len(file_queue):
                                    count = 0
                                    send_mode = False
                                    print(f'switch to receive mode, remain:{remain}')

                            else:
                                # 수신 작업 수행, 클라이언트가 보내는 응답 수신
                                # sequence용 큐에 응답 seq 저장
                                if count != len(file_queue):
                                    recvseq, client = sock.recvfrom(2)
                                    seq_queue.append(struct.unpack('>H', recvseq)[0])

                                    count += 1
                                    print(f'[receive] count:{count}/{len(file_queue)}, seq:{seq_queue[count-1]}')

                                # 응답이 모두 들어온 경우
                                if count == len(file_queue):
                                    pop_count = 0

                                    # 누락된 패킷이 있는지 검사
                                    # 서버에서 보낸 첫번째 패킷의 seq+1이 존재 하는지 확인(=target)
                                    firstseq = struct.unpack('>H', file_queue[0][:2])[0]
                                    target = (firstseq + 1) % 16

                                    while len(seq_queue) > 0:
                                        if target in seq_queue:
                                            # target이 있을 경우, target 다음 걸 찾기 위해 순회
                                            target = (target + 1) % 16
                                            remain -= len(file_queue[pop_count][4:])
                                            pop_count += 1
                                        else:
                                            # target이 없을 경우 == 해당 패킷 누락 확인
                                            break

                                    # pop_count 만큼 제대로 전송되었으므로,
                                    # 그 횟수 만큼 파일 큐에서 pop 및 가능한 만큼 read
                                    file_queue = process_queue(f, pop_count, file_queue)

                                    # 파일 큐가 비었을 경우, 송수신 종료
                                    if len(file_queue) == 0:
                                        break

                                    # 보낼 파일큐가 준비 되었으므로, 전송 모드로 전환
                                    seq_queue = []
                                    count = 0
                                    send_mode = True
                                    print(f'switch to send mode, remain:{remain}')

                        except socket.timeout:
                            if remain == 0:
                                print(f'[SUCCESS] \n')
                                break
                            else:
                                # client가 보낸 패킷이 누락되었을 경우, count 1 올리고 넘기기
                                count += 1
                                print(f'time out in receive\n')
                                continue
                    print(f'\n[SUCCESS] {filename} send')
                    print(f'ready to listening\n')


        except socket.timeout:
            if remain > 0:
                print(f'[Timed out] lost size {remain}\n')
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
