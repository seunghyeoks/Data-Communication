import socket
import os

FLAGS = _ = None
DEBUG = False

ipaddress = '127.0.0.1'
port = 3034

chunk_size = 1500


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))
    print(f'Listening on {sock}')

    while True:
        try:
            data, client = sock.recvfrom(2 ** 16)
            data = data.decode('utf-8').strip().split()
            print(f'Received {data} from {client}')

            # file 검색
            command = str(data[0]).upper()
            filename = "./store/" + data[1]

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
                current = 0

                with open(filename, 'rb') as f:
                    while remain > 0:
                        block = f.read(chunk_size)
                        sock.sendto(block, client)
                        print(f'Send block {int(current / chunk_size)} to {client}')
                        remain -= chunk_size
                        current += chunk_size
                    print(f'[FINISHED] {data[1]} transfer\n')
        except KeyboardInterrupt:
            print(f'Shutting down... {sock}')
            break


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--address', type=str, default=ipaddress)
    parser.add_argument('--port', type=int, default=port)

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()
