from util.Lexer import Lexer, Token


class TokenGenerator:
    def __init__(self, file_path, token_expr):
        self.file_path = file_path
        self.reach_end = False
        file_object = open(self.file_path, 'r')
        self.lexer = Lexer(file_object.read(), token_expr)
        file_object.close()

    def next_token(self):
        if self.reach_end:
            raise AssertionError("File read completed")
        if self.lexer.has_next():
            return self.lexer.next()
        else:
            self.reach_end = True
            return Token('$', None)


class FileTokenGenerator(TokenGenerator):
    def __init__(self, file_path, token_expr):
        super(FileTokenGenerator, self).__init__()


class StringTokenGenerator(TokenGenerator):
    def __init__(self, file_path, token_expr):
        super().__init__(file_path, token_expr)
