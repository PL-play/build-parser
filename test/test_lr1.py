import unittest

from LR.LALR1Parser import LALR1Parser
from LR.LR0Parser import LR0Parser
from LR.LR1Parser import LR1Parser
from LR.SLR1Parser import SLR1Parser
from util.Lexer import Lexer, Token


class LR1Test(unittest.TestCase):
    def test1(self):
        parser = LR1Parser('g8.bnf')
        states, trans_map = parser.canonical_collection()
        parser.print_state(states, trans_map)
        action_table, goto_table = parser.build_parse_table()

    def test2(self):
        parser = LR1Parser('g9.bnf')
        states, trans_map = parser.canonical_collection()
        parser.print_state(states, trans_map)
        action_table, goto_table = parser.build_parse_table()

    def test3(self):
        parser = LR1Parser('g5.bnf')
        states, trans_map = parser.canonical_collection()
        parser.print_state(states, trans_map)
        action_table, goto_table = parser.build_parse_table()
        token_exprs = [
            (r'[ \n\t]+', None),
            (r'#[^\n]*', None),
            (r'[-]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', 'NUMBER'),
            (r'\(', '('),
            (r'\)', ')'),
            (r'\+', '+'),
            (r'\-', '-'),
            (r'\*', '*'),
            (r'\/', '/'),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),
        ]
        text = "1+2*3"
        lexer = Lexer(text, token_exprs)
        inputs = []
        while lexer.has_next():
            inputs.append(lexer.next())
        inputs.append(Token('$', '$'))

        parser.parse(inputs)

    def test4(self):
        bnf = 'g9.bnf'
        parsers = [LR0Parser(bnf), SLR1Parser(bnf), LALR1Parser(bnf), LR1Parser(bnf)]
        for p in parsers:
            try:
                p.canonical_collection()
                print("================")
                p.build_parse_table()
            except Exception as e:
                import traceback
                traceback.print_exc()
