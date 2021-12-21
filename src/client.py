import socket

from src.utils import ConnectionSystem


class FolderMonitor:
    pass


class TCPClient(ConnectionSystem):
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

    def signup(self, serverIp, serverPort):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((serverIp, serverPort))

    def startMonitoring(self):
        pass
    
    


