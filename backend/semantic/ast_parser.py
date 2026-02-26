# =============================================================================
# ast_parser.py — SeaStack AST-Building Parser
#
# HOW THIS PARSER WORKS (read before editing):
# ─────────────────────────────────────────────
# This parser runs AFTER the syntax parser has already validated the token
# stream. That means we can assume the input is structurally correct and never
# need to do error recovery — we just build the tree.
#
# It is a top-down predictive parser (LL(1)), using the exact same PREDICT
# table as syn_parser.py. Every method corresponds to one grammar non-terminal.
#
# KEY DIFFERENCES FROM syn_parser:
#   syn_parser:  self.eat('id')              — consumes token, returns nothing
#   ast_parser:  tok = self.current_token    — SAVE the token FIRST
#                self.eat('id')              — then consume
#                name = tok.value            — then USE the saved value
#
# Every method that builds part of the tree RETURNS a node (or a list of
# nodes, a string, an operator symbol, etc.). Callers collect these return
# values and compose them into parent nodes.
#
# EXPRESSION-BUILDING PATTERN:
#   The grammar uses right-recursive "tail" rules to avoid left recursion:
#     coin_val  → coin_ope  coin_arith
#     coin_arith → arith_op coin_ope coin_arith | λ
#   These represent:  coin_ope (op coin_ope)*
#   We convert them into LEFT-associative BinaryOpNode trees by passing a
#   running left-hand accumulator through the tail methods:
#     coin_val():
#         left = coin_ope()
#         return coin_arith(left)   ← left is the accumulator
#     coin_arith(left):
#         if op found:
#             right = coin_ope()
#             node = BinaryOpNode(left, op, right)
#             return coin_arith(node)   ← node becomes new left
#         else: return left   ← λ production, stop
#   This produces the same left-associative tree a LALR parser would.
#
# ID-TAIL DISAMBIGUATION:
#   <id-tail> determines what kind of expression follows a bare `id`:
#     {index}       → array access   → ArrayAccessNode
#     $id           → member access  → MemberAccessNode
#     (args)        → function call  → FuncCallNode
#     λ             → plain variable → IdentNode
#   The id_tail() method receives the already-consumed name and token, and
#   returns the correct expression node.
#
# PRODUCTION NUMBER ALIGNMENT:
#   All production numbers in this file match syn_parser.py exactly.
#   When in doubt, cross-reference with syn_parser.py.
# =============================================================================

from syntax.Predict_Set import PREDICT
from semantic.ast_nodes import (
    ProgramNode, AhoyNode,
    ConstDeclNode,
    VarDeclNode, ArrayDeclNode,
    StructDefNode, MemberDeclNode,
    StructVarDeclNode, PositionalInitNode, NamedInitNode,
    FuncDefNode, ParamNode,
    AssignNode, CompoundAssignNode,
    AskNode, AddressNode, EchoNode,
    LookNode, ChartNode, CourseNode,
    HoistNode, HoistInitNode, HoistUpdateNode,
    HeaveNode, HaulHeaveNode,
    SailNode, LandNode,
    ReturnNode, BackNode,
    UnaryStmtNode, FuncCallStmtNode,
    LiteralNode, IdentNode,
    ArrayAccessNode, MemberAccessNode,
    ScrollCharAccessNode, StringConcatNode,
    FuncCallNode, BinaryOpNode, UnaryOpNode,
)


