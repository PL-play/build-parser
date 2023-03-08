import copy

from util.BnfBuilder import BnfBuilder


class Item0:
    def __init__(self, lhs: str, rule: tuple, pos: int, eof_symbol: str = '$') -> None:
        self.lhs = lhs
        self.rule = rule if isinstance(rule, tuple) else tuple(rule)
        self.pos = pos
        self.eof_symbol = eof_symbol

    def peek_dot_right(self):
        if self.pos > len(self.rule) - 1:
            return self.eof_symbol
        return self.rule[self.pos]

    def move(self):
        if self.pos < len(self.rule):
            new_item = copy.deepcopy(self)
            new_item.pos += 1
            return new_item
        return None

    def __str__(self) -> str:
        s = [r for r in self.rule]
        s.insert(self.pos, '⊙')
        return f"{self.lhs}: {''.join(s)}"

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.lhs, self.rule, self.pos

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Item0):
            return self.__key() == other.__key()
        return False


class LRState:
    def __init__(self, name: int, items: set[Item0], eof_symbol: str = '$'):
        self.name = name if name is not None else 0
        self.items = items if items is not None else set()
        self.eof_symbol = eof_symbol

    def add_item(self, item: Item0):
        self.items.add(item)

    def add_items(self, items: set[Item0]):
        self.items = self.items.union(items)

    def set_name(self, name: int):
        self.name = name

    def next_symbols(self):
        return [s.peek_dot_right() for s in self.items if s.peek_dot_right() is not self.eof_symbol]

    def __str__(self) -> str:
        s = []
        for i in self.items:
            s.append(f"      {str(i)}\n")
        return f"state {self.name}:\n {' '.join(s)}\n"

    def __repr__(self):
        return self.__str__()


class LR0Parser:
    def __init__(self, bnf_file: str):
        self.bnf_file = bnf_file
        self.bnf_builder = BnfBuilder(bnf_file)
        self.bnf_builder.build()
        self.grammar = self.bnf_builder.production_map
