import os
import socket

from src.requestsUtil import *


class ServerCommunicator(BaseCommunicator):
    def __init__(self, clientSocket):
        super().__init__(clientSocket)

    def sendToClient(self, data):
        self.send(data)

    def readFromClient(self):
        return self.read()

class RequestHandler:
    def __init__(self, client=None):
        self.server = None
        self.requests = {REGISTER: self.register, UPLOAD_FOLDER: self.uploadFolder, CREATED: self.created}
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
            data = self.communicator.readFromClient()
            clientRoot = data.split("root=")[1]
            print('[REQUEST HANDLER]: client root: ', clientRoot)
            print('[REQUEST HANDLER]: uploading...')
            self.client.setRoot(clientRoot)
            data = self.communicator.readFromClient()
            while data != DONE:
                dataType, remotePath = data.split(SEPERATOR)[0], data.split(SEPERATOR)[1]
                localPath = Parser.convertClientPathToLocal(self.client, remotePath)
                if dataType == FOLDER_TYPE:
                    os.mkdir(localPath)
                else:
                    file = self.communicator.readFile()
                    self.communicator.saveFile(localPath, file)
                data = self.communicator.readFromClient()
            print('[REQUEST HANDLER]: uploading complete!')
            print("[REQUEST HANDLER]: %s request handled" % UPLOAD_FOLDER)
        else:
            print("[REQUEST HANDLER]: access token doesn't exists in the system, access denied.")

    def created(self):
        print("[REQUEST HANDLER]: please enter access token")
        accessToken = self.communicator.readFromClient()
        if accessToken in self.server.clients:
            print("[REQUEST HANDLER]: access approved!")
            self.client = self.server.clients[accessToken]
            data = self.communicator.readFromClient()
            while data != DONE:
                print(data)
                data = self.communicator.readFromClient()

            # os.mkdir(self.client.folderLocalCopyRoot + "/" + "newFolder")
        print("[REQUEST HANDLER]: %s request handled" % CREATED)



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
                while request != REQUEST_DONE:
                    print("[CLIENT REQUEST]:", request)
                    self.requestHandler.handleRequest(request)
                    request = communicator.readFromClient()
                print("[SERVER]: closing client socket\n")
                communicator.close()
            except socket.timeout:
                continue

    def getClient(self, accessToken):
        return self.clients[accessToken]

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
