# Recursive descent implementation.
from Tokenizer import Tokenizer
from util.util import number


class Parser:

    def __init__(self):
        self._string = None
        self._tokenizer = None
        self._lookahead = None

    def parse(self, string):
        """
        Parse a string into an AST.

        :param string:
        :return: AST
        """
        self._string = string
        self._tokenizer = Tokenizer(self._string)
        # Prime the tokenizer to obtain the first token which is our lookahead.
        # The lookahead is used for predictive parsing.
        self._lookahead = self._tokenizer.get_next_token()

        # Parse recursively starting from the main entry point.
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
        token = self._eat('NUMBER')
        return {
            'type': 'NumericLiteral',
            'value': number(token.get('value'))
        }

    # Expects a token from given type
    def _eat(self, token_type):
        token = self._lookahead
        if token is None:
            raise SyntaxError(f'Unexpected end of input,expected: {token_type}')
        if token.get('type') != token_type:
            raise SyntaxError(f'Unexpected token:{token.get("value")},expected:{token_type}')

        # Advance to next token
        self._lookahead = self._tokenizer.get_next_token()
        return token
