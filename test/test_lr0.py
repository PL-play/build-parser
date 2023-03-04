import unittest

from LR.LR0 import closure, Item0, LRState


class LL1Test(unittest.TestCase):
    def test1(self):
        items = []
        grammar = {
            "S": [["C", "C"]],
            "C": [["c", "C"], "d"],
        }
        items.append(Item0("S'", ["S"], 0))
        result = closure(items, grammar)
        init = LRState()
        init.add_items(result)

        print(init)
