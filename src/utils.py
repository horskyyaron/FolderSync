REGISTER = "register"


class ConnectionSystem:
    def __init__(self):
        self.connection = None

    def send(self, data):
        self.connection.send(bytes(data, 'utf-8'))

    def read(self):
        respond = self.connection.recv(1024).decode('utf-8')
        return respond
