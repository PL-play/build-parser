import copy

from LR.LR0Parser import LR0Parser, Item0, LRState


class Item1(Item0):
    def __init__(self, lhs: str, rule: tuple, pos: int, lookahead: str, eof_symbol: str = '$'):
        super().__init__(lhs, rule, pos, eof_symbol)
        self.lookahead = lookahead

    def __str__(self) -> str:
        s = [r for r in self.rule]
        s.insert(self.pos, ' . ')
        return f"{self.lhs} -> {''.join(s)}," + "{" + f"{','.join(self.lookahead)}" + "}"

    def __key(self):
        return self.lhs, self.rule, self.pos, self.lookahead

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Item1):
            return self.__key() == other.__key()
        return False

    def after_dot_next(self):
        if self.peek_dot_right() == self.eof_symbol:
            return [self.lookahead]
        else:
            return list(self.rule[self.pos + 1:]) + [self.lookahead]


class LR1Parser(LR0Parser):
    def __int__(self, bnf_file: str, eof: str = '$'):
        super().__init__(bnf_file, eof)

    def augment_grammar(self):
        old_start = self.bnf_builder.start_symbol
        new_start = old_start + "'"
        self.grammar[new_start] = [[old_start]]
        self.non_terminals.add(new_start)
        self.start_symbol = new_start
        self.first_set[new_start] = self.first_set[old_start]
        self.follow_set[new_start] = set(self.eof)
        self.init_state = LRState(0, (self.closure([Item1(f"{new_start}", (old_start,), 0, self.eof)])))
        self.grammar_list.insert(0, (new_start, (old_start,)))
        self.semantic_action.insert(0, None)

    def closure(self, items: list[Item1]) -> set[Item1]:
        """
        CLOSURE(I):
            J = I
            while CLOSURE(I) still changing:
                foreach LR(1) item A -> α▪Ββ,a in CLOSURE(I):
                    foreach B -> γ:
                        foreach terminal b in FIRST(βa):
                            add B -> ▪γ,b to J

            return J

        :param items:
        :return:
        """
        result = set(copy.deepcopy(items))
        is_change = True
        last_size = len(result)

        while is_change:
            new_items = set()
            for item in result:
                next_i = item.peek_dot_right()
                if self.is_non_terminal(next_i):
                    for rule in self.grammar[next_i]:
                        after_next = item.after_dot_next()
                        first = self.get_first(after_next)
                        for f in first:
                            i = Item1(next_i, rule, 0, f)
                            if i not in result:
                                new_items.add(i)
            result |= new_items
            if len(result) != last_size:
                is_change = True
                last_size = len(result)
            else:
                is_change = False

        return result

    def get_first(self, symbols: list[str]) -> set[str]:
        first_set = set()
        for s in symbols:
            first = self.first_set.get(s, set(s))
            if self.epsilon not in first:
                first_set |= first
                return first_set
            else:
                first_set |= first
                first_set.remove(self.epsilon)

        return first_set

    def lookahead_symbols(self, item: [Item1]):
        return [item.lookahead]
