# Tokenizer class.
# Lazy pulls a token from a stream.
import re

spec = [
    # white space
    [r'^\s+', None],
    # comments,skip single line comments.
    [r'^\/\/.*', None],
    # skip multi line comments.
    [r'^\/\*[\s\S]*?\*\/', None],
    [r'^\d+', 'NUMBER'],
    [r'^"[^"]*"|^\'[^\']*\'', 'STRING'],
]


class Tokenizer:
    def __init__(self, string):
        self._string = string
        self._cursor = 0

    def get_next_token(self):
        """
        Obtain next token
        :return:
        """
        if not self.has_more_tokens():
            return None

        string = self._string[self._cursor:]

        for reg, token_type in spec:
            token = self.match(reg, string)
            # couldn't match rule,continue
            if token is None:
                continue

            # should skip token. e.g white space
            if token_type is None:
                return self.get_next_token()

            return {"type": token_type, "value": token}

        raise SyntaxError(f'Unexpected token:{string[0]}')

    # Whether still have more tokens.
    def has_more_tokens(self):
        return self._cursor < len(self._string)

    def is_eof(self):
        return len(self._string) == self._cursor

    def match(self, reg, string):
        m = re.search(reg, string)
        if m:
            token = m.group()
            self._cursor += len(token)
            return token
        return None
