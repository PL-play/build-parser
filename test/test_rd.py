import unittest

from LL.RecursiveDecent import ExpressionEvaluator


class LL1Test(unittest.TestCase):
    def test1(self):
        text = '3 - 4*1 +(5/3)*2'

        token_exprs = [
            (r'[ \n\t]+', None),
            (r'#[^\n]*', None),
            (r'[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', 'NUMBER'),
            (r'\(', 'LPAREN'),
            (r'\)', 'RPAREN'),
            (r'\+', 'PLUS'),
            (r'\-', 'MINUS'),
            (r'\*', 'MULTIPLY'),
            (r'\/', 'DIVIDE'),
        ]
        eva = ExpressionEvaluator()
        result = eva.parse(text, token_exprs)
        print(result)
