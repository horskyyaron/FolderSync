import socket

from src.requestsUtil import *




class RequestHandler:
    def handleRequest(self, request, client_socket):
        if request == REGISTER:
            client_socket.send(MsgHandler.addHeader(generateAccessToken()))
            print("[REQUEST HANDLER]: %s request handled" % request)


class TCPServer:
    def __init__(self, port):
        self.port = port
        self.requestHandler = RequestHandler()
        self.curClient = None
        self.stop = False
        self.request = None

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', self.port))
        print("[SERVER]: started. listening on port", self.port)
        print("\n")
        server.listen(5)
        # server.settimeout(10)

        while not self.stop:
            try:
                self.curClient, client_address = server.accept()
                print("[SERVER]: client connected!")
                print("[SERVER]: waiting for client request")
                self.request = self.readFromClient()
                while self.request != DONE:
                    print("[CLIENT REQUEST]:", self.request)
                    self.requestHandler.handleRequest(self.request, self.curClient)
                    self.request = self.readFromClient()
                print("[SERVER]: closing client socket\n")
                self.curClient.close()
            except socket.timeout:
                continue

    def sendToClient(self, data):
        self.curClient.send(MsgHandler.addHeader(data))

    def readFromClient(self):
        requestSize = int(self.curClient.recv(len(str(MAX_MSG_SIZE))))
        request = self.curClient.recv(requestSize)
        return MsgHandler.decode(request)

    @classmethod
    def generateAccessToken(cls):
        return "123"
