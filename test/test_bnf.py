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

    def test2(self):
        builder = BnfBuilder('g5.bnf')
        builder.build()
        print(builder.semantic_action)
        semantic_action = builder.semantic_action[0].strip()[1:-1].strip()
        print(semantic_action)

        v = {"p1": 2, "p2": "+", "p3": 5, "result": None}
        exec(semantic_action, v)
        print(v.get('result'))
