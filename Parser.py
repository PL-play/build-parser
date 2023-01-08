# Recursive descent implementation.
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

    """
    Main entry point.

    Program
      : NumericLiteral
      ;

    """

    def program(self):
        return {'type': 'Program', 'body': self.numeric_literal()}

    def numeric_literal(self):
        return {
            'type': 'NumericLiteral',
            'value': self.number(self._string)
        }

    def number(self, x):
        # it may be already int or float
        if isinstance(x, (int, float)):
            return x
        # all int like strings can be converted to float so int tries first
        try:
            return int(x)
        except (TypeError, ValueError):
            pass
        try:
            return float(x)
        except (TypeError, ValueError):
            return None
