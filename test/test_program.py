import unittest

from Parser import Parser


class ParserTest(unittest.TestCase):
    def test1(self):
        parser = Parser()
        print(parser.parse('42'))
