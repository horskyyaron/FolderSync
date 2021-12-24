import threading
from watchdog.events import FileSystemEventHandler


class FakeFolderMonitor:
    def __init__(self, folder, eventHandler):
        self.folder = folder
        self.eventHandler = eventHandler()
        self.stop = False
        self.events = []
        self.lock = threading.Lock()

    def monitorOnDifThread(self):
        while not self.stop:
            if self.events:
                self.lock.acquire()
                if self.events:
                    self.eventHandler.on_any_event(self.events.pop(0))
                self.lock.release()

    def start(self):
        t = threading.Thread(name='Monitor-Thread',
                             target=self.monitorOnDifThread)
        t.start()

    def handle(self, event):
        self.events.append(event)

    def stopMonitoring(self):
        self.stop = True


class FakeFolder:
    def __init__(self):
        self.monitor = None

    def addMonitor(self, monitor):
        self.monitor = monitor

    def notifyEvent(self, event):
        self.monitor.handle(event)


class FakeEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print(event)
