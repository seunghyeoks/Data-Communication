import socket
import random

FLAGS = _ = None
DEBUG = False


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))
    print(f'Listening on {sock}')

    while True:
        numbers = list(range(1, 46))
        data, client = sock.recvfrom(2 ** 16)
        data = data.decode('utf-8').strip().split()
        temp = []
        print(f'Received {data} from {client}')

        # 입력 데이터 처리
        for k in data:
            temp.append(int(k))
            numbers.remove(int(k))

        # 랜덤 선택 처리
        temp2 = random.sample(numbers, 6 - len(data))
        for t in temp2:
            print("auto picked : " + str(t))

        # 병합 및 변환
        result = temp + temp2
        result.sort()
        string_list = [str(num) for num in result]
        result = ' '.join(string_list)

        sock.sendto(result.encode('utf-8'), client)
        print(f'Send {result} to {client}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--address', type=str, default='127.0.0.1',
                        help='The address to serve service')
    parser.add_argument('--port', type=int, default=3034,
                        help='The port to serve service')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()
