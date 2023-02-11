terminal = {'+', '*', '(', ')', 'number'}
non_terminal = {'E', "E'", 'T', "T'", 'F'}
epsilon = 'ε'
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


def first(Grammar, Non_terminals):
    cache = {}

    def _first(G, non_terminal):
        if cache.get(non_terminal, None) is not None:
            return cache.get(non_terminal)
        print(f"get first of {non_terminal}")
        first_set = set()
        for production in G[non_terminal]:
            # X -> a，a为终结符，将a加入first(X)
            if is_terminal(production[0]):
                first_set.add(production[0])
                cache[non_terminal] = first_set
                print(f"add cache: {cache}")
            # X -> εY1Y2...Yk，将ε加入first(X),同时将first(Y1Y2...Yk)加入first(X)
            elif is_epsilon(production[0]):
                first_set.add(production[0])
                if len(production) > 1:
                    first_set |= _first(G, production[1])
                cache[non_terminal] = first_set
                print(f"add cache: {cache}")
            # X -> C,C为非终结符，first(X) = first(C)
            elif is_non_terminal(production[0]):
                first_set = _first(G, production[0])
                cache[non_terminal] = first_set
                print(f"add cache: {cache}")
        return first_set

    for nt in Non_terminals:
        _first(Grammar, nt)

    return cache


if __name__ == '__main__':
    print(first(grammar, non_terminal))
