import copy

terminal = {"c", "d"}
non_terminal = {"C", "S"}
epsilon = 'ε'
start_symbol = 'S'
eof = '$'

"""
<S> ::= <C> <C>
<C> ::= "c" <C>
     | "d"
"""

grammar = {
    "S": [["C", "C"]],
    "C": [["c", "C"], "d"],
}


def is_terminal(p):
    if isinstance(p, str):
        return p in terminal
    elif isinstance(p, (tuple, list)) and len(p) == 1:
        return p[0] in terminal
    else:
        raise AssertionError(f'is_terminal {type(p)} not supported.')


def is_epsilon(p):
    if isinstance(p, str):
        return p == epsilon
    elif isinstance(p, (tuple, list)) and len(p) == 1:
        return p[0] == epsilon
    else:
        raise AssertionError(f'is_epsilon {type(p)} not supported.')


def is_non_terminal(p):
    if isinstance(p, str):
        return p in non_terminal
    elif isinstance(p, (tuple, list)) and len(p) == 1:
        return p[0] in non_terminal
    else:
        raise AssertionError(f'is_non_terminal {type(p)} not supported.')


def is_start(p):
    if isinstance(p, str):
        return p == start_symbol
    elif isinstance(p, (tuple, list)) and len(p) == 1:
        return p[0] == start_symbol
    else:
        raise AssertionError(f'is_start {type(p)} not supported.')


def first(Grammar, Non_terminals):
    cache = {}

    for nt in Non_terminals:
        get_first(Grammar, nt, cache)

    return cache


def get_first(G, non_terminal, cache):
    """
    1) If x is terminal, then FIRST(x)={x}

    2) If X→ ε is production, then add ε to FIRST(X)

    3) If X is a non-terminal and X → PQR then FIRST(X)=FIRST(P)

       If FIRST(P) contains ε, then

       FIRST(X) = (FIRST(P) – {ε}) U FIRST(QR)
    :param G:
    :param non_terminal:
    :param cache:
    :return:
    """
    if cache.get(non_terminal, None) is not None:
        return cache.get(non_terminal)
    first_set = set()
    for production in G[non_terminal]:
        # X -> a，a为终结符，将a加入first(X)
        if is_terminal(production[0]):
            first_set.add(production[0])
            cache[non_terminal] = first_set
        # X -> εY1Y2...Yk，将ε加入first(X),同时将first(Y1Y2...Yk)加入first(X)
        elif is_epsilon(production[0]):
            first_set.add(production[0])
            if len(production) > 1:
                first_set |= get_first(G, production[1], cache)
            cache[non_terminal] = first_set
        # X -> C,C为非终结符，first(X) = first(C)
        elif is_non_terminal(production[0]):
            first_set = get_first(G, production[0], cache)
            cache[non_terminal] = first_set
    return first_set


def follow(Grammar, Non_terminals, first_set):
    cache = {}

    for nt in Non_terminals:
        get_follow(Grammar, nt, first_set, cache)

    return cache


