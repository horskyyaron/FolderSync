import threading
from time import sleep
import unittest
from hamcrest import *

from src.client import *
from src.server import TCPServer

DIR_PATH = "/home/yaron/Desktop/watched"
SERVER_PORT = 8082


class FakeRequestHandler:
    pass


class FakeTCPServer(TCPServer):

    def __init__(self, port):
        super().__init__(port)
        self.stop = False
        self.response = None
        self.requestHandler = FakeRequestHandler()

    def start_server(self):
        print("thread:", threading.currentThread())
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', self.port))
        print("[FAKE SERVER]: started. listening on port", self.port)
        server.listen(5)
        server.settimeout(10)

        while not self.stop:
            try:
                client_socket, client_address = server.accept()
                print("[FAKE SERVER]: client connected!")
                print("[FAKE SERVER]: waiting for client request")
                client_socket.recv(1024).decode('utf-8')
                print("[FAKE SERVER]: registering client, sending access token")
                client_socket.send(b"123")
                print("[FAKE SERVER]: downloading client folder...")
                self.response = client_socket.recv(1024).decode('utf-8')
                client_socket.close()
                print("[FAKE SERVER]: closing client socket")
            except socket.timeout:
                continue

        print("[FAKE SERVER]: closing server.")
        server.close()

    def run(self):
        # Start the server in a new thread
        daemon = threading.Thread(name='server thread',
                                  target=self.start_server)
        daemon.setDaemon(True)  # Set as a daemon so it will be killed once the main thread is dead.
        daemon.start()

    def stopServer(self):
        self.stop = True


class FakeFolderMonitor:
    def __init__(self, folder, eventHandler):
        self.folder = folder
        self.eventHandler = eventHandler

    def monitorOnDifThread(self):
        print("thread:", threading.currentThread())
        print("[CLIENT]: monitoring...")
        observer = Observer()
        observer.schedule(self.eventHandler, self.folder, recursive=True)
        observer.start()
        try:
            while observer.is_alive():
                observer.join(1)
        except KeyboardInterrupt:
            observer.stop()
        finally:
            observer.stop()
            observer.join()

    def start(self):
        # Start the server in a new thread
        daemon = threading.Thread(name='monitor thread',
                                  target=self.monitorOnDifThread)
        daemon.setDaemon(True)  # Set as a daemon so it will be killed once the main thread is dead.
        daemon.start()


class FakeEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print("something happened")



class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.server = FakeTCPServer(SERVER_PORT)
        self.server.run()
        sleep(0.1)




    def test_FolderSyncEndToEnd_signup_and_get_access_token(self):
        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, "some interval"]
        client = TCPClient(params, None)
        client.signup()
        sleep(0.1)
        client.shutdown()
        assert_that(client.accessToken, equal_to("123"))

    def test_uploadingEmptyFolderToServer(self):
        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, "some interval"]
        client = TCPClient(params, None)
        client.signup()
        client.uploadFolder()
        sleep(0.1)
        client.shutdown()
        assert_that(self.server.response, is_("sent folder"))

    @classmethod
    def tearDownClass(self):
        self.server.stopServer()
        sleep(1)


if __name__ == '__main__':
    unittest.main()
