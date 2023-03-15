import unittest

from LR.LR0Parser import LR0Parser, Item0, LRState
from LR.SLR1Parser import SLR1Parser
from util.Lexer import Lexer, Token


class SLR1Test(unittest.TestCase):

    def test5(self):
        parser = SLR1Parser('g5.bnf')
        parser.canonical_collection()
        action_table, goto_table = parser.build_parse_table()

    def test6(self):
        parser = SLR1Parser('g5.bnf')
        parser.canonical_collection()
        parser.build_parse_table()
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
        text = "1+3*4"
        lexer = Lexer(text, token_exprs)
        inputs = []
        while lexer.has_next():
            inputs.append(lexer.next())
        inputs.append(Token('$', '$'))

        parser.parse(inputs)

    def test7(self):
        parser = SLR1Parser('g7.bnf')
        parser.canonical_collection()
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