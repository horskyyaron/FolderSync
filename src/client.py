import socket
import threading
from datetime import time
from watchdog.events import *
from watchdog.observers import Observer
from src.requestsUtil import *

ARG_IP = 0
ARG_PORT = 1
ARG_DIR = 2

CREATED = "created"


class EventHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.events = []
        self.tcpClient = None

    def setTCPClient(self, client):
        self.tcpClient = client

    def on_any_event(self, event):
        print("[EVENT HANDLER]: event happened: ", event)
        if self.__isKeyEvent(event):
            self.events.append(event)
            self.notify(event)

    def __isKeyEvent(self, event):
        if (isinstance(event, DirModifiedEvent) or isinstance(event, FileModifiedEvent) or isinstance(event,
                                                                                                      FileClosedEvent)):
            return False
        return True

    def notify(self, event):
        self.tcpClient.updateServer(event)


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


class ClientCommunicator(BaseCommunicator):
    def __init__(self, serverSocket):
        super().__init__(serverSocket)

    def sendToServer(self, data):
        self.send(data)

    def readFromServer(self):
        return self.read()


class TCPClient:
    def __init__(self, params):
        self.accessToken = None
        self.params = params
        self.monitor = None
        self.serverSocket = None
        self.communicator = None
        self.eventHandler = None

    def register(self):
        self.connect()
        self.communicator.sendToServer(REGISTER)
        self.accessToken = self.communicator.readFromServer()
        self.communicator.sendToServer(DONE)

    def uploadFolder(self):
        self.connect()
        self.communicator.sendToServer(UPLOAD_FOLDER)
        self.communicator.sendToServer(self.accessToken)
        self.communicator.sendFolder(self.params[ARG_DIR])
        self.communicator.sendToServer(DONE)

    def connect(self):
        serverIp, serverPort = self.params[ARG_IP], int(self.params[ARG_PORT])
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.connect((serverIp, serverPort))
        self.communicator = ClientCommunicator(self.serverSocket)

    def startMonitoring(self):
        self.eventHandler = EventHandler()
        self.eventHandler.setTCPClient(self)
        self.monitor = FolderMonitor(self.params[ARG_DIR], self.eventHandler)
        self.monitor.start()


    def stopMonitoring(self):
        self.monitor.stopMonitoring()

    def updateServer(self, event):
        pass

    def shutdown(self):
        try:
            self.serverSocket.close()
        except Exception:
            print("oops")
