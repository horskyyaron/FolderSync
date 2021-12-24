import unittest
from hamcrest import *
from src.client import *


class MyTestCase(unittest.TestCase):
    def test_empty_msg(self):
        msg = MsgBuilder.addHeader("")
        assert_that(msg, is_(b"0"))


    def test_add_header(self):
        res = MsgBuilder.addHeader("hello")
        assert_that(res, is_(b'0' * (len(str(MAX_MSG_SIZE)) - 1) + b'5hello'))
        res = MsgBuilder.addHeader("yaron is my name")
        assert_that(res, is_(b'0' * (len(str(MAX_MSG_SIZE)) - 2) + b'16yaron is my name'))




if __name__ == '__main__':
    unittest.main()
