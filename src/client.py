import socket
from datetime import time
from watchdog.events import *
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
        if self.__isKeyEvent(event):
            print("append: ", event)
            self.events.append(event)

    def __isKeyEvent(self, event):
        if (isinstance(event, DirModifiedEvent) or isinstance(event, FileModifiedEvent) or isinstance(event,
                                                                                                      FileClosedEvent)):
            return False
        return True


class FolderMonitor(FileSystemEventHandler):
    def __init__(self, folder, eventHandler):
        self.folder = folder
        self.eventHandler = eventHandler
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


class ClientCommunicator:
    def __init__(self, serverSocket):
        self.serverSocket = serverSocket

    def sendToServer(self, data):
        self.serverSocket.send(MsgHandler.addHeader(data))

    def readFromServer(self):
        responseSize = int(self.serverSocket.recv(len(str(MAX_MSG_SIZE))))
        response = self.serverSocket.recv(responseSize)
        return MsgHandler.decode(response)


class TCPClient:

    def __init__(self, params, monitor):
        self.accessToken = None
        self.params = params
        self.monitor = monitor
        self.serverSocket = None
        self.communicator = None

    def register(self):
        self.connect()
        self.communicator.sendToServer(REGISTER)
        self.accessToken = self.communicator.readFromServer()
        self.communicator.sendToServer(DONE)

    def uploadFolder(self):
        self.connect()
        self.communicator.sendToServer(UPLOAD_FOLDER)
        self.communicator.sendToServer(self.accessToken)
        sendFolderTo(self.serverSocket, self.params[ARG_DIR])
        self.communicator.sendToServer(DONE)

    def connect(self):
        serverIp, serverPort = self.params[ARG_IP], int(self.params[ARG_PORT])
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.connect((serverIp, serverPort))
        self.communicator = ClientCommunicator(self.serverSocket)

    def startMonitoring(self):
        self.monitor.start()

    def stopMonitoring(self):
        self.monitor.stop()

    def shutdown(self):
        try:
            self.serverSocket.close()
        except Exception:
            print("oops")
