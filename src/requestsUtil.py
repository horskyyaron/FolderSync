import os
import random
import string

REGISTER = 'REGISTER'
DONE = 'DONE'
UPLOAD_FOLDER = 'UPLOAD_FOLDER'
REQUEST_HANDLED = 'REQUEST_HANDLED'

SEPERATOR = '#######'
FOLDER_TYPE = 'folder'
FILE_TYPE = 'file'

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


def sendFile(destSocket, filePath):
    destSocket.send(MsgHandler.addHeader("file bytes"))


def sendFolderTo(destSocket, folderPath):
    destSocket.send(MsgHandler.addHeader("root=" + folderPath))
    for root, dirs, files in os.walk(folderPath, topdown=True):
        for dir in dirs:
            destSocket.send(MsgHandler.addHeader(FOLDER_TYPE + SEPERATOR + root + "/" + dir))
        for file in files:
            destSocket.send(MsgHandler.addHeader(FILE_TYPE + SEPERATOR + root + "/" + file))
            sendFile(destSocket, root + "/" + file)
    destSocket.send(MsgHandler.addHeader(DONE))


class Parser:
    @staticmethod
    def convertClientPathToLocal(client, remotePath):
        noRootPrefixRemotePath = Parser.__removePrefix(remotePath, client.folderRoot)
        if noRootPrefixRemotePath[0] == "/":
            return client.folderLocalCopyRoot + noRootPrefixRemotePath
        else:
            return client.folderLocalCopyRoot + "/" + noRootPrefixRemotePath

    @staticmethod
    def __removePrefix(txt, prefix):
        return txt[len(prefix):] if txt.startswith(prefix) else txt
