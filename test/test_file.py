import unittest


class LL1Test(unittest.TestCase):
    def test1(self):
        f = open('f6', "r")
        # points at the start
        print(f.tell())
        f.close()

    def test2(self):
        f = open("f6", "r")
        # read a line
        print(f.readline())
        # points after reading a line
        print(f.tell())
        f.close()
