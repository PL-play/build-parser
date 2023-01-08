# Tokenizer class.
# Lazy pulls a token from a stream.
class Tokenizer:
    def __init__(self, string):
        self._string = string
        self._cursor = 0

    def get_next_token(self):
        if not self.has_more_tokens():
            return None

    # Whether still have more tokens.
    def has_more_tokens(self):
        return self._cursor < len(self._string)
