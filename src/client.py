import socket
from datetime import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.utils import ConnectionSystem

ARG_IP = 0
ARG_PORT = 1


class EventHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        print("something happened")


class FolderMonitor(FileSystemEventHandler):
    def __init__(self, folder):
        self.folder = folder
        self.eventHandler = EventHandler()

    def start(self):
        print("[CLIENT]: monitoring...")
        observer = Observer()
        observer.schedule(self.eventHandler, self.folder, recursive=True)
        observer.start()
        try:
            while observer.is_alive():
                observer.join(1)
        except KeyboardInterrupt:
            observer.stop()
        finally:
            observer.stop()
            observer.join()


class TCPClient(ConnectionSystem):

    def __init__(self, params, monitor):
        self.params = params
        self.monitor = monitor
        self.connection = None

    def signup(self):
        serverIp, serverPort = self.params[ARG_IP], int(self.params[ARG_PORT])
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((serverIp, serverPort))

    def startMonitoring(self):
        self.monitor.start()

    def shutdown(self):
        try:
            self.connection.close()
        except Exception:
            print("oops")
