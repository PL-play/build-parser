import unittest

from LR.LR1Parser import LR1Parser


class LR1Test(unittest.TestCase):
    def test1(self):
        parser = LR1Parser('g8.bnf')
        states, trans_map = parser.canonical_lr0_collection()
        parser.print_state(states, trans_map)
        action_table, goto_table = parser.build_parse_table()

    def test2(self):
        parser = LR1Parser('g9.bnf')
        states, trans_map = parser.canonical_lr0_collection()
        parser.print_state(states, trans_map)
        action_table, goto_table = parser.build_parse_table()

    def test3(self):
        parser = LR1Parser('g5.bnf')
        states, trans_map = parser.canonical_lr0_collection()
        parser.print_state(states, trans_map)
        action_table, goto_table = parser.build_parse_table()