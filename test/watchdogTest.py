import os
import threading
from time import sleep

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

DIR_PATH = "/home/yaron/Desktop/watched"


class FakeEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print(event.event_type)


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


os.mkdir(DIR_PATH)
with open(DIR_PATH + "/file","w") as f:
    f.write("")

handler = FakeEventHandler()
monitor = FolderMonitor(DIR_PATH, handler)
threading.Thread(target=monitor.start, daemon=True).start()
while True:
    pass
