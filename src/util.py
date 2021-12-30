import filecmp
import os
import random
import string
from time import sleep
from watchdog.events import *

REGISTER = 'REGISTER'
DONE = 'DONE'
REQUEST_DONE = 'REQUEST_DONE'
UPLOAD_FOLDER = 'UPLOAD_FOLDER'
CREATED = 'CREATED'
DELETED = 'DELETED'
MOVED = 'MOVED'
REQUEST_HANDLED = 'REQUEST_HANDLED'

SEPERATOR = '#######'
FOLDER_TYPE = 'folder'
FILE_TYPE = 'file'

# MAX SIZE 10GB
MAX_MSG_SIZE = 10737418240
READING_SPEED_FACTOR = 40
FORMAT = 'utf-8'


class MsgHandler:

    @staticmethod
    def addHeader(msg, msg_in_bytes=False):
        prefix = MsgHandler.__calcZerosPrefix(msg)
        if msg_in_bytes:
            return prefix + msg
        else:
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


class BaseCommunicator:
    def __init__(self, destSocket):
        self.destSocket = destSocket

    def sendFolder(self, folderPath):
        for root, dirs, files in os.walk(folderPath, topdown=True):
            for dir in dirs:
                self.destSocket.send(MsgHandler.addHeader(FOLDER_TYPE + SEPERATOR + root + "/" + dir))
            for file in files:
                self.destSocket.send(MsgHandler.addHeader(FILE_TYPE + SEPERATOR + root + "/" + file))
                self.sendFile(root + "/" + file)
        self.destSocket.send(MsgHandler.addHeader(DONE))

    def send(self, data, msg_in_bytes=False):
        self.destSocket.send(MsgHandler.addHeader(data, msg_in_bytes))

    def read(self, read_in_bytes=False):
        request = self.destSocket.recv(self.__readRequestSize())
        if read_in_bytes:
            return request
        return MsgHandler.decode(request)

    def __readRequestSize(self):
        return int(self.destSocket.recv(len(str(MAX_MSG_SIZE))))

    def close(self):
        self.destSocket.close()

    def sendFile(self, path):
        length = os.path.getsize(path)
        self.send(str(length))

        with open(path, "rb") as f:
            data = f.read(1024 * READING_SPEED_FACTOR)
            while data:
                self.send(data, msg_in_bytes=True)
                # for testing purposes
                sleep(0.002)
                data = f.read(1024 * READING_SPEED_FACTOR)

    def readFile(self):
        fileSize = int(self.read())
        current_size = 0
        buffer = b""
        while current_size < fileSize:
            data = self.read(read_in_bytes=True)
            if not data:
                break
            if len(data) + current_size > fileSize:
                data = data[:fileSize - current_size]
            buffer += data
            current_size += len(data)
        return buffer

    def saveFile(self, path, data):
        with open(path, "wb") as f:
            f.write(data)

    def disconnect(self):
        self.destSocket.close()


class Parser:
    @staticmethod
    def convertClientPathToLocal(client, remotePath):
        noRootPrefixRemotePath = Parser.__removePrefix(remotePath, client.folderRoot)
        if noRootPrefixRemotePath[0] == "/":
            return client.folderLocalCopyRoot + noRootPrefixRemotePath
        else:
            return client.folderLocalCopyRoot + "/" + noRootPrefixRemotePath

    @staticmethod
    def convertEventToMsg(event):
        dest_path = None
        try:
            dest_path = event.dest_path
        except AttributeError:
            dest_path = ""
        return str(event.event_type) + "," + str(event.src_path) + "," + str(event.is_directory) + "," + str(dest_path)

    @staticmethod
    def convertMsgToEvent(msg):
        params = msg.split(',')
        return Event(params[0], params[1], params[2], params[3])

    @staticmethod
    def __removePrefix(txt, prefix):
        return txt[len(prefix):] if txt.startswith(prefix) else txt


class Event:
    def __init__(self, event_type, src_path, is_directory, dest_path):
        self.event_type = event_type
        self.src_path = src_path
        self.is_directory = False if is_directory == 'False' else True
        self.dest_path = dest_path


class FileSystemUtils:
    @staticmethod
    def areDirsIdentical(dir1, dir2):
        res = filecmp.dircmp(dir1, dir2)
        if len(res.left_only) > 0 or len(res.right_only) > 0:
            return False
        else:
            match, mismatch, errors = filecmp.cmpfiles(dir1, dir2, res.common_files)
            if len(match) != len(res.common_files):
                return False
            if res.common_dirs:
                for com_dir in res.common_dirs:
                    if not FileSystemUtils.areDirsIdentical(dir1 + "/" + com_dir, dir2 + "/" + com_dir):
                        return False
            return True

    @staticmethod
    def deleteDir(path):
        for root, dirs, files in os.walk(path, topdown=True):
            for dir in dirs:
                if FileSystemUtils.isEmpty(root + "/" + dir):
                    os.rmdir(root + "/" + dir)
                else:
                    FileSystemUtils.deleteDir(root + "/" + dir)
            for file in files:
                os.remove(root + "/" + file)
            os.rmdir(root)

    @staticmethod
    def deleteFile(path):
        os.remove(path)

    @staticmethod
    def isEmpty(dirPath):
        return len(os.listdir(dirPath)) == 0

    @staticmethod
    def exists(path):
        try:
            os.listdir(path)
            return True
        except NotADirectoryError:
            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def move(src, dst):
        os.replace(src, dst)

    @staticmethod
    def createFolder(path):
        os.mkdir(path)

    @staticmethod
    def createFile(path, data=""):
        with open(path, "w") as f:
            f.write(data)
