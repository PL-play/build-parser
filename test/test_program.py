import re
import unittest

from Parser import Parser


class ParserTest(unittest.TestCase):
    def test1(self):
        parser = Parser()
        print(parser.parse('42'))

    def test2(self):
        parser = Parser()
        print(parser.parse('\'hello\''))

    def test3(self):
        match = r'^\d+'
        text = '23452'
        m = re.search(match, text)
        if m:
            print(m.group())
        else:
            print('not found')

    def test4(self):
        match = r'"[^"]*"'
        text = '"feaed"'
        m = re.search(match, text)
        if m:
            print(m.group())
        else:
            print('not found')

    def test5(self):
        parser = Parser()
        print(parser.parse('   \'hello\'   '))

    def test6(self):
        parser = Parser()
        print(parser.parse('  "   42  "   '))

    def test7(self):
        parser = Parser()
        print(parser.parse('     42     '))

    def test8(self):
        parser = Parser()
        print(parser.parse('''
            // comment
            42
        '''))

    def test9(self):
        parser = Parser()
        print(parser.parse('''
               /*
               * comment
               */
               42
           '''))
