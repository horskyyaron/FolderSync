import socket
from server import *
from requestsUtil import *

SERVER_PORT = 8091


class FakeRequestHandler(RequestHandler):
    def handleRequest(self, request, client_socket):
        if request == REGISTER:
            client_socket.send(MsgHandler.addHeader("123"))
            print("[REQUEST HANDLER]: %s request handled" % request)
        if request == UPLOAD_FOLDER:
            print("[REQUEST HANDLER]: please enter access token")
            msgSize = int(client_socket.recv(len(str(MAX_MSG_SIZE))))
            accessToken = MsgHandler.decode(client_socket.recv(msgSize))
            if accessToken == "123":
                print("[REQUEST HANDLER]: access approved!")
                print("[REQUEST HANDLER]: %s request handled" % request)



class FakeTCPServer(TCPServer):

    def __init__(self, port):
        super().__init__(port)
        self.stop = False
        self.request = None
        self.requestHandler = FakeRequestHandler()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', self.port))
        print("[FAKE SERVER]: started. listening on port", self.port)
        print("\n")
        server.listen(5)
        # server.settimeout(10)

        while not self.stop:
            try:
                self.curClient, client_address = server.accept()
                print("[FAKE SERVER]: client connected!")
                print("[FAKE SERVER]: waiting for client request")
                self.request = self.readFromClient()
                while self.request != DONE:
                    print("[CLIENT REQUEST]:", self.request)
                    self.requestHandler.handleRequest(self.request, self.curClient)
                    self.request = self.readFromClient()
                print("[FAKE SERVER]: closing client socket\n")
                self.curClient.close()
            except socket.timeout:
                continue

        print("[FAKE SERVER]: closing server.")
        server.close()

    def run(self):
        self.start_server()

    def stopServer(self):
        self.stop = True


server = FakeTCPServer(SERVER_PORT)
server.run()
