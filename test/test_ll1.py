import unittest

from LL.LL1 import eliminateLeftRecursion


class LL1Test(unittest.TestCase):
    def test1(self):
        grammar = {
            'E': [['E', '+', "T"], 'T'],
            "T": [['T', "*", "F"], 'F'],
            'F': [['number'], ['(', 'E', ')']]

        }
        g = eliminateLeftRecursion(grammar)
        print(g)
