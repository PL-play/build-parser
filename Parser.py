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
        return {"type": "Program", "body": self.literal()}

    def literal(self):
        """
        Literal
            : NumberLiteral
            | StringLiteral
            ;
        :return:
        """
        token_type = self._lookahead.get('type')
        if token_type == 'NUMBER':
            return self.numeric_literal()
        elif token_type == 'STRING':
            return self.string_literal()
        else:
            raise SyntaxError('Literal:unexpected literal production')

    def string_literal(self):
        """
        StringLiteral
            : STRING
            ;
        :return:
        """
        token = self._eat('STRING')
        return {
            "type": "StringLiteral",
            "value": token.get('value')[1:-1]
        }

    def numeric_literal(self):
        """
        NumericalLiteral
            : NUMBER
            ;
        :return:
        """
        token = self._eat('NUMBER')
        return {
            "type": "NumericLiteral",
            "value": number(token.get('value'))
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
