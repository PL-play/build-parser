import unittest

from LR.LALR1Parser import LALR1Parser
from util.Lexer import Lexer, Token


class LR1Test(unittest.TestCase):
    def test1(self):
        parser = LALR1Parser('g9.bnf')
        states, trans_map = parser.canonical_collection()

        parser.print_state(states, trans_map)
        action_table, goto_table = parser.build_parse_table()

    def test2(self):
        parser = LALR1Parser('g7.bnf')
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