import os
import threading
import unittest
from time import sleep
from hamcrest import *
import filecmp

from src.client import TCPClient, FolderMonitor, EventHandler
from src.server import TCPServer

DIR_PATH = "/home/yaron/Desktop/watched"
SERVER_PORT = 8087


def isSame(dir1, dir2):
    res = filecmp.dircmp(dir1, dir2)
    if len(res.left_only) > 0 or len(res.right_only) > 0:
        return False
    else:
        match, mismatch, errors = filecmp.cmpfiles(dir1, dir2, res.common_files)
        if len(match) != len(res.common_files):
            return False
        if res.common_dirs:
            for com_dir in res.common_dirs:
                if not isSame(dir1+"/"+com_dir, dir2+"/"+com_dir):
                    return False
        return True






class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.server = TCPServer(SERVER_PORT)
        self.t = threading.Thread(name="server-thread", target=self.server.run)
        self.t.setDaemon(True)
        self.t.start()
        sleep(1)

    def test_client_signup_to_server_uploads_folder_and_server_saves_folder_locally_folders_should_be_identical(self):
        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, "some interval"]
        client = TCPClient(params, FolderMonitor(DIR_PATH, EventHandler()))
        client.register()
        sleep(0.1)
        assert_that(128, is_(len(client.accessToken)))
        client.uploadFolder()
        sleep(5)
        assert_that(DIR_PATH, is_(self.server.clients[client.accessToken].folderRoot))
        assert_that(isSame(DIR_PATH, self.server.getClient(client.accessToken).folderLocalCopyRoot), is_(True))

        client.shutdown()
        # os.rmdir(self.server.clients[client.accessToken].folderLocalCopyRoot)




if __name__ == '__main__':
    unittest.main()
