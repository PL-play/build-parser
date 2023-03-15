from LR.LR0Parser import LR0Parser, Item0


class SLR1Parser(LR0Parser):
    def __init__(self, bnf_file: str, eof: str = '$'):
        super().__init__(bnf_file, eof)

    def lookahead_symbols(self, item: [Item0]):
        return self.follow_set[item.lhs]
