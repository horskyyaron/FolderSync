import socket

from src.utils import ConnectionSystem


class FolderMonitor:
    def __init__(self, folder):
        self.folder = folder

    def start(self):
        pass


class TCPClient(ConnectionSystem):
    def __init__(self, params, monitor):
        self.params = params
        self.monitor = monitor
        self.connection = None

    def signup(self, serverIp, serverPort):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((serverIp, serverPort))

    def startMonitoring(self):
        self.monitor.start()

    def shutdown(self):
        try:
            self.connection.close()
        except Exception:
            print("oops")

    
    


