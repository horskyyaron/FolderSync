import threading
import time
import unittest

# * client signs up to server and uploads empty folder. (WALKING SKELETON) and monitor for changes.
import socket

import src.client
from src.client import *
from src.server import TCPServer
from src.utils import *


class FakeTCPServer(TCPServer):
    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', self.port))
        print("[FAKE SERVER]: started. listening on port", self.port)
        server.listen(5)
        client_socket, client_address = server.accept()
        print("[FAKE SERVER]: client connected!")


    def run(self):
        # Start the server in a new thread
        daemon = threading.Thread(name='daemon_server',
                                  target=self.start_server)
        daemon.setDaemon(True)  # Set as a daemon so it will be killed once the main thread is dead.
        daemon.start()



class FakeFolderMonitor(FolderMonitor):
    def __init__(self, path):
        self.folderPath = path


class MyTestCase(unittest.TestCase):

    def test_FolderSyncEndToEnd(self):
        server = FakeTCPServer(12345)
        server.run()
        time.sleep(1)
        params = ["127.0.0.1", "12345", "some path", "some interval"]
        client = TCPClient(params, FakeFolderMonitor("somePath"))
        client.signup("127.0.0.1", 12345)
        client.startMonitoring()


if __name__ == '__main__':
    unittest.main()
