
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
        self.curClient.send(bytes(data, 'utf-8)'))

    def readFromClient(self):
        request = self.curClient.recv(1024).decode('utf-8')
        return request