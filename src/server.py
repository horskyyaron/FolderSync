from src.requestsUtil import *


class RequestHandler:
    def handleRequest(self, request, client_socket):
        pass


class TCPServer:
    def __init__(self, port):
        self.port = port
        self.requestHandler = RequestHandler()
        self.curClient = None

    def run(self):
        pass

    def sendToClient(self, data):
        self.curClient.send(MsgHandler.addHeader(data))

    def readFromClient(self):
        requestSize = int(self.curClient.recv(len(str(MAX_MSG_SIZE))))
        request = self.curClient.recv(requestSize)
        return MsgHandler.decode(request)