def get_follow(G, p, first_set, follow_set):
    """
    1) For Start symbol, place $ in FOLLOW(S)

    2) If A→ α B, then FOLLOW(B) = FOLLOW(A)

    3) If A→ α B β, then

      If ε not in FIRST(β),

           FOLLOW(B) = FIRST(β)

      else do,

           FOLLOW(B) = (FIRST(β)-{ε}) U FOLLOW(A)

    一个文法符号的FOLLOW集就是可能出现在这个文法符号后面的终结符.

    比如 S->ABaD, 那么FOLLOW(B)的值就是a。

    如果First(B)包含空:
    1). FOLLOW(A)的值包含了FIRST(B)中除了ε以外的所有终结符;
    2). 把FOLLOW(B)的值也添加到FOLLOW(A)中

    D是文法符号S的最右符号，
    那么所有跟在S后面的符号必定跟在D后面。所以FOLLOW(S)所有的值都在FOLLOW(D)中.

    以下是书中的总结

    不断应用下面这两个规则，直到没有新的FOLLOW集被加入
    规则一: FOLLOW(S)中加入$, S是文法开始符号
    规则二: A->CBY FOLLOW(B) 就是FIRST(Y)
    规则三: A->CB 或者 A->CBZ(Z可以推导出ε) 所有FOLLOW(A)的符号都在FOLLOW(B)

    :param G:
    :param p:
    :param first_set:
    :param follow_set:
    :return:
    """
    if p in follow_set:
        return follow_set[p]
    f = set()
    # put $ to follow(S) if S is start symbol
    if is_start(p):
        f.add(eof)
    for nt, prod_list in G.items():
        for prod in prod_list:
            if p not in prod:
                continue
            i = prod.index(p)
            # A -> aB, follow(B) = follow(A)
            if i == len(prod) - 1:
                # prevent infinite recursion of like E -> aE
                if nt != p:
                    f |= get_follow(G, nt, first_set, follow_set)
            else:
                # A -> Bc, put c in follow(B)
                if is_terminal(prod[i + 1]):
                    f.add(prod[i + 1])
                # A -> aBC, put first(C) - ε to follow(B)
                elif is_non_terminal(prod[i + 1]):
                    next_first = copy.deepcopy(first_set[prod[i + 1]])
                    if epsilon in next_first:
                        next_first.remove(epsilon)
                        if nt != p:
                            f |= get_follow(G, prod[i + 1], first_set, follow_set)
                    f |= next_first

    follow_set[p] = f
    return f


class Item0:
    def __init__(self, lhs: str, rule: tuple, pos: int) -> None:
        self.lhs = lhs
        self.rule = rule if isinstance(rule, tuple) else tuple(rule)
        self.pos = pos

    def peek_dot_right(self):
        if self.pos > len(self.rule) - 1:
            return eof
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
    def __init__(self, name: int, items: set[Item0]):
        self.name = name if name is not None else 0
        self.items = items if items is not None else set()

    def add_item(self, item: Item0):
        self.items.add(item)

    def add_items(self, items: set[Item0]):
        self.items = self.items.union(items)

    def set_name(self, name: int):
        self.name = name

    def next_symbols(self):
        return [s.peek_dot_right() for s in self.items if s.peek_dot_right() is not eof]

    def __str__(self) -> str:
        s = []
        for i in self.items:
            s.append(f"      {str(i)}\n")
        return f"state {self.name}:\n {' '.join(s)}\n"

    def __repr__(self):
        return self.__str__()


def closure(items: list[Item0], G: dict) -> list[Item0]:
    """
     对于某个项集 I,首先把它里面的所有项放到它的闭包CLOSURE(I)中，接着遍历CLOSURE(I)中的每一项。如果遍历到的这一项点号右边恰好是非终结符，
     把这个非终结符对应的若干产生式，做成“LR(0) 项”（点号放在产生式体最左边），再全部添加到CLOSURE(I)中。反复遍历，直到没有新项被添加到
     CLOSURE(I)中为止。此时的CLOSURE(I)就叫做“项集I的闭包"
    :param items:
    :param G:
    :return:
    """
    result = []
    work_list = [] + items
    while len(work_list) > 0:
        item = work_list.pop()
        result.append(item)
        next_i = item.peek_dot_right()
        if is_non_terminal(next_i):
            for rule in G[next_i]:
                work_list.append(Item0(next_i, rule, 0))
    return result


