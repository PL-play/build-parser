import copy

terminal = {'+', '*', '(', ')', 'number'}
non_terminal = {'E', "E'", 'T', "T'", 'F'}
epsilon = 'ε'
start_symbol = 'E'
eof = '$'
"""
 1. E:TE'
 2. E':+TE'
 3. |ε
 4. T:FT'
 5. T':*F
 6. |ε  
 7. F:number
 8. |(E)

"""
grammar = {
    'E': [['T', "E'"]],
    "E'": [['+', 'T', "E'"], 'ε'],
    'T': [['F', "T'"]],
    "T'": [['*', 'F', "T'"], 'ε'],
    'F': [['number'], '(E)']

}


def is_terminal(p):
    if isinstance(p, str):
        return p in terminal
    elif isinstance(p, (tuple, list)):
        return p[0] in terminal
    else:
        print(f'is_terminal {type(p)} not supported.')


def is_epsilon(p):
    if isinstance(p, str):
        return p == epsilon
    elif isinstance(p, (tuple, list)):
        return p[0] == epsilon
    else:
        print(f'is_epsilon {type(p)} not supported.')


def is_non_terminal(p):
    if isinstance(p, str):
        return p in non_terminal
    elif isinstance(p, (tuple, list)):
        return p[0] in non_terminal
    else:
        print(f'is_non_terminal {type(p)} not supported.')


def is_start(p):
    if isinstance(p, str):
        return p == start_symbol
    elif isinstance(p, (tuple, list)):
        return p[0] == start_symbol
    else:
        print(f'is_start {type(p)} not supported.')


def first(Grammar, Non_terminals):
    cache = {}

    for nt in Non_terminals:
        get_first(Grammar, nt, cache)

    return cache


def get_first(G, non_terminal, cache):
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
            if p in prod:
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


def parsing_table(G, first_set, follow_set):
    table = dict()
    for nt, production_rules in G.items():
        table[nt] = dict()
        print(f"-- start construct {nt} row")
        for production_rule in production_rules:
            print(f"{nt} -> {production_rule}")
            first_symbol = production_rule[0]
            print(f"    first symbol is: {first_symbol}")
            if is_terminal(first_symbol) or first_symbol == eof:
                predict_set = {first_symbol}
                print(f"    first symbol {first_symbol} is terminal, predict set is {predict_set}")
            elif is_epsilon(first_symbol):
                predict_set = follow_set[nt]
                print(f"    first symbol {first_symbol} is epsilon, predict set the follow set of {nt}: {predict_set}")
            else:
                predict_set = first_set[first_symbol]
                print(
                    f"    first symbol {first_symbol} is not epsilon, predict set is the first set of first symbol {first_symbol}: {predict_set}")
            for symbol in predict_set:
                if symbol in table[nt]:
                    print(
                        f"Grammar is not LL(1) at {nt}:{production_rule} \
                        and {table[nt][symbol]}")
                else:
                    table[nt][symbol] = production_rule
                    print(f"    table[{nt}][{symbol}] is: {production_rule}")
        print(f"merged table[{nt}] is {table[nt]}")
        print()
    return table


def parse(start_symbol, parsing_table, input_string):
    input_list = input_string.split()
    input_list.append(eof)
    stack = [eof, start_symbol]
    i = 0
    while len(stack) > 0:
        top = stack.pop()
        # Rule1: if a non-terminal on top of the stack,replace it with its RHS.
        # T[non-terminal,lookahead] = production
        if is_non_terminal(top):
            production = parsing_table[top].get(input_list[i], None)
            if production is None:
                print(f"no production for table[{top},{input_list[i]}], parse error!")
                return False
            for symbol in reversed(production):
                if not is_epsilon(symbol):
                    stack.append(symbol)
        # Rule2: if a terminal on top of the stack,pop it and advance string cursor
        elif is_terminal(top):
            if top == input_list[i]:
                i += 1
            else:
                print(f"expect \"{top}\" but get \"{input_list[i]}\"")
                return False

    return True


if __name__ == '__main__':
    first_set = first(grammar, non_terminal)
    print('first set:', first_set)
    follow_set = follow(grammar, non_terminal, first_set)
    print('follow set:', follow_set)

    table = parsing_table(grammar, first_set, follow_set)
    print('parsing table', table)

    accepted = parse(start_symbol, table, '( number + number * number )')
    print(accepted)
