import shlex


class BNF:
    def __init__(self):
        pass


class BnfBuilder:
    def __init__(self, bnf_path: str, prod_delimiter: str = ':', or_delimiter: str = '|', epsilon: str = 'ε',
                 comment_symbol: str = '//') -> None:
        self.bnf_path = bnf_path
        self.prod_delimiter = prod_delimiter
        self.or_delimiter = or_delimiter
        self.production_map = {}
        self.non_terminals = set()
        self.terminals = set()
        self.symbols = set()
        self.epsilon = epsilon
        self.current_non_terminal = None
        self.start_symbol = None
        self.comment_symbol = comment_symbol
        self.current_line = None

    def build(self):
        file = open(self.bnf_path, "r")
        line = file.readline()
        while line:
            self.current_line = line
            self.build_production(shlex.split(line))
            line = file.readline()
        file.close()
        self.terminals = self.symbols - self.non_terminals

    def _find_index(self, p: list, item) -> int:
        for index, s in enumerate(p):
            if s == item:
                return index
        return -1

    def build_production(self, p):
        if not p:
            return
        if p[0] == self.comment_symbol:
            return
        d_index = self._find_index(p, self.prod_delimiter)
        if d_index == -1:
            if not self.current_non_terminal:
                raise AssertionError(f'No lhs found in "{self.current_line}"')
            if p[0] != self.or_delimiter:
                raise AssertionError(f"expect '{self.or_delimiter}' for this line")
            if len(p) == 1:
                self.production_map[self.current_non_terminal].append([self.epsilon])
            else:
                self.production_map[self.current_non_terminal].append(p[1:])
        else:
            if d_index != 1:
                raise AssertionError(f"production delimiter must be after lhs: {self.current_line}")
            if len(p) <= 2:
                raise AssertionError(f"no rhs found in :{self.current_line}")
            else:
                self.current_non_terminal = p[0]
                self.production_map[p[0]] = [p[2:]]
                self.non_terminals.add(p[0])
                if not self.start_symbol:
                    self.start_symbol = p[0]

        for s in p:
            if s != self.epsilon and s != self.or_delimiter and s != self.prod_delimiter:
                self.symbols.add(s)

    def is_terminal(self, symbol: str) -> bool:
        return symbol in self.terminals

    def is_non_terminal(self, symbol: str) -> bool:
        return symbol in self.non_terminals

    def is_epsilon(self, symbol: str) -> bool:
        return symbol == self.epsilon

    def start_symbol(self) -> str:
        return self.start_symbol
