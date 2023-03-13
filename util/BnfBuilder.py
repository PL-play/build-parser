import copy
import shlex


class BNF:
    def __init__(self):
        pass


class BnfBuilder:
    def __init__(self, bnf_path: str, prod_delimiter: str = '->', or_delimiter: str = '|', epsilon: str = 'ε',
                 comment_symbol: str = '//') -> None:
        self.bnf_path = bnf_path
        self.prod_delimiter = prod_delimiter
        self.or_delimiter = or_delimiter
        self.production_map = {}
        self.non_terminals = set()
        self.terminals = set()
        self.symbols = set()
        self.epsilon = epsilon
        self.current_non_terminal = None
        self.start_symbol = None
        self.comment_symbol = comment_symbol
        self.current_line = None
        self.first_set = None
        self.follow_set = None
        self.grammar_list = []
        self.semantic_action_cache = []
        self.semantic_action = []

    def build_first_set(self):
        self.first_set = self.first(self.production_map, epsilon_symbol=self.epsilon)

    def build_follow_set(self):
        self.follow_set = self.follow(self.production_map, self.first_set, self.non_terminals, self.start_symbol,
                                      self.epsilon)

    def build(self):
        file = open(self.bnf_path, "r")
        line = file.readline()
        while line:
            self.current_line = line
            self.build_production(shlex.split(line))
            line = file.readline()
        file.close()
        if self.semantic_action_cache:
            self.semantic_action[-1] = ''.join(self.semantic_action_cache)
            self.semantic_action_cache = []
        self.terminals = self.symbols - self.non_terminals

    def _find_index(self, p: list, item) -> int:
        for index, s in enumerate(p):
            if s == item:
                return index
        return -1

    def build_production(self, p):
        if not p:
            return
        if p[0] == self.comment_symbol:
            return
        d_index = self._find_index(p, self.prod_delimiter)
        if d_index == -1:
            if not self.current_non_terminal:
                raise AssertionError(f'No lhs found in "{self.current_line}"')
            if p[0] != self.or_delimiter:
                self.semantic_action_cache.append(self.current_line)
                return
                # raise AssertionError(f"expect '{self.or_delimiter}' for this line")

            if len(p) == 1:
                self.production_map[self.current_non_terminal].append([self.epsilon])
                self.grammar_list.append((self.current_non_terminal, (self.epsilon,)))
                self.semantic_action.append(None)
                if self.semantic_action_cache:
                    self.semantic_action[len(self.grammar_list) - 2]=''.join(self.semantic_action_cache)
                    self.semantic_action_cache = []

            else:
                self.production_map[self.current_non_terminal].append(p[1:])
                self.grammar_list.append((self.current_non_terminal, tuple(p[1:])))
                self.semantic_action.append(None)
                if self.semantic_action_cache:
                    self.semantic_action[len(self.grammar_list) - 2] = ''.join(self.semantic_action_cache)
                    self.semantic_action_cache = []


        else:
            if d_index != 1:
                raise AssertionError(f"production delimiter must be after lhs: {self.current_line}")
            if len(p) <= 2:
                raise AssertionError(f"no rhs found in :{self.current_line}")
            else:
                self.current_non_terminal = p[0]
                self.production_map[p[0]] = [p[2:]]
                self.grammar_list.append((self.current_non_terminal, tuple(p[2:])))
                self.non_terminals.add(p[0])
                if not self.start_symbol:
                    self.start_symbol = p[0]
                self.semantic_action.append(None)
                if self.semantic_action_cache:
                    self.semantic_action[(len(self.grammar_list)) - 2] = ''.join(self.semantic_action_cache)
                    self.semantic_action_cache = []

        for s in p:
            if s != self.epsilon and s != self.or_delimiter and s != self.prod_delimiter:
                self.symbols.add(s)

    @staticmethod
    def first(grammar: dict, epsilon_symbol: str = 'ε'):
        """
        Rules:
            #1. First(a) = a, a is terminal.
            #2. X -> Y1Y2...Yn, for each symbol Yi, if 'ε' is not in First(Yi), First(X) = First(X) U First(Yi).
                If 'ε' is in First(Yi), First(X) = First(X) U First(Yi) U First(Yi+1).
            #3. if X -> ε, add 'ε' to First(X).
        :param grammar:
        :return:
        """
        result = {}
        last_result_count = {}
        is_change = True
        for g in grammar:
            result[g] = set()
            last_result_count[g] = 0
        while is_change:
            for g in grammar:
                rhs = grammar[g]
                for rules in rhs:
                    for r in rules:
                        f = copy.deepcopy(result.get(r, {r}))
                        result[g] |= f
                        if epsilon_symbol not in f:
                            break
            is_change = False
            for r in result:
                if len(result[r]) != last_result_count[r]:
                    last_result_count[r] = len(result[r])
                    is_change = True
        return result

    @staticmethod
    def follow(grammar: dict, first_set: dict, non_terminals: set, start_symbol: str, epsilon_symbol: str = 'ε',
               eof: str = '$') -> dict:
        """
        Rules:
            #1. If S is start symbol,add eof to Follow(S).
            #2. A -> xBy, add {First(y) - ε} to Follow(B).
            #3. A -> xB, add Follow(A) to Follow(B).
        :param grammar:
        :param first_set:
        :return:
        """
        result = {}
        last_result_count = {}
        is_change = True
        for g in grammar:
            result[g] = set()
            last_result_count[g] = 0
            if g == start_symbol:
                result[g].add(eof)
                last_result_count[g] += 1

        while is_change:
            for g in grammar:
                rhs = grammar[g]
                for rule in rhs:
                    l = len(rule)
                    for i, s in enumerate(rule):
                        if s not in non_terminals:
                            continue
                        if i == l - 1:
                            result[s] |= copy.deepcopy(result[g])
                        else:
                            result[s] |= copy.deepcopy(first_set.get(rule[i + 1], {rule[i + 1]}) - set(epsilon_symbol))

            is_change = False
            for r in result:
                if len(result[r]) != last_result_count[r]:
                    last_result_count[r] = len(result[r])
                    is_change = True
        return result
