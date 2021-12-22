from socket import socket

from src.utils import ConnectionSystem


class RequestHandler:
    pass


class TCPServer(ConnectionSystem):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.requestHandler = RequestHandler()

    def run(self):
        pass