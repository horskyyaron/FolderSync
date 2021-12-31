import threading
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import os

from src.util import FileSystemUtils as fsu

DIR_PATH = "/home/yaron/Desktop/watched"


class FakeEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print(event)


class FolderMonitor:
    def __init__(self, folder, eventHandler):
        self.observer = Observer()
        self.observer.schedule(eventHandler, folder, recursive=True)
        self.stop = False

    def start(self):
        print('[MONITOR]: started monitoring')
        self.observer.start()
        while not self.stop:
            try:
                while self.observer.is_alive():
                    self.observer.join(1)
            except KeyboardInterrupt:
                self.observer.stop()
            finally:
                self.observer.stop()
                self.observer.join()

    def stopMonitoring(self):
        self.observer.stop()
        self.stop = True


fsu.createNonEmptyFolder(DIR_PATH, 5)

handler = FakeEventHandler()
monitor = FolderMonitor(DIR_PATH, handler)
t = threading.Thread(target=monitor.start, name="monitor-thread", daemon=True)
t.start()
try:
    while True:
        pass
except KeyboardInterrupt:
    monitor.stopMonitoring()
    fsu.deleteDir(DIR_PATH)
