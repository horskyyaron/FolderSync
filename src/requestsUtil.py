import random
import string

REGISTER = 'REGISTER'
DONE = 'DONE'
UPLOAD_FOLDER = 'UPLOAD_FOLDER'
REQUEST_HANDLED = 'REQUEST_HANDLED'

SEPERATOR = '#######'

# MAX SIZE 10GB
MAX_MSG_SIZE = 10737418240
FORMAT = 'utf-8'


class MsgHandler:

    @staticmethod
    def addHeader(msg):
        prefix = MsgHandler.__calcZerosPrefix(msg)
        return prefix + bytes(msg, FORMAT)

    @staticmethod
    def __calcZerosPrefix(msg):
        maxSizeNumberOfDigits = len(str(MAX_MSG_SIZE))
        msgLenNumOfDigits = len(str(len(msg)))
        zeros = maxSizeNumberOfDigits - msgLenNumOfDigits
        prefix = b'0' * zeros + bytes(str(len(msg)), FORMAT)
        return prefix

    @staticmethod
    def msgLen(msg):
        return int(msg[:len(str(MAX_MSG_SIZE))])

    @staticmethod
    def msgData(msg):
        return msg[len(str(MAX_MSG_SIZE)):].decode(FORMAT)

    @staticmethod
    def decode(msg):
        return msg.decode(FORMAT)


def generateToken(size=128, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))


def sendFolderTo(destSocket, folder):
    destSocket.send(MsgHandler.addHeader("hello"))
    destSocket.send(MsgHandler.addHeader("my"))
    destSocket.send(MsgHandler.addHeader("name"))
    destSocket.send(MsgHandler.addHeader("is"))
    destSocket.send(MsgHandler.addHeader("yaron"))
    destSocket.send(MsgHandler.addHeader(DONE))
