import time
import socket

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
            stime = time.time()
            request = f'{data}'
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))

            response, server = sock.recvfrom(FLAGS.chunk_maxsize)
            data_size = len(response)
            response = response.decode('utf-8')
            etime = time.time()
            print(f'Received {response} from {server} after {etime-stime}')
            print(f'> Throughput: {round((data_size*8*2)/(etime-stime)):,d} bps')
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
