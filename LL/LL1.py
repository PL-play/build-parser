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

    for nt in Non_terminals:
        get_first(Grammar, nt, cache)

    return cache


def get_first(G, non_terminal, cache):
    if cache.get(non_terminal, None) is not None:
        return cache.get(non_terminal)
    print(f"--- get first of {non_terminal}")
    first_set = set()
    for production in G[non_terminal]:
        if is_terminal(production[0]):
            first_set.add(production[0])
            cache[non_terminal] = first_set
            print(f"add cache of {non_terminal}: {cache}")
        elif is_epsilon(production[0]):
            first_set.add(production[0])
            if len(production) > 1:
                first_set |= get_first(G, production[1], cache)
            cache[non_terminal] = first_set
            print(f"add cache of {non_terminal}: {cache}")
        elif is_non_terminal(production[0]):
            first_set = get_first(G, production[0], cache)
            cache[non_terminal] = first_set
            print(f"add cache of {non_terminal}: {cache}")
    return first_set


if __name__ == '__main__':
    print(first(grammar, non_terminal))
