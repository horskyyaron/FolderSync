import socket
from datetime import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from src.requestsUtil import *

ARG_IP = 0
ARG_PORT = 1
ARG_DIR = 2


class MsgHandler():

    @staticmethod
    def addHeader(msg):
        prefix = MsgHandler.__calcZerosPrefix(msg)
        return prefix + bytes(msg, 'utf-8')

    @staticmethod
    def __calcZerosPrefix(msg):
        maxSizeNumberOfDigits = len(str(MAX_MSG_SIZE))
        msgLenNumOfDigits = len(str(len(msg)))
        zeros = maxSizeNumberOfDigits - msgLenNumOfDigits
        prefix = b'0' * zeros + bytes(str(len(msg)), 'utf-8')
        return prefix

    @staticmethod
    def msgLen(msg):
        return int(msg[:len(str(MAX_MSG_SIZE))])

    @staticmethod
    def msgData(msg):
        return msg[len(str(MAX_MSG_SIZE)):].decode('utf-8')


class EventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print("something happened")


class FolderMonitor(FileSystemEventHandler):
    def __init__(self, folder):
        self.folder = folder
        self.eventHandler = EventHandler()

    def start(self):
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

    def shutdown(self):
        try:
            self.server.close()
        except Exception:
            print("oops")

    def uploadFolder(self):
        self.connect()
        self.sendToServer("UPLOAD_FOLDER")
        self.sendToServer(self.accessToken)
        self.sendToServer(DONE)

    def sendToServer(self, data):
        self.server.send(MsgHandler.addHeader(data))

    def readFromServer(self):
        response = self.server.recv(1024).decode('utf-8')
        return response

    def connect(self):
        serverIp, serverPort = self.params[ARG_IP], int(self.params[ARG_PORT])
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((serverIp, serverPort))
