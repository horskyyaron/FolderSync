import os
from time import sleep
import unittest
from hamcrest import *

from src.FakeServer import FakeTCPServer
from src.client import *
from src.FakeUtils import *
from watchdog.events import *

DIR_PATH = "/home/yaron/Desktop/watched"
SERVER_PORT = 8900


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self) -> None:
        self.server = FakeTCPServer(SERVER_PORT)
        self.t = threading.Thread(name="server-thread", target=self.server.run)
        self.t.setDaemon(True)
        self.t.start()
        sleep(1)

    def test_FolderSyncEndToEnd_signup_and_get_access_token(self):
        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, "some interval"]
        client = TCPClient(params, FolderMonitor)
        client.signup()
        client.shutdown()
        assert_that(client.accessToken, equal_to("123"))
        print("\n")

    def test_signup_and_upload_folder(self):
        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, "some interval"]
        client = TCPClient(params, FolderMonitor)
        client.signup()
        client.uploadFolder()
        client.shutdown()
        print("\n")

    def test_signup_and_upload_folder_and_monitor_with_fakes(self):
        monitor = FakeFolderMonitor(None, FakeEventHandler)
        fakeFolder = FakeFolder()
        fakeFolder.addMonitor(monitor)
        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, "some interval"]
        client = TCPClient(params, monitor)
        client.startMonitoring()
        fakeFolder.notifyEvent("folder created")
        fakeFolder.notifyEvent("file created")
        fakeFolder.notifyEvent("folder deleted")
        fakeFolder.notifyEvent("folder moved")
        sleep(0.1)
        monitor.stopMonitoring()
        print("\n")


if __name__ == '__main__':
    unittest.main()
