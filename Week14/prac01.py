import socket
import struct

FLAGS = _ = None
DEBUG = False


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f'Ready to send using {sock}')

    while True:
        try:
            data = input('Data: ').strip()
            request = f'{data}'
            size = len(request)
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))
            for _ in range(size):
                chunk, server = sock.recvfrom(FLAGS.chunk_maxsize)
                seq = chunk[:2]
                seq = struct.unpack('>H', seq)[0]
                data = chunk[2:]
                data = data.decode('utf-8')
                print(f'Received {data} from {server} with {seq}')
        except KeyboardInterrupt:
            print(f'Shutting down... {sock}')
            break


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--address', type=str, default='localhost',
                        help='The address to send data')
    parser.add_argument('--port', type=int, default=3034,
                        help='The port to send data')
    parser.add_argument('--chunk_maxsize', type=int, default=2**16,
                        help='The recvfrom chunk max size')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()
