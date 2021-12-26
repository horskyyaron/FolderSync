import threading
import unittest
from time import sleep

from hamcrest import *

from src.client import *

DIR_PATH = "/home/yaron/Desktop/watched"


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.monitor = FolderMonitor(DIR_PATH, EventHandler())
        self.client = TCPClient(None, self.monitor)

    def test_monitor_created_new_folder(self):
        threading.Thread(name="monitor-thread", target=self.client.startMonitoring).start()
        sleep(0.1)
        os.mkdir(DIR_PATH + "/newDir")
        sleep(0.1)
        print("\n")
        self.client.stopMonitoring()
        os.rmdir(DIR_PATH + "/" + "newDir")
        eventsStack = self.monitor.eventHandler.events

        assert_that(DirCreatedEvent(DIR_PATH + "/newDir"), is_(eventsStack.pop()))

    def test_monitor_delete_empty_folder(self):
        os.mkdir(DIR_PATH + "/newDir")
        threading.Thread(name="monitor-thread", target=self.client.startMonitoring).start()
        sleep(0.1)
        os.rmdir(DIR_PATH + "/newDir")
        sleep(0.1)
        print("\n")
        self.client.stopMonitoring()

        eventsStack = self.monitor.eventHandler.events
        assert_that(DirDeletedEvent(DIR_PATH + "/" + "newDir"), is_(eventsStack.pop()))

    def test_monitor_move_empty_folder(self):
        os.mkdir(DIR_PATH + "/a")
        os.mkdir(DIR_PATH + "/b")
        threading.Thread(name="monitor-thread", target=self.client.startMonitoring).start()
        sleep(0.1)
        os.rename(DIR_PATH + "/a", DIR_PATH + "/b/a")
        sleep(0.1)
        print("\n")
        self.client.stopMonitoring()

        os.rmdir(DIR_PATH + "/b/a")
        os.rmdir(DIR_PATH + "/b")

        eventsStack = self.monitor.eventHandler.events
        assert_that(DirMovedEvent(DIR_PATH + "/a", DIR_PATH + "/b/a"), is_(eventsStack.pop()))

    def test_monitor_create_file(self):
        threading.Thread(name="monitor-thread", target=self.client.startMonitoring).start()
        sleep(0.1)
        with open(DIR_PATH + "/file.txt", "w") as f:
            f.write("hello")
        sleep(0.1)
        print("\n")
        self.client.stopMonitoring()

        os.remove(DIR_PATH + "/file.txt")

        eventsStack = self.monitor.eventHandler.events
        assert_that(FileCreatedEvent(DIR_PATH + "/file.txt"), is_(eventsStack.pop()))

    def test_monitor_delete_file(self):
        with open(DIR_PATH + "/file.txt", "w") as f:
            f.write("hello")
        threading.Thread(name="monitor-thread", target=self.client.startMonitoring).start()
        sleep(0.1)
        os.remove(DIR_PATH + "/file.txt")
        sleep(0.1)
        print("\n")
        self.client.stopMonitoring()

        eventsStack = self.monitor.eventHandler.events
        assert_that(FileDeletedEvent(DIR_PATH + "/file.txt"), is_(eventsStack.pop()))

    def test_monitor_move_file(self):
        with open(DIR_PATH + "/file.txt", "w") as f:
            f.write("hello")
        os.mkdir(DIR_PATH + "/sub")
        threading.Thread(name="monitor-thread", target=self.client.startMonitoring).start()
        sleep(0.1)
        os.replace(DIR_PATH + "/file.txt", DIR_PATH + "/sub/file.txt")
        sleep(0.1)
        print("\n")
        self.client.stopMonitoring()

        os.remove(DIR_PATH + "/sub/file.txt")
        os.rmdir(DIR_PATH + "/sub")

        eventsStack = self.monitor.eventHandler.events
        assert_that(FileMovedEvent(DIR_PATH+"/file.txt", DIR_PATH + "/sub/file.txt"), is_(eventsStack.pop()))


if __name__ == '__main__':
    unittest.main()
