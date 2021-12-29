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
SERVER_PORT = 8082

fsu = FileSystemUtils()

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
            os.mkdir(DIR_PATH)

    def setUp(self):
        if not fsu.isEmpty(DIR_PATH):
            fsu.deleteDir(DIR_PATH)
            os.mkdir(DIR_PATH)

    def test_client_register_to_server_uploads_folder_and_server_saves_folder_locally_folders_should_be_identical(self):
        print("TEST: REGISTER AND UPLOAD TO SERVER\n________________________________________\n")
        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, None]
        client = TCPClient(params)
        client.register()
        sleep(0.1)
        assert_that(128, is_(len(client.accessToken)))
        client.uploadFolder()
        sleep(3)
        assert_that(DIR_PATH, is_(self.server.getClient(client.accessToken).folderRoot))
        self.serverFolderCopy = self.server.getClient(client.accessToken).folderLocalCopyRoot
        assert_that(fsu.areDirsIdentical(DIR_PATH, self.serverFolderCopy), is_(True))

    def test_client_monitoring_and_detect_new_folder_and_updates_server(self):
        print("TEST: NEW FOLDER IN MONITORED FOLDER\n________________________________________\n")
        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, None]
        client = TCPClient(params)
        client.register()
        sleep(0.1)
        threading.Thread(name="monitor-thread", target=client.startMonitoring, daemon=True).start()
        sleep(0.1)
        os.mkdir(DIR_PATH + "/" + "newFolder")
        sleep(0.5)
        client.stopMonitoring()
        self.serverFolderCopy = self.server.getClient(client.accessToken).folderLocalCopyRoot
        assert_that(fsu.areDirsIdentical(DIR_PATH, self.serverFolderCopy), is_(True))

    def test_client_monitoring_and_detect_new_file_and_updates_server(self):
        print("TEST: NEW FILE IN MONITORED FOLDER\n________________________________________\n")
        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, None]
        client = TCPClient(params)
        client.register()
        sleep(0.1)
        threading.Thread(name="monitor-thread", target=client.startMonitoring, daemon=True).start()
        sleep(0.1)
        # creates new file in the folder
        with open(DIR_PATH + "/newFile", "w") as f:
            f.write("")
        sleep(0.5)
        client.stopMonitoring()
        self.serverFolderCopy = self.server.getClient(client.accessToken).folderLocalCopyRoot
        assert_that(fsu.areDirsIdentical(DIR_PATH, self.serverFolderCopy), is_(True))

    def test_client_monitoring_and_detect_delete_file_and_updates_server(self):
        print("TEST: DELETE FILE IN MONITORED FOLDER\n________________________________________\n")
        # creates new file in the folder
        with open(DIR_PATH + "/newFile", "w") as f:
            f.write("")

        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, None]
        client = TCPClient(params)
        client.register()
        sleep(0.1)
        client.uploadFolder()
        sleep(0.1)
        # start monitoring
        threading.Thread(name="monitor-thread", target=client.startMonitoring, daemon=True).start()
        sleep(0.1)
        # removing a file
        os.remove(DIR_PATH + "/newFile")
        sleep(0.5)
        client.stopMonitoring()
        self.serverFolderCopy = self.server.getClient(client.accessToken).folderLocalCopyRoot
        assert_that(fsu.areDirsIdentical(DIR_PATH, self.serverFolderCopy), is_(True))

    def test_client_monitoring_and_detect_delete_empty_folder_and_updates_server(self):
        print("TEST: DELETE EMPTY-FOLDER IN MONITORED FOLDER\n________________________________________\n")
        # creates new folder in the monitored folder
        os.mkdir(DIR_PATH + "/newFolder")

        params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, None]
        client = TCPClient(params)
        client.register()
        sleep(0.1)
        client.uploadFolder()
        sleep(0.1)
        # start monitoring
        threading.Thread(name="monitor-thread", target=client.startMonitoring, daemon=True).start()
        sleep(0.1)
        # removing a file
        os.rmdir(DIR_PATH + "/newFolder")
        sleep(0.5)
        client.stopMonitoring()
        self.serverFolderCopy = self.server.getClient(client.accessToken).folderLocalCopyRoot
        assert_that(fsu.areDirsIdentical(DIR_PATH, self.serverFolderCopy), is_(True))

    # def test_client_monitoring_and_detect_delete_non_empty_folder_and_updates_server(self):
    #     print("TEST: DELETE EMPTY-FOLDER IN MONITORED FOLDER\n________________________________________\n")
    #     # creates new folder and a file in it in the monitored folder
    #     os.mkdir(DIR_PATH + "/newFolder")
    #     with open(DIR_PATH + "/newFolder/newFile", "w") as f:
    #         f.write("")
    #
    #     params = ["127.0.0.1", str(SERVER_PORT), DIR_PATH, None]
    #     client = TCPClient(params)
    #     client.register()
    #     sleep(0.1)
    #     client.uploadFolder()
    #     sleep(0.1)
    #     # start monitoring
    #     threading.Thread(name="monitor-thread", target=client.startMonitoring, daemon=True).start()
    #     sleep(0.5)
    #     client.stopMonitoring()
    #     self.serverFolderCopy = self.server.getClient(client.accessToken).folderLocalCopyRoot
    #     assert_that(areDirsIdentical(DIR_PATH, self.serverFolderCopy), is_(True))

    def tearDown(self):
        fsu.deleteDir(self.serverFolderCopy)
        fsu.deleteDir(DIR_PATH)
        os.mkdir(DIR_PATH)

    @classmethod
    def tearDownClass(cls):
        fsu.deleteDir(DIR_PATH)


if __name__ == '__main__':
    unittest.main()

