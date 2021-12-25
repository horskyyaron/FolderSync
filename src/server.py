import os
import socket

from src.requestsUtil import *


class ServerCommunicator:
    def __init__(self, clientSocket):
        self.clientSocket = clientSocket

    def sendToClient(self, data):
        self.clientSocket.send(MsgHandler.addHeader(data))

    def readFromClient(self):
        request = self.clientSocket.recv(self.__readRequestSize())
        return MsgHandler.decode(request)

    def __readRequestSize(self):
        return int(self.clientSocket.recv(len(str(MAX_MSG_SIZE))))

    def close(self):
        self.clientSocket.close()


class RequestHandler:
    def __init__(self, client=None):
        self.server = None
        self.requests = {REGISTER: self.register, UPLOAD_FOLDER: self.uploadFolder}
        self.communicator = None

    def setCommunicator(self, communicator):
        self.communicator = communicator

    def addServer(self, server):
        self.server = server

    def handleRequest(self, request_type):
        self.requests[request_type]()

    def register(self):
        accessToken = generateToken()
        deviceId = generateToken(size=5)
        self.server.addClient(accessToken, deviceId)
        self.communicator.sendToClient(accessToken)
        print("[REQUEST HANDLER]: %s request handled" % REGISTER)

    def uploadFolder(self):
        print("[REQUEST HANDLER]: please enter access token")
        accessToken = self.communicator.readFromClient()
        if accessToken in self.server.clients:
            self.client = self.server.clients[accessToken]
            print("[REQUEST HANDLER]: access approved!")
            print("[REQUEST HANDLER]: getting root folder path")
            data = self.communicator.readFromClient()
            clientRoot = data.split("root=")[1]
            print('[REQUEST HANDLER]: client root: ', clientRoot)
            self.client.setRoot(clientRoot)
            data = self.communicator.readFromClient()
            while data != DONE:
                dataType, remotePath = data.split(SEPERATOR)[0], data.split(SEPERATOR)[1]
                localPath = Parser.convertClientPathToLocal(self.client, remotePath)
                if dataType == FOLDER_TYPE:
                    os.mkdir(localPath)
                else:
                    file = self.communicator.readFromClient()
                    print(file)
                data = self.communicator.readFromClient()
            print("[REQUEST HANDLER]: %s request handled" % UPLOAD_FOLDER)
        else:
            print("[REQUEST HANDLER]: access token doesn't exists in the system, access denied.")


class TCPServer:
    def __init__(self, port):
        self.port = port
        self.requestHandler = RequestHandler()
        self.requestHandler.addServer(self)
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
                client_socket, client_address = server.accept()
                communicator = ServerCommunicator(client_socket)
                self.requestHandler.setCommunicator(communicator)
                print("[SERVER]: client connected!")
                print("[SERVER]: waiting for client request")
                request = communicator.readFromClient()
                while request != DONE:
                    print("[CLIENT REQUEST]:", request)
                    self.requestHandler.handleRequest(request)
                    request = communicator.readFromClient()
                print("[SERVER]: closing client socket\n")
                communicator.close()
            except socket.timeout:
                continue

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
