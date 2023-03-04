import re

# Define the regular expressions for each token type
TOKEN_REGEX = [
    ('NUMBER', r'\d+(\.\d+)?'),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('MULTIPLY', r'\*'),
    ('DIVIDE', r'/'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
]


# Define the Token class to hold each token's type and value
class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value

    def __repr__(self):
        return f'Token({self.type}, {self.value})'


# Define the Lexer class to tokenize the input text
class Lexer:
    def __init__(self, input, token_exprs):
        self.input = input
        self.pos = 0
        self.token_exprs = token_exprs
        self.cached_tokens = []
        self.current_token = None

    def _get_next_token(self):
        if self.pos >= len(self.input):
            return None
        for token_expr in self.token_exprs:
            pattern, tag = token_expr
            regex = re.compile(pattern)
            match = regex.match(self.input, self.pos)
            if match:
                text = match.group(0)
                if tag:
                    token = Token(tag, text)
                    self.pos = match.end(0)
                    return token
                else:
                    self.pos = match.end(0)
                    continue
        else:
            raise ValueError('Illegal character: %s' % self.input[self.pos])

    def next(self):
        if self.cached_tokens:
            return self.cached_tokens.pop()
        token = self._get_next_token()
        return token

    def putback(self, token):
        self.cached_tokens.append(token)

    def has_next(self):
        if self.cached_tokens:
            return True
        try:
            token = self._get_next_token()
            if token:
                self.putback(token)
                return True
            else:
                return False
        except ValueError:
            return False
