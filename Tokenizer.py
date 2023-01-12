# Tokenizer class.
# Lazy pulls a token from a stream.
from util.util import number


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
        if number(string[0]) is not None:
            number_token = ''
            while not self.is_eof() and number(string[self._cursor]) is not None:
                number_token = number_token + string[self._cursor]
                self._cursor += 1
            return {
                'type': 'NUMBER',
                'value': number_token
            }

        if string[0] == '"':
            string_token = ""
            string_token += string[self._cursor]
            self._cursor += 1
            while not self.is_eof() and string[self._cursor] != '"':
                string_token = string_token + string[self._cursor]
                self._cursor += 1
            string_token += string[self._cursor]
            self._cursor += 1
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
