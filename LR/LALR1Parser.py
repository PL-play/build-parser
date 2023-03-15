from LR.LR1Parser import LR1Parser


class LALR1Parser(LR1Parser):
    def __init__(self, bnf_file: str, eof: str = '$'):
        super().__init__(bnf_file, eof)
