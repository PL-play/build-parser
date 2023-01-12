# Tokenizer class.
# Lazy pulls a token from a stream.
import re


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
        match = r'^\d+'
        m = re.search(match, string)
        if m:
            number_token = m.group()
            self._cursor += len(number_token)
            return {
                'type': 'NUMBER',
                'value': number_token
            }
        match = r'^"[^"]*"'
        m = re.search(match, string)
        if m:
            string_token = m.group()
            self._cursor += len(string_token)
            return {
                'type': 'STRING',
                'value': string_token
            }
        return None

    # Whether still have more tokens.
    def has_more_tokens(self):
        return self._cursor < len(self._string)

    def is_eof(self):
        return len(self._string) == self._cursor
