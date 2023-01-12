# Recursive descent implementation.
from util import util


class Parser:

    def __init__(self):
        self._string = None

    def parse(self, string):
        """
        Parse a string into an AST.

        :param string:
        :return: AST
        """
        self._string = string
        return self.program()

    def program(self):
        """
        Main entry point.

        Program
            : NumericLiteral
            ;

        """
        return {'type': 'Program', 'body': self.numeric_literal()}

    def numeric_literal(self):
        """
        NumericalLiteral
            : Number
            ;
        :return:
        """
        return {
            'type': 'NumericLiteral',
            'value': util.number(self._string)
        }