def goto(state: LRState, symbol: str, G: dict) -> list[Item0]:
    """
    GOTO 函数有两个参数，其中一个是某个项集，另一个是语法中的符号——可以是终结符，也可以是非终结符，还可以是 eof.
    对于某个项I和语法符号X，要计算GOTO(I, X，可以采用下面的方法:
    1. 新建一个空项集。
    2. 遍历项集中所有的条目，确定点号右边是不是 X
    3. 如果是的话，就把它单抽出来，把点号右移一位，再放到那个空项集里。我们把这些项叫做“内核项”。
    4. 遍历完之后，返回这个新项集的闭包。我们把闭包中新加入的项叫做“非内核项”。

    :param state:
    :param symbol:
    :param G:
    :return:
    """
    new_items = []
    for i in state.items:
        if i.peek_dot_right() == symbol:
            moved_item = i.move()
            if moved_item:
                new_items.append(moved_item)
    return closure(new_items, G)


def _find_index(states: list[LRState], items: set[Item0]):
    for index, s in enumerate(states):
        if s.items == items:
            return index
    return -1


def canonical_lr0_collection(init_state: LRState, G: dict) -> tuple[list[LRState], dict[tuple:int]]:
    """
    到这个语法对应的规范-LR(0) 项集族；这个族中的每一个项集对应 LR(0) 自动机中的一个状态
    :param init_state:
    :param G:
    :return:
    """
    states = [init_state]
    trans_map = {}
    work_list = [init_state]

    while len(work_list) > 0:
        state = work_list.pop()
        symbols = state.next_symbols()
        for s in symbols:
            items = set(goto(state, s, G))
            index = _find_index(states, items)
            if index == -1:
                new_state = LRState(len(states), items)
                states.append(new_state)
                trans_map[(state.name, s)] = new_state.name
                work_list.append(new_state)
            else:
                trans_map[(state.name, s)] = index

    return states, trans_map


def slr1_table(states: list[LRState], trans_map: dict[tuple:int], start_symbol: str, follow_set: dict) -> tuple[
    dict, dict]:
    """
    SLR 解析表是基于上面的 LR(0) 自动机制作的。我们知道 SLR 表有两个部分，一个部分是 Action 表，另外一部分是 Goto 表。

    构造 SLR 解析表中的 Action 表需要三步：
    1. 生成“规范-LR(0) 项集族”。
    2. 遍历项集族中的项集 I0,I1...In
    3. 对于其中的一个项集Ii，遍历其中的每一个 LR(0) 项
        * 如果这个项的点号右边是终结符a并且 goto(Ii, a) = Ij，就把 Action[i, a] 设成“移入 j”——相当于解析器读入了一个符号之后，
        被这个符号带到了状态 j。
        * 如果这个项的点号在整个产生式的最右边（形如 A -> a.），并且 A不是增广文法的开始符号，就找出A的 FOLLOW 集，遍历其中的终结符
        a，把 Action[i, a] 设成“归约 i”——相当于我们已经处理完了 A 这个非终结符，可以开始处理下一个了。
        * 如果这个项是 S' -> S（S 可以是任意开始符），就把 Action[i, eof] 设成“接受”

    构造 Goto 表,
    遍历所有非终结符。如果对于某个非终结符 A，有 goto(Ii, A) = Ij，那么我们就把 GOTO[i, A] 设成 j——这样告诉解析器，归约了A之后，
    要切换到状态 j 接受新的输入。
    这样 Goto 和 Action 的构造就完成了。

    :param states:
    :param trans_map:
    :return:
    """
    action_table = {}
    goto_table = {}
    keys = trans_map.keys()
    for s in states:
        for item in s.items:
            next_symbol = item.peek_dot_right()
            if is_terminal(next_symbol):
                action_table[(s.name, next_symbol)] = ('s', trans_map[(s.name, next_symbol)])
            elif next_symbol == eof and item.lhs != start_symbol:
                for f in follow_set[item.lhs]:
                    if is_terminal(f):
                        action_table[(s.name, f)] = ('r', (item.lhs, item.rule))
            elif next_symbol == eof and item.lhs == start_symbol:
                action_table[(s.name, next_symbol)] = 'acc'
    for s in states:
        for nt in non_terminal:
            key = (s.name, nt)
            if key in keys:
                goto_table[key] = trans_map[key]

    return action_table, goto_table


if __name__ == '__main__':
    pass