class ASTParser:
    def __init__(self, tokens, source_code):
        # ── Filter whitespace/comments exactly like syn_parser ──
        ignored_types = ['whitespace', 'newline', 'single-comment', 'multi-comment']
        self.tokens = [t for t in tokens if t.type not in ignored_types]

        # Normalize numbered id types (id1, id2 → id)
        for t in self.tokens:
            if t.type.startswith('id') and t.type[2:].isdigit():
                t.type = 'id'

        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def advance(self):
        """Move to the next token."""
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, token_type):
        """
        Consume the current token, asserting it matches token_type.
        Since syn_parser already validated the stream, a mismatch here
        indicates a bug in the ast_parser — not a user error.
        """
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            found = self.current_token.type if self.current_token else 'EOF'
            raise RuntimeError(
                f'ASTParser internal error: expected {token_type!r}, '
                f'got {found!r} at line {getattr(self.current_token, "line", "?")}. '
                f'This is a bug in the AST parser, not the SeaStack program.'
            )

    def get_production(self, non_terminal):
        """Look up which production to use given the current token."""
        if not self.current_token:
            return None
        return PREDICT.get(non_terminal, {}).get(self.current_token.type)

    # =========================================================================
    # ENTRY POINT
    # =========================================================================

    def build(self):
        """
        Build and return the root ProgramNode.
        Call this after syn_parser.parse() returns no errors.
        """
        return self.program()

    # =========================================================================
    # PROGRAM STRUCTURE
    # prod 1: <program> → <global-dec> AHOY() [ <ahoy-local-dec> <ahoy-stmnts> ]
    # =========================================================================

    def program(self):
        tok = self.current_token
        global_decls = self.global_dec()        # returns list[ASTNode]
        self.eat('AHOY')
        self.eat('(')
        self.eat(')')
        self.eat('[')
        local_decls = self.ahoy_local_dec()     # returns list[ASTNode]
        statements = self.ahoy_stmnts()         # returns list[ASTNode]
        self.eat(']')
        return ProgramNode(global_decls, AhoyNode(local_decls, statements, tok), tok)

    # ─────────────────────────────────────────────────────────────────────────
    # GLOBAL DECLARATIONS
    # prods 2–6: <global-dec> → var-arr-func | const global-dec | struct sub-func
    #                         | nonreturn-func | λ
    #
    # Returns a flat list of all declarations found at global scope.
    # ─────────────────────────────────────────────────────────────────────────

    def global_dec(self):
        nodes = []
        prod = self.get_production('<global-dec>')
        if prod == 2:
            nodes.extend(self.var_arr_func())
        elif prod == 3:
            nodes.extend(self.const())
            nodes.extend(self.global_dec())
        elif prod == 4:
            nodes.extend(self.struct())
            nodes.extend(self.sub_func())
        elif prod == 5:
            nodes.append(self.nonreturn_func())
        elif prod == 6:
            pass  # λ
        return nodes

    # ─────────────────────────────────────────────────────────────────────────
    # VAR / ARR / FUNC  (global level)
    # prods 7–11
    # ─────────────────────────────────────────────────────────────────────────

    def var_arr_func(self):
        prod = self.get_production('<var-arr-func>')
        dtype_tok = self.current_token
        if prod == 7:
            self.eat('COIN')
            name_tok = self.current_token; self.eat('id')
            return self.coin_dec(dtype_tok, name_tok)
        elif prod == 8:
            self.eat('DIME')
            name_tok = self.current_token; self.eat('id')
            return self.dime_dec(dtype_tok, name_tok)
        elif prod == 9:
            self.eat('PARCH')
            name_tok = self.current_token; self.eat('id')
            return self.parch_dec(dtype_tok, name_tok)
        elif prod == 10:
            self.eat('SCROLL')
            name_tok = self.current_token; self.eat('id')
            return self.scroll_dec(dtype_tok, name_tok)
        elif prod == 11:
            self.eat('BOOL')
            name_tok = self.current_token; self.eat('id')
            return self.bool_dec(dtype_tok, name_tok)
        return []

    # ─────────────────────────────────────────────────────────────────────────
    # TYPE-SPECIFIC DECLARATIONS
    # prods 12/13, 49/50, 79/80, 103/104, 135/136
    # ─────────────────────────────────────────────────────────────────────────

    def coin_dec(self, dtype_tok, name_tok):
        prod = self.get_production('<coin-dec>')
        nodes = []
        if prod == 12:
            nodes.extend(self.coin_var_arr('COIN', name_tok))
            self.eat('!!')
            nodes.extend(self.global_dec())
        elif prod == 13:
            nodes.append(self.coin_func('COIN', name_tok))
        return nodes

    def dime_dec(self, dtype_tok, name_tok):
        prod = self.get_production('<dime-var-arr-func>')
        nodes = []
        if prod == 58:
            nodes.extend(self.dime_var_arr('DIME', name_tok))
            self.eat('!!')
            nodes.extend(self.global_dec())
        elif prod == 59:
            nodes.append(self.dime_func('DIME', name_tok))
        return nodes

    def parch_dec(self, dtype_tok, name_tok):
        prod = self.get_production('<parch-var-arr-func>')
        nodes = []
        if prod == 98:
            nodes.extend(self.parch_var_arr('PARCH', name_tok))
            self.eat('!!')
            nodes.extend(self.global_dec())
        elif prod == 99:
            nodes.append(self.parch_func('PARCH', name_tok))
        return nodes

    def scroll_dec(self, dtype_tok, name_tok):
        prod = self.get_production('<scroll-var-arr-func>')
        nodes = []
        if prod == 122:
            nodes.extend(self.scroll_var_arr('SCROLL', name_tok))
            self.eat('!!')
            nodes.extend(self.global_dec())
        elif prod == 123:
            nodes.append(self.scroll_func('SCROLL', name_tok))
            nodes.extend(self.sub_func())
        return nodes

    def bool_dec(self, dtype_tok, name_tok):
        prod = self.get_production('<bool-var-arr-func>')
        nodes = []
        if prod == 164:
            nodes.extend(self.bool_var_arr('BOOL', name_tok))
            self.eat('!!')
            nodes.extend(self.global_dec())
        elif prod == 165:
            nodes.append(self.bool_func('BOOL', name_tok))
        return nodes

    # ─────────────────────────────────────────────────────────────────────────
    # COIN VAR/ARR
    # prods 14/15 (coin_var_arr), 16 (coin_var), 17/18 (coin_init),
    #        19/20 (coin_init_mult), 36 (coin_arr),
    #        37/38/39 (coin_arr_tail), 40 (coin_arr1), 41/42 (cav_tail),
    #        43/44 (coin_arr2_tail), 45/46/47 (coin_arr2, cav2_tail)
    # ─────────────────────────────────────────────────────────────────────────

    def coin_var_arr(self, dtype, name_tok):
        prod = self.get_production('<coin-var-arr>')
        if prod == 14:
            return self.coin_var(dtype, name_tok)
        elif prod == 15:
            return [self.coin_arr(dtype, name_tok)]
        return []

    def coin_var(self, dtype, name_tok):
        # prod 16
        init = self.coin_init()
        nodes = [VarDeclNode(dtype, name_tok.value, init, name_tok)]
        nodes.extend(self.coin_init_mult(dtype))
        return nodes

    def coin_init(self):
        prod = self.get_production('<coin-init>')
        if prod == 17:
            self.eat('=')
            return self.coin_val()
        # prod 18: λ
        return None

    def coin_init_mult(self, dtype):
        prod = self.get_production('<coin-init-mult>')
        if prod == 19:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            init = self.coin_init()
            node = VarDeclNode(dtype, name_tok.value, init, name_tok)
            return [node] + self.coin_init_mult(dtype)
        return []  # prod 20: λ

    def coin_arr(self, dtype, name_tok):
        # prod 36
        self.eat('{'); dim1_tok = self.current_token; self.eat('COIN-lit'); self.eat('}')
        dim1 = int(dim1_tok.value)
        return self.coin_arr_tail(dtype, name_tok, dim1)

    def coin_arr_tail(self, dtype, name_tok, dim1):
        prod = self.get_production('<coin-arr-tail>')
        if prod == 40:                          # 1D with initializer: = [...]
            self.eat('='); self.eat('[')
            values = self.coin_arr1()
            self.eat(']')
            return ArrayDeclNode(dtype, name_tok.value, [dim1], False, values, name_tok)
        elif prod == 41:                        # 2D: {size2} ...
            self.eat('{'); dim2_tok = self.current_token; self.eat('COIN-lit'); self.eat('}')
            dim2 = int(dim2_tok.value)
            return self.coin_arr2_tail(dtype, name_tok, dim1, dim2)
        else:                                   # prod 42: λ — no init
            return ArrayDeclNode(dtype, name_tok.value, [dim1], False, None, name_tok)

    def coin_arr2_tail(self, dtype, name_tok, dim1, dim2):
        prod = self.get_production('<coin-arr2-tail>')
        if prod == 49:                          # 2D with initializer: = [[...], ...]
            self.eat('='); self.eat('[')
            rows = self.coin_arr2()
            self.eat(']')
            return ArrayDeclNode(dtype, name_tok.value, [dim1, dim2], True, rows, name_tok)
        else:                                   # prod 50: λ
            return ArrayDeclNode(dtype, name_tok.value, [dim1, dim2], True, None, name_tok)

    def coin_arr1(self):
        # prod 40
        val = self.coin_val()
        return [val] + self.cav_tail()

    def cav_tail(self):
        prod = self.get_production('<cav-tail>')
        if prod == 47:
            self.eat(',')
            return self.coin_arr1()
        return []  # prod 48: λ

    def coin_arr2(self):
        # prod 45
        self.eat('[')
        row = self.coin_arr1()
        self.eat(']')
        rows = [row]
        return rows + self.cav2_tail()

    def cav2_tail(self):
        prod = self.get_production('<cav2-tail>')
        if prod == 52:
            self.eat(',')
            return self.coin_arr2()
        return []  # prod 53: λ

    # ─────────────────────────────────────────────────────────────────────────
    # DIME VAR/ARR
    # prods 51/52, 53, 54/55, 56/57, 66, 67/68/69, 70, 71/72, 73/74, 75, 76/77
    # ─────────────────────────────────────────────────────────────────────────

    def dime_var_arr(self, dtype, name_tok):
        prod = self.get_production('<dime-var-arr>')
        if prod == 60:
            return self.dime_var(dtype, name_tok)
        elif prod == 61:
            return [self.dime_arr(dtype, name_tok)]
        return []

    def dime_var(self, dtype, name_tok):
        # prod 53
        init = self.dime_init()
        nodes = [VarDeclNode(dtype, name_tok.value, init, name_tok)]
        nodes.extend(self.dime_init_mult(dtype))
        return nodes

    def dime_init(self):
        prod = self.get_production('<dime-init>')
        if prod == 63:
            self.eat('=')
            return self.dime_val()
        return None  # prod 64: λ

    def dime_init_mult(self, dtype):
        prod = self.get_production('<dime-init-mult>')
        if prod == 65:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            init = self.dime_init()
            return [VarDeclNode(dtype, name_tok.value, init, name_tok)] + self.dime_init_mult(dtype)
        return []  # prod 66: λ

    def dime_arr(self, dtype, name_tok):
        # prod 66
        self.eat('{'); dim1_tok = self.current_token; self.eat('COIN-lit'); self.eat('}')
        dim1 = int(dim1_tok.value)
        return self.dime_arr_tail(dtype, name_tok, dim1)

    def dime_arr_tail(self, dtype, name_tok, dim1):
        prod = self.get_production('<dime-arr-tail>')
        if prod == 80:
            self.eat('='); self.eat('[')
            values = self._arr1_values(self.dime_val)
            self.eat(']')
            return ArrayDeclNode(dtype, name_tok.value, [dim1], False, values, name_tok)
        elif prod == 81:
            self.eat('{'); dim2_tok = self.current_token; self.eat('COIN-lit'); self.eat('}')
            dim2 = int(dim2_tok.value)
            return self.dime_arr2_tail(dtype, name_tok, dim1, dim2)
        else:  # prod 82: λ
            return ArrayDeclNode(dtype, name_tok.value, [dim1], False, None, name_tok)

    def dime_arr2_tail(self, dtype, name_tok, dim1, dim2):
        prod = self.get_production('<dime-arr2-tail>')
        if prod == 89:
            self.eat('='); self.eat('[')
            rows = self._arr2_rows(self.dime_val)
            self.eat(']')
            return ArrayDeclNode(dtype, name_tok.value, [dim1, dim2], True, rows, name_tok)
        else:  # prod 90: λ
            return ArrayDeclNode(dtype, name_tok.value, [dim1, dim2], True, None, name_tok)

    # ─────────────────────────────────────────────────────────────────────────
    # PARCH VAR/ARR
    # prods 81/82, 83, 84/85, 86/87, 90, 91/92/93, 94, 95/96, 97/98, 99, 100/101
    # ─────────────────────────────────────────────────────────────────────────

    def parch_var_arr(self, dtype, name_tok):
        prod = self.get_production('<parch-var-arr>')
        if prod == 100:
            return self.parch_var(dtype, name_tok)
        elif prod == 101:
            return [self.parch_arr(dtype, name_tok)]
        return []

    def parch_var(self, dtype, name_tok):
        # prod 83
        init = self.parch_init()
        nodes = [VarDeclNode(dtype, name_tok.value, init, name_tok)]
        nodes.extend(self.parch_init_mult(dtype))
        return nodes

    def parch_init(self):
        prod = self.get_production('<parch-init>')
        if prod == 103:
            self.eat('=')
            return self.parch_val()
        return None  # prod 104: λ

    def parch_init_mult(self, dtype):
        prod = self.get_production('<parch-init-mult>')
        if prod == 105:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            init = self.parch_init()
            return [VarDeclNode(dtype, name_tok.value, init, name_tok)] + self.parch_init_mult(dtype)
        return []  # prod 106: λ

    def parch_arr(self, dtype, name_tok):
        # prod 90
        self.eat('{'); dim1_tok = self.current_token; self.eat('COIN-lit'); self.eat('}')
        dim1 = int(dim1_tok.value)
        return self.parch_arr_tail(dtype, name_tok, dim1)

    def parch_arr_tail(self, dtype, name_tok, dim1):
        prod = self.get_production('<parch-arr-tail>')
        if prod == 110:
            self.eat('='); self.eat('[')
            values = self._arr1_values(self.parch_val)
            self.eat(']')
            return ArrayDeclNode(dtype, name_tok.value, [dim1], False, values, name_tok)
        elif prod == 111:
            self.eat('{'); dim2_tok = self.current_token; self.eat('COIN-lit'); self.eat('}')
            dim2 = int(dim2_tok.value)
            return self.parch_arr2_tail(dtype, name_tok, dim1, dim2)
        else:  # prod 112: λ
            return ArrayDeclNode(dtype, name_tok.value, [dim1], False, None, name_tok)

    def parch_arr2_tail(self, dtype, name_tok, dim1, dim2):
        prod = self.get_production('<parch-arr2-tail>')
        if prod == 116:
            self.eat('='); self.eat('[')
            rows = self._arr2_rows(self.parch_val)
            self.eat(']')
            return ArrayDeclNode(dtype, name_tok.value, [dim1, dim2], True, rows, name_tok)
        else:  # prod 117: λ
            return ArrayDeclNode(dtype, name_tok.value, [dim1, dim2], True, None, name_tok)

    # ─────────────────────────────────────────────────────────────────────────
    # SCROLL VAR/ARR
    # prods 105/106, 107, 108/109, 110/111, 122, 123/124/125, 126, 127/128,
    #        129/130, 131, 132/133
    # ─────────────────────────────────────────────────────────────────────────

    def scroll_var_arr(self, dtype, name_tok):
        prod = self.get_production('<scroll-var-arr>')
        if prod == 124:
            return self.scroll_var(dtype, name_tok)
        elif prod == 125:
            return [self.scroll_arr(dtype, name_tok)]
        return []

    def scroll_var(self, dtype, name_tok):
        # prod 107
        init = self.scroll_init()
        nodes = [VarDeclNode(dtype, name_tok.value, init, name_tok)]
        nodes.extend(self.scroll_init_mult(dtype))
        return nodes

    def scroll_init(self):
        prod = self.get_production('<scroll-init>')
        if prod == 127:
            self.eat('=')
            return self.scroll_val()
        return None  # prod 128: λ

    def scroll_init_mult(self, dtype):
        prod = self.get_production('<scroll-init-mult>')
        if prod == 129:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            init = self.scroll_init()
            return [VarDeclNode(dtype, name_tok.value, init, name_tok)] + self.scroll_init_mult(dtype)
        return []  # prod 130: λ

    def scroll_arr(self, dtype, name_tok):
        # prod 122
        self.eat('{'); dim1_tok = self.current_token; self.eat('COIN-lit'); self.eat('}')
        dim1 = int(dim1_tok.value)
        return self.scroll_arr_tail(dtype, name_tok, dim1)

    def scroll_arr_tail(self, dtype, name_tok, dim1):
        prod = self.get_production('<scroll-arr-tail>')
        if prod == 146:
            self.eat('='); self.eat('[')
            values = self._arr1_values(self.scroll_val)
            self.eat(']')
            return ArrayDeclNode(dtype, name_tok.value, [dim1], False, values, name_tok)
        elif prod == 147:
            self.eat('{'); dim2_tok = self.current_token; self.eat('COIN-lit'); self.eat('}')
            dim2 = int(dim2_tok.value)
            return self.scroll_arr2_tail(dtype, name_tok, dim1, dim2)
        else:  # prod 148: λ
            return ArrayDeclNode(dtype, name_tok.value, [dim1], False, None, name_tok)

    def scroll_arr2_tail(self, dtype, name_tok, dim1, dim2):
        prod = self.get_production('<scroll-arr2-tail>')
        if prod == 155:
            self.eat('='); self.eat('[')
            rows = self._arr2_rows(self.scroll_val)
            self.eat(']')
            return ArrayDeclNode(dtype, name_tok.value, [dim1, dim2], True, rows, name_tok)
        else:  # prod 156: λ
            return ArrayDeclNode(dtype, name_tok.value, [dim1, dim2], True, None, name_tok)

    # ─────────────────────────────────────────────────────────────────────────
    # BOOL VAR/ARR
    # prods 137/138, 139, 140/141, 142/143, 202, 203/204/205, 206, 207/208,
    #        209/210, 211, 212/213
    # ─────────────────────────────────────────────────────────────────────────

    def bool_var_arr(self, dtype, name_tok):
        prod = self.get_production('<bool-var-arr>')
        if prod == 166:
            return self.bool_var(dtype, name_tok)
        elif prod == 167:
            return [self.bool_arr(dtype, name_tok)]
        return []

    def bool_var(self, dtype, name_tok):
        # prod 139
        init = self.bool_init()
        nodes = [VarDeclNode(dtype, name_tok.value, init, name_tok)]
        nodes.extend(self.bool_init_mult(dtype))
        return nodes

    def bool_init(self):
        prod = self.get_production('<bool-init>')
        if prod == 169:
            self.eat('=')
            return self.bool_val()
        return None  # prod 170: λ

    def bool_init_mult(self, dtype):
        prod = self.get_production('<bool-init-mult>')
        if prod == 171:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            init = self.bool_init()
            return [VarDeclNode(dtype, name_tok.value, init, name_tok)] + self.bool_init_mult(dtype)
        return []  # prod 172: λ

    def bool_arr(self, dtype, name_tok):
        # prod 202
        self.eat('{'); dim1_tok = self.current_token; self.eat('COIN-lit'); self.eat('}')
        dim1 = int(dim1_tok.value)
        return self.bool_arr_tail(dtype, name_tok, dim1)

    def bool_arr_tail(self, dtype, name_tok, dim1):
        prod = self.get_production('<bool-arr-tail>')
        if prod == 261:
            self.eat('='); self.eat('[')
            values = self._arr1_values(self.bool_val)
            self.eat(']')
            return ArrayDeclNode(dtype, name_tok.value, [dim1], False, values, name_tok)
        elif prod == 262:
            self.eat('{'); dim2_tok = self.current_token; self.eat('COIN-lit'); self.eat('}')
            dim2 = int(dim2_tok.value)
            return self.bool_arr2_tail(dtype, name_tok, dim1, dim2)
        else:  # prod 263: λ
            return ArrayDeclNode(dtype, name_tok.value, [dim1], False, None, name_tok)

    def bool_arr2_tail(self, dtype, name_tok, dim1, dim2):
        prod = self.get_production('<bool-arr2-tail>')
        if prod == 296:
            self.eat('='); self.eat('[')
            rows = self._arr2_rows(self.bool_val)
            self.eat(']')
            return ArrayDeclNode(dtype, name_tok.value, [dim1, dim2], True, rows, name_tok)
        else:  # prod 297: λ
            return ArrayDeclNode(dtype, name_tok.value, [dim1, dim2], True, None, name_tok)

    # ─────────────────────────────────────────────────────────────────────────
    # GENERIC ARRAY HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    def _arr1_values(self, val_method):
        values = [val_method()]
        while self.current_token and self.current_token.type == ',':
            self.eat(',')
            values.append(val_method())
        return values

    def _arr2_rows(self, val_method):
        rows = []
        while self.current_token and self.current_token.type == '[':
            self.eat('[')
            rows.append(self._arr1_values(val_method))
            self.eat(']')
            if self.current_token and self.current_token.type == ',':
                self.eat(',')
        return rows

    # =========================================================================
    # CONSTANTS (LOCKE)
    # prod 265: LOCKE <const-init>!!
    # Returns list[ConstDeclNode]
    # =========================================================================

    def const(self):
        self.eat('LOCKE')
        nodes = self.const_init()
        self.eat('!!')
        return nodes

    def const_init(self):
        prod = self.get_production('<const-init>')
        if prod == 443:
            self.eat('COIN')
            return self.coin_locke_list('COIN')
        elif prod == 444:
            self.eat('DIME')
            return self.dime_locke_list('DIME')
        elif prod == 445:
            self.eat('PARCH')
            return self.parch_locke_list('PARCH')
        elif prod == 446:
            self.eat('SCROLL')
            return self.scroll_locke_list('SCROLL')
        elif prod == 447:
            self.eat('BOOL')
            return self.bool_locke_list('BOOL')
        return []

    def coin_locke_list(self, dtype):
        """
        prod 271: id = COIN-lit
        prod 272/273: coin_locke_mult (comma-separated additional entries)
        """
        nodes = []
        name_tok = self.current_token; self.eat('id')
        self.eat('=')
        val_tok = self.current_token; self.eat('COIN-lit')
        nodes.append(ConstDeclNode(dtype, name_tok.value,
                                   LiteralNode('COIN', int(val_tok.value), val_tok), name_tok))
        # prod 272: , coin_locke coin_locke_mult | prod 273: λ
        prod = self.get_production('<coin-locke-mult>')
        while prod == 449:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            self.eat('=')
            val_tok = self.current_token; self.eat('COIN-lit')
            nodes.append(ConstDeclNode(dtype, name_tok.value,
                                       LiteralNode('COIN', int(val_tok.value), val_tok), name_tok))
            prod = self.get_production('<coin-locke-mult>')
        return nodes

    def dime_locke_list(self, dtype):
        """
        prod 274: id = locke_digit
        prod 275/276: COIN-lit | DIME-lit
        prod 277/278: dime_locke_mult
        """
        nodes = []
        name_tok = self.current_token; self.eat('id')
        self.eat('=')
        val_tok = self.current_token
        if self.current_token.type == 'COIN-lit':
            self.eat('COIN-lit')
            lit = LiteralNode('COIN', int(val_tok.value), val_tok)
        else:
            self.eat('DIME-lit')
            lit = LiteralNode('DIME', float(val_tok.value), val_tok)
        nodes.append(ConstDeclNode(dtype, name_tok.value, lit, name_tok))
        prod = self.get_production('<dime-locke-mult>')
        while prod == 454:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            self.eat('=')
            val_tok = self.current_token
            if self.current_token.type == 'COIN-lit':
                self.eat('COIN-lit')
                lit = LiteralNode('COIN', int(val_tok.value), val_tok)
            else:
                self.eat('DIME-lit')
                lit = LiteralNode('DIME', float(val_tok.value), val_tok)
            nodes.append(ConstDeclNode(dtype, name_tok.value, lit, name_tok))
            prod = self.get_production('<dime-locke-mult>')
        return nodes

    def parch_locke_list(self, dtype):
        """
        prod 279: id = PARCH-lit
        prod 280/281: parch_locke_mult
        """
        nodes = []
        name_tok = self.current_token; self.eat('id')
        self.eat('=')
        val_tok = self.current_token; self.eat('PARCH-lit')
        nodes.append(ConstDeclNode(dtype, name_tok.value,
                                   LiteralNode('PARCH', val_tok.value, val_tok), name_tok))
        prod = self.get_production('<parch-locke-mult>')
        while prod == 457:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            self.eat('=')
            val_tok = self.current_token; self.eat('PARCH-lit')
            nodes.append(ConstDeclNode(dtype, name_tok.value,
                                       LiteralNode('PARCH', val_tok.value, val_tok), name_tok))
            prod = self.get_production('<parch-locke-mult>')
        return nodes

    def scroll_locke_list(self, dtype):
        """
        prod 282: id = SCROLL-lit <scr_id>
        prod 283/284: scr_id ({COIN-lit} | λ)
        prod 285/286: scroll_locke_mult
        """
        nodes = []
        name_tok = self.current_token; self.eat('id')
        self.eat('=')
        str_tok = self.current_token; self.eat('SCROLL-lit')
        base = LiteralNode('SCROLL', str_tok.value, str_tok)
        val = self.scr_id_const(base, str_tok)
        nodes.append(ConstDeclNode(dtype, name_tok.value, val, name_tok))
        prod = self.get_production('<scroll-locke-mult>')
        while prod == 462:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            self.eat('=')
            str_tok = self.current_token; self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', str_tok.value, str_tok)
            val = self.scr_id_const(base, str_tok)
            nodes.append(ConstDeclNode(dtype, name_tok.value, val, name_tok))
            prod = self.get_production('<scroll-locke-mult>')
        return nodes

    def scr_id_const(self, base_expr, tok):
        """Optional {COIN-lit} after a SCROLL-lit in a LOCKE context.
        prod 283: {COIN-lit}
        prod 284: λ
        """
        prod = self.get_production('<scr-id>')
        if prod == 460:
            self.eat('{')
            idx_tok = self.current_token; self.eat('COIN-lit')
            self.eat('}')
            return ScrollCharAccessNode(base_expr, LiteralNode('COIN', int(idx_tok.value), idx_tok), tok)
        return base_expr  # prod 461: λ

    def bool_locke_list(self, dtype):
        """
        prod 287: id = locke_bool
        prod 288/289: AYE | NAY
        prod 290/291: bool_locke_mult
        """
        nodes = []
        name_tok = self.current_token; self.eat('id')
        self.eat('=')
        val_tok = self.current_token
        if self.current_token.type == 'AYE':
            self.eat('AYE')
            lit = LiteralNode('BOOL', True, val_tok)
        else:
            self.eat('NAY')
            lit = LiteralNode('BOOL', False, val_tok)
        nodes.append(ConstDeclNode(dtype, name_tok.value, lit, name_tok))
        prod = self.get_production('<bool-locke-mult>')
        while prod == 467:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            self.eat('=')
            val_tok = self.current_token
            if self.current_token.type == 'AYE':
                self.eat('AYE'); lit = LiteralNode('BOOL', True, val_tok)
            else:
                self.eat('NAY'); lit = LiteralNode('BOOL', False, val_tok)
            nodes.append(ConstDeclNode(dtype, name_tok.value, lit, name_tok))
            prod = self.get_production('<bool-locke-mult>')
        return nodes

    # =========================================================================
    # STRUCT DEFINITIONS
    # prod 292: MAST id [ mem-dec mem-dec-tail ]!! struct()
    # prod 293: λ
    # Returns list[StructDefNode]
    # =========================================================================

    def struct(self):
        nodes = []
        prod = self.get_production('<struct>')
        while prod == 469:
            self.eat('MAST')
            name_tok = self.current_token; self.eat('id')
            self.eat('[')
            members = self.mem_dec()
            members.extend(self.mem_dec_tail())
            self.eat(']')
            self.eat('!!')
            nodes.append(StructDefNode(name_tok.value, members, name_tok))
            prod = self.get_production('<struct>')
        return nodes  # prod 470: λ

    def mem_dec(self):
        """
        prod 294: <d-type> id <mem-mult>!!
        Returns list[MemberDeclNode]
        """
        dtype = self.d_type()
        name_tok = self.current_token; self.eat('id')
        members = [MemberDeclNode(dtype, name_tok.value, name_tok)]
        members.extend(self.mem_mult(dtype))
        self.eat('!!')
        return members

    def mem_mult(self, dtype):
        prod = self.get_production('<mem-mult>')
        if prod == 472:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            return [MemberDeclNode(dtype, name_tok.value, name_tok)] + self.mem_mult(dtype)
        return []  # prod 473: λ

    def mem_dec_tail(self):
        prod = self.get_production('<mem-dec-tail>')
        if prod == 474:
            members = self.mem_dec()
            return members + self.mem_dec_tail()
        return []  # prod 475: λ

    # =========================================================================
    # FUNCTION DEFINITIONS
    # =========================================================================

    def sub_func(self):
        """
        prod 299: return_func
        prod 300: nonreturn_func
        prod 301: λ
        """
        prod = self.get_production('<sub-func>')
        if prod == 476:
            return [self.return_func()]
        elif prod == 477:
            return [self.nonreturn_func()]
        return []  # prod 478: λ

    def return_func(self):
        """
        prod 302: COIN id coin_func
        prod 303: DIME id dime_func
        prod 304: PARCH id parch_func
        prod 305: SCROLL id scroll_func
        prod 306: BOOL id bool_func
        """
        prod = self.get_production('<return-func>')
        dtype_map = {479: 'COIN', 480: 'DIME', 481: 'PARCH', 482: 'SCROLL', 483: 'BOOL'}
        token_map = {479: 'COIN', 480: 'DIME', 481: 'PARCH', 482: 'SCROLL', 483: 'BOOL'}
        dtype = dtype_map[prod]
        self.eat(token_map[prod])
        name_tok = self.current_token; self.eat('id')
        return self._build_return_func(dtype, name_tok)

    def _build_return_func(self, dtype, name_tok):
        """
        Shared logic for building a returning function definition.
        Corresponds to the body of coin_func (prod 48), dime_func (prod 78),
        parch_func (prod 102), scroll_func (prod 134), bool_func (prod 214).
        """
        self.eat('(')
        params = self.params()
        self.eat(')')
        self.eat('[')
        local_decls = self.local_dec()
        body = self.ret_stmnts()
        self.eat('BACK')
        return_expr = self.return_val_for(dtype)
        self.eat('!!')
        self.eat(']')
        self.sub_func()   # trailing sub_funcs (consumed but handled by global context)
        return FuncDefNode(dtype, name_tok.value, params, local_decls,
                           body, return_expr, name_tok)

    def coin_func(self, dtype, name_tok):
        # prod 48
        return self._build_return_func(dtype, name_tok)

    def dime_func(self, dtype, name_tok):
        # prod 78
        return self._build_return_func(dtype, name_tok)

    def parch_func(self, dtype, name_tok):
        # prod 102
        return self._build_return_func(dtype, name_tok)

    def scroll_func(self, dtype, name_tok):
        # prod 134
        return self._build_return_func(dtype, name_tok)

    def bool_func(self, dtype, name_tok):
        # prod 214
        return self._build_return_func(dtype, name_tok)

    def return_val_for(self, dtype):
        """Dispatch to the correct return-value expression method."""
        if dtype == 'COIN':   return self.coin_val()
        if dtype == 'DIME':   return self.dime_val()
        if dtype == 'PARCH':  return self.parch_val()
        if dtype == 'SCROLL': return self.scroll_val()
        if dtype == 'BOOL':   return self.bool_val()

    def nonreturn_func(self):
        """
        prod 307: ABYSS id (params) [ ahoy_local_dec nonret_stmnts nonret_back ]
        """
        tok = self.current_token
        self.eat('ABYSS')
        name_tok = self.current_token; self.eat('id')
        self.eat('(')
        params = self.params()
        self.eat(')')
        self.eat('[')
        local_decls = self.ahoy_local_dec()
        body = self.nonret_stmnts()
        back = self.nonret_back()
        if back:
            body.append(back)
        self.eat(']')
        self.sub_func()
        return FuncDefNode('ABYSS', name_tok.value, params, local_decls, body, None, tok)

    def nonret_stmnts(self):
        """
        prod 308: nonret_stmnt nonret_tail
        (NOT a lambda — syn_parser errors if missing; body always has ≥1 stmt)
        """
        first = self.statements()
        rest = self.nonret_tail()
        return [first] + rest

    def nonret_tail(self):
        """
        prod 309: nonret_stmnts
        prod 310: λ
        """
        prod = self.get_production('<nonret-tail>')
        if prod == 486:
            return self.nonret_stmnts()
        return []  # prod 487: λ

    def nonret_back(self):
        """
        prod 323: BACK!!  → BackNode
        prod 324: λ       → None
        """
        prod = self.get_production('<nonret-back>')
        if prod == 488:
            tok = self.current_token
            self.eat('BACK'); self.eat('!!')
            return BackNode(tok)
        return None  # prod 489: λ

    # ─────────────────────────────────────────────────────────────────────────
    # PARAMETERS
    # prod 215: dtype id param_mult
    # prod 216: λ
    # prod 217: , params
    # prod 218: λ
    # Returns list[ParamNode]
    # ─────────────────────────────────────────────────────────────────────────

    def params(self):
        prod = self.get_production('<params>')
        if prod == 331:
            dtype = self.d_type()
            name_tok = self.current_token; self.eat('id')
            first = ParamNode(dtype, name_tok.value, name_tok)
            return [first] + self.param_mult()
        return []  # prod 216: λ

    def param_mult(self):
        prod = self.get_production('<param-mult>')
        if prod == 333:
            self.eat(',')
            return self.params()
        return []  # prod 334: λ

    def d_type(self):
        """Consume a type keyword and return it as a string."""
        tok = self.current_token
        type_map = {'COIN': 'COIN', 'DIME': 'DIME', 'PARCH': 'PARCH',
                    'SCROLL': 'SCROLL', 'BOOL': 'BOOL'}
        self.eat(tok.type)
        return type_map[tok.type]

    # =========================================================================
    # LOCAL DECLARATIONS
    # prod 325/326/327 (inside functions), 425/426/427 (inside AHOY)
    # Returns list[ASTNode]
    # =========================================================================

    def local_dec(self):
        nodes = []
        prod = self.get_production('<local-dec>')
        while prod == 502:
            nodes.extend(self.var_arr_local())
            self.eat('!!')
            prod = self.get_production('<local-dec>')
        if prod == 503:
            nodes.extend(self.struct_dec())
        return nodes  # prod 504: λ

    def ahoy_local_dec(self):
        nodes = []
        prod = self.get_production('<ahoy-local-dec>')
        while prod == 666:
            nodes.extend(self.var_arr_local())
            self.eat('!!')
            prod = self.get_production('<ahoy-local-dec>')
        if prod == 667:
            nodes.extend(self.ahoy_struct_dec())
        return nodes  # prod 668: λ

    def var_arr_local(self):
        """
        Local variable/array declaration (no function definitions allowed).
        prod 328–332 (same non-terminal <var-arr> as syn_parser)
        """
        prod = self.get_production('<var-arr>')
        if prod == 505:
            self.eat('COIN')
            name_tok = self.current_token; self.eat('id')
            return self.coin_var_arr('COIN', name_tok)
        elif prod == 506:
            self.eat('DIME')
            name_tok = self.current_token; self.eat('id')
            return self.dime_var_arr('DIME', name_tok)
        elif prod == 507:
            self.eat('PARCH')
            name_tok = self.current_token; self.eat('id')
            return self.parch_var_arr('PARCH', name_tok)
        elif prod == 508:
            self.eat('SCROLL')
            name_tok = self.current_token; self.eat('id')
            return self.scroll_var_arr('SCROLL', name_tok)
        elif prod == 509:
            self.eat('BOOL')
            name_tok = self.current_token; self.eat('id')
            return self.bool_var_arr('BOOL', name_tok)
        return []

    def struct_dec(self):
        """
        prod 333: MAST id id str_dec_init!! struct_dec
        prod 334: λ
        Returns list[StructVarDeclNode]
        """
        nodes = []
        prod = self.get_production('<struct-dec>')
        while prod == 510:
            self.eat('MAST')
            type_tok = self.current_token; self.eat('id')
            var_tok = self.current_token; self.eat('id')
            inits, extra_names = self.str_dec_init()
            self.eat('!!')
            nodes.append(StructVarDeclNode(type_tok.value, var_tok.value, inits, var_tok))
            for extra_name in extra_names:
                nodes.append(StructVarDeclNode(type_tok.value, extra_name, None, var_tok))
            prod = self.get_production('<struct-dec>')
        return nodes  # prod 511: λ

    def ahoy_struct_dec(self):
        """
        prod 428: MAST id id str_dec_init!! ahoy_struct_dec
        prod 429: λ
        Mirrors struct_dec but uses the ahoy variant production numbers.
        """
        nodes = []
        prod = self.get_production('<ahoy-struct-dec>')
        while prod == 669:
            self.eat('MAST')
            type_tok = self.current_token; self.eat('id')
            var_tok = self.current_token; self.eat('id')
            inits, extra_names = self.str_dec_init()
            self.eat('!!')
            nodes.append(StructVarDeclNode(type_tok.value, var_tok.value, inits, var_tok))
            for extra_name in extra_names:
                nodes.append(StructVarDeclNode(type_tok.value, extra_name, None, var_tok))
            prod = self.get_production('<ahoy-struct-dec>')
        return nodes  # prod 670: λ

    def str_dec_init(self):
        """
        prod 335: , id str_dec_tail  (extra var names, no initializer)
        prod 336: = [ str_val str_val_tail ]  (initializer list)
        prod 337: λ
        Returns (inits, extra_names)
        """
        prod = self.get_production('<str-dec-init>')
        if prod == 512:
            extra_names = []
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            extra_names.append(name_tok.value)
            extra_names.extend(self.str_dec_tail())
            return None, extra_names
        elif prod == 513:
            self.eat('='); self.eat('[')
            inits = self.str_val_list()
            self.eat(']')
            return inits, []
        return None, []  # prod 514: λ

    def str_dec_tail(self):
        """
        prod 338: , id str_dec_tail
        prod 339: λ
        """
        prod = self.get_production('<str-dec-tail>')
        if prod == 515:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            return [name_tok.value] + self.str_dec_tail()
        return []  # prod 516: λ

    def str_val_list(self):
        """Collect str_val entries separated by commas.
        prod 340/341: str_val
        prod 342: , str_val str_val_tail
        prod 343: λ
        Returns list[PositionalInitNode | NamedInitNode]
        """
        inits = [self.str_val()]
        prod = self.get_production('<str-val-tail>')
        while prod == 519:
            self.eat(',')
            inits.append(self.str_val())
            prod = self.get_production('<str-val-tail>')
        return inits  # prod 520: λ stops loop

    def str_val(self):
        """
        prod 340: value            → PositionalInitNode
        prod 341: $id = value      → NamedInitNode
        """
        prod = self.get_production('<str-val>')
        if prod == 518:
            self.eat('$')
            name_tok = self.current_token; self.eat('id')
            self.eat('=')
            val = self.value()
            return NamedInitNode(name_tok.value, val, name_tok)
        else:  # prod 517
            val = self.value()
            return PositionalInitNode(val, self.current_token)

    # =========================================================================
    # STATEMENTS
    # =========================================================================

    def ret_stmnts(self):
        """
        prod 224: statements ret_stmnts
        prod 225: λ
        Statements inside a returning function body.
        """
        stmts = []
        prod = self.get_production('<ret-stmnts>')
        while prod == 340:
            stmts.append(self.statements())
            prod = self.get_production('<ret-stmnts>')
        return stmts  # prod 341: λ

    def ahoy_stmnts(self):
        """
        prod 671: ahoy_stmnt ahoy_tail
        (syn_parser errors if no statement at all, but ahoy_tail handles repetition)
        """
        stmts = []
        prod = self.get_production('<ahoy-stmnts>')
        if prod == 671:
            stmts.append(self.ahoy_stmnt())
            stmts.extend(self.ahoy_tail())
        return stmts

    def ahoy_tail(self):
        """
        prod 431: ahoy_stmnts
        prod 432: λ
        """
        prod = self.get_production('<ahoy-tail>')
        if prod == 672:
            return self.ahoy_stmnts()
        return []  # prod 673: λ

    def statements(self):
        """
        Dispatch to the correct statement type based on the current token.
        Returns a single statement ASTNode.

        prod 344: assign_stmnt
        prod 345: ask_stmnt
        prod 346: echo_stmnt
        prod 347: look_stmnt
        prod 348: chart_stmnt
        prod 349: hoist_stmnt
        prod 350: heave_stmnt
        prod 351: haul_stmnt
        prod 352: unary_exp!!
        """
        prod = self.get_production('<statements>')
        if prod == 553:
            return self.assign_stmnt()
        elif prod == 554:
            return self.ask_stmnt()
        elif prod == 555:
            return self.echo_stmnt()
        elif prod == 556:
            return self.look_stmnt()
        elif prod == 557:
            return self.chart_stmnt()
        elif prod == 558:
            return self.hoist_stmnt()
        elif prod == 559:
            return self.heave_stmnt()
        elif prod == 560:
            return self.haul_stmnt()
        elif prod == 561:
            node = self.unary_exp()
            self.eat('!!')
            return node

    # ─────────────────────────────────────────────────────────────────────────
    # ASSIGNMENT
    # prod 353: id assign_tail!!
    # prod 354: arr_str assign_body   (var/array/member assignment)
    # prod 355: (args)                (function call statement)
    # ─────────────────────────────────────────────────────────────────────────

    def assign_stmnt(self):
        # prod 353
        tok = self.current_token
        name_tok = self.current_token; self.eat('id')
        node = self.assign_tail(name_tok)
        self.eat('!!')
        return node

    def assign_tail(self, name_tok):
        prod = self.get_production('<assign-tail>')
        if prod == 563:
            target_kind, idx1, idx2, member = self.arr_str()
            return self.assign_body(name_tok, target_kind, idx1, idx2, member)
        elif prod == 564:
            self.eat('(')
            args = self.args()
            self.eat(')')
            return FuncCallStmtNode(FuncCallNode(name_tok.value, args, name_tok), name_tok)

    def arr_str(self):
        """
        prod 356: {index} elmt2   → array access
        prod 357: $id             → member access
        prod 358: λ               → plain variable
        Returns (target_kind, index1, index2, member)
        """
        prod = self.get_production('<arr-str>')
        if prod == 565:
            self.eat('{')
            idx1 = self.index_expr()
            self.eat('}')
            # arr_str_tail: prod 568 → second dimension, prod 569 → λ
            prod2 = self.get_production('<arr-str-tail>')
            if prod2 == 568:
                self.eat('{')
                idx2 = self.index_expr()
                self.eat('}')
                return 'array2d', idx1, idx2, None
            return 'array1d', idx1, None, None
        elif prod == 566:
            self.eat('$')
            member_tok = self.current_token; self.eat('id')
            return 'member', None, None, member_tok.value
        return 'var', None, None, None  # prod 567: λ

    def assign_body(self, name_tok, target_kind, idx1, idx2, member):
        """
        prod 359: = value
        prod 360: arith_assign_op dime_ope dime_arith
        """
        prod = self.get_production('<assign-body>')
        if prod == 570:
            self.eat('=')
            val = self.value()
            return AssignNode(name_tok.value, target_kind, idx1, idx2, member, val, name_tok)
        elif prod == 571:
            op_tok = self.current_token
            op = self.arith_assign_op()
            val = self.dime_val()
            return CompoundAssignNode(name_tok.value, target_kind, idx1, idx2,
                                      member, op, val, op_tok)

    def arith_assign_op(self):
        """prods 361–366: +=, -=, *=, /=, %=, ^="""
        tok = self.current_token
        self.eat(tok.type)
        return tok.type

    # ─────────────────────────────────────────────────────────────────────────
    # I/O STATEMENTS
    # ─────────────────────────────────────────────────────────────────────────

    def ask_stmnt(self):
        """
        prod 367: ASK(SCROLL-lit, addr)!!
        prod 368: @id arr_str addr_tail  (addr)
        prod 369/370: addr_tail
        """
        tok = self.current_token
        self.eat('ASK'); self.eat('(')
        fmt_tok = self.current_token; self.eat('SCROLL-lit')
        self.eat(',')
        targets = self.addr_list()
        self.eat(')'); self.eat('!!')
        return AskNode(fmt_tok.value, targets, tok)

    def addr_list(self):
        """Collect all @id targets using addr and addr_tail."""
        targets = [self.addr()]
        prod = self.get_production('<addr-tail>')
        while prod == 612:
            self.eat(',')
            targets.append(self.addr())
            prod = self.get_production('<addr-tail>')
        return targets  # prod 613: λ

    def addr(self):
        """
        prod 368: @id arr_str addr_tail
        Returns AddressNode.
        """
        tok = self.current_token
        self.eat('@')
        name_tok = self.current_token; self.eat('id')
        target_kind, idx1, idx2, member = self.arr_str()
        return AddressNode(name_tok.value, target_kind, idx1, idx2, member, tok)

    def echo_stmnt(self):
        """
        prod 371: ECHO(SCROLL-lit args_mult)!!
        args_mult reused: prod 236 (, value args_mult) | prod 237 (λ)
        """
        tok = self.current_token
        self.eat('ECHO'); self.eat('(')
        fmt_tok = self.current_token; self.eat('SCROLL-lit')
        args = self.echo_args()
        self.eat(')'); self.eat('!!')
        return EchoNode(fmt_tok.value, args, tok)

    def echo_args(self):
        """Reuses args_mult logic: prod 236/237."""
        args = []
        prod = self.get_production('<args-mult>')
        while prod == 350:
            self.eat(',')
            args.append(self.value())
            prod = self.get_production('<args-mult>')
        return args  # prod 351: λ

    # ─────────────────────────────────────────────────────────────────────────
    # CONDITIONAL: LOOK / DROPLOOK / DROP
    # prod 372: LOOK(condition)[look_body jump_stmnt] look_tail
    # prod 373: condition → bool_val
    # prod 374/375: look_body
    # prod 376/377/378: jump_stmnt
    # prod 379/380/381: look_tail
    # ─────────────────────────────────────────────────────────────────────────

    def look_stmnt(self):
        # prod 372
        tok = self.current_token
        self.eat('LOOK'); self.eat('(')
        cond = self.condition()
        self.eat(')'); self.eat('[')
        body = self.look_body()
        jump = self.jump_stmnt()
        if jump:
            body.append(jump)
        self.eat(']')
        droplooks, drop_body = self.look_tail()
        return LookNode(cond, body, droplooks, drop_body, tok)

    def condition(self):
        """prod 373: bool_val"""
        return self.bool_val()

    def look_body(self):
        """
        prod 374: statements look_body
        prod 375: λ
        """
        stmts = []
        prod = self.get_production('<look-body>')
        while prod == 617:
            stmts.append(self.statements())
            prod = self.get_production('<look-body>')
        return stmts  # prod 618: λ

    def jump_stmnt(self):
        """
        prod 376: SAIL!!  → SailNode
        prod 377: LAND!!  → LandNode
        prod 378: λ       → None
        """
        prod = self.get_production('<jump-stmnt>')
        tok = self.current_token
        if prod == 619:
            self.eat('SAIL'); self.eat('!!')
            return SailNode(tok)
        elif prod == 620:
            self.eat('LAND'); self.eat('!!')
            return LandNode(tok)
        return None  # prod 621: λ

    def look_tail(self):
        """
        prod 379: DROPLOOK(condition)[look_body jump_stmnt] look_tail
        prod 380: DROP[look_body jump_stmnt]
        prod 381: λ
        Returns (droplooks, drop_body)
        """
        droplooks = []
        drop_body = None
        prod = self.get_production('<look-tail>')
        while prod == 622:
            self.eat('DROPLOOK'); self.eat('(')
            cond = self.condition()
            self.eat(')'); self.eat('[')
            body = self.look_body()
            jump = self.jump_stmnt()
            if jump:
                body.append(jump)
            self.eat(']')
            droplooks.append((cond, body))
            prod = self.get_production('<look-tail>')
        if prod == 623:
            self.eat('DROP'); self.eat('[')
            drop_body = self.look_body()
            jump = self.jump_stmnt()
            if jump:
                drop_body.append(jump)
            self.eat(']')
        return droplooks, drop_body  # prod 624: λ

    # ─────────────────────────────────────────────────────────────────────────
    # SWITCH: CHART
    # prod 382: CHART(chart_cond)[courses course_tail adrift_case]
    # prod 383/384: chart_cond
    # prod 385/386/387: chart_const
    # prod 388: courses
    # prod 389/390: course_body
    # prod 391/392/393: course_jmp
    # prod 394/395: course_tail
    # prod 396/397: adrift_case
    # prod 398/399: adrift_body
    # ─────────────────────────────────────────────────────────────────────────

    def chart_stmnt(self):
        # prod 382
        tok = self.current_token
        self.eat('CHART'); self.eat('(')
        expr = self.chart_cond()
        self.eat(')'); self.eat('[')
        courses = [self.courses()]
        courses.extend(self.course_tail())
        adrift_body = self.adrift_case()
        self.eat(']')
        return ChartNode(expr, courses, adrift_body, tok)

    def chart_cond(self):
        """
        prod 383: id id_tail
        prod 384: chart_const
        """
        prod = self.get_production('<chart-cond>')
        if prod == 626:
            tok = self.current_token; self.eat('id')
            return self.id_tail(tok.value, tok)
        else:
            return self.chart_const()

    def chart_const(self):
        """
        prod 385: COIN-lit
        prod 386: PARCH-lit
        prod 387: SCROLL-lit scr_id
        """
        prod = self.get_production('<chart-const>')
        tok = self.current_token
        if prod == 628:
            self.eat('COIN-lit')
            return LiteralNode('COIN', int(tok.value), tok)
        elif prod == 629:
            self.eat('PARCH-lit')
            return LiteralNode('PARCH', tok.value, tok)
        else:  # prod 630: SCROLL-lit with optional {idx}
            self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            return self.scr_id_const(base, tok)

    def courses(self):
        """prod 388: COURSE chart_const : course_body course_jmp"""
        tok = self.current_token
        self.eat('COURSE')
        val = self.chart_const()
        self.eat(':')
        body = self.course_body()
        jump = self.course_jmp()
        if jump:
            body.append(jump)
        return CourseNode(val, body, jump.__class__.__name__.replace('Node', '') if jump else None, tok)

    def course_body(self):
        """
        prod 389: statements course_body
        prod 390: λ
        """
        stmts = []
        prod = self.get_production('<course-body>')
        while prod == 632:
            stmts.append(self.statements())
            prod = self.get_production('<course-body>')
        return stmts  # prod 633: λ

    def course_jmp(self):
        """
        prod 391: SAIL!!  → SailNode
        prod 392: LAND!!  → LandNode
        prod 393: λ       → None
        """
        prod = self.get_production('<course-jmp>')
        tok = self.current_token
        if prod == 634:
            self.eat('SAIL'); self.eat('!!')
            return SailNode(tok)
        elif prod == 635:
            self.eat('LAND'); self.eat('!!')
            return LandNode(tok)
        return None  # prod 636: λ

    def course_tail(self):
        """
        prod 394: courses course_tail
        prod 395: λ
        """
        courses = []
        prod = self.get_production('<course-tail>')
        while prod == 637:
            courses.append(self.courses())
            prod = self.get_production('<course-tail>')
        return courses  # prod 638: λ

    def adrift_case(self):
        """
        prod 396: ADRIFT : adrift_body LAND!!
        prod 397: λ
        """
        prod = self.get_production('<adrift-case>')
        if prod == 639:
            self.eat('ADRIFT'); self.eat(':')
            body = self.adrift_body()
            self.eat('LAND'); self.eat('!!')
            return body
        return None  # prod 640: λ

    def adrift_body(self):
        """
        prod 398: statements adrift_body
        prod 399: λ
        """
        stmts = []
        prod = self.get_production('<adrift-body>')
        while prod == 641:
            stmts.append(self.statements())
            prod = self.get_production('<adrift-body>')
        return stmts  # prod 642: λ

    # ─────────────────────────────────────────────────────────────────────────
    # LOOPS
    # ─────────────────────────────────────────────────────────────────────────

    def hoist_stmnt(self):
        """
        prod 400: HOIST(hoist_init!! hoist_cond!! hoist_upd)[look_body jump_stmnt]
        """
        tok = self.current_token
        self.eat('HOIST'); self.eat('(')
        inits = self.hoist_init()
        self.eat('!!')
        cond = self.hoist_cond()
        self.eat('!!')
        updates = self.hoist_upd()
        self.eat(')')
        self.eat('[')
        body = self.look_body()
        jump = self.jump_stmnt()
        if jump:
            body.append(jump)
        self.eat(']')
        return HoistNode(inits, cond, updates, body, None, tok)

    def hoist_init(self):
        """
        prod 401: COIN id = COIN-lit init1_mult  (declares new loop var)
        prod 402: id arr_str = COIN-lit init2_mult  (uses existing var)
        prod 403: λ
        Returns list[HoistInitNode]
        """
        prod = self.get_production('<hoist-init>')
        inits = []
        if prod == 644:
            self.eat('COIN')
            name_tok = self.current_token; self.eat('id')
            self.eat('=')
            val_tok = self.current_token; self.eat('COIN-lit')
            inits.append(HoistInitNode(True, name_tok.value,
                                       LiteralNode('COIN', int(val_tok.value), val_tok), name_tok))
            inits.extend(self.init1_mult())
        elif prod == 645:
            name_tok = self.current_token; self.eat('id')
            self.arr_str()
            self.eat('=')
            val_tok = self.current_token; self.eat('COIN-lit')
            inits.append(HoistInitNode(False, name_tok.value,
                                       LiteralNode('COIN', int(val_tok.value), val_tok), name_tok))
            inits.extend(self.init2_mult())
        return inits  # prod 646: λ → empty list

    def init1_mult(self):
        """
        prod 404: , id = COIN-lit init1_mult
        prod 405: λ
        """
        inits = []
        prod = self.get_production('<init1-mult>')
        while prod == 647:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            self.eat('=')
            val_tok = self.current_token; self.eat('COIN-lit')
            inits.append(HoistInitNode(True, name_tok.value,
                                       LiteralNode('COIN', int(val_tok.value), val_tok), name_tok))
            prod = self.get_production('<init1-mult>')
        return inits  # prod 648: λ

    def init2_mult(self):
        """
        prod 406: , id arr_str = COIN-lit init2_mult
        prod 407: λ
        """
        inits = []
        prod = self.get_production('<init2-mult>')
        while prod == 649:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            self.arr_str()
            self.eat('=')
            val_tok = self.current_token; self.eat('COIN-lit')
            inits.append(HoistInitNode(False, name_tok.value,
                                       LiteralNode('COIN', int(val_tok.value), val_tok), name_tok))
            prod = self.get_production('<init2-mult>')
        return inits  # prod 650: λ

    def hoist_cond(self):
        """
        prod 408: dime_ope bool_arith releq_op dime_ope bool_arith3 hoist_log
        Returns a BinaryOpNode (guaranteed BOOL result).
        """
        left = self.dime_ope()
        left = self.arith_fold(left)
        op_tok = self.current_token
        op = self.releq_op()
        right = self.dime_ope()
        right = self.arith_fold(right)
        node = BinaryOpNode(left, op, right, op_tok)
        return self.hoist_log_fold(node)

    def releq_op(self):
        """
        prod 409: rel_op
        prod 410: eq_op
        """
        tok = self.current_token
        self.eat(tok.type)
        return tok.type

    def hoist_log_fold(self, node):
        """
        prod 411: log_op hoist_cond
        prod 412: λ
        """
        prod = self.get_production('<hoist-log>')
        if prod == 654:
            op_tok = self.current_token
            op = self.log_op()
            right_cond = self.hoist_cond()
            return BinaryOpNode(node, op, right_cond, op_tok)
        return node  # prod 655: λ

    def hoist_upd(self):
        """
        prod 413: upd upd_mult
        Returns list[HoistUpdateNode]
        """
        updates = [self.upd()]
        prod = self.get_production('<upd-mult>')
        while prod == 659:
            self.eat(',')
            updates.append(self.upd())
            prod = self.get_production('<upd-mult>')
        return updates  # prod 660: λ

    def upd(self):
        """
        prod 414: hoist_unary
        prod 415: hoist_assign
        """
        prod = self.get_production('<upd>')
        if prod == 657:
            return self.hoist_unary_upd()
        else:
            return self.hoist_assign_upd()

    def hoist_unary_upd(self):
        """prod 416: unary_op id arr_str"""
        op_tok = self.current_token
        op = '+#' if self.current_token.type == '+#' else '-#'
        self.eat(self.current_token.type)
        name_tok = self.current_token; self.eat('id')
        target_kind, idx1, _, member = self.arr_str()
        return HoistUpdateNode('unary', name_tok.value, target_kind, idx1, member,
                               op, None, None, op_tok)

    def hoist_assign_upd(self):
        """prod 417: id arr_str arith_assign_op coin_ope coin_arith"""
        name_tok = self.current_token; self.eat('id')
        target_kind, idx1, _, member = self.arr_str()
        op_tok = self.current_token
        op = self.arith_assign_op()
        val = self.coin_val()   # prod 417 uses coin_ope coin_arith (i.e. coin_val)
        return HoistUpdateNode('compound', name_tok.value, target_kind, idx1, member,
                               None, op, val, op_tok)

    def heave_stmnt(self):
        """prod 420: HEAVE(condition)[look_body jump_stmnt]"""
        tok = self.current_token
        self.eat('HEAVE'); self.eat('(')
        cond = self.condition()
        self.eat(')'); self.eat('[')
        body = self.look_body()
        jump = self.jump_stmnt()
        if jump:
            body.append(jump)
        self.eat(']')
        return HeaveNode(cond, body, None, tok)

    def haul_stmnt(self):
        """prod 421: HAUL[look_body jump_stmnt] HEAVE(condition)!!"""
        tok = self.current_token
        self.eat('HAUL'); self.eat('[')
        body = self.look_body()
        jump = self.jump_stmnt()
        if jump:
            body.append(jump)
        self.eat(']')
        self.eat('HEAVE'); self.eat('(')
        cond = self.condition()
        self.eat(')'); self.eat('!!')
        return HaulHeaveNode(body, cond, None, tok)

    def unary_exp(self):
        """
        prod 422: unary_op id arr_str
        Returns UnaryStmtNode.
        """
        op_tok = self.current_token
        op = self.unary_op()
        name_tok = self.current_token; self.eat('id')
        target_kind, idx1, idx2, member = self.arr_str()
        return UnaryStmtNode(op, name_tok.value, target_kind, idx1, idx2, member, op_tok)

    def unary_op(self):
        """
        prod 423: +#
        prod 424: -#
        """
        tok = self.current_token
        self.eat(tok.type)
        return tok.type

    # =========================================================================
    # EXPRESSIONS
    # =========================================================================

    # ─────────────────────────────────────────────────────────────────────────
    # VALUE — universal expression entry point
    # prod 238: id id_tail exp
    # prod 239: (value) exp
    # prod 240: digit digit_tail
    # prod 241: PARCH-lit parch_tail
    # prod 242: SCROLL-lit scr_char scroll_tail
    # prod 243: bool bool_eq bool_exp
    # ─────────────────────────────────────────────────────────────────────────

    def value(self):
        prod = self.get_production('<value>')
        if prod == 352:
            tok = self.current_token; self.eat('id')
            node = self.id_tail(tok.value, tok)
            return self.var_exp(node)
        elif prod == 353:
            self.eat('(')
            node = self.value()
            self.eat(')')
            return self.var_exp(node)
        elif prod == 354:
            node = self.var_digit()
            return self.digit_tail(node)
        elif prod == 355:
            tok = self.current_token; self.eat('PARCH-lit')
            node = LiteralNode('PARCH', tok.value, tok)
            return self.parch_eq_opt(node)
        elif prod == 356:
            tok = self.current_token; self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            node = self.scr_char_opt(base, tok)
            return self.scroll_tail(node)
        else:  # prod 357: bool bool_eq bool_exp
            return self.bool_val()

    def var_digit(self):
        """prod 162/163/164: COIN-lit | DIME-lit | - neg_digit"""
        tok = self.current_token
        if tok.type == 'COIN-lit':
            self.eat('COIN-lit')
            return LiteralNode('COIN', int(tok.value), tok)
        elif tok.type == 'DIME-lit':
            self.eat('DIME-lit')
            return LiteralNode('DIME', float(tok.value), tok)
        else:  # negative
            self.eat('-')
            inner = self.neg_digit_ope()
            return UnaryOpNode('-', inner, tok)

    def neg_digit_ope(self):
        """prod 165/166: id id_tail | (dime_val)"""
        tok = self.current_token
        if tok.type == 'id':
            self.eat('id')
            return self.id_tail(tok.value, tok)
        else:
            self.eat('(')
            val = self.dime_val()
            self.eat(')')
            return val

    def digit_tail(self, left):
        """
        prod 244: var_arith var_releq
        prod 245: λ
        """
        prod = self.get_production('<digit-tail>')
        if prod == 358:
            left = self.var_arith_fold(left)
            return self.var_releq(left)
        return left  # prod 359: λ

    def var_arith_fold(self, left):
        """
        prod 246: arith_op dime_ope var_arith
        prod 247: λ
        """
        prod = self.get_production('<var-arith>')
        if prod == 360:
            op_tok = self.current_token
            op = self.arith_op()
            right = self.dime_ope()
            return self.var_arith_fold(BinaryOpNode(left, op, right, op_tok))
        return left  # prod 361: λ

    def var_releq(self, left):
        """
        prod 248: rel_op dime_ope bool_arith2 var_logeq
        prod 249: eq_op dime_ope bool_arith3 bool_exp
        prod 250: λ
        """
        prod = self.get_production('<var-releq>')
        if prod == 362:
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_ope()
            right = self.arith_fold(right)
            node = BinaryOpNode(left, op, right, op_tok)
            return self.var_logeq(node)
        elif prod == 363:
            op_tok = self.current_token; op = self.eq_op()
            right = self.eq_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)
        return left  # prod 364: λ

    def var_logeq(self, left):
        """
        prod 251: log_op bool_ope bool_exp
        prod 252: eq_op eq_ope bool_exp
        prod 253: λ
        """
        prod = self.get_production('<logeq-var>')
        if prod == 369:
            op_tok = self.current_token
            if self.current_token.type in ('||', '&&'):
                op = self.log_op()
                right = self.bool_ope()
            else:
                op = self.eq_op()
                right = self.eq_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)
        return left  # prod 370: λ

    def var_exp(self, left):
        """
        prod 259: arith_op dime_ope var_arith var_releq
        prod 260: rel_op dime_ope bool_arith2 var_logeq
        prod 261: log_op bool_ope bool_exp
        prod 262: eq_op eq_ope bool_exp
        prod 263: & scroll_ope scroll_concat
        prod 264: λ
        Handle any operator that can follow an id or grouped expression.
        """
        prod = self.get_production('<exp>')
        if prod == 382:
            left = self.var_arith_fold(left)
            return self.var_releq(left)
        elif prod == 383:
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_ope()
            right = self.arith_fold(right)
            node = BinaryOpNode(left, op, right, op_tok)
            return self.var_logeq(node)
        elif prod == 384:
            op_tok = self.current_token; op = self.log_op()
            right = self.bool_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)
        elif prod == 385:
            op_tok = self.current_token; op = self.eq_op()
            right = self.eq_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)
        elif prod == 386:
            return self.scroll_concat_fold(left)
        return left  # prod 387: λ

    def parch_eq_opt(self, left):
        """
        prod 254: eq_op parch_val bool_exp
        prod 255: λ
        """
        prod = self.get_production('<parch-tail>')
        if prod == 375:
            op_tok = self.current_token; op = self.eq_op()
            right = self.parch_val()
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)
        return left  # prod 376: λ

    def scroll_tail(self, left):
        """
        prod 256: & scroll_ope scroll_concat
        prod 257: eq_op scroll_ope bool_exp
        prod 258: λ
        """
        prod = self.get_production('<scroll-tail>')
        if prod == 377:
            return self.scroll_concat_fold(left)
        elif prod == 378:
            op_tok = self.current_token; op = self.eq_op()
            right = self.scroll_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)
        return left  # prod 379: λ

    # ─────────────────────────────────────────────────────────────────────────
    # ID-TAIL DISAMBIGUATION
    # prod 226: {index} elmt2   → ArrayAccessNode
    # prod 227: $id             → MemberAccessNode
    # prod 228: (args)          → FuncCallNode
    # prod 229: λ               → IdentNode
    # ─────────────────────────────────────────────────────────────────────────

    def id_tail(self, name, tok):
        prod = self.get_production('<id-tail>')
        if prod == 342:
            self.eat('{')
            idx1 = self.index_expr()
            self.eat('}')
            # elmt2 (now arr-str-tail for id context): prod 346 → {index}, prod 347 → λ
            prod2 = self.get_production('<elmt2>')
            if prod2 == 346:
                self.eat('{')
                idx2 = self.index_expr()
                self.eat('}')
                return ArrayAccessNode(name, [idx1, idx2], tok)
            return ArrayAccessNode(name, [idx1], tok)
        elif prod == 343:
            self.eat('$')
            member_tok = self.current_token; self.eat('id')
            return MemberAccessNode(name, member_tok.value, tok)
        elif prod == 344:
            self.eat('(')
            args = self.args()
            self.eat(')')
            return FuncCallNode(name, args, tok)
        else:  # prod 345: λ → plain variable
            return IdentNode(name, tok)

    def index_expr(self):
        """
        prod 118: COIN-lit
        prod 119: id
        Returns a COIN expression for an array index.
        """
        prod = self.get_production('<index>')
        tok = self.current_token
        if prod == 138:
            self.eat('id')
            return IdentNode(tok.value, tok)
        else:  # prod 137
            self.eat('COIN-lit')
            return LiteralNode('COIN', int(tok.value), tok)

    def args(self):
        """
        prod 234: value args_mult
        prod 235: λ
        Returns list of argument expression nodes.
        """
        prod = self.get_production('<args>')
        if prod == 348:
            first = self.value()
            rest = self.args_mult()
            return [first] + rest
        return []  # prod 349: λ

    def args_mult(self):
        """
        prod 236: , args
        prod 237: λ
        """
        prod = self.get_production('<args-mult>')
        if prod == 350:
            self.eat(',')
            return self.args()
        return []  # prod 351: λ

    # ─────────────────────────────────────────────────────────────────────────
    # TYPE-SPECIFIC EXPRESSION BUILDERS
    # ─────────────────────────────────────────────────────────────────────────

    def coin_val(self):
        """prod 21: coin_ope coin_arith. Returns numeric ASTNode."""
        left = self.coin_ope()
        return self.arith_fold(left)

    def coin_ope(self):
        """
        prod 22: COIN-lit
        prod 23: neg neg_coin_ope
        """
        tok = self.current_token
        if tok.type == 'COIN-lit':
            self.eat('COIN-lit')
            return LiteralNode('COIN', int(tok.value), tok)
        else:
            if tok.type == '-':
                self.eat('-')
                inner = self.neg_coin_ope()
                return UnaryOpNode('-', inner, tok)
            return self.neg_coin_ope()

    def neg_coin_ope(self):
        """
        prod 26: id id_tail
        prod 27: (coin_val)
        """
        tok = self.current_token
        if tok.type == 'id':
            self.eat('id')
            return self.id_tail(tok.value, tok)
        else:
            self.eat('(')
            val = self.coin_val()
            self.eat(')')
            return val

    def dime_val(self):
        """prod 58: dime_ope dime_arith."""
        left = self.dime_ope()
        return self.arith_fold(left)

    def dime_ope(self):
        """
        prod 59: DIME-lit
        prod 60: COIN-lit
        prod 61: neg neg_dime_ope
        """
        tok = self.current_token
        if tok.type == 'DIME-lit':
            self.eat('DIME-lit')
            return LiteralNode('DIME', float(tok.value), tok)
        elif tok.type == 'COIN-lit':
            self.eat('COIN-lit')
            return LiteralNode('COIN', int(tok.value), tok)
        elif tok.type == '-':
            self.eat('-')
            inner = self.neg_dime_ope()
            return UnaryOpNode('-', inner, tok)
        else:
            return self.neg_dime_ope()

    def neg_dime_ope(self):
        """
        prod 62: id id_tail
        prod 63: (dime_val)
        """
        tok = self.current_token
        if tok.type == 'id':
            self.eat('id')
            return self.id_tail(tok.value, tok)
        else:
            self.eat('(')
            val = self.dime_val()
            self.eat(')')
            return val

    def arith_fold(self, left):
        """
        prod 28/64: arith_op operand arith_fold  (left-associative accumulator)
        prod 29/65: λ
        """
        if self.current_token and self.current_token.type in ('+', '-', '*', '/', '%', '^'):
            op_tok = self.current_token
            op = self.arith_op()
            right = self.dime_ope()
            return self.arith_fold(BinaryOpNode(left, op, right, op_tok))
        return left

    def arith_op(self):
        """prods 30–35: +, -, *, /, %, ^"""
        tok = self.current_token
        self.eat(tok.type)
        return tok.type

    def parch_val(self):
        """
        prod 88: PARCH-lit
        prod 89: id id_tail
        """
        tok = self.current_token
        if tok.type == 'PARCH-lit':
            self.eat('PARCH-lit')
            return LiteralNode('PARCH', tok.value, tok)
        else:
            self.eat('id')
            return self.id_tail(tok.value, tok)

    def scroll_val(self):
        """prod 112: scroll_ope scroll_concat"""
        first = self.scroll_ope()
        return self.scroll_concat_fold(first)

    def scroll_ope(self):
        """
        prod 113: SCROLL-lit scr_char
        prod 114: id id_tail
        prod 115: (scroll_val)
        """
        tok = self.current_token
        if tok.type == 'SCROLL-lit':
            self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            return self.scr_char_opt(base, tok)
        elif tok.type == 'id':
            self.eat('id')
            return self.id_tail(tok.value, tok)
        else:
            self.eat('(')
            val = self.scroll_val()
            self.eat(')')
            return val

    def scr_char_opt(self, base, tok):
        """
        prod 116: {index}  → ScrollCharAccessNode (returns PARCH)
        prod 117: λ        → base unchanged
        """
        prod = self.get_production('<scr-char>')
        if prod == 135:
            self.eat('{')
            idx = self.index_expr()
            self.eat('}')
            return ScrollCharAccessNode(base, idx, tok)
        return base  # prod 136: λ

    def scroll_concat_fold(self, left):
        """
        prod 120: & scroll_ope scroll_concat (left-fold into StringConcatNode)
        prod 121: λ
        """
        if self.current_token and self.current_token.type == '&':
            tok = self.current_token
            operands = [left]
            while self.current_token and self.current_token.type == '&':
                self.eat('&')
                operands.append(self.scroll_ope())
            return StringConcatNode(operands, tok)
        return left  # prod 121: λ

    # ─────────────────────────────────────────────────────────────────────────
    # BOOLEAN EXPRESSIONS
    # prod 144: bool_ope bool_exp
    # prod 145: bool bool_eq
    # prod 146: id id_tail bool_exp2
    # prod 147: (value) bool_exp2
    # prod 148: digit bool_arith rel_eq
    # prod 149: PARCH-lit eq_op parch_val
    # prod 150: SCROLL-lit scr_char eq_op scroll_val
    # prod 151/152/153/154/155/156/157/158/159: bool sub-prods
    # prod 160/161: bool_eq
    # prod 181-184: bool_exp2
    # prod 185-190: eq_ope
    # prod 198/199: bool_exp
    # ─────────────────────────────────────────────────────────────────────────

    def bool_val(self):
        """prod 144: bool_ope bool_exp"""
        left = self.bool_ope()
        return self.bool_exp_fold(left)

    def bool_ope(self):
        """
        prod 145: bool bool_eq
        prod 146: id id_tail bool_exp2
        prod 147: (value) bool_exp2
        prod 148: digit bool_arith rel_eq
        prod 149: PARCH-lit eq_op parch_val
        prod 150: SCROLL-lit scr_char eq_op scroll_val
        """
        prod = self.get_production('<bool-ope>')
        tok = self.current_token
        if prod == 174:
            self.eat('id')
            node = self.id_tail(tok.value, tok)
            return self.bool_exp2(node)
        elif prod == 175:
            self.eat('(')
            inner = self.value()
            self.eat(')')
            return self.bool_exp2(inner)
        elif prod == 176:
            return self.bool_literal_and_eq()
        elif prod == 177:
            left = self.var_digit()
            left = self.arith_fold(left)
            return self.rel_eq_fold(left)
        elif prod == 178:
            self.eat('PARCH-lit')
            left = LiteralNode('PARCH', tok.value, tok)
            op_tok = self.current_token; op = self.eq_op()
            right = self.parch_val()
            return BinaryOpNode(left, op, right, op_tok)
        elif prod == 179:
            self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            left = self.scr_char_opt(base, tok)
            op_tok = self.current_token; op = self.eq_op()
            right = self.scroll_val()
            return BinaryOpNode(left, op, right, op_tok)

    def bool_literal_and_eq(self):
        """
        prod 151/152: bool → bool_lit | not_op not_ope
        prod 153/154: bool_lit → AYE | NAY
        prod 160/161: bool_eq → eq_op bool_ope | λ
        """
        prod = self.get_production('<bool>')
        if prod == 180:
            # bool_lit
            tok = self.current_token
            val = True if tok.type == 'AYE' else False
            self.eat(tok.type)
            node = LiteralNode('BOOL', val, tok)
        elif prod == 181:
            # not_op not_ope
            node = self.not_expr()
        else:
            tok = self.current_token
            val = True if tok.type == 'AYE' else False
            self.eat(tok.type)
            node = LiteralNode('BOOL', val, tok)
        # bool_eq: prod 189 | 190
        prod_eq = self.get_production('<bool-eq>')
        if prod_eq == 189:
            op_tok = self.current_token; op = self.eq_op()
            right = self.bool_ope()
            return BinaryOpNode(node, op, right, op_tok)
        return node  # prod 190: λ

    def not_expr(self):
        """prod 152: not_op not_ope"""
        tok = self.current_token
        op = tok.type  # '!' or '!#'
        self.eat(tok.type)
        inner = self.not_operand()
        return UnaryOpNode(op, inner, tok)

    def not_operand(self):
        """
        prod 157: id id_tail
        prod 158: (bool_val)
        prod 159: bool_lit
        """
        prod = self.get_production('<not-ope>')
        tok = self.current_token
        if prod == 186:
            self.eat('id')
            return self.id_tail(tok.value, tok)
        elif prod == 187:
            self.eat('(')
            val = self.bool_val()
            self.eat(')')
            return val
        else:  # prod 188: bool_lit
            val = True if tok.type == 'AYE' else False
            self.eat(tok.type)
            return LiteralNode('BOOL', val, tok)

    def bool_exp2(self, left):
        """
        prod 181: arith_op dime_ope bool_arith rel_eq
        prod 182: rel_op dime_ope bool_arith2 bool_eq
        prod 183: eq_op eq_ope
        prod 184: λ
        """
        prod = self.get_production('<bool-exp2>')
        if prod == 212:
            left = self.arith_fold(left)
            return self.rel_eq_fold(left)
        elif prod == 213:
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_ope()
            right = self.arith_fold(right)
            node = BinaryOpNode(left, op, right, op_tok)
            # bool_eq: optional == or !=
            prod_eq = self.get_production('<bool-eq>')
            if prod_eq == 189:
                op_tok2 = self.current_token; op2 = self.eq_op()
                right2 = self.bool_ope()
                return BinaryOpNode(node, op2, right2, op_tok2)
            return node
        elif prod == 214:
            op_tok = self.current_token; op = self.eq_op()
            right = self.eq_ope()
            return BinaryOpNode(left, op, right, op_tok)
        return left  # prod 215: λ

    def rel_eq_fold(self, left):
        """
        prod 169: rel_op dime_ope bool_arith2 bool_eq
        prod 170: eq_op dime_ope bool_arith3
        """
        prod = self.get_production('<rel-eq>')
        if prod == 198:
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_ope()
            right = self.arith_fold(right)
            node = BinaryOpNode(left, op, right, op_tok)
            # bool_eq: prod 189 | 190
            prod_eq = self.get_production('<bool-eq>')
            if prod_eq == 189:
                op_tok2 = self.current_token; op2 = self.eq_op()
                right2 = self.bool_ope()
                return BinaryOpNode(node, op2, right2, op_tok2)
            return node
        elif prod == 199:
            op_tok = self.current_token; op = self.eq_op()
            right = self.dime_ope()
            right = self.arith_fold(right)
            return BinaryOpNode(left, op, right, op_tok)
        return left

    def eq_ope(self):
        """
        prod 185: id id_tail bool_exp3
        prod 186: (value) bool_exp3
        prod 187: digit bool_arith4 bool_rel
        prod 188: PARCH-lit
        prod 189: SCROLL-lit scr_char
        prod 190: bool
        """
        prod = self.get_production('<eq-ope>')
        tok = self.current_token
        if prod == 216:
            self.eat('id')
            node = self.id_tail(tok.value, tok)
            return self.bool_exp3(node)
        elif prod == 217:
            self.eat('(')
            val = self.value()
            self.eat(')')
            return self.bool_exp3(val)
        elif prod == 218:
            left = self.var_digit()
            left = self.arith_fold(left)
            # bool_rel: prod 225 rel_op | prod 226 λ
            if self.current_token and self.current_token.type in ('<', '>', '<=', '>='):
                op_tok = self.current_token; op = self.rel_op()
                right = self.dime_ope()
                right = self.arith_fold(right)
                return BinaryOpNode(left, op, right, op_tok)
            return left
        elif prod == 219:
            # eq_ope1: 220=PARCH, 221=SCROLL, 222=bool
            tok = self.current_token
            if tok.type == 'PARCH-lit':
                self.eat('PARCH-lit')
                return LiteralNode('PARCH', tok.value, tok)
            elif tok.type == 'SCROLL-lit':
                self.eat('SCROLL-lit')
                base = LiteralNode('SCROLL', tok.value, tok)
                return self.scr_char_opt(base, tok)
            else:
                return self.bool_literal_and_eq()

    def bool_exp3(self, left):
        """
        prod 195: arith_op bool_arith4 bool_rel
        prod 196: rel_op dime_ope bool_arith3
        prod 197: λ
        """
        prod = self.get_production('<bool-exp3>')
        # Handles optional arith ops and rel ops after an id/grouped expression in eq_ope context
        if self.current_token and self.current_token.type in ('+', '-', '*', '/', '%', '^'):
            left = self.arith_fold(left)
        if self.current_token and self.current_token.type in ('<', '>', '<=', '>='):
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_ope()
            right = self.arith_fold(right)
            return BinaryOpNode(left, op, right, op_tok)
        return left

    def bool_exp_fold(self, left):
        """
        prod 198: log_op bool_ope bool_exp  (left-associative fold)
        prod 199: λ
        """
        prod = self.get_production('<bool-exp>')
        if prod == 227:
            op_tok = self.current_token
            op = self.log_op()
            right = self.bool_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)
        return left  # prod 228: λ

    def rel_op(self):
        """prods 171–174: <, >, <=, >="""
        tok = self.current_token
        self.eat(tok.type)
        return tok.type

    def eq_op(self):
        """prods 179/180: ==, !="""
        tok = self.current_token
        self.eat(tok.type)
        return tok.type

    def log_op(self):
        """prods 200/201: ||, &&"""
        tok = self.current_token
        self.eat(tok.type)
        return tok.type
