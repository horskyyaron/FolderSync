from socket import socket

from src.utils import ConnectionSystem


class TCPServer(ConnectionSystem):
    def __init__(self, port):
        self.port = port

    def run(self):
        pass