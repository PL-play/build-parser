import re
import shlex
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

    def test3(self):
        text = "    {  afsdf zdfa asdf asdfa asdf {asdf} asdf () x*8} }"
        result = re.findall(r'\{(.*?)\}', text)
        print(result)

    def test4(self):
        text = "    {  afsdf zdfa asdf asdfa asdf {asdf} asdf () x*8  x }"
        text = text.strip()
        print(text[0], text[-1])
        print(text[1:-1])

    def test5(self):
        text = "  }  "
        test = text.rstrip()
        print(test)