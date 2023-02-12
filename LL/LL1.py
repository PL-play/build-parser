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
    'E': [('T', "E'")],
    "E'": [('+', 'T', "E'"), 'ε'],
    'T': [('F', "T'")],
    "T'": ['*F', 'ε'],
    'F': [('number',), ('(', 'E', ')')]

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
    print(f"--- get first of {non_terminal}")
    first_set = set()
    for production in G[non_terminal]:
        # X -> a，a为终结符，将a加入first(X)
        if is_terminal(production[0]):
            first_set.add(production[0])
            cache[non_terminal] = first_set
            print(f"add cache of {non_terminal}: {cache}")
        # X -> εY1Y2...Yk，将ε加入first(X),同时将first(Y1Y2...Yk)加入first(X)
        elif is_epsilon(production[0]):
            first_set.add(production[0])
            if len(production) > 1:
                first_set |= get_first(G, production[1], cache)
            cache[non_terminal] = first_set
            print(f"add cache of {non_terminal}: {cache}")
        # X -> C,C为非终结符，first(X) = first(C)
        elif is_non_terminal(production[0]):
            first_set = get_first(G, production[0], cache)
            cache[non_terminal] = first_set
            print(f"add cache of {non_terminal}: {cache}")
    return first_set


def follow(Grammar, Non_terminals, first_set):
    cache = {}

    for nt in Non_terminals:
        get_follow(Grammar, nt, first_set, cache)

    return cache


def get_follow(G, p, first_set, follow_set):
    if p in follow_set:
        return follow_set[p]
    print(f"--- get follow of {p}")
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
                                next_first |= get_follow(G, nt, first_set, follow_set)
                        f |= next_first
    follow_set[p] = f
    return f


if __name__ == '__main__':
    first_set = first(grammar, non_terminal)
    follow_set = follow(grammar, non_terminal, first_set)
    print('follow set:', follow_set)
    print('first set:', first_set)
