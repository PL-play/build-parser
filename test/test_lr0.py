import unittest

from LR.LR0 import closure, Item0, LRState, goto


class LL1Test(unittest.TestCase):
    def test1(self):
        items = []
        grammar = {
            "S": [["C", "C"]],
            "C": [["c", "C"], "d"],
        }
        items.append(Item0("S'", ("S",), 0))
        result = closure(items, grammar)
        init = LRState()
        init.add_items(set(result))

        print(init)

    def test2(self):
        items = []
        grammar = {
            "S": [["C", "C"]],
            "C": [["c", "C"], "d"],
        }
        items.append(Item0("S'", ("S",), 0))
        result = closure(items, grammar)
        init = LRState(0, (set(result)))
        print(init)

        itmes1 = goto(init, "S", grammar)
        itmes2 = goto(init, "C", grammar)

        state1 = LRState(1, set(itmes1))

        state2 = LRState(2, set(itmes2))

        print(state1)
        print(state2)
