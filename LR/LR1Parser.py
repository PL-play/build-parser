import copy

from graphviz import Digraph

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
    def __init__(self, bnf_file: str, eof: str = '$'):
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

    def graph_state(self, states: list[LRState], trans: dict[tuple:int], acton_table: dict):
        dot = Digraph("state transaction", node_attr={'shape': 'box'}, engine='neato')
        # dot.attr(rankdir='LR')
        # dot.attr(splines='ortho')
        # true则用样条曲线画边，polyline则用折线，ortho则用垂直或水平的折线，false或line则线段，dot默认true，其它默认false。
        dot.attr(splines='true')
        # dot.attr(overlap="false")
        # 若结点相交，mode为”false”时调整结点，mode为”scale”时放大布局，mode为”true”时容许相交（默认）（用于twopi）
        dot.attr(overlap="false")
        # dot.attr(size='10,10')

        conflict_states = set()
        acc_from_node = None
        for k in acton_table:
            if isinstance(acton_table[k], list):
                conflict_states.add(k[0])
            if acton_table[k] == ('acc',):
                dot.node(f"acc", 'accept', color='green')
                acc_from_node = k[0]

        for s in states:
            items_dict = {}
            for i in s.items:
                k = [r for r in i.rule]
                k.insert(i.pos, ' . ')
                k = f"{i.lhs} -> {''.join(k)}"
                if k not in items_dict:
                    items_dict[k] = set(i.lookahead)
                else:
                    items_dict[k].add(i.lookahead)

            label = list([f"{i}, {' '.join(items_dict[i])}" for i in items_dict.keys()])

            label.insert(0, f"State {s.name}\n")
            if s.name in conflict_states:
                dot.node(f"{s.name}", '\n'.join(label), color='red')
            else:
                dot.node(f"{s.name}", '\n'.join(label))
        if acc_from_node:
            dot.edge(f"{acc_from_node}", f"acc", f"$", constraint='false', fontcolor="blue")

        for k in trans:
            s, e = k[0], k[1]
            v = trans[k]
            if isinstance(v, int):
                dot.edge(f"{s}", f"{v}", f"{e}", constraint='false', fontcolor="blue")
            elif v == ('acc',):
                dot.node(f"acc", "ACCEPT", color="green")
                dot.edge(f"{s}", f"acc", f"{e}", constraint='false', fontcolor="blue")

        dot.view()
