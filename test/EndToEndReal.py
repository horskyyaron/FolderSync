import threading
import unittest
from time import sleep
from hamcrest import *

from src.client import TCPClient, FolderMonitor, EventHandler
from src.server import TCPServer

DIR_PATH = "/home/yaron/Desktop/watched"
SERVER_PORT = 8906


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.server = TCPServer(SERVER_PORT)
        self.t = threading.Thread(name="server-thread", target=self.server.run)
        self.t.setDaemon(True)
        self.t.start()
        sleep(1)

    def test_client_signup_to_server_uploads_folder_and_start_monitoring_server_saves_folder_locally(self):
        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, "some interval"]
        client = TCPClient(params, FolderMonitor(DIR_PATH, EventHandler()))
        client.register()
        sleep(0.1)
        assert_that(128, is_(len(client.accessToken)))
        client.uploadFolder()
        sleep(0.1)
        # client.startMonitoring()
        # client.stopMonitoring()
        client.shutdown()


if __name__ == '__main__':
    unittest.main()
