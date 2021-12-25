import socket
from datetime import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from src.requestsUtil import *


ARG_IP = 0
ARG_PORT = 1
ARG_DIR = 2


class EventHandler(FileSystemEventHandler):

    def __init__(self) -> None:
        super().__init__()
        self.events = []

    def on_any_event(self, event):
        print("[EVENT HANDLER]: event happened: ", event)
        self.events.append(event)




class FolderMonitor(FileSystemEventHandler):
    def __init__(self, folder, eventHandler):
        self.folder = folder
        self.eventHandler = eventHandler()
        self.observer = Observer()

    def start(self):
        print('[MONITOR]: started monitoring')
        self.observer.schedule(self.eventHandler, self.folder, recursive=True)
        self.observer.start()
        try:
            while self.observer.is_alive():
                self.observer.join(1)
        except KeyboardInterrupt:
            self.observer.stop()
        finally:
            self.observer.stop()
            self.observer.join()

    def stop(self):
        self.observer.stop()


class TCPClient:

    def __init__(self, params, monitor):
        self.accessToken = None
        self.params = params
        self.monitor = monitor
        self.server = None

    def signup(self):
        self.connect()
        self.sendToServer(REGISTER)
        self.accessToken = self.readFromServer()
        self.sendToServer(DONE)

    def startMonitoring(self):
        self.monitor.start()

    def stopMonitoring(self):
        self.monitor.stop()

    def uploadFolder(self):
        self.connect()
        self.sendToServer(UPLOAD_FOLDER)
        self.sendToServer(self.accessToken)
        self.sendToServer(DONE)

    def sendToServer(self, data):
        self.server.send(MsgHandler.addHeader(data))

    def readFromServer(self):
        responseSize = int(self.server.recv(len(str(MAX_MSG_SIZE))))
        response = self.server.recv(responseSize)
        return MsgHandler.decode(response)

    def connect(self):
        serverIp, serverPort = self.params[ARG_IP], int(self.params[ARG_PORT])
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((serverIp, serverPort))

    def shutdown(self):
        try:
            self.server.close()
        except Exception:
            print("oops")

