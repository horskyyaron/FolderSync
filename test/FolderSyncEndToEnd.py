from time import sleep
import unittest
from hamcrest import *

from src.client import *
from src.server import TCPServer
from testUtil import FakeTCPServer

DIR_PATH = "/home/yaron/Desktop/watched"
SERVER_PORT = 8083


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
