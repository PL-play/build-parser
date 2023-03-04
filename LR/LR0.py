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
    def __init__(self, lhs: str, rule: list, pos: int) -> None:
        self.lhs = lhs
        self.rule = rule
        self.pos = pos

    def peek_dot_right(self):
        if self.pos > len(self.rule) - 1:
            return eof
        return self.rule[self.pos]

    def __str__(self) -> str:
        s = [r for r in self.rule]
        s.insert(self.pos, '⊙')
        return f"{self.lhs}: {''.join(s)}"

    def __repr__(self):
        return self.__str__()


class LRState:
    def __init__(self):
        self.name = 0
        self.items = []

    def add_item(self, item: Item0):
        self.items.append(item)

    def add_items(self, items: list[Item0]):
        self.items = self.items + items

    def set_name(self, name: int):
        self.name = name

    def __str__(self) -> str:
        s = []
        for i in self.items:
            s.append(f"      {str(i)}\n")
        return f"state {self.name}:\n {' '.join(s)}\n"

    def __repr__(self):
        return self.__str__()


def closure(items: list[Item0], G: dict) -> list[Item0]:
    """

    :param state:
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


if __name__ == '__main__':
    pass
