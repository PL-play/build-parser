"""
BNF:
    expr ::= expr + term
         | expr - term
         | term
    term ::= term * factor
         | term / factor
         | factor
    factor ::= (expr)
         | NUMBER

EBNF:
    expr ::= term { (+|-) term }*
    term ::= factor { (*|/) factor }*
    factor ::= (expr)
           | NUMBER
"""
from LL.Lexer import Lexer
from util.util import number


class ExpressionEvaluatorEBNF:
    def __init__(self):
        self._text = None
        self._lexer = None
        self._lookahead = None

    def parse(self, string, token_expr):
        """
        :param string:
        :param token_expr:
        :return:
        """
        self._text = string
        self._lexer = Lexer(self._text, token_expr)
        self._lookahead = self._lexer.next()
        return self.expr()

    def parse_ast(self, string, token_expr):
        self._text = string
        self._lexer = Lexer(self._text, token_expr)
        self._lookahead = self._lexer.next()
        return self.expr_tree()

    def expr_tree(self):
        """
               expr ::= term { (+|-) term }*
               :return:
               """
        val = self.term_tree()
        while self._lookahead and (self._lookahead.type == 'PLUS' or self._lookahead.type == 'MINUS'):
            if self._lookahead.type == 'PLUS':
                self.eat('PLUS')
                right = self.term_tree()
                val = ('+', val, right)
            else:
                self.eat('MINUS')
                right = self.term_tree()
                val = ('-', val, right)
        return val

    def expr(self):
        """
        expr ::= term { (+|-) term }*
        :return:
        """
        val = self.term()
        while self._lookahead and (self._lookahead.type == 'PLUS' or self._lookahead.type == 'MINUS'):
            if self._lookahead.type == 'PLUS':
                self.eat('PLUS')
                right = self.term()
                val += right
            else:
                self.eat('MINUS')
                right = self.term()
                val -= right
        return val

    def term(self):
        """
        term ::= factor { (*|/) factor }*
        :return:
        """
        val = self.factor()
        while self._lookahead and (self._lookahead.type == 'MULTIPLY' or self._lookahead.type == 'DIVIDE'):
            if self._lookahead.type == 'MULTIPLY':
                self.eat('MULTIPLY')
                right = self.factor()
                val *= right
            else:
                self.eat('DIVIDE')
                right = self.factor()
                val /= right
        return val

    def term_tree(self):
        """
        term ::= factor { (*|/) factor }*
        :return:
        """
        val = self.factor_tree()
        while self._lookahead and (self._lookahead.type == 'MULTIPLY' or self._lookahead.type == 'DIVIDE'):
            if self._lookahead.type == 'MULTIPLY':
                self.eat('MULTIPLY')
                right = self.factor_tree()
                val = ('*', val, right)
            else:
                self.eat('DIVIDE')
                right = self.factor_tree()
                val = ('/', val, right)
        return val

    def factor(self):
        """
        factor ::= (expr)
                | NUMBER
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

    def factor_tree(self):
        """
        factor ::= (expr)
                | NUMBER
        :return:
        """
        token_type = self._lookahead.type if self._lookahead else None
        if token_type == 'NUMBER':
            val = self.eat('NUMBER')
            return number(val.value)
        elif token_type == 'LPAREN':
            self.eat('LPAREN')
            exprval = self.expr_tree()
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
