import copy
import json

import jsbeautifier
from graphviz import Digraph
from prettytable import PrettyTable, ALL

from util.BnfBuilder import BnfBuilder
from util.Lexer import Token


class Item0:
    def __init__(self, lhs: str, rule: tuple, pos: int, eof_symbol: str = '$') -> None:
        self.lhs = lhs
        self.rule = rule if isinstance(rule, tuple) else tuple(rule)
        self.pos = pos
        self.eof_symbol = eof_symbol

    def peek_dot_right(self):
        if self.pos > len(self.rule) - 1:
            return self.eof_symbol
        return self.rule[self.pos]

    def move(self):
        if self.pos < len(self.rule):
            new_item = copy.deepcopy(self)
            new_item.pos += 1
            return new_item
        return None

    def __str__(self) -> str:
        s = [r for r in self.rule]
        s.insert(self.pos, ' . ')
        return f"{self.lhs} -> {''.join(s)}"

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
    def __init__(self, name: int, items: set[Item0], eof_symbol: str = '$'):
        self.name = name if name is not None else 0
        self.items = items if items is not None else set()
        self.eof_symbol = eof_symbol

    def add_item(self, item: Item0):
        self.items.add(item)

    def add_items(self, items: set[Item0]):
        self.items = self.items.union(items)

    def set_name(self, name: int):
        self.name = name

    def next_symbols(self):
        return [s.peek_dot_right() for s in self.items if s.peek_dot_right() is not self.eof_symbol]

    def __str__(self) -> str:
        s = []
        for i in self.items:
            s.append(f"      {str(i)}\n")
        return f"state {self.name}:\n {' '.join(s)}\n"

    def __repr__(self):
        return self.__str__()


