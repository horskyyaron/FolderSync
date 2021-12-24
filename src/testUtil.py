import threading
import socket
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from server import *
from requestsUtil import *

SERVER_PORT = 8090


class FakeRequestHandler(RequestHandler):
    def handleRequest(self, request, client_socket):
        if request == REGISTER:
            client_socket.send(b"123")
            print("[REQUEST HANDLER]: %s request handled" % request)
        if request == UPLOAD_FOLDER:
            if client_socket.recv(1024).decode('utf-8') == '123':
                print("[SERVER]: access confirmed")
                print("uploading folder...")




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


class FakeFolderMonitor:
    def __init__(self, folder, eventHandler):
        self.folder = folder
        self.eventHandler = eventHandler

    def monitorOnDifThread(self):
        print("thread:", threading.currentThread())
        print("[CLIENT]: monitoring...")
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

    def start(self):
        # Start the server in a new thread
        daemon = threading.Thread(name='monitor thread',
                                  target=self.monitorOnDifThread)
        daemon.setDaemon(True)  # Set as a daemon so it will be killed once the main thread is dead.
        daemon.start()


class FakeEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print("something happened")


server = FakeTCPServer(SERVER_PORT)
server.run()
