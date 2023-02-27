import copy

from LL.Lexer import Lexer

token_exprs = [
    (r'[ \n\t]+', None),
    (r'#[^\n]*', None),
    (r'[-]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', 'NUMBER'),
    # (r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', 'NUMBER'),
    (r'\(', '('),
    (r'\)', ')'),
    (r'\+', '+'),
    (r'\-', '-'),
    (r'\*', '*'),
    (r'\/', '/'),
    (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),
]

terminal = {'+', '*', '(', ')', 'NUMBER'}
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
    'F': [['NUMBER', ], ['(', 'E', ')']]

}
semantic_actions = {

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


def parsing_table(G, first_set, follow_set):
    """
    Step 1: For each production A → α , of the given grammar perform Step 2 and Step 3.

    Step 2: For each terminal symbol ‘a’ in FIRST(α), ADD A → α in table T[A,a], where ‘A’ determines row & ‘a’ determines column.

    Step 3:  If ε is present in FIRST(α) then find FOLLOW(A), ADD A → ε, at all columns ‘b’, where ‘b’ is FOLLOW(A).  (T[A,b])

    Step 4: If ε is in FIRST(α) and $ is the FOLLOW(A), ADD A → α to T[A,$].

    :param G:
    :param first_set:
    :param follow_set:
    :return:
    """
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


def parse(start_symbol, parsing_table, input_list):
    """
    https://stackoverflow.com/questions/54706455/ll-top-down-parser-from-cst-to-ast/54751222#54751222

    So that's probably the mechanism of choice for building syntax trees from top-down parsers as well.
    We add a "reduction" marker to the end of every right-hand side. Since the marker goes at the end of
    the right-hand side, so it is pushed first.

    We also need a value stack, to record the AST nodes (or semantic values) being constructed.
    In the basic algorithm, we now have one more case. We start by popping the top of the parser stack,
    and then examine this object:

    * The top of the parser stack was a terminal. If the current input symbol is the same terminal, we remove the
      input symbol from the input, and push it (or its semantic value) onto the value stack.
    * The top of the parser stack was a marker. The associated reduction action is triggered, which will create
      the new AST node by popping an appropriate number of values from the value stack and combining them into a new
      AST node which is then pushed onto the value stack. (As a special case, the marker action for the augmented
      start symbol's unique production S' -> S $ causes the parse to be accepted, returning the (only) value in
      the value stack as the AST.)
    * The top of the parser stack was a non-terminal. We then identify the appropriate right-hand side using the
      current input symbol, and push that right-hand side (right-to-left) onto the parser stack.

    :param start_symbol:
    :param parsing_table:
    :param input_string:
    :return:
    """
    input_list.append(eof)
    stack = [eof, start_symbol]
    i = 0

    while len(stack) > 0:
        print(stack)
        top = stack.pop()
        # Rule1: if a non-terminal on top of the stack,replace it with its RHS.
        # T[non-terminal,lookahead] = production
        if is_non_terminal(top):
            production = parsing_table[top].get(input_list[i], None)
            print(f'  top:{top}, input cursor:{input_list[i]}: {production}')
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


def parse_ast(start_symbol, parsing_table, input_list):
    input_list.append(eof)
    stack = [eof, start_symbol]
    value_stack = []
    i = 0

    while len(stack) > 0:
        top = stack.pop()
        if is_non_terminal(top):
            production = parsing_table[top].get(input_list[i], None)
            if production is None:
                print(f"no production for table[{top},{input_list[i]}], parse error!")
                return None

            for symbol in reversed(production):
                if not is_epsilon(symbol):
                    stack.append(symbol)
        elif is_terminal(top):
            if top == input_list[i]:
                i += 1
                value_stack.append(top)
            else:
                print(f"expect \"{top}\" but get \"{input_list[i]}\"")
                return None
        else:
            # Reduction marker
            if top == reduction_marker:
                # Pop the right-hand side symbols from the stack
                rhs = []
                while stack[-1] != reduction_marker:
                    rhs.append(stack.pop())
                stack.pop()  # Pop the reduction marker

                # Determine the reduction rule to apply
                non_terminal = stack[-1]
                production = parsing_table[non_terminal][reduction_marker]
                rule_len = len(production) - 1

                # Pop the semantic values from the value stack and pass them to the semantic action
                semantic_values = [value_stack.pop() for _ in range(rule_len)][::-1]
                ast_node = production.semantic_action(semantic_values)

                # Push the new AST node onto the value stack
                value_stack.append(ast_node)

                # Push the non-terminal symbol back onto the stack
                stack.append(non_terminal)
            else:
                print(f"unexpected symbol \"{top}\"")
                return None

    # The only value left on the value stack should be the AST
    if len(value_stack) == 1:
        return value_stack[0]
    else:
        print("parse error!")
        return None


def eliminateLeftRecursion(grammar):
    # Step 1: Identify left-recursive non-terminals and create new non-terminals
    new_rules = {}
    for non_terminal, rules in grammar.items():
        left_recursive = [rule for rule in rules if is_non_terminal(rule[0]) and rule[0] == non_terminal]
        non_left_recursive = [rule for rule in rules if not is_non_terminal(rule[0]) or rule[0] != non_terminal]
        if len(left_recursive) > 0:
            new_non_terminal = non_terminal + "'"
            new_rules[new_non_terminal] = []
            for rule in left_recursive:
                new_rules[new_non_terminal].append(rule[1:] + [new_non_terminal])
            for rule in non_left_recursive:
                new_rules[non_terminal] = new_rules.get(non_terminal, []) + [
                    rule if isinstance(rule, (list, tuple)) else [rule] + [new_non_terminal]]

    # Step 2: Update the grammar with the new non-terminals
    for non_terminal, rules in new_rules.items():
        if non_terminal in rules[0]:
            # Add an epsilon rule to the new non-terminal
            rules.append(['ε'])
        grammar[non_terminal] = rules

    return grammar


if __name__ == '__main__':
    first_set = first(grammar, non_terminal)
    print('first set:', first_set)
    follow_set = follow(grammar, non_terminal, first_set)
    print('follow set:', follow_set)

    table = parsing_table(grammar, first_set, follow_set)
    print('parsing table', table)

    text = '(3 + 4 )*(4+1)'
    lexer = Lexer(text, token_exprs)
    inputs = []
    while lexer.has_next():
        inputs.append(lexer.next().type)
    print(inputs)
    accepted = parse(start_symbol, table, inputs)
    print(accepted)

    ast, semantic_values = parse_ast(start_symbol, table, inputs)

    print(f"ast: {ast}")
    print(f"semantic_values: {semantic_values}")