class LR0Parser:

    def __init__(self, bnf_file: str, eof: str = '$', print_ast=True, show_parsing_table=True, show_graph_state=True,
                 print_first_follow=True, show_parsing_steps=True):
        self.bnf_file = bnf_file
        self.bnf_builder = BnfBuilder(bnf_file)
        self.bnf_builder.build()
        self.grammar = self.bnf_builder.production_map
        self.grammar_list = self.bnf_builder.grammar_list
        self.semantic_action = self.bnf_builder.semantic_action
        self.non_terminals = self.bnf_builder.non_terminals
        self.terminals = self.bnf_builder.terminals
        self.epsilon = self.bnf_builder.epsilon
        self.start_symbol = self.bnf_builder.start_symbol
        self.precedence = self.bnf_builder.precedence
        self.eof = eof
        self.lr0_states = None
        self.lr0_trans_function = None
        self.init_state = None
        self.action_table = None
        self.goto_table = None
        self.parsing_table = None
        self.bnf_builder.build_first_set()
        self.bnf_builder.build_follow_set()
        self.first_set = self.bnf_builder.first_set
        self.follow_set = self.bnf_builder.follow_set
        self.augment_grammar()
        if print_first_follow:
            self.print_first_follow()
        self.ast = None
        self.print_ast = print_ast
        self.show_parsing_table = show_parsing_table
        self.show_graph_state = show_graph_state
        self.show_parsing_steps = show_parsing_steps

    def print_first_follow(self):
        x = PrettyTable()
        x.title = 'First & Follow set'
        x.field_names = ["Symbol", "First", "Follow"]
        for nt in self.non_terminals:
            x.add_row([nt, f" {' '.join(self.first_set[nt])} ", f" {' '.join(self.follow_set[nt])} "])

        print(x)

    def graph_state(self, states: list[LRState], trans: dict[tuple:int], acton_table: dict):
        dot = Digraph("state transaction", node_attr={'shape': 'box'}, engine='neato')
        # dot.attr(rankdir='LR')
        # dot.attr(splines='ortho')
        # true则用样条曲线画边，polyline则用折线，ortho则用垂直或水平的折线，false或line则线段，dot默认true，其它默认false。
        dot.attr(splines='true')
        # dot.attr(overlap="false")
        # 若结点相交，mode为”false”时调整结点，mode为”scale”时放大布局，mode为”true”时容许相交（默认）（用于twopi）
        dot.attr(overlap="scale")
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
            label = list([str(i) for i in s.items])
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

    # dot.render('test.gv', view=True)

    def print_state(self, states: list[LRState], trans: dict[tuple:int]):
        print('LR0 states')
        print()
        print('++++++++')
        for s in states:
            x = PrettyTable()
            x.title = f'State: {s.name}'
            x.field_names = ["No.", "Rule"]
            for index, item in enumerate(s.items):
                x.add_row([index + 1, item])
            print(x)

            trans_row = []
            for t in trans:
                if t[0] == s.name:
                    trans_row.append([s.name, t[1], trans[t]])
            if len(trans_row) > 0:
                x = PrettyTable()
                x.title = f'state trans'
                x.field_names = ["From", "Symbol", "Target"]
                x.add_rows(trans_row)
                print(x)

            print('++++++++')
            print()

    def augment_grammar(self):
        old_start = self.bnf_builder.start_symbol
        new_start = old_start + "'"
        self.grammar[new_start] = [[old_start]]
        self.non_terminals.add(new_start)
        self.start_symbol = new_start
        self.first_set[new_start] = self.first_set[old_start]
        self.follow_set[new_start] = set(self.eof)
        self.init_state = LRState(0, (self.closure([Item0(f"{new_start}", (old_start,), 0)])))
        self.grammar_list.insert(0, (new_start, (old_start,)))
        self.semantic_action.insert(0, None)

    def is_terminal(self, symbol: str) -> bool:
        return symbol in self.terminals

    def is_non_terminal(self, symbol: str) -> bool:
        return symbol in self.non_terminals

    def is_epsilon(self, symbol: str) -> bool:
        return symbol == self.epsilon

    def is_start(self, symbol: str) -> bool:
        return symbol == self.start_symbol

    def closure(self, items: list[Item0]) -> set[Item0]:
        """
        对于某个项集 I,首先把它里面的所有项放到它的闭包CLOSURE(I)中，接着遍历CLOSURE(I)中的每一项。如果遍历到的这一项点号右边恰好是非终结符，
        把这个非终结符对应的若干产生式，做成“LR(0) 项”（点号放在产生式体最左边），再全部添加到CLOSURE(I)中。反复遍历，直到没有新项被添加到
        CLOSURE(I)中为止。此时的CLOSURE(I)就叫做“项集I的闭包"
        :param items:
        :param G:
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
                        i = Item0(next_i, rule, 0)
                        if i not in result:
                            new_items.add(i)
            result |= new_items

            if len(result) != last_size:
                is_change = True
                last_size = len(result)
            else:
                is_change = False

        return result

    def goto(self, state: LRState, symbol: str) -> set[Item0]:
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
        return self.closure(new_items)

    def find_index(self, states: list[LRState], items: set[Item0]) -> int:
        for index, s in enumerate(states):
            if s.items == items:
                return index
        return -1

    def canonical_collection(self) -> tuple[list[LRState], dict[tuple:int]]:
        """
        到这个语法对应的规范-LR(0) 项集族；这个族中的每一个项集对应 LR(0) 自动机中的一个状态
        :param init_state:
        :param G:
        :return:
        """
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
        self.lr0_states = states
        self.lr0_trans_function = trans_map
        # self.print_state(states, trans_map)
        # self.graph_state(states, trans_map)
        return states, trans_map

    def _rightmost_terminal(self, item) -> int:
        for i in range(len(item) - 1, -1, -1):
            if self.is_terminal(item[i]):
                return i
        return -1

    def _precedence(self, terminal) -> tuple:
        for i, ps in enumerate(self.precedence):
            for p in ps:
                if p[1] == terminal:
                    return i, p[0]
        return None, None

    def lookahead_symbols(self, item: [Item0]):
        return list(self.terminals) + [self.eof]

    def build_parse_table(self) -> tuple[dict, dict]:
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
        self.print_grammar()
        action_table = {}
        goto_table = {}
        keys = self.lr0_trans_function.keys()
        for s in self.lr0_states:
            for item in s.items:
                next_symbol = item.peek_dot_right()
                key = (s.name, next_symbol)
                if self.is_terminal(next_symbol):
                    old = action_table.get(key, None)
                    # ambiguous grammar. Need precedence and associate
                    if old:
                        if old == ('s', self.lr0_trans_function[key]):
                            continue
                        if isinstance(old, list):
                            if ('s', self.lr0_trans_function[key]) in old:
                                continue
                            old.append(('s', self.lr0_trans_function[key]))
                        else:
                            action_table[key] = [old, ('s', self.lr0_trans_function[key])]
                    else:
                        action_table[key] = ('s', self.lr0_trans_function[key])
                elif next_symbol == self.eof and item.lhs != self.start_symbol:
                    for f in self.lookahead_symbols(item):
                        old = action_table.get((s.name, f), None)
                        if old:
                            if old == ('r', self.lookup_grammar(item.lhs, item.rule)):
                                continue
                            if isinstance(old, list):
                                if ('r', self.lookup_grammar(item.lhs, item.rule)) in old:
                                    continue
                                old.append(('r', self.lookup_grammar(item.lhs, item.rule)))
                            else:
                                action_table[(s.name, f)] = [old, ('r', self.lookup_grammar(item.lhs, item.rule))]
                        else:
                            action_table[(s.name, f)] = ('r', self.lookup_grammar(item.lhs, item.rule))
                elif next_symbol == self.eof and item.lhs == self.start_symbol:
                    old = action_table.get(key, None)
                    if old:
                        if isinstance(old, list):
                            old.append(('acc',))
                        else:
                            action_table[key] = [old, ('acc',)]
                    else:
                        action_table[key] = ('acc',)
        for s in self.lr0_states:
            for nt in self.non_terminals:
                key = (s.name, nt)
                if key in keys:
                    goto_table[key] = self.lr0_trans_function[key]
        self.action_table = action_table
        self.goto_table = goto_table
        self.resolve_ambiguity()
        if self.show_parsing_table:
            self.print_parsing_table(action_table, goto_table, self.lr0_states, self.grammar)
        self.parsing_table = {**action_table, **goto_table}
        if self.show_graph_state:
            self.graph_state(self.lr0_states, self.lr0_trans_function, self.action_table)
        for k in self.parsing_table:
            if isinstance(self.parsing_table[k], list):
                raise AssertionError(f'parsing table conflict')

        return action_table, goto_table

    def resolve_ambiguity(self):
        """
        消除文法的二义性

        对于shift/reduce冲突
        1. 给每一个终结符赋予一个优先级，例如 * 的优先级比 +的优先级要高。表达式的优先级与它最右边的终结符的优先级一致，如果表达式不含有终结符，
        那么表达式的优先级为 0;
        2. 当 shift/reduce 矛盾发生时，当前输入的终结符它的优先级要和做 reduce 操作的表达式的优先级做比较，如果他们的优先级一样，那么默认
        选择做 shift 操作，如果当前输入的终结符优先级高，那么做 shift 操作，要不然做reduce 操作。

        对于reduce/reduce冲突
        1. 一般选择位置高的产生式规约
        :return:
        """
        if len(self.precedence) == 0:
            return

        for key in self.action_table:
            state, terminal = key[0], key[1]
            action = self.action_table[key]
            if not isinstance(action, list):
                continue
            if isinstance(action, list) and len(action) != 2:
                continue
            precedence, association = self._precedence(terminal)
            if precedence is None:
                continue
            a0, a1 = action[0], action[1]
            # shift/reduce conflict
            if a0[0] == 's' and a1[0] == 'r' or a0[0] == 'r' and a1[0] == 's':
                if a0[0] == 'r':
                    # make a0 shift and a1 reduce
                    a0, a1 = a1, a0

                lhs, rhs = self.grammar_list[a1[1]]
                # no terminal
                i = self._rightmost_terminal(rhs)
                if i == -1:
                    precedence2, association2 = i, None
                else:
                    precedence2, association2 = self._precedence(rhs[i])
                if precedence2 is None:
                    continue
                # current symbol precedence > expression precedence, shift
                if precedence > precedence2:
                    self.action_table[key] = a0
                # same precedence, look at association
                elif precedence == precedence2:
                    # reduce
                    if association == 'left':
                        self.action_table[key] = a1
                    else:
                        # shift
                        self.action_table[key] = a0
                else:
                    # current symbol precedence < expression precedence, reduce
                    self.action_table[key] = a1
            # reduce/reduce conflict
            elif a0[0] == 'r' and a1[0] == 'r':
                # choose top grammar
                self.action_table[key] = a0 if a0[1] < a1[1] else a1

    def lookup_grammar(self, lhs: str, rhs: tuple) -> int:
        for index, g in enumerate(self.grammar_list):
            if g[0] == lhs and g[1] == rhs:
                return index
        raise AssertionError(f"rule {lhs} -> {' '.join(rhs)} not found")

    def print_grammar(self):
        x = PrettyTable()
        x.title = "Grammar"
        for index, g in enumerate(self.grammar_list):
            nt = g[0]
            rule = g[1]
            x.field_names = ["No.", "Production"]
            x.add_row([index, f"{nt} -> {' '.join(rule)}"])
        print(x)

    def print_parsing_table(self, action_table: dict, goto_table: dict, states: list[LRState], grammar: dict):
        x = PrettyTable()

        x.title = f'{self.__class__.__name__} Parsing Table'
        terminals = list(self.terminals)
        terminals.append(self.eof)
        non_terminals = list(self.non_terminals - {self.start_symbol})
        action_fields = [''] + terminals
        goto_fields = ['goto'] + non_terminals
        x.field_names = action_fields + goto_fields
        x.hrules = ALL
        for s in states:
            row = [''] * len(x.field_names)
            row[0] = s.name
            for index, t in enumerate(terminals):
                if (s.name, t) in action_table:
                    action = action_table[(s.name, t)]
                    if not isinstance(action, list):
                        row[index + 1] = f"{action[0]}{action[1] if len(action) > 1 else ''}"
                    else:
                        content = [f"{a[0]}{a[1] if len(a) > 1 else ''}" for a in action]
                        row[index + 1] = '/'.join(content)
            for index, nt in enumerate(non_terminals):
                if (s.name, nt) in goto_table:
                    goto = goto_table[(s.name, nt)]
                    row[index + 2 + len(terminals)] = f"{goto}"
            x.add_row(row)

        print(x)

    def parse(self, tokens: list[Token]):
        """
        push $
        push start state s0
        word <- NextWord()
        while(true):
            state <- top of stack
            if Action[state,word] = "reduce A -> B":
                pop 2 * |B|
                state <- top of stack
                push A
                push Goto[state,A]
            else if Action[state,word] = "shift si":
                push word
                push si
                word <- NextWord()
            else if Action[state,word] = "accept":
                break
            else:
                Fail()
        report success

        https://serokell.io/blog/how-to-implement-lr1-parser
        :param tokens:
        :return:
        """
        steps = []
        stage = 0
        stack = [(0, Token(self.eof, self.eof))]
        pos = 0
        word = tokens[pos]
        value_stack = []
        while True:
            # stage,stack,symbols,input,action
            stage += 1
            stack_ = " ".join([str(s[0]) for s in stack])
            symbol_ = " ".join([s[1] if isinstance(s[1], str) else s[1].type for s in stack])
            # show at most 15 tokens
            input_ = "".join([t.value for t in tokens[pos:pos + 15]])

            step = [stage, stack_, symbol_, input_]
            state = stack[-1]
            key = (state[0], word[0])
            if self.parsing_table[key][0] == 'r':
                g = self.parsing_table[key][1]
                lhs, rhs = self.grammar_list[g][0], self.grammar_list[g][1]
                values = []
                for _ in range(len(rhs)):
                    stack.pop()
                    values.append(value_stack.pop())
                values.reverse()
                semantic_action = self.semantic_action[g]
                if semantic_action:
                    semantic_action = semantic_action.strip()[1:-1].strip()
                else:
                    semantic_action = """result={}"""
                params = {
                    "result": None,
                }
                for index, v in enumerate(values):
                    params[f"p{index + 1}"] = v.value if isinstance(v, Token) else v
                exec(semantic_action, params)
                value_stack.append(params.get("result"))
                goto_state = self.parsing_table[(stack[-1][0], lhs)]
                new_state = (goto_state, lhs)
                stack.append(new_state)
                r = self.parsing_table[key]
                step.append(f"{r[0]}{r[1]}: reduce by {lhs} -> {' '.join(rhs)},goto {goto_state}")
                steps.append(step)
            elif self.parsing_table[key][0] == 's':
                goto_state = self.parsing_table[key][1]
                stack.append((goto_state, word))
                value_stack.append(word)
                s = self.parsing_table[key]
                step.append(f'{s[0]}{s[1]}: shift {word.type},goto {goto_state}')
                steps.append(step)
                pos += 1
                word = tokens[pos]
            elif self.parsing_table[key][0] == 'acc':
                step.append('accept')
                steps.append(step)
                break
            else:
                raise AssertionError("Parse failed")

        if self.show_parsing_steps:
            self.print_parsing_steps(steps)

        self.ast = value_stack.pop()
        if self.print_ast:
            print("AST:")
            opts = jsbeautifier.default_options()
            opts.indent_size = 2
            print(jsbeautifier.beautify(json.dumps(self.ast), opts))

    def print_parsing_steps(self, steps: list):
        x = PrettyTable()
        x.title = 'Parsing Steps'
        x.field_names = ['STAGE', 'STACK', 'SYMBOLS', 'INPUT', 'ACTION']
        x.add_rows(steps)
        print(x)
