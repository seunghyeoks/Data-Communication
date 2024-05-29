import socket

FLAGS = _ = None
DEBUG = False
# ipaddress = '127.0.0.1
ipaddress = '172.16.98.134'
port = 3034
chunk_maxsize = 1500


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5.0)
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
            with open(filename, 'wb') as f:
                while remain > 0:
                    chunk, server = sock.recvfrom(FLAGS.chunk_maxsize)

                    chunk_size = len(chunk)
                    if chunk_size == 0:
                        break
                    remain -= chunk_size

                    f.write(chunk)

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
