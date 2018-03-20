#!/usr/bin/python3

import socket
import argparse
from sntp_message import StnpMessage
import sys


def create_parser():
    parser = argparse.ArgumentParser(
        description='Сервер точного времени, который врет на заданное в своем '
                    'конфигурационном файле число секунд')
    return parser.parse_args()


class PseudoSntpServer:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._socket = None

    def run(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self._socket.bind((self._host, self._port))
        except OSError as e:
            print(e)
            sys.exit(1)

        try:
            while True:
                data, address = self._socket.recvfrom(100)
                response = StnpMessage.make_response(bytearray(data))
                if response is not None:
                    self._socket.sendto(response, address)
        finally:
            self._socket.close()


if __name__ == '__main__':
    _parser = create_parser()
    PseudoSntpServer('localhost', 123).run()

