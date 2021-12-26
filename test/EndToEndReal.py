import os
import threading
import unittest
from time import sleep
from hamcrest import *
import filecmp

from src.client import TCPClient, FolderMonitor, EventHandler
from src.server import TCPServer

DIR_PATH = "/home/yaron/Desktop/watched"
SERVER_PORT = 8091


def areDirsIdentical(dir1, dir2):
    res = filecmp.dircmp(dir1, dir2)
    if len(res.left_only) > 0 or len(res.right_only) > 0:
        return False
    else:
        match, mismatch, errors = filecmp.cmpfiles(dir1, dir2, res.common_files)
        if len(match) != len(res.common_files):
            return False
        if res.common_dirs:
            for com_dir in res.common_dirs:
                if not areDirsIdentical(dir1 + "/" + com_dir, dir2 + "/" + com_dir):
                    return False
        return True


def deleteDir(path):
    for root, dirs, files in os.walk(path, topdown=True):
        for dir in dirs:
            if isEmpty(root + "/" + dir):
                os.rmdir(root + "/" + dir)
            else:
                deleteDir(root + "/" + dir)
        for file in files:
            os.remove(root + "/" + file)
        os.rmdir(root)


def isEmpty(dirPath):
    return len(os.listdir(dirPath)) == 0


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.server = TCPServer(SERVER_PORT)
        self.t = threading.Thread(name="server-thread", target=self.server.run)
        self.t.setDaemon(True)
        self.t.start()
        sleep(1)

    def test_client_register_to_server_uploads_folder_and_server_saves_folder_locally_folders_should_be_identical(self):
        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, None]
        client = TCPClient(params)
        client.register()
        sleep(0.1)
        assert_that(128, is_(len(client.accessToken)))
        client.uploadFolder()
        sleep(3)
        assert_that(DIR_PATH, is_(self.server.clients[client.accessToken].folderRoot))
        serverFolderCopy = self.server.getClient(client.accessToken).folderLocalCopyRoot
        assert_that(areDirsIdentical(DIR_PATH, serverFolderCopy), is_(True))

        client.shutdown()
        deleteDir(serverFolderCopy)

    def test_client_monitoring_and_detect_new_folder_and_updates_server(self):
        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, None]
        client = TCPClient(params)
        client.register()
        sleep(0.1)
        threading.Thread(name="monitor-thread", target=client.startMonitoring, daemon=True).start()
        sleep(0.1)
        os.mkdir(DIR_PATH+"/"+"newFolder")
        sleep(0.5)
        client.stopMonitoring()
        serverFolderCopy = self.server.getClient(client.accessToken).folderLocalCopyRoot
        assert_that(areDirsIdentical(DIR_PATH, serverFolderCopy), is_(True))

        client.shutdown()
        os.rmdir(DIR_PATH+"/"+"newFolder")
        deleteDir(serverFolderCopy)

if __name__ == '__main__':
    unittest.main()
