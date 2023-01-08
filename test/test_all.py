import unittest

from test import test_program

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(test_program.ParserTest))

    runner = unittest.TextTestRunner()
    runner.run(suite)
