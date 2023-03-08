import unittest

from util.BnfBuilder import BnfBuilder


class LL1Test(unittest.TestCase):
    def test1(self):
        builder = BnfBuilder('g5.bnf')
        builder.build()
        print(builder.production_map)
        print(builder.terminals)
        print(builder.non_terminals)
        print(builder.start_symbol)
