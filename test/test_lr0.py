import unittest

from LR.LR0 import closure, Item0, LRState, goto, canonical_lr0_collection, first, follow, slr1_table
from LR.LR0Parser import LR0Parser


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

    def test3(self):
        items = []
        grammar = {
            "S": [["C", "C"]],
            "C": [["c", "C"], "d"],
        }
        items.append(Item0("S'", ("S",), 0))
        result = closure(items, grammar)
        init = LRState(0, (set(result)))

        states, trans_map = canonical_lr0_collection(init, grammar)
        print(states)
        print(trans_map)

    def test4(self):
        items = []
        grammar = {
            "S": [["C", "C"]],
            "C": [["c", "C"], "d"],
        }
        non_terminal = {"C", "S"}
        first_set = first(grammar, non_terminal)
        print('first set:', first_set)
        follow_set = follow(grammar, non_terminal, first_set)
        print('follow set:', follow_set)

        items.append(Item0("S'", ("S",), 0))
        result = closure(items, grammar)
        init = LRState(0, (set(result)))

        states, trans_map = canonical_lr0_collection(init, grammar)

        action_table, goto_table = slr1_table(states, trans_map, "S'", follow_set)
        print(action_table)
        print(goto_table)

    def test5(self):
        parser = LR0Parser('g5.bnf')
        action_table, goto_table = parser.slr1_table()
        print(action_table)
        print(goto_table)
