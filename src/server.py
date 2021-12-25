import os
import socket

from src.requestsUtil import *

class RequestHandler:
    def __init__(self, readFromClientMethod, sendToClientMethod, client=None):
        self.server = None
        self.requests = {REGISTER: self.register, UPLOAD_FOLDER: self.uploadFolder}
        self.client_socket = None
        self.read = readFromClientMethod
        self.send = sendToClientMethod
        self.client = client

    def addServer(self, server):
        self.server = server

    def handleRequest(self, request_type, client_socket):
        self.client_socket = client_socket
        self.requests[request_type]()

    def register(self):
        accessToken = generateToken()
        deviceId = generateToken(size=5)
        self.server.addClient(accessToken, deviceId)
        self.send(accessToken)
        print("[REQUEST HANDLER]: %s request handled" % REGISTER)

    def uploadFolder(self):
        print("[REQUEST HANDLER]: please enter access token")
        accessToken = self.read()
        if accessToken in self.server.clients:
            self.client = self.server.clients[accessToken]
            print("[REQUEST HANDLER]: access approved!")
            print("[REQUEST HANDLER]: getting root folder path")
            data = self.read()
            clientRoot = data.split("root=")[1]
            print('[REQUEST HANDLER]: client root: ', clientRoot)
            self.client.setRoot(clientRoot)
            data = self.read()
            while data != DONE:
                dataType, remotePath = data.split(SEPERATOR)[0], data.split(SEPERATOR)[1]
                localPath = Parser.convertClientPathToLocal(self.client, remotePath)
                if dataType == FOLDER_TYPE:
                    os.mkdir(localPath)
                else:

                    file = self.read()
                    print(file)
                data = self.read()
            print("[REQUEST HANDLER]: %s request handled" % UPLOAD_FOLDER)
        else:
            print("[REQUEST HANDLER]: access token doesn't exists in the system, access denied.")


class TCPServer:
    def __init__(self, port):
        self.port = port
        self.requestHandler = RequestHandler(self.readFromClient, self.sendToClient)
        self.requestHandler.addServer(self)
        self.curClientSocket = None
        self.stop = False
        self.clients = {}

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', self.port))
        print("[SERVER]: started. listening on port", self.port)
        print("\n")
        server.listen(5)
        # server.settimeout(10)

        while not self.stop:
            try:
                self.curClientSocket, client_address = server.accept()
                print("[SERVER]: client connected!")
                print("[SERVER]: waiting for client request")
                request = self.readFromClient()
                while request != DONE:
                    print("[CLIENT REQUEST]:", request)
                    self.requestHandler.handleRequest(request, self.curClientSocket)
                    request = self.readFromClient()
                print("[SERVER]: closing client socket\n")
                self.curClientSocket.close()
            except socket.timeout:
                continue

    def sendToClient(self, data):
        self.curClientSocket.send(MsgHandler.addHeader(data))

    def readFromClient(self):
        request = self.curClientSocket.recv(self.__readRequestSize())
        return MsgHandler.decode(request)

    def __readRequestSize(self):
        return int(self.curClientSocket.recv(len(str(MAX_MSG_SIZE))))

    def addClient(self, accessToken, deviceId):
        clientFolderLocalCopy = "client_" + generateToken(size=5)
        os.mkdir(clientFolderLocalCopy)
        newClient = Client(accessToken, clientFolderLocalCopy)
        newClient.addDevice(Device(deviceId))
        self.clients[accessToken] = newClient


class Client:
    def __init__(self, accessToken, localCopyPath):
        self.accessToken = accessToken
        self.devices = []
        self.folderLocalCopyRoot = localCopyPath
        self.folderRoot = None

    def addDevice(self, device):
        self.devices.append(device)

    def setRoot(self, rootPath):
        self.folderRoot = rootPath


class Device:
    def __init__(self, id):
        self.id = id


