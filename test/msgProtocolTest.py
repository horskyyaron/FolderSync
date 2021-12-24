import unittest
from hamcrest import *
from src.client import *


class MyTestCase(unittest.TestCase):
    def test_empty_msg(self):
        msg = MsgHandler.addHeader("")
        assert_that(msg, is_(b"0"*len(str(MAX_MSG_SIZE))))


    def test_add_header(self):
        res = MsgHandler.addHeader("hello")
        assert_that(res, is_(b'0' * (len(str(MAX_MSG_SIZE)) - 1) + b'5hello'))
        res = MsgHandler.addHeader("yaron is my name")
        assert_that(res, is_(b'0' * (len(str(MAX_MSG_SIZE)) - 2) + b'16yaron is my name'))

    def test_msg_len(self):
        msg = MsgHandler.addHeader("hello")
        assert_that(5, is_(MsgHandler.msgLen(msg)))

        msg = MsgHandler.addHeader("yaron is my name")
        assert_that(16, is_(MsgHandler.msgLen(msg)))

    def test_msg_data(self):
        msg = MsgHandler.addHeader("hello")
        assert_that("hello", is_(MsgHandler.msgData(msg)))

        msg = MsgHandler.addHeader("yaron is my name")
        assert_that("yaron is my name", is_(MsgHandler.msgData(msg)))






if __name__ == '__main__':
    unittest.main()
