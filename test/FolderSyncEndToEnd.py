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
        client_socket.close()
        print("[FAKE SERVER]: closing client socket")
        print("[FAKE SERVER]: closing server.")
        server.close()


    def run(self):
        # Start the server in a new thread
        daemon = threading.Thread(name='daemon_server',
                                  target=self.start_server)
        daemon.setDaemon(True)  # Set as a daemon so it will be killed once the main thread is dead.
        daemon.start()


class FakeFolderMonitor(FolderMonitor):
    def start(self):
        print("[MONITOR]: monitoring folder")


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.serverPort = 8080

    def test_FolderSyncEndToEnd(self):
        server = FakeTCPServer(self.serverPort)
        server.run()
        time.sleep(1)
        params = ["127.0.0.1", "12345", "some path", "some interval"]
        client = TCPClient(params, FakeFolderMonitor("somePath"))
        client.signup("127.0.0.1", self.serverPort)
        time.sleep(1)
        client.startMonitoring()
        client.shutdown()


if __name__ == '__main__':
    unittest.main()
