from time import sleep
import unittest
from hamcrest import *
from src.client import *

DIR_PATH = "/home/yaron/Desktop/watched"
SERVER_PORT = 8090


class MyTestCase(unittest.TestCase):


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


    # def test_uploadingEmptyFolderToServer(self):
    #     params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, "some interval"]
    #     client = TCPClient(params, None)
    #     client.signup()
    #     client.uploadFolder()
    #     sleep(0.1)
    #     client.shutdown()
    #     assert_that(self.server.response, is_("sent folder"))


if __name__ == '__main__':
    unittest.main()
