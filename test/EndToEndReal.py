import os
import threading
import unittest
from time import sleep
from hamcrest import *
import filecmp

from src.util import FileSystemUtils
from src.client import TCPClient, FolderMonitor, EventHandler
from src.server import TCPServer

DIR_PATH = "/home/yaron/Desktop/watched"
SERVER_PORT = 8099


class Counter:
    def __init__(self):
        self.num = 0

    def inc(self):
        self.num += 1
        return str(self.num)


fsu = FileSystemUtils()
counter = Counter()


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.server = TCPServer(SERVER_PORT)
        self.t = threading.Thread(name="server-thread", target=self.server.run)
        self.t.setDaemon(True)
        self.t.start()
        sleep(1)

        if not fsu.exists(DIR_PATH):
            print("created 'watched' folder at {}".format(DIR_PATH))
            fsu.createFolder(DIR_PATH)

    def setUp(self):
        if not fsu.isEmpty(DIR_PATH):
            fsu.deleteDir(DIR_PATH)
            fsu.createFolder(DIR_PATH)

        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, None]
        self.client = TCPClient(params)
        self.client.register()
        sleep(0.1)



    def test_client_register_to_server_uploads_folder_and_server_saves_folder_locally_folders_should_be_identical(self):
        print(
            "TEST {}: REGISTER AND UPLOAD TO SERVER\n________________________________________\n".format(counter.inc()))

        fsu.createNonEmptyFolder(DIR_PATH + "/newFolder", 2)
        assert_that(128, is_(len(self.client.accessToken)))
        self.client.uploadFolder()
        sleep(0.5)
        assert_that(DIR_PATH, is_(self.server.getClient(self.client.accessToken).folderRoot))
        self.serverFolderCopy = self.server.getClient(self.client.accessToken).folderLocalCopyRoot
        assert_that(fsu.areDirsIdentical(DIR_PATH, self.serverFolderCopy), is_(True))

    def test_client_monitoring_and_detect_new_folder_and_updates_server(self):
        print(
            "TEST {}: NEW FOLDER IN MONITORED FOLDER\n________________________________________\n".format(counter.inc()))

        self.startMonitoringThread()
        sleep(0.1)
        fsu.createFolder(DIR_PATH + "/newFolder")
        sleep(0.1)
        self.serverFolderCopy = self.server.getClient(self.client.accessToken).folderLocalCopyRoot
        assert_that(fsu.areDirsIdentical(DIR_PATH, self.serverFolderCopy), is_(True))



    def test_client_monitoring_and_detect_new_file_and_updates_server(self):
        print("TEST {}: NEW FILE IN MONITORED FOLDER\n________________________________________\n".format(counter.inc()))
        self.startMonitoringThread()
        sleep(0.1)
        fsu.createFile(DIR_PATH + "/newFile")
        sleep(0.3)
        self.serverFolderCopy = self.server.getClient(self.client.accessToken).folderLocalCopyRoot
        assert_that(fsu.areDirsIdentical(DIR_PATH, self.serverFolderCopy), is_(True))

    def test_client_monitoring_and_detect_delete_file_and_updates_server(self):
        print("TEST {}: DELETE FILE IN MONITORED FOLDER\n________________________________________\n".format(
            counter.inc()))
        # creates new file in the folder
        fsu.createFile(DIR_PATH + "/newFile")
        # start monitoring
        self.startMonitoringThread()
        self.client.uploadFolder()
        fsu.deleteFile(DIR_PATH + "/newFile")
        sleep(0.3)
        self.serverFolderCopy = self.server.getClient(self.client.accessToken).folderLocalCopyRoot
        assert_that(fsu.areDirsIdentical(DIR_PATH, self.serverFolderCopy), is_(True))

    def test_client_monitoring_and_detect_delete_empty_folder_and_updates_server(self):
        print("TEST {}: DELETE EMPTY-FOLDER IN MONITORED FOLDER\n________________________________________\n".format(
            counter.inc()))
        # creates new folder in the monitored folder
        fsu.createFolder(DIR_PATH + "/newFolder")
        self.client.uploadFolder()
        self.startMonitoringThread()
        sleep(0.1)
        fsu.deleteDir(DIR_PATH + "/newFolder")
        sleep(0.3)
        self.serverFolderCopy = self.server.getClient(self.client.accessToken).folderLocalCopyRoot
        assert_that(fsu.areDirsIdentical(DIR_PATH, self.serverFolderCopy), is_(True))

    # couldn't model a user deletion of a non-empty folder, but tested for it manually and it works as well.
    def test_client_monitoring_and_detect_delete_non_empty_folder_and_updates_server(self):
        print("TEST {}: DELETE EMPTY-FOLDER IN MONITORED FOLDER\n________________________________________\n".format(
            counter.inc()))
        fsu.createNonEmptyFolder(DIR_PATH + "/newFolder", 1)
        self.client.uploadFolder()
        self.startMonitoringThread()
        sleep(0.1)
        fsu.deleteDir(DIR_PATH + "/newFolder")
        sleep(0.5)
        self.serverFolderCopy = self.server.getClient(self.client.accessToken).folderLocalCopyRoot
        assert_that(fsu.areDirsIdentical(DIR_PATH, self.serverFolderCopy), is_(True))

    def test_client_monitoring_and_detect_file_moved_and_updates_server(self):
        print("TEST {}: DELETE EMPTY-FOLDER IN MONITORED FOLDER\n________________________________________\n".format(
            counter.inc()))
        # creates new folder and a file in it in the monitored folder
        fsu.createFolder(DIR_PATH + "/newFolder")
        fsu.createFile(DIR_PATH + "/newFile")
        self.client.uploadFolder()
        self.startMonitoringThread()
        sleep(0.1)
        fsu.move(DIR_PATH + "/newFile", DIR_PATH + "/newFolder/newFile")
        sleep(0.5)
        self.serverFolderCopy = self.server.getClient(self.client.accessToken).folderLocalCopyRoot
        assert_that(fsu.areDirsIdentical(DIR_PATH, self.serverFolderCopy), is_(True))

    def tearDown(self):
        self.client.stopMonitoring()
        fsu.deleteDir(self.serverFolderCopy)
        fsu.deleteDir(DIR_PATH)
        fsu.createFolder(DIR_PATH)

    @classmethod
    def tearDownClass(cls):
        fsu.deleteDir(DIR_PATH)

    def startMonitoringThread(self):
        threading.Thread(name="monitor-thread", target=self.client.startMonitoring, daemon=True).start()


if __name__ == '__main__':
    unittest.main()
