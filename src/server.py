import socket

from src.requestsUtil import *


class RequestHandler:
    def __init__(self, readFromClientMethod, sendToClientMethod):
        self.server = None
        self.requests = {REGISTER: self.register, UPLOAD_FOLDER: self.uploadFolder}
        self.client_socket = None
        self.read = readFromClientMethod
        self.send = sendToClientMethod

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
            print("[REQUEST HANDLER]: access approved!")
            data = self.read()
            while data != DONE:
                print(data)
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
        self.clients[accessToken] = (accessToken, deviceId)
