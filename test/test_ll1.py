import unittest

from LL.LL1 import eliminateLeftRecursion, first, follow, parsing_table, parse
from LL.Lexer import Lexer


class LL1Test(unittest.TestCase):
    def test1(self):
        grammar = {
            'E': [['E', '+', "T"], 'T'],
            "T": [['T', "*", "F"], 'F'],
            'F': [['number'], ['(', 'E', ')']]

        }
        g = eliminateLeftRecursion(grammar)
        print(g)

    def test2(self):
        token_exprs = [
            (r'[ \n\t]+', None),
            (r'#[^\n]*', None),
            (r'[-]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', 'NUMBER'),
            (r'\(', 'LPAREN'),
            (r'\)', 'RPAREN'),
            (r'\+', 'PLUS'),
            (r'\-', 'MINUS'),
            (r'\*', 'MULTIPLY'),
            (r'\/', 'DIVIDE'),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),
        ]
        text = '3.6 + 4   *   (2 - 1) / 5 * aa'
        lexer = Lexer(text, token_exprs)
        while lexer.has_next():
            tokens = lexer.next()
            print(tokens)
        # Output: [Token(INTEGER, 3), Token(PLUS, '+'), Token(INTEGER, 4), Token(MULTIPLY, '*'), Token(LPAREN, '('), Token(INTEGER, 2), Token(MINUS, '-'), Token(INTEGER, 1), Token(RPAREN, ')'), Token(DIVIDE, '/'), Token(INTEGER, 5)]

    def test3(self):
        token_exprs = [
            (r'[ \n\t]+', None),
            (r'#[^\n]*', None),
            (r'[-]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', 'NUMBER'),
            # (r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', 'NUMBER'),
            (r'\(', '('),
            (r'\)', ')'),
            (r'\+', '+'),
            (r'\-', '-'),
            (r'\*', '*'),
            (r'\/', '/'),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),
        ]
        grammar = {
            'E': [['T', "E'"]],
            "E'": [['+', 'T', "E'"], 'ε'],
            'T': [['F', "T'"]],
            "T'": [['*', 'F', "T'"], 'ε'],
            'F': [['NUMBER', ], ['(', 'E', ')']]

        }
        non_terminal = {'E', "E'", 'T', "T'", 'F'}
        start_symbol = 'E'
        first_set = first(grammar, non_terminal)
        print('first set:', first_set)
        follow_set = follow(grammar, non_terminal, first_set)
        print('follow set:', follow_set)

        table = parsing_table(grammar, first_set, follow_set)
        print('parsing table', table)

        text = '2'
        lexer = Lexer(text, token_exprs)
        inputs = []
        while lexer.has_next():
            inputs.append(lexer.next().type)
        print(inputs)
        accepted = parse(start_symbol, table, inputs)
        print(accepted)
