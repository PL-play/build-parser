"""
BNF:
 expression : expression + term
               | expression - term
               | term

 term : term * factor
            | term / factor
            | factor

 factor     : NUMBER
            | ( expression )

REMOVE LEFT RECURSION

    E -> TE'
    E' -> +TE'|-TE'|ε

    T -> FT'
    T' -> *FT'|/FT'|ε

    F -> NUMBER|(E)
"""

from util.Lexer import Lexer
from util.util import number


class ExpressionEvaluator:
    def __init__(self):
        self._text = None
        self._lexer = None
        self._lookahead = None

    def parse(self, string, token_expr):
        """
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
        ]

        :param string:
        :param token_expr:
        :return:
        """
        self._text = string
        self._lexer = Lexer(self._text, token_expr)
        self._lookahead = self._lexer.next()
        return self.expr()

    def expr(self):
        """
         E -> TE'
        :return:
        """
        val = self.term()
        return self.expr_(val)

    def expr_(self, lvalue):
        """
        E' -> +TE'|-TE'|ε
        :return:
        """
        token_type = self._lookahead.type if self._lookahead else None
        if token_type == 'PLUS':
            self.eat('PLUS')
            val = lvalue + self.term()
            return self.expr_(val)
        elif token_type == 'MINUS':
            self.eat('MINUS')
            val = lvalue - self.term()
            return self.expr_(val)
        else:
            return lvalue

    def term(self):
        """
         T -> FT'
        :return:
        """
        val = self.factor()
        return self.term_(val)

    def term_(self, lvalue):
        """
        T' -> *FT'|/FT'|ε
        :return:
        """
        token_type = self._lookahead.type if self._lookahead else None
        if token_type == 'MULTIPLY':
            self.eat('MULTIPLY')
            val = lvalue * self.factor()
            return self.term_(val)
        elif token_type == 'DIVIDE':
            self.eat('DIVIDE')
            val = lvalue / self.factor()
            return self.term_(val)
        else:
            return lvalue

    def factor(self):
        """
         F -> NUMBER|(E)
        :return:
        """
        token_type = self._lookahead.type if self._lookahead else None
        if token_type == 'NUMBER':
            val = self.eat('NUMBER')
            return number(val.value)
        elif token_type == 'LPAREN':
            self.eat('LPAREN')
            exprval = self.expr()
            self.eat('RPAREN')
            return exprval
        else:
            raise SyntaxError(f'Unexpected token:{token_type}')

    def eat(self, token_type):
        token = self._lookahead
        if token is None:
            raise SyntaxError(f'Unexpected end of input,expected: {token_type}')
        if token.type != token_type:
            raise SyntaxError(f'Unexpected token:{token.value},expected:{token_type}')

        self._lookahead = self._lexer.next()
        return token
