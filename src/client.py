import socket
import threading
from datetime import time
from watchdog.events import *
from watchdog.observers import Observer
from src.util import *

ARG_IP = 0
ARG_PORT = 1
ARG_DIR = 2


class EventHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.events = []
        self.tcpClient = None

    def setTCPClient(self, client):
        self.tcpClient = client

    def on_any_event(self, event):
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
        self.communicator = None
        self.eventHandler = None

    def register(self):
        self.connect()
        self.communicator.sendToServer(REGISTER)
        self.communicator.sendToServer(self.params[ARG_DIR])
        self.accessToken = self.communicator.readFromServer()
        self.communicator.sendToServer(REQUEST_DONE)
        self.disconnect()

    def uploadFolder(self):
        self.connect()
        self.communicator.sendToServer(UPLOAD_FOLDER)
        self.communicator.sendToServer(self.accessToken)
        self.communicator.sendFolder(self.params[ARG_DIR])
        self.communicator.sendToServer(REQUEST_DONE)
        self.disconnect()

    def connect(self):
        serverIp, serverPort = self.params[ARG_IP], int(self.params[ARG_PORT])
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.connect((serverIp, serverPort))
        self.communicator = ClientCommunicator(serverSocket)

    def startMonitoring(self):
        self.eventHandler = EventHandler()
        self.eventHandler.setTCPClient(self)
        self.monitor = FolderMonitor(self.params[ARG_DIR], self.eventHandler)
        self.monitor.start()

    def stopMonitoring(self):
        self.monitor.stopMonitoring()

    def updateServer(self, event):
        if event.event_type.upper() == CREATED.upper():
            self.createdUpdate(event)
        if event.event_type.upper() == DELETED.upper():
            self.deletedUpdate(event)

    def disconnect(self):
        self.communicator.disconnect()

    def createdUpdate(self, event):
        self.connect()
        self.communicator.sendToServer(CREATED)
        self.communicator.sendToServer(self.accessToken)
        self.communicator.sendToServer(Parser.convertEventToMsg(event))
        if not event.is_directory:
            self.communicator.sendFile(event.src_path)
        self.communicator.sendToServer(DONE)
        self.communicator.sendToServer(REQUEST_DONE)
        self.disconnect()

    def deletedUpdate(self, event):
        self.connect()
        self.communicator.sendToServer(DELETED)
        self.communicator.sendToServer(self.accessToken)
        self.communicator.sendToServer(Parser.convertEventToMsg(event))
        self.communicator.sendToServer(DONE)
        self.communicator.sendToServer(REQUEST_DONE)
        self.disconnect()
