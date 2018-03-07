#!/usr/bin/python3

import socket
import argparse


def create_parser():
    parser = argparse.ArgumentParser(description='Сервер точного времени, который врет на заданное в своем '
                                                 'конфигурационном файле число секунд')
    return parser.parse_args()


class PseudoSntpServer:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._socket = None

    def run(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((self._host, self._port))
        self._socket.listen(10)

        try:
            while True:
                pass
        finally:
            self._socket.close()



if __name__ == '__main__':
    _parser = create_parser()
    PseudoSntpServer('127.0.0.1', 123).run()
