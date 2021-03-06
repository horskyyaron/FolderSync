import os
import socket

from src.util import *


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
        self.requests = {REGISTER: self.register, UPLOAD_FOLDER: self.uploadFolder,
                         CREATED: self.created, DELETED: self.deleted, MOVED: self.moved}
        self.communicator = None
        self.client = client

    def setCommunicator(self, communicator):
        self.communicator = communicator

    def addServer(self, server):
        self.server = server

    def handleRequest(self, request_type):
        self.requests[request_type]()

    def register(self):
        clientRoot = self.communicator.readFromClient()
        accessToken = generateToken()
        deviceId = generateToken(size=5)
        self.server.addClient(accessToken, deviceId, clientRoot)
        self.communicator.sendToClient(accessToken)
        print("[REQUEST HANDLER]: %s request handled" % REGISTER)

    def __isAccessApproved(self):
        print("[REQUEST HANDLER]: please enter access token")
        client_accessToken = self.communicator.readFromClient()
        if self.server.isClientExists(client_accessToken):
            self.client = self.server.getClient(client_accessToken)
            print("[REQUEST HANDLER]: access approved!")
            return True
        else:
            print("[REQUEST HANDLER]: client token doesn't exists, access DENIED!")
            return False

    def __printRequestCompletedMsg(self, request):
        print("[REQUEST HANDLER]: %s request handled" % request)

    def uploadFolder(self):
        if self.__isAccessApproved():
            print('[REQUEST HANDLER]: client root: ', self.client.folderPathOnClientDevice)
            print('[REQUEST HANDLER]: uploading...')
            msg = self.communicator.readFromClient()
            while msg != DONE:
                dataType, remotePath = msg.split(SEPERATOR)[0], msg.split(SEPERATOR)[1]
                localPath = Parser.convertClientPathToLocal(self.client, remotePath)
                if dataType == FOLDER_TYPE:
                    os.mkdir(localPath)
                else:
                    file = self.communicator.readFile()
                    self.communicator.saveFile(localPath, file)
                msg = self.communicator.readFromClient()
            self.__printRequestCompletedMsg(UPLOAD_FOLDER)

    def created(self):
        if self.__isAccessApproved():
            msg = self.communicator.readFromClient()
            while msg != DONE:
                event = Parser.convertMsgToEvent(msg)
                if event.is_directory:
                    print("[SERVER]: new FOLDER created on client, updating local copy... creating new file",
                          Parser.convertClientPathToLocal(self.client, event.src_path))
                    os.mkdir(Parser.convertClientPathToLocal(self.client, event.src_path))
                else:
                    file = self.communicator.readFile()
                    localPath = Parser.convertClientPathToLocal(self.client, event.src_path)
                    print("[SERVER]: new FILE on client, updating local copy... creating new file", localPath)
                    self.communicator.saveFile(localPath, file)
                msg = self.communicator.readFromClient()
            self.__printRequestCompletedMsg(CREATED)

    def deleted(self):
        if self.__isAccessApproved():
            msg = self.communicator.readFromClient()
            while msg != DONE:
                event = Parser.convertMsgToEvent(msg)
                localPath = Parser.convertClientPathToLocal(self.client, event.src_path)
                if event.is_directory:
                    print("[SERVER]: folder DELETED on client, updating local copy... deleting", localPath)
                    if FileSystemUtils.isEmpty(localPath):
                        print("deleted empty folder")
                    else:
                        print("deleted non-empty folder")
                    FileSystemUtils.deleteDir(localPath)
                else:
                    print("[SERVER]: file DELETED on client, updating local copy... deleting", localPath)
                    os.remove(localPath)
                msg = self.communicator.readFromClient()
            self.__printRequestCompletedMsg(DELETED)

    def moved(self):
        if self.__isAccessApproved():
            msg = self.communicator.readFromClient()
            while msg != DONE:
                event = Parser.convertMsgToEvent(msg)
                localPath_src = Parser.convertClientPathToLocal(self.client, event.src_path)
                localPath_dst = Parser.convertClientPathToLocal(self.client, event.dest_path)
                if event.is_directory:
                    self.__folderMoved(localPath_src, localPath_dst)
                else:
                    self.__fileMoved(localPath_src, localPath_dst)
                msg = self.communicator.readFromClient()
            self.__printRequestCompletedMsg(MOVED)

    def __fileMoved(self, src, dst):
        os.replace(src, dst)
        print("[SERVER]: moved file from {} to {}".format(src, dst))

    def __folderMoved(self, src, dst):
        folder_status = self.communicator.readFromClient()
        if folder_status == EMPTY_FOLDER:
            os.replace(src, dst)
        else:
            FileSystemUtils.moveFolder(src, dst)
        print("[SERVER]: moved {} from {} to {}".format(folder_status, src, dst))


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

    def getClientFolder(self, accessToken):
        return self.clients[accessToken].folder

    def isClientExists(self, client_accessToken):
        return client_accessToken in self.clients.keys()

    def addClient(self, accessToken, deviceId, folderPathOnClientDevice):
        clientFolder = "client_" + generateToken(size=5)
        os.mkdir(clientFolder)
        newClient = Client(accessToken, clientFolder)
        newClient.addDevice(Device(deviceId))
        newClient.folderPathOnClientDevice = folderPathOnClientDevice
        self.clients[accessToken] = newClient


class Client:
    def __init__(self, accessToken, path):
        self.accessToken = accessToken
        self.devices = []
        self.folder = path
        self.folderPathOnClientDevice = None

    def addDevice(self, device):
        self.devices.append(device)


class Device:
    def __init__(self, id):
        self.id = id
