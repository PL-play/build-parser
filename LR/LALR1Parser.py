from LR.LR0Parser import LRState, Item0
from LR.LR1Parser import LR1Parser, Item1


class LALR1Parser(LR1Parser):
    def __init__(self, bnf_file: str, eof: str = '$'):
        super().__init__(bnf_file, eof)

    def group_indices(self, A):
        index_list = []
        for i, elem in enumerate(A):
            added = False
            for group in index_list:
                if elem == A[group[0]]:
                    group.append(i)
                    added = True
                    break
            if not added:
                index_list.append([i])
        return index_list

    def combine(self, name: int, states: list[LRState], state_item_lookahead: list[dict[Item0:set]]):
        items = set()
        name_trans = {}
        for index, state in enumerate(states):
            d = state_item_lookahead[index]
            name_trans[state.name] = name
            for item in state.items:
                item0, lookahead = item.split()
                lookaheads = d[item0]
                for l in lookaheads:
                    items.add(Item1(item0.lhs, item0.rule, item0.pos, l))
        return LRState(name, items), name_trans

    def merge_state(self, states: list[LRState], goto: dict[tuple:int]):
        item_set = []
        state_item_lookahead = []

        for index, s in enumerate(states):
            item0_set = set()
            state_item_lookahead.append(dict())
            for i in s.items:
                item0, lookahead = i.split()
                item0_set.add(item0)
                if item0 not in state_item_lookahead[index]:
                    state_item_lookahead[index][item0] = set(lookahead)
                else:
                    state_item_lookahead[index][item0].add(lookahead)
            item_set.append(item0_set)

        group = self.group_indices(item_set)
        new_states = []
        name_trans_map = {}
        for index, g in enumerate(group):
            new_state, name_trans = self.combine(index, [states[i] for i in g], [state_item_lookahead[i] for i in g])
            name_trans_map.update(name_trans)
            new_states.append(new_state)
        new_goto = {}
        for name, symbol in goto:
            new_goto[(name_trans_map[name], symbol)] = name_trans_map[goto[(name, symbol)]]
        return new_states, new_goto

    def canonical_collection(self) -> tuple[list[LRState], dict[tuple:int]]:
        states = [self.init_state]
        trans_map = {}
        work_list = [self.init_state]

        while len(work_list) > 0:
            state = work_list.pop()
            symbols = state.next_symbols()
            for s in symbols:
                items = self.goto(state, s)
                index = self.find_index(states, items)
                if index == -1:
                    new_state = LRState(len(states), items)
                    states.append(new_state)
                    trans_map[(state.name, s)] = new_state.name
                    work_list.append(new_state)
                else:
                    trans_map[(state.name, s)] = index
        states, trans_map = self.merge_state(states, trans_map)
        self.lr0_states = states
        self.lr0_trans_function = trans_map

        return states, trans_map
