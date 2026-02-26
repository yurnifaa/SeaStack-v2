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
# table as syn_parser.py. Every method corresponds to one grammar non-terminal,
# and they are named identically to their syn_parser counterparts so you can
# diff the two files side by side.
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
#   The grammar uses right-recursive "tail" rules to avoid left recursion.
#   We convert them into LEFT-associative BinaryOpNode trees by passing a
#   running left-hand accumulator through the tail methods.
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
        global_decls = self.global_dec()
        self.eat('AHOY')
        self.eat('(')
        self.eat(')')
        self.eat('[')
        local_decls = self.ahoy_local_dec()
        statements = self.ahoy_stmnts()
        self.eat(']')
        return ProgramNode(global_decls, AhoyNode(local_decls, statements, tok), tok)

    # ─────────────────────────────────────────────────────────────────────────
    # GLOBAL DECLARATIONS
    # prods 2–6
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
    # prods 7–11: eat type keyword + id, then dispatch to type-specific handler
    # ─────────────────────────────────────────────────────────────────────────

    def var_arr_func(self):
        prod = self.get_production('<var-arr-func>')
        if prod == 7:
            self.eat('COIN')
            name_tok = self.current_token; self.eat('id')
            return self.coin_var_arr_func('COIN', name_tok)
        elif prod == 8:
            self.eat('DIME')
            name_tok = self.current_token; self.eat('id')
            return self.dime_var_arr_func('DIME', name_tok)
        elif prod == 9:
            self.eat('PARCH')
            name_tok = self.current_token; self.eat('id')
            return self.parch_var_arr_func('PARCH', name_tok)
        elif prod == 10:
            self.eat('SCROLL')
            name_tok = self.current_token; self.eat('id')
            return self.scroll_var_arr_func('SCROLL', name_tok)
        elif prod == 11:
            self.eat('BOOL')
            name_tok = self.current_token; self.eat('id')
            return self.bool_var_arr_func('BOOL', name_tok)
        return []

    # ─────────────────────────────────────────────────────────────────────────
    # TYPE-SPECIFIC GLOBAL DISPATCH
    # prods 12/13, 58/59, 98/99, 122/123, 164/165
    # ─────────────────────────────────────────────────────────────────────────

    def coin_var_arr_func(self, dtype, name_tok):
        prod = self.get_production('<coin-var-arr-func>')
        nodes = []
        if prod == 12:
            nodes.extend(self.coin_var_arr(dtype, name_tok))
            self.eat('!!')
            nodes.extend(self.global_dec())
        elif prod == 13:
            nodes.append(self.coin_func(dtype, name_tok))
        return nodes

    def dime_var_arr_func(self, dtype, name_tok):
        prod = self.get_production('<dime-var-arr-func>')
        nodes = []
        if prod == 58:
            nodes.extend(self.dime_var_arr(dtype, name_tok))
            self.eat('!!')
            nodes.extend(self.global_dec())
        elif prod == 59:
            nodes.append(self.dime_func(dtype, name_tok))
        return nodes

    def parch_var_arr_func(self, dtype, name_tok):
        prod = self.get_production('<parch-var-arr-func>')
        nodes = []
        if prod == 98:
            nodes.extend(self.parch_var_arr(dtype, name_tok))
            self.eat('!!')
            nodes.extend(self.global_dec())
        elif prod == 99:
            nodes.append(self.parch_func(dtype, name_tok))
        return nodes

    def scroll_var_arr_func(self, dtype, name_tok):
        prod = self.get_production('<scroll-var-arr-func>')
        nodes = []
        if prod == 122:
            nodes.extend(self.scroll_var_arr(dtype, name_tok))
            self.eat('!!')
            nodes.extend(self.global_dec())
        elif prod == 123:
            nodes.append(self.scroll_func(dtype, name_tok))
            nodes.extend(self.sub_func())
        return nodes

    def bool_var_arr_func(self, dtype, name_tok):
        prod = self.get_production('<bool-var-arr-func>')
        nodes = []
        if prod == 164:
            nodes.extend(self.bool_var_arr(dtype, name_tok))
            self.eat('!!')
            nodes.extend(self.global_dec())
        elif prod == 165:
            nodes.append(self.bool_func(dtype, name_tok))
        return nodes

    # ─────────────────────────────────────────────────────────────────────────
    # COIN VAR/ARR
    # prods 14/15, 16, 17/18, 19/20
    # prods 39/40/41/42 (arr_tail), 43/44/45/46 (arr1), 47/48, 49/50, 51/52/53
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
        # prod 17: = coin_val coin_exp   prod 18: λ
        prod = self.get_production('<coin-init>')
        if prod == 17:
            self.eat('=')
            val = self.coin_val()
            return val
        return None  # prod 18: λ

    def coin_init_mult(self, dtype):
        prod = self.get_production('<coin-init-mult>')
        if prod == 19:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            init = self.coin_init()
            return [VarDeclNode(dtype, name_tok.value, init, name_tok)] + self.coin_init_mult(dtype)
        return []  # prod 20: λ

    def coin_arr(self, dtype, name_tok):
        # prod 39
        self.eat('{'); dim1_tok = self.current_token; self.eat('COIN-lit'); self.eat('}')
        dim1 = int(dim1_tok.value)
        return self.coin_arr_tail(dtype, name_tok, dim1)

    def coin_arr_tail(self, dtype, name_tok, dim1):
        prod = self.get_production('<coin-arr-tail>')
        if prod == 40:   # = [ arr1 ]
            self.eat('='); self.eat('[')
            values = self.coin_arr1()
            self.eat(']')
            return ArrayDeclNode(dtype, name_tok.value, [dim1], False, values, name_tok)
        elif prod == 41:  # {dim2} arr2_tail
            self.eat('{'); dim2_tok = self.current_token; self.eat('COIN-lit'); self.eat('}')
            dim2 = int(dim2_tok.value)
            return self.coin_arr2_tail(dtype, name_tok, dim1, dim2)
        else:             # prod 42: λ
            return ArrayDeclNode(dtype, name_tok.value, [dim1], False, None, name_tok)

    def coin_arr2_tail(self, dtype, name_tok, dim1, dim2):
        prod = self.get_production('<coin-arr2-tail>')
        if prod == 49:   # = [ arr2 ]
            self.eat('='); self.eat('[')
            rows = self.coin_arr2()
            self.eat(']')
            return ArrayDeclNode(dtype, name_tok.value, [dim1, dim2], True, rows, name_tok)
        else:             # prod 50: λ
            return ArrayDeclNode(dtype, name_tok.value, [dim1, dim2], True, None, name_tok)

    def coin_arr1(self):
        # prod 43: coin_arr_val cav_tail
        val = self.coin_arr_val()
        return [val] + self.cav_tail()

    def coin_arr_val(self):
        # prod 44: coin_val coin_arr_exp
        val = self.coin_val()
        return val

    def cav_tail(self):
        prod = self.get_production('<cav-tail>')
        if prod == 47:
            self.eat(',')
            return self.coin_arr1()
        return []  # prod 48: λ

    def coin_arr2(self):
        # prod 51
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
    # prods 60/61, 62, 63/64, 65/66
    # prods 75/76/77/78, 79/80/81, 87/88, 89/90, 91/92/93
    # ─────────────────────────────────────────────────────────────────────────

    def dime_var_arr(self, dtype, name_tok):
        prod = self.get_production('<dime-var-arr>')
        if prod == 60:
            return self.dime_var(dtype, name_tok)
        elif prod == 61:
            return [self.dime_arr(dtype, name_tok)]
        return []

    def dime_var(self, dtype, name_tok):
        # prod 62
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
        # prod 79
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
    # prods 100/101, 102, 103/104, 105/106
    # prods 109/110/111/112, 113/114/115, 116/117, 118/119/120
    # ─────────────────────────────────────────────────────────────────────────

    def parch_var_arr(self, dtype, name_tok):
        prod = self.get_production('<parch-var-arr>')
        if prod == 100:
            return self.parch_var(dtype, name_tok)
        elif prod == 101:
            return [self.parch_arr(dtype, name_tok)]
        return []

    def parch_var(self, dtype, name_tok):
        # prod 102
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
        # prod 109
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
    # prods 124/125, 126, 127/128, 129/130
    # prods 145/146/147/148, 149/150/151, 153/154, 155/156, 157/158/159
    # ─────────────────────────────────────────────────────────────────────────

    def scroll_var_arr(self, dtype, name_tok):
        prod = self.get_production('<scroll-var-arr>')
        if prod == 124:
            return self.scroll_var(dtype, name_tok)
        elif prod == 125:
            return [self.scroll_arr(dtype, name_tok)]
        return []

    def scroll_var(self, dtype, name_tok):
        # prod 126
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
        # prod 145
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
    # prods 166/167, 168, 169/170, 171/172
    # ─────────────────────────────────────────────────────────────────────────

    def bool_var_arr(self, dtype, name_tok):
        prod = self.get_production('<bool-var-arr>')
        if prod == 166:
            return self.bool_var(dtype, name_tok)
        elif prod == 167:
            return [self.bool_arr(dtype, name_tok)]
        return []

    def bool_var(self, dtype, name_tok):
        # prod 168
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
        # prod 260
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
    # prod 442: LOCKE <const-init>!!
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
        # prod 448: id = COIN-lit   + prod 449/450 mult
        nodes = []
        name_tok = self.current_token; self.eat('id')
        self.eat('=')
        val_tok = self.current_token; self.eat('COIN-lit')
        nodes.append(ConstDeclNode(dtype, name_tok.value,
                                   LiteralNode('COIN', int(val_tok.value), val_tok), name_tok))
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
        # prod 451: id = locke_digit   + mult
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
        # prod 457: id = PARCH-lit   + mult
        nodes = []
        name_tok = self.current_token; self.eat('id')
        self.eat('=')
        val_tok = self.current_token; self.eat('PARCH-lit')
        nodes.append(ConstDeclNode(dtype, name_tok.value,
                                   LiteralNode('PARCH', val_tok.value, val_tok), name_tok))
        prod = self.get_production('<parch-locke-mult>')
        while prod == 458:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            self.eat('=')
            val_tok = self.current_token; self.eat('PARCH-lit')
            nodes.append(ConstDeclNode(dtype, name_tok.value,
                                       LiteralNode('PARCH', val_tok.value, val_tok), name_tok))
            prod = self.get_production('<parch-locke-mult>')
        return nodes

    def scroll_locke_list(self, dtype):
        # prod 460: id = SCROLL-lit scr_id   + mult
        nodes = []
        name_tok = self.current_token; self.eat('id')
        self.eat('=')
        str_tok = self.current_token; self.eat('SCROLL-lit')
        base = LiteralNode('SCROLL', str_tok.value, str_tok)
        val = self.scr_id_const(base, str_tok)
        nodes.append(ConstDeclNode(dtype, name_tok.value, val, name_tok))
        prod = self.get_production('<scroll-locke-mult>')
        while prod == 463:
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
        """Optional {COIN-lit} after a SCROLL-lit in a LOCKE context."""
        # scr-id: prod (with {COIN-lit}) or λ — check via scr_char
        prod = self.get_production('<scr-char>')
        if prod == 135:
            self.eat('{')
            idx_tok = self.current_token; self.eat('COIN-lit')
            self.eat('}')
            return ScrollCharAccessNode(base_expr, LiteralNode('COIN', int(idx_tok.value), idx_tok), tok)
        return base_expr  # λ

    def bool_locke_list(self, dtype):
        # prod 465: id = AYE|NAY   + mult
        nodes = []
        name_tok = self.current_token; self.eat('id')
        self.eat('=')
        val_tok = self.current_token
        if self.current_token.type == 'AYE':
            self.eat('AYE'); lit = LiteralNode('BOOL', True, val_tok)
        else:
            self.eat('NAY'); lit = LiteralNode('BOOL', False, val_tok)
        nodes.append(ConstDeclNode(dtype, name_tok.value, lit, name_tok))
        prod = self.get_production('<bool-locke-mult>')
        while prod == 468:
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
    # prod 469: MAST id [ mem-dec mem-dec-tail ]!!  (global struct typedef)
    # Returns list[StructDefNode]
    # =========================================================================

    def struct(self):
        nodes = []
        # struct non-terminal uses prod numbers in the global context
        # The syn_parser uses a while-struct loop; we replicate that
        while self.current_token and self.current_token.type == 'MAST':
            # Check we're in a struct DEFINITION context (has '[' after second id)
            # Since syn_parser uses PREDICT table, we rely on it:
            prod = self.get_production('<struct>')
            if prod != 469:
                break
            self.eat('MAST')
            name_tok = self.current_token; self.eat('id')
            self.eat('[')
            members = self.mem_dec()
            members.extend(self.mem_dec_tail())
            self.eat(']')
            self.eat('!!')
            nodes.append(StructDefNode(name_tok.value, members, name_tok))
        return nodes

    def mem_dec(self):
        """prod 471→ syn uses d_type id mem_mult!! """
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
        prod 476: return_func
        prod 477: nonreturn_func
        prod 478: λ
        """
        prod = self.get_production('<sub-func>')
        if prod == 476:
            return [self.return_func()]
        elif prod == 477:
            return [self.nonreturn_func()]
        return []  # prod 478: λ

    def return_func(self):
        """
        prod 479: COIN id coin_func
        prod 480: DIME id dime_func
        prod 481: PARCH id parch_func
        prod 482: SCROLL id scroll_func  (+ sub_func)
        prod 483: BOOL id bool_func
        """
        prod = self.get_production('<return-func>')
        dtype_map = {479: 'COIN', 480: 'DIME', 481: 'PARCH', 482: 'SCROLL', 483: 'BOOL'}
        token_map = {479: 'COIN', 480: 'DIME', 481: 'PARCH', 482: 'SCROLL', 483: 'BOOL'}
        dtype = dtype_map[prod]
        self.eat(token_map[prod])
        name_tok = self.current_token; self.eat('id')
        node = self._build_return_func(dtype, name_tok)
        
        # Note: _build_return_func handles the final sub_func call 
        # to correctly mirror syn_parser chaining execution
        if prod == 482:
            self.sub_func() 
            
        return node

    def _build_return_func(self, dtype, name_tok):
        """Shared logic for a returning function body."""
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
        self.sub_func()
        return FuncDefNode(dtype, name_tok.value, params, local_decls,
                           body, return_expr, name_tok)

    def coin_func(self, dtype, name_tok):
        # prod 54
        return self._build_return_func(dtype, name_tok)

    def dime_func(self, dtype, name_tok):
        # prod 94
        return self._build_return_func(dtype, name_tok)

    def parch_func(self, dtype, name_tok):
        # prod 121
        return self._build_return_func(dtype, name_tok)

    def scroll_func(self, dtype, name_tok):
        # prod 160
        return self._build_return_func(dtype, name_tok)

    def bool_func(self, dtype, name_tok):
        # prod 301 (bool_func in the new grammar)
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
        prod 484: ABYSS id (params) [ local_dec nonret_stmnts nonret_back ]
        """
        tok = self.current_token
        self.eat('ABYSS')
        name_tok = self.current_token; self.eat('id')
        self.eat('(')
        params = self.params()
        self.eat(')')
        self.eat('[')
        local_decls = self.local_dec()
        body = self.nonret_stmnts()
        back = self.nonret_back()
        if back:
            body.append(back)
        self.eat(']')
        self.sub_func()
        return FuncDefNode('ABYSS', name_tok.value, params, local_decls, body, None, tok)

    def nonret_stmnts(self):
        """
        prod 485: nonret_stmnt nonret_tail
        """
        first = self.nonret_stmnt()
        rest = self.nonret_tail()
        return [first] + rest

    def nonret_tail(self):
        """
        prod 486: nonret_stmnts
        prod 487: λ
        """
        prod = self.get_production('<nonret-tail>')
        if prod == 486:
            return self.nonret_stmnts()
        return []  # prod 487: λ

    def nonret_back(self):
        """
        prod 488: BACK!!  → BackNode
        prod 489: λ       → None
        """
        prod = self.get_production('<nonret-back>')
        if prod == 488:
            tok = self.current_token
            self.eat('BACK'); self.eat('!!')
            return BackNode(tok)
        return None  # prod 489: λ

    # ─────────────────────────────────────────────────────────────────────────
    # PARAMETERS
    # prod 331/332, 333/334
    # ─────────────────────────────────────────────────────────────────────────

    def params(self):
        prod = self.get_production('<params>')
        if prod == 331:
            dtype = self.d_type()
            name_tok = self.current_token; self.eat('id')
            first = ParamNode(dtype, name_tok.value, name_tok)
            return [first] + self.param_mult()
        return []  # prod 332: λ

    def param_mult(self):
        prod = self.get_production('<param-mult>')
        if prod == 333:
            self.eat(',')
            return self.params()
        return []  # prod 334: λ

    def d_type(self):
        """Consume a type keyword and return it as a string."""
        tok = self.current_token
        self.eat(tok.type)
        return tok.type  # 'COIN', 'DIME', 'PARCH', 'SCROLL', or 'BOOL'

    # =========================================================================
    # LOCAL DECLARATIONS
    # prod 502/503/504 (inside functions)
    # prod 666/667/668 (inside AHOY)
    # =========================================================================

    def local_dec(self):
        """
        prod 502: var_arr local_dec
        prod 503: struct_dec
        prod 504: λ
        """
        nodes = []
        prod = self.get_production('<local-dec>')
        while prod == 502:
            nodes.extend(self.var_arr())
            prod = self.get_production('<local-dec>')
        if prod == 503:
            nodes.extend(self.struct_dec())
        return nodes  # prod 504: λ

    def ahoy_local_dec(self):
        """
        prod 666: var_arr ahoy_local_dec
        prod 667: ahoy_struct_dec
        prod 668: λ
        """
        nodes = []
        prod = self.get_production('<ahoy-local-dec>')
        while prod == 666:
            nodes.extend(self.var_arr())
            prod = self.get_production('<ahoy-local-dec>')
        if prod == 667:
            nodes.extend(self.ahoy_struct_dec())
        return nodes  # prod 668: λ

    def var_arr(self):
        """
        prod 505–509: dtype id var_arr_body!!
        The !! is consumed HERE (inside var_arr), matching the new syn_parser.
        Returns list[ASTNode]
        """
        prod = self.get_production('<var-arr>')
        if prod == 505:
            self.eat('COIN')
            name_tok = self.current_token; self.eat('id')
            nodes = self.coin_var_arr('COIN', name_tok)
            self.eat('!!')
            return nodes
        elif prod == 506:
            self.eat('DIME')
            name_tok = self.current_token; self.eat('id')
            nodes = self.dime_var_arr('DIME', name_tok)
            self.eat('!!')
            return nodes
        elif prod == 507:
            self.eat('PARCH')
            name_tok = self.current_token; self.eat('id')
            nodes = self.parch_var_arr('PARCH', name_tok)
            self.eat('!!')
            return nodes
        elif prod == 508:
            self.eat('SCROLL')
            name_tok = self.current_token; self.eat('id')
            nodes = self.scroll_var_arr('SCROLL', name_tok)
            self.eat('!!')
            return nodes
        elif prod == 509:
            self.eat('BOOL')
            name_tok = self.current_token; self.eat('id')
            nodes = self.bool_var_arr('BOOL', name_tok)
            self.eat('!!')
            return nodes
        return []

    def struct_dec(self):
        """
        prod 510: MAST id id str_dec_init!! struct_dec
        prod 511: λ
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
        prod 669: MAST id id str_dec_init!! ahoy_struct_dec
        prod 670: λ
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
        prod 512: , id str_dec_tail      (extra var names, no initializer)
        prod 513: = [ str_val str_val_tail ]  (initializer list)
        prod 514: λ
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
        prod 515: , id str_dec_tail
        prod 516: λ
        """
        prod = self.get_production('<str-dec-tail>')
        if prod == 515:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            return [name_tok.value] + self.str_dec_tail()
        return []  # prod 516: λ

    def str_val_list(self):
        """Collect str_val entries separated by commas (prod 519/520)."""
        inits = [self.str_val()]
        prod = self.get_production('<str-val-tail>')
        while prod == 519:
            self.eat(',')
            inits.append(self.str_val())
            prod = self.get_production('<str-val-tail>')
        return inits  # prod 520: λ

    def str_val(self):
        """
        prod 517: value_str       → PositionalInitNode
        prod 518: $id = value_str → NamedInitNode
        """
        prod = self.get_production('<str-val>')
        if prod == 518:
            self.eat('$')
            name_tok = self.current_token; self.eat('id')
            self.eat('=')
            val = self.value_str()
            return NamedInitNode(name_tok.value, val, name_tok)
        else:  # prod 517
            val = self.value_str()
            return PositionalInitNode(val, self.current_token)

    def value_str(self):
        """
        prod 521: id [id_tail] exp_str
        prod 522: (value_grp) exp_str
        prod 523: digit digit_tail_str
        prod 524: PARCH-lit parch_tail_str
        prod 525: SCROLL-lit [scr_char] scroll_tail_str
        prod 526: bool logeq_str
        Note: value_str is used inside struct initializers. We build a full
        expression node just like value(), but str-context tails are no-ops
        for AST construction (they don't change the type of node returned).
        """
        prod = self.get_production('<value-str>')
        if prod == 521:
            tok = self.current_token; self.eat('id')
            node = self.id_tail(tok.value, tok)
            # exp_str tail: same as exp() but in str context — delegate to value's exp logic
            return self._exp_str(node)
        elif prod == 522:
            self.eat('(')
            node = self.value_grp()
            self.eat(')')
            return self._exp_str(node)
        elif prod == 523:
            node = self.var_digit()
            return self._digit_tail_str(node)
        elif prod == 524:
            tok = self.current_token; self.eat('PARCH-lit')
            node = LiteralNode('PARCH', tok.value, tok)
            return self._parch_tail_str(node)
        elif prod == 525:
            tok = self.current_token; self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            node = self.scr_char_opt(base, tok)
            return self._scroll_tail_str(node)
        else:  # prod 526: bool
            return self.bool_val()

    # value_str tails — delegate to the unified expression builders
    def _exp_str(self, left):
        """exp_str: same semantics as exp(); reuses exp() logic."""
        return self._exp_shared(left)

    def _digit_tail_str(self, node):
        prod = self.get_production('<digit-tail-str>')
        if prod == 527:
            node = self.arith_fold(node)
            return self._releq_str(node)
        return node  # prod 528: λ

    def _releq_str(self, left):
        prod = self.get_production('<releq-str>')
        if prod == 531:
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_ope(); right = self.arith_fold(right)
            node = BinaryOpNode(left, op, right, op_tok)
            return self._logeq_str(node)
        elif prod == 532:
            op_tok = self.current_token; op = self.eq_op()
            right = self.dime_ope(); right = self.arith_fold(right)
            return BinaryOpNode(left, op, right, op_tok)
        return left  # prod 533: λ

    def _logeq_str(self, left):
        prod = self.get_production('<logeq-str>')
        if prod == 538:
            op_tok = self.current_token
            op = self._logeq_op()
            right = self._log_ope_str()
            return BinaryOpNode(left, op, right, op_tok)
        return left  # prod 539: λ

    def _logeq_op(self):
        tok = self.current_token
        self.eat(tok.type)
        return tok.type

    def _log_ope_str(self):
        """log_ope in str/arr context — same as bool_ope."""
        return self.bool_ope()

    def _parch_tail_str(self, left):
        prod = self.get_production('<parch-tail-str>')
        if prod == 540:
            op_tok = self.current_token; op = self.eq_op()
            right_tok = self.current_token; self.eat('PARCH-lit')
            right = LiteralNode('PARCH', right_tok.value, right_tok)
            return BinaryOpNode(left, op, right, op_tok)
        return left  # prod 541: λ

    def _scroll_tail_str(self, left):
        prod = self.get_production('<scroll-tail-str>')
        if prod == 542:
            return self.scroll_concat_fold(left)
        elif prod == 543:
            op_tok = self.current_token; op = self.eq_op()
            right = self.scroll_val()
            return BinaryOpNode(left, op, right, op_tok)
        return left  # prod 544: λ

    # =========================================================================
    # STATEMENTS
    # =========================================================================

    def ret_stmnts(self):
        """
        prod 340: statements ret_stmnts
        prod 341: λ
        """
        stmts = []
        prod = self.get_production('<ret-stmnts>')
        while prod == 340:
            stmts.append(self.statements())
            prod = self.get_production('<ret-stmnts>')
        return stmts

    def ahoy_stmnts(self):
        """
        prod 671: ahoy_stmnt ahoy_tail
        """
        stmts = []
        prod = self.get_production('<ahoy-stmnts>')
        if prod == 671:
            stmts.append(self.ahoy_stmnt())
            stmts.extend(self.ahoy_tail())
        return stmts

    def ahoy_tail(self):
        """
        prod 672: ahoy_stmnts
        prod 673: λ
        """
        prod = self.get_production('<ahoy-tail>')
        if prod == 672:
            return self.ahoy_stmnts()
        return []  # prod 673: λ

    def ahoy_stmnt(self):
        """
        prod 674–682: same statement types as statements(), plus ahoy_look_tail.
        Delegates to the unified statement builders.
        """
        prod = self.get_production('<ahoy-stmnt>')
        if prod == 674:
            tok = self.current_token
            name_tok = self.current_token; self.eat('id')
            node = self.assign_tail(name_tok)
            self.eat('!!')
            return node
        elif prod == 675:
            return self.ask_stmnt()
        elif prod == 676:
            return self.echo_stmnt()
        elif prod == 677:
            return self._look_stmnt_with_tail('ahoy')
        elif prod == 678:
            return self.chart_stmnt()
        elif prod == 679:
            return self.hoist_stmnt()
        elif prod == 680:
            return self.heave_stmnt()
        elif prod == 681:
            return self.haul_stmnt()
        elif prod == 682:
            node = self.unary_exp()
            self.eat('!!')
            return node

    def nonret_stmnt(self):
        """
        prod 490–498: statement types in a non-returning function.
        """
        prod = self.get_production('<nonret-stmnt>')
        if prod == 490:
            name_tok = self.current_token; self.eat('id')
            node = self.assign_tail(name_tok)
            self.eat('!!')
            return node
        elif prod == 491:
            return self.ask_stmnt()
        elif prod == 492:
            return self.echo_stmnt()
        elif prod == 493:
            return self._look_stmnt_with_tail('nonret')
        elif prod == 494:
            return self.chart_stmnt()
        elif prod == 495:
            return self.hoist_stmnt()
        elif prod == 496:
            return self.heave_stmnt()
        elif prod == 497:
            return self.haul_stmnt()
        elif prod == 498:
            node = self.unary_exp()
            self.eat('!!')
            return node

    def statements(self):
        """
        prod 553–561: dispatch to correct statement type.
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
    # prod 562: id assign_tail!!
    # ─────────────────────────────────────────────────────────────────────────

    def assign_stmnt(self):
        # prod 562
        name_tok = self.current_token; self.eat('id')
        node = self.assign_tail(name_tok)
        self.eat('!!')
        return node

    def assign_tail(self, name_tok):
        """
        prod 563: [arr_str] assign_body   (var/array/member assignment)
        prod 564: (args)                  (function call statement)
        Note: arr_str is now OPTIONAL — the syn_parser checks for { or $ first.
        """
        prod = self.get_production('<assign-tail>')
        if prod == 563:
            # arr_str is optional; check if { or $ is present
            if self.current_token and self.current_token.type in ('{', '$'):
                target_kind, idx1, idx2, member = self.arr_str()
            else:
                target_kind, idx1, idx2, member = 'var', None, None, None
            return self.assign_body(name_tok, target_kind, idx1, idx2, member)
        elif prod == 564:
            self.eat('(')
            args = self.args()
            self.eat(')')
            return FuncCallStmtNode(FuncCallNode(name_tok.value, args, name_tok), name_tok)

    def arr_str(self):
        """
        prod 565: {index} arr_str_tail → array access
        prod 566: $id                  → member access
        prod 567: λ                    → plain variable
        Returns (target_kind, index1, index2, member)
        """
        prod = self.get_production('<arr-str>')
        if prod == 565:
            self.eat('{')
            idx1 = self.index_expr()
            self.eat('}')
            # arr_str_tail: prod 568 → {index}, prod 569 → λ
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
        prod 570: = value_as
        prod 571: arith_assign_op dime_ret_val
        """
        prod = self.get_production('<assign-body>')
        if prod == 570:
            self.eat('=')
            val = self.value_as()
            return AssignNode(name_tok.value, target_kind, idx1, idx2, member, val, name_tok)
        elif prod == 571:
            op_tok = self.current_token
            op = self.arith_assign_op()
            val = self.dime_val()
            return CompoundAssignNode(name_tok.value, target_kind, idx1, idx2,
                                      member, op, val, op_tok)

    def value_as(self):
        """
        Assignment RHS — semantically equivalent to value().
        prod 572–577 mirror value()'s prods 352–357.
        """
        prod = self.get_production('<value-as>')
        if prod == 572:
            tok = self.current_token; self.eat('id')
            node = self.id_tail(tok.value, tok)
            return self._exp_as(node)
        elif prod == 573:
            self.eat('(')
            node = self.value_grp()
            self.eat(')')
            return self._exp_as(node)
        elif prod == 574:
            node = self.var_digit()
            return self._digit_tail_as(node)
        elif prod == 575:
            tok = self.current_token; self.eat('PARCH-lit')
            node = LiteralNode('PARCH', tok.value, tok)
            return self._parch_tail_as(node)
        elif prod == 576:
            tok = self.current_token; self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            node = self.scr_char_opt(base, tok)
            return self._scroll_tail_as(node)
        else:  # prod 577: bool logeq_as
            return self.bool_val()

    def _exp_as(self, left):
        """exp-as: same semantics as exp(); reuses shared logic."""
        return self._exp_shared(left)

    def _digit_tail_as(self, node):
        prod = self.get_production('<digit-tail-as>')
        if prod == 578:
            node = self.arith_fold(node)
            return self._releq_as(node)
        return node  # prod 579: λ

    def _releq_as(self, left):
        prod = self.get_production('<releq-as>')
        if prod == 582:
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_ope(); right = self.arith_fold(right)
            node = BinaryOpNode(left, op, right, op_tok)
            return self._logeq_as(node)
        elif prod == 583:
            op_tok = self.current_token; op = self.eq_op()
            right = self.dime_ope(); right = self.arith_fold(right)
            return BinaryOpNode(left, op, right, op_tok)
        return left  # prod 584: λ

    def _logeq_as(self, left):
        prod = self.get_production('<logeq-as>')
        if prod == 589:
            op_tok = self.current_token; op = self._logeq_op()
            right = self.bool_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)
        return left  # prod 590: λ

    def _parch_tail_as(self, left):
        prod = self.get_production('<parch-tail-as>')
        if prod == 591:
            op_tok = self.current_token; op = self.eq_op()
            right_tok = self.current_token; self.eat('PARCH-lit')
            right = LiteralNode('PARCH', right_tok.value, right_tok)
            return BinaryOpNode(left, op, right, op_tok)
        return left  # prod 592: λ

    def _scroll_tail_as(self, left):
        prod = self.get_production('<scroll-tail-as>')
        if prod == 593:
            return self.scroll_concat_fold(left)
        elif prod == 594:
            op_tok = self.current_token; op = self.eq_op()
            right = self.scroll_val()
            return BinaryOpNode(left, op, right, op_tok)
        return left  # prod 595: λ

    def concat_as(self):
        # <concat-as>
        prod = self.get_production('<concat-as>')
        if prod == 596:
            self.eat('&')
            self.scroll_val()
            self.concat_as()
        elif prod == 597:
            pass  # Lambda

    def exp_as(self):
        # <exp-as>
        prod = self.get_production('<exp-as>')
        if prod == 598:
            self.dime_arith()
            self.arith_as()
            self.releq_as()
        elif prod == 599:
            self.rel()
            self.arith_as2()
            self.logeq_as()
        elif prod == 600:
            self.log_op()
            self.bool_ope_ret()
            self.bool_exp_ret()
        elif prod == 601:
            self.eq_op()
            self.eq_ope_ret()
            self.bool_exp_ret()
        elif prod == 602:
            self.eat('&')
            self.scroll_val()
            self.concat_as()
        elif prod == 603:
            pass  # Lambda

    def arith_assign_op(self):
        """prods 604–609: +=, -=, *=, /=, %=, ^="""
        tok = self.current_token
        self.eat(tok.type)
        return tok.type

    # ─────────────────────────────────────────────────────────────────────────
    # I/O STATEMENTS
    # ─────────────────────────────────────────────────────────────────────────

    def ask_stmnt(self):
        """prod 610: ASK(SCROLL-lit, addr)!!"""
        tok = self.current_token
        self.eat('ASK'); self.eat('(')
        fmt_tok = self.current_token; self.eat('SCROLL-lit')
        self.eat(',')
        targets = self.addr_list()
        self.eat(')'); self.eat('!!')
        return AskNode(fmt_tok.value, targets, tok)

    def addr_list(self):
        """Collect all @id targets using addr and addr_tail (prod 612/613)."""
        targets = [self.addr()]
        prod = self.get_production('<addr-tail>')
        while prod == 612:
            self.eat(',')
            targets.append(self.addr())
            prod = self.get_production('<addr-tail>')
        return targets  # prod 613: λ

    def addr(self):
        """
        prod 611: @id [arr_str] addr_tail
        """
        tok = self.current_token
        self.eat('@')
        name_tok = self.current_token; self.eat('id')
        # arr_str is optional — check for { or $
        if self.current_token and self.current_token.type in ('{', '$'):
            target_kind, idx1, idx2, member = self.arr_str()
        else:
            target_kind, idx1, idx2, member = 'var', None, None, None
        return AddressNode(name_tok.value, target_kind, idx1, idx2, member, tok)

    def echo_stmnt(self):
        """prod 614: ECHO(SCROLL-lit args_mult)!!"""
        tok = self.current_token
        self.eat('ECHO'); self.eat('(')
        fmt_tok = self.current_token; self.eat('SCROLL-lit')
        args = self.echo_args()
        self.eat(')'); self.eat('!!')
        return EchoNode(fmt_tok.value, args, tok)

    def echo_args(self):
        """Reuses args_mult logic: prod 350/351."""
        args = []
        prod = self.get_production('<args-mult>')
        while prod == 350:
            self.eat(',')
            args.append(self.args_inner())
            prod = self.get_production('<args-mult>')
        return args  # prod 351: λ

    def args_inner(self):
        """Single arg: prod 348 value args_mult | 349 λ — returns one value node."""
        return self.value()

    # ─────────────────────────────────────────────────────────────────────────
    # CONDITIONAL: LOOK / DROPLOOK / DROP
    # ─────────────────────────────────────────────────────────────────────────

    def look_stmnt(self):
        # prod 615
        return self._look_stmnt_with_tail('ret')

    def _look_stmnt_with_tail(self, context):
        """
        Shared LOOK builder used by statements(), ahoy_stmnt(), nonret_stmnt().
        context: 'ret' | 'ahoy' | 'nonret' — selects the correct look_tail non-terminal.
        """
        tok = self.current_token
        self.eat('LOOK'); self.eat('(')
        cond = self.condition()
        self.eat(')'); self.eat('[')
        body = self.look_body()
        jump = self.jump_stmnt()
        if jump:
            body.append(jump)
        self.eat(']')
        if context == 'ahoy':
            droplooks, drop_body = self.ahoy_look_tail()
        elif context == 'nonret':
            droplooks, drop_body = self.nonret_look_tail()
        else:
            droplooks, drop_body = self.look_tail()
        return LookNode(cond, body, droplooks, drop_body, tok)

    def condition(self):
        """prod 616: bool_grp_val"""
        return self.bool_grp_val()

    def look_body(self):
        """
        prod 617: statements look_body
        prod 618: λ
        """
        stmts = []
        prod = self.get_production('<look-body>')
        while prod == 617:
            stmts.append(self.statements())
            prod = self.get_production('<look-body>')
        return stmts  # prod 618: λ

    def jump_stmnt(self):
        """
        prod 619: SAIL!!  → SailNode
        prod 620: LAND!!  → LandNode
        prod 621: λ       → None
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
        prod 622: DROPLOOK(...)[...] look_tail
        prod 623: DROP[...]
        prod 624: λ
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

    def ahoy_look_tail(self):
        """
        prod 683: DROPLOOK(...)[...] ahoy_look_tail
        prod 684: DROP[...]
        prod 685: λ
        """
        droplooks = []
        drop_body = None
        prod = self.get_production('<ahoy-look-tail>')
        while prod == 683:
            self.eat('DROPLOOK'); self.eat('(')
            cond = self.condition()
            self.eat(')'); self.eat('[')
            body = self.look_body()
            jump = self.jump_stmnt()
            if jump:
                body.append(jump)
            self.eat(']')
            droplooks.append((cond, body))
            prod = self.get_production('<ahoy-look-tail>')
        if prod == 684:
            self.eat('DROP'); self.eat('[')
            drop_body = self.look_body()
            jump = self.jump_stmnt()
            if jump:
                drop_body.append(jump)
            self.eat(']')
        return droplooks, drop_body  # prod 685: λ

    def nonret_look_tail(self):
        """
        prod 499: DROPLOOK(...)[...] nonret_look_tail
        prod 500: DROP[...]
        prod 501: λ
        """
        droplooks = []
        drop_body = None
        prod = self.get_production('<nonret-look-tail>')
        while prod == 499:
            self.eat('DROPLOOK'); self.eat('(')
            cond = self.condition()
            self.eat(')'); self.eat('[')
            body = self.look_body()
            jump = self.jump_stmnt()
            if jump:
                body.append(jump)
            self.eat(']')
            droplooks.append((cond, body))
            prod = self.get_production('<nonret-look-tail>')
        if prod == 500:
            self.eat('DROP'); self.eat('[')
            drop_body = self.look_body()
            jump = self.jump_stmnt()
            if jump:
                drop_body.append(jump)
            self.eat(']')
        return droplooks, drop_body  # prod 501: λ

    # ─────────────────────────────────────────────────────────────────────────
    # SWITCH: CHART
    # prod 625–642
    # ─────────────────────────────────────────────────────────────────────────

    def chart_stmnt(self):
        # prod 625
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
        prod 626: id [id_tail]
        prod 627: chart_const
        """
        prod = self.get_production('<chart-cond>')
        if prod == 626:
            tok = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                return self.id_tail(tok.value, tok)
            return IdentNode(tok.value, tok)
        else:
            return self.chart_const()

    def chart_const(self):
        """
        prod 628: COIN-lit
        prod 629: PARCH-lit
        prod 630: SCROLL-lit [scr_id]
        """
        prod = self.get_production('<chart-const>')
        tok = self.current_token
        if prod == 628:
            self.eat('COIN-lit')
            return LiteralNode('COIN', int(tok.value), tok)
        elif prod == 629:
            self.eat('PARCH-lit')
            return LiteralNode('PARCH', tok.value, tok)
        else:  # prod 630
            self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            # optional {COIN-lit} char index
            if self.current_token and self.current_token.type == '{':
                self.eat('{')
                idx_tok = self.current_token; self.eat('COIN-lit')
                self.eat('}')
                return ScrollCharAccessNode(base, LiteralNode('COIN', int(idx_tok.value), idx_tok), tok)
            return base

    def courses(self):
        """prod 631: COURSE chart_const : course_body course_jmp"""
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
        """prod 632: statements course_body | prod 633: λ"""
        stmts = []
        prod = self.get_production('<course-body>')
        while prod == 632:
            stmts.append(self.statements())
            prod = self.get_production('<course-body>')
        return stmts

    def course_jmp(self):
        """prod 634: SAIL!! | prod 635: LAND!! | prod 636: λ"""
        prod = self.get_production('<course-jmp>')
        tok = self.current_token
        if prod == 634:
            self.eat('SAIL'); self.eat('!!')
            return SailNode(tok)
        elif prod == 635:
            self.eat('LAND'); self.eat('!!')
            return LandNode(tok)
        return None

    def course_tail(self):
        """prod 637: courses course_tail | prod 638: λ"""
        courses = []
        prod = self.get_production('<course-tail>')
        while prod == 637:
            courses.append(self.courses())
            prod = self.get_production('<course-tail>')
        return courses

    def adrift_case(self):
        """prod 639: ADRIFT : adrift_body LAND!! | prod 640: λ"""
        prod = self.get_production('<adrift-case>')
        if prod == 639:
            self.eat('ADRIFT'); self.eat(':')
            body = self.adrift_body()
            self.eat('LAND'); self.eat('!!')
            return body
        return None

    def adrift_body(self):
        """prod 641: statements adrift_body | prod 642: λ"""
        stmts = []
        prod = self.get_production('<adrift-body>')
        while prod == 641:
            stmts.append(self.statements())
            prod = self.get_production('<adrift-body>')
        return stmts

    # ─────────────────────────────────────────────────────────────────────────
    # LOOPS
    # ─────────────────────────────────────────────────────────────────────────

    def hoist_stmnt(self):
        """prod 643: HOIST(hoist_init!! hoist_cond!! hoist_upd)[look_body jump_stmnt]"""
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
        prod 644: COIN id = COIN-lit init1_mult  (new loop var)
        prod 645: id [arr_str] = COIN-lit init2_mult  (existing var)
        prod 646: λ
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
            if self.current_token and self.current_token.type in ('{', '$'):
                self.arr_str()  # consumed for syntax; no index stored in HoistInitNode
            self.eat('=')
            val_tok = self.current_token; self.eat('COIN-lit')
            inits.append(HoistInitNode(False, name_tok.value,
                                       LiteralNode('COIN', int(val_tok.value), val_tok), name_tok))
            inits.extend(self.init2_mult())
        return inits  # prod 646: λ → empty list

    def init1_mult(self):
        """prod 647: , id = COIN-lit init1_mult | prod 648: λ"""
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
        return inits

    def init2_mult(self):
        """prod 649: , id [arr_str] = COIN-lit init2_mult | prod 650: λ"""
        inits = []
        prod = self.get_production('<init2-mult>')
        while prod == 649:
            self.eat(',')
            name_tok = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$'):
                self.arr_str()
            self.eat('=')
            val_tok = self.current_token; self.eat('COIN-lit')
            inits.append(HoistInitNode(False, name_tok.value,
                                       LiteralNode('COIN', int(val_tok.value), val_tok), name_tok))
            prod = self.get_production('<init2-mult>')
        return inits

    def hoist_cond(self):
        """
        prod 651: dime_val bool_arith releq_op dime_val bool_arith3_grp hoist_log
        Returns a BinaryOpNode (guaranteed BOOL result).
        """
        left = self.dime_val()
        # bool_arith: optional extra arith ops — already folded into dime_val
        op_tok = self.current_token
        op = self.releq_op()
        right = self.dime_val()
        node = BinaryOpNode(left, op, right, op_tok)
        return self.hoist_log_fold(node)

    def releq_op(self):
        """prod 652: rel_op | prod 653: eq_op"""
        tok = self.current_token
        self.eat(tok.type)
        return tok.type

    def hoist_log_fold(self, node):
        """
        prod 654: log_op hoist_cond
        prod 655: λ
        """
        prod = self.get_production('<hoist-log>')
        if prod == 654:
            op_tok = self.current_token
            op = self.log_op()
            right_cond = self.hoist_cond()
            return BinaryOpNode(node, op, right_cond, op_tok)
        return node  # prod 655: λ

    def hoist_upd(self):
        """prod 656: upd upd_mult — Returns list[HoistUpdateNode]"""
        updates = [self.upd()]
        prod = self.get_production('<upd-mult>')
        while prod == 659:
            self.eat(',')
            updates.append(self.upd())
            prod = self.get_production('<upd-mult>')
        return updates  # prod 660: λ

    def upd(self):
        """
        prod 657: unary_op id [arr_str]
        prod 658: id [arr_str] arith_assign_op dime_grp_val
        """
        prod = self.get_production('<upd>')
        if prod == 657:
            return self.hoist_unary_upd()
        else:
            return self.hoist_assign_upd()

    def hoist_unary_upd(self):
        """prod 657: unary_op id [arr_str]"""
        op_tok = self.current_token
        op = '+#' if self.current_token.type == '+#' else '-#'
        self.eat(self.current_token.type)
        name_tok = self.current_token; self.eat('id')
        if self.current_token and self.current_token.type in ('{', '$'):
            target_kind, idx1, _, member = self.arr_str()
        else:
            target_kind, idx1, member = 'var', None, None
        return HoistUpdateNode('unary', name_tok.value, target_kind, idx1, member,
                               op, None, None, op_tok)

    def hoist_assign_upd(self):
        """prod 658: id [arr_str] arith_assign_op dime_grp_val"""
        name_tok = self.current_token; self.eat('id')
        if self.current_token and self.current_token.type in ('{', '$'):
            target_kind, idx1, _, member = self.arr_str()
        else:
            target_kind, idx1, member = 'var', None, None
        op_tok = self.current_token
        op = self.arith_assign_op()
        val = self.dime_val()
        return HoistUpdateNode('compound', name_tok.value, target_kind, idx1, member,
                               None, op, val, op_tok)

    def heave_stmnt(self):
        """prod 661: HEAVE(condition)[look_body jump_stmnt]"""
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
        """prod 662: HAUL[look_body jump_stmnt] HEAVE(condition)!!"""
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
        """prod 663: unary_op id [arr_str] — Returns UnaryStmtNode."""
        op_tok = self.current_token
        op = self.unary_op()
        name_tok = self.current_token; self.eat('id')
        if self.current_token and self.current_token.type in ('{', '$'):
            target_kind, idx1, idx2, member = self.arr_str()
        else:
            target_kind, idx1, idx2, member = 'var', None, None, None
        return UnaryStmtNode(op, name_tok.value, target_kind, idx1, idx2, member, op_tok)

    def unary_op(self):
        """prod 664: +# | prod 665: -#"""
        tok = self.current_token
        self.eat(tok.type)
        return tok.type

    # =========================================================================
    # EXPRESSIONS
    # =========================================================================

    # ─────────────────────────────────────────────────────────────────────────
    # VALUE — universal expression entry point
    # prod 352: id [id_tail] exp
    # prod 353: (value_grp) exp
    # prod 354: digit digit_tail
    # prod 355: PARCH-lit parch_tail
    # prod 356: SCROLL-lit [scr_char] scroll_tail
    # prod 357: bool logeq_var
    # ─────────────────────────────────────────────────────────────────────────

    def value(self):
        prod = self.get_production('<value>')
        if prod == 352:
            tok = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                node = self.id_tail(tok.value, tok)
            else:
                node = IdentNode(tok.value, tok)
            return self._exp_shared(node)
        elif prod == 353:
            self.eat('(')
            node = self.value_grp()
            self.eat(')')
            return self._exp_shared(node)
        elif prod == 354:
            node = self.var_digit()
            return self._digit_tail_var(node)
        elif prod == 355:
            tok = self.current_token; self.eat('PARCH-lit')
            node = LiteralNode('PARCH', tok.value, tok)
            return self._parch_tail_var(node)
        elif prod == 356:
            tok = self.current_token; self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            node = self.scr_char_opt(base, tok)
            return self._scroll_tail_var(node)
        else:  # prod 357: bool logeq_var
            return self.bool_val()

    def _digit_tail_var(self, node):
        prod = self.get_production('<digit-tail>')
        if prod == 358:
            node = self.arith_fold(node)
            return self._releq_var(node)
        return node  # prod 359: λ

    def _releq_var(self, left):
        prod = self.get_production('<releq-var>')
        if prod == 362:
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_ope(); right = self.arith_fold(right)
            node = BinaryOpNode(left, op, right, op_tok)
            return self._logeq_var(node)
        elif prod == 363:
            op_tok = self.current_token; op = self.eq_op()
            right = self.dime_ope(); right = self.arith_fold(right)
            node = BinaryOpNode(left, op, right, op_tok)
            return self._log_var(node)
        return left  # prod 364: λ

    def _logeq_var(self, left):
        prod = self.get_production('<logeq-var>')
        if prod == 369:
            op_tok = self.current_token; op = self._logeq_op()
            right = self.bool_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self._log_var(node)
        return left  # prod 370: λ

    def _log_var(self, left):
        prod = self.get_production('<log-var>')
        if prod == 373:
            op_tok = self.current_token; op = self.log_op()
            right = self.bool_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self._log_var(node)
        return left  # prod 374: λ

    def _parch_tail_var(self, left):
        prod = self.get_production('<parch-tail>')
        if prod == 375:
            op_tok = self.current_token; op = self.eq_op()
            right_tok = self.current_token; self.eat('PARCH-lit')
            right = LiteralNode('PARCH', right_tok.value, right_tok)
            node = BinaryOpNode(left, op, right, op_tok)
            return self._log_var(node)
        return left  # prod 376: λ

    def _scroll_tail_var(self, left):
        prod = self.get_production('<scroll-tail>')
        if prod == 377:
            return self.scroll_concat_fold(left)
        elif prod == 378:
            op_tok = self.current_token; op = self.eq_op()
            right = self.scroll_val()
            node = BinaryOpNode(left, op, right, op_tok)
            return self._log_var(node)
        return left  # prod 379: λ

    def _exp_shared(self, left):
        """
        exp: prod 382–387
        Handles operator tails after an id or parenthesized expression.
        """
        prod = self.get_production('<exp>')
        if prod == 382:
            left = self.arith_fold(left)
            return self._releq_var(left)
        elif prod == 383:
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_ope(); right = self.arith_fold(right)
            node = BinaryOpNode(left, op, right, op_tok)
            return self._logeq_var(node)
        elif prod == 384:
            op_tok = self.current_token; op = self.log_op()
            right = self.bool_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self._log_var(node)
        elif prod == 385:
            op_tok = self.current_token; op = self.eq_op()
            right = self._eq_var()
            node = BinaryOpNode(left, op, right, op_tok)
            return self._log_var(node)
        elif prod == 386:
            return self.scroll_concat_fold(left)
        return left  # prod 387: λ

    def _eq_var(self):
        """eq_var: prod 402–405 — the RHS of an == or != in a general expression."""
        prod = self.get_production('<eq-var>')
        if prod == 402:
            tok = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                node = self.id_tail(tok.value, tok)
            else:
                node = IdentNode(tok.value, tok)
            node = self.arith_fold(node)
            return self._rel_var(node)
        elif prod == 403:
            self.eat('(')
            node = self.value_grp()
            self.eat(')')
            node = self.arith_fold(node)
            return self._rel_var(node)
        elif prod == 404:
            node = self.var_digit()
            node = self.arith_fold(node)
            return self._rel_var(node)
        else:  # prod 405: eq_ope1
            return self._eq_ope1()

    def _rel_var(self, left):
        prod = self.get_production('<rel-var>')
        if prod == 408:
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_ope(); right = self.arith_fold(right)
            return BinaryOpNode(left, op, right, op_tok)
        return left  # prod 409: λ

    def value_grp(self):
        """
        value_grp: prod 410–415 — same as value() but used inside parentheses.
        We reuse the same builders; the grp-context tails are no-ops for AST.
        """
        prod = self.get_production('<value-grp>')
        if prod == 410:
            tok = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                node = self.id_tail(tok.value, tok)
            else:
                node = IdentNode(tok.value, tok)
            return self._exp_grp(node)
        elif prod == 411:
            self.eat('(')
            node = self.value_grp()
            self.eat(')')
            return self._exp_grp(node)
        elif prod == 412:
            node = self.var_digit()
            return self._digit_tail_grp(node)
        elif prod == 413:
            tok = self.current_token; self.eat('PARCH-lit')
            node = LiteralNode('PARCH', tok.value, tok)
            return self._parch_tail_grp(node)
        elif prod == 414:
            tok = self.current_token; self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            node = self.scr_char_opt(base, tok)
            return self._scroll_tail_grp(node)
        else:  # prod 415: bool logeq_grp
            return self.bool_val()

    def _exp_grp(self, left):
        """exp_grp: prod 436–441"""
        prod = self.get_production('<exp-grp>')
        if prod == 436:
            left = self.arith_fold(left)
            return self._releqvar_grp(left)
        elif prod == 437:
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_ope(); right = self.arith_fold(right)
            node = BinaryOpNode(left, op, right, op_tok)
            return self._logeq_grp(node)
        elif prod == 438:
            op_tok = self.current_token; op = self.log_op()
            right = self.bool_grp_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self._bool_exp_grp(node)
        elif prod == 439:
            op_tok = self.current_token; op = self.eq_op()
            right = self._eq_ope_grp()
            node = BinaryOpNode(left, op, right, op_tok)
            return self._bool_exp_grp(node)
        elif prod == 440:
            return self.scroll_concat_fold(left)
        return left  # prod 441: λ

    def _digit_tail_grp(self, node):
        prod = self.get_production('<digit-tail-grp>')
        if prod == 416:
            node = self.arith_fold(node)
            return self._releqvar_grp(node)
        return node  # prod 417: λ

    def _releqvar_grp(self, left):
        prod = self.get_production('<releqvar-grp>')
        if prod == 420:
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_ope(); right = self.arith_fold(right)
            node = BinaryOpNode(left, op, right, op_tok)
            return self._logeq_grp(node)
        elif prod == 421:
            op_tok = self.current_token; op = self.eq_op()
            right = self.dime_ope(); right = self.arith_fold(right)
            return BinaryOpNode(left, op, right, op_tok)
        return left  # prod 422: λ

    def _logeq_grp(self, left):
        prod = self.get_production('<logeq-grp>')
        if prod == 427:
            op_tok = self.current_token; op = self._logeq_op()
            right = self.bool_grp_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self._bool_exp_grp(node)
        return left  # prod 428: λ

    def _bool_exp_grp(self, left):
        prod = self.get_production('<bool-exp-grp>')
        if prod == 258:
            op_tok = self.current_token; op = self.log_op()
            right = self.bool_grp_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self._bool_exp_grp(node)
        return left  # prod 259: λ

    def _parch_tail_grp(self, left):
        prod = self.get_production('<parch-tail-grp>')
        if prod == 429:
            op_tok = self.current_token; op = self.eq_op()
            right_tok = self.current_token; self.eat('PARCH-lit')
            right = LiteralNode('PARCH', right_tok.value, right_tok)
            return BinaryOpNode(left, op, right, op_tok)
        return left  # prod 430: λ

    def _scroll_tail_grp(self, left):
        prod = self.get_production('<scroll-tail-grp>')
        if prod == 431:
            return self.scroll_concat_fold(left)
        elif prod == 432:
            op_tok = self.current_token; op = self.eq_op()
            right = self.scroll_val()
            return BinaryOpNode(left, op, right, op_tok)
        return left  # prod 433: λ

    def _eq_ope_grp(self):
        """eq_ope_grp: prod 250–253"""
        prod = self.get_production('<eq-ope-grp>')
        if prod == 250:
            tok = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                node = self.id_tail(tok.value, tok)
            else:
                node = IdentNode(tok.value, tok)
            node = self.arith_fold(node)
            return node
        elif prod == 251:
            self.eat('(')
            node = self.value_grp()
            self.eat(')')
            return self.arith_fold(node)
        elif prod == 252:
            node = self.var_digit()
            return self.arith_fold(node)
        else:  # prod 253: eq_ope1
            return self._eq_ope1()

    def _eq_ope1(self):
        """eq_ope1: prod 220/221/222"""
        prod = self.get_production('<eq-ope1>')
        tok = self.current_token
        if prod == 220:
            self.eat('PARCH-lit')
            return LiteralNode('PARCH', tok.value, tok)
        elif prod == 221:
            self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            return self.scr_char_opt(base, tok)
        else:  # prod 222: bool
            return self.bool_val()

    # ─────────────────────────────────────────────────────────────────────────
    # ID-TAIL DISAMBIGUATION
    # prod 342: {index} elmt2   → ArrayAccessNode
    # prod 343: $id             → MemberAccessNode
    # prod 344: (args)          → FuncCallNode
    # prod 345: λ               → IdentNode
    # ─────────────────────────────────────────────────────────────────────────

    def id_tail(self, name, tok):
        prod = self.get_production('<id-tail>')
        if prod == 342:
            self.eat('{')
            idx1 = self.index_expr()
            self.eat('}')
            # elmt2: prod 346 → {index}, prod 347 → λ
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
        prod 137: COIN-lit
        prod 138: id (wait — prod 137 is id, 138 is COIN-lit per syn_parser)
        Actually: prod 137 = id, prod 138 = COIN-lit (per syn_parser lines 983-988)
        """
        prod = self.get_production('<index>')
        tok = self.current_token
        if prod == 137:
            self.eat('id')
            return IdentNode(tok.value, tok)
        else:  # prod 138: COIN-lit
            self.eat('COIN-lit')
            return LiteralNode('COIN', int(tok.value), tok)

    def args(self):
        """
        prod 348: value args_mult
        prod 349: λ
        """
        prod = self.get_production('<args>')
        if prod == 348:
            first = self.value()
            rest = self.args_mult_inner()
            return [first] + rest
        return []  # prod 349: λ

    def args_mult_inner(self):
        """prod 350: , args | prod 351: λ"""
        prod = self.get_production('<args-mult>')
        if prod == 350:
            self.eat(',')
            return self.args()
        return []

    # ─────────────────────────────────────────────────────────────────────────
    # TYPE-SPECIFIC EXPRESSION BUILDERS
    # ─────────────────────────────────────────────────────────────────────────

    def coin_val(self):
        """prod 21/22: coin_val coin_exp (COIN-lit or neg id/grouped)."""
        prod = self.get_production('<coin-val>')
        tok = self.current_token
        if prod == 21:
            self.eat('COIN-lit')
            node = LiteralNode('COIN', int(tok.value), tok)
        else:  # prod 22: neg neg_coin_val
            op_tok = tok
            has_neg = self.current_token.type == '-'
            if has_neg:
                self.eat('-')
            node = self.neg_coin_val()
            if has_neg:
                node = UnaryOpNode('-', node, op_tok)
        # coin_exp: prod 27 (coin_arith chain) | prod 28 (λ) → fold via arith_fold
        return self.arith_fold(node)

    def neg_coin_val(self):
        """prod 25: id [id_tail] | prod 26: (coin_val_grp)"""
        prod = self.get_production('<neg-coin-val>')
        tok = self.current_token
        if prod == 25:
            self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                return self.id_tail(tok.value, tok)
            return IdentNode(tok.value, tok)
        else:  # prod 26
            self.eat('(')
            val = self.coin_val()
            self.eat(')')
            return val

    def dime_val(self):
        """prod 68/69/70: DIME-lit | COIN-lit | neg neg_dime_val."""
        prod = self.get_production('<dime-val>')
        tok = self.current_token
        if prod == 68:
            self.eat('DIME-lit')
            node = LiteralNode('DIME', float(tok.value), tok)
        elif prod == 69:
            self.eat('COIN-lit')
            node = LiteralNode('COIN', int(tok.value), tok)
        else:  # prod 70: neg neg_dime_val
            op_tok = tok
            has_neg = self.current_token.type == '-'
            if has_neg:
                self.eat('-')
            node = self.neg_dime_val()
            if has_neg:
                node = UnaryOpNode('-', node, op_tok)
        return self.arith_fold(node)

    def neg_dime_val(self):
        """prod 71: id [id_tail] | prod 72: (dime_grp_val)"""
        prod = self.get_production('<neg-dime-val>')
        tok = self.current_token
        if prod == 71:
            self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                return self.id_tail(tok.value, tok)
            return IdentNode(tok.value, tok)
        else:  # prod 72
            self.eat('(')
            val = self.dime_val()
            self.eat(')')
            return val

    def dime_ope(self):
        """Alias for dime_val — used as a building block in binary ops."""
        return self.dime_val()

    def arith_fold(self, left):
        """Left-associative fold over arith_op dime_val sequences."""
        while self.current_token and self.current_token.type in ('+', '-', '*', '/', '%', '^'):
            op_tok = self.current_token
            op = self.arith_op()
            right = self.dime_val()
            left = BinaryOpNode(left, op, right, op_tok)
        return left

    def arith_op(self):
        """prods 33–38: +, -, *, /, %, ^"""
        tok = self.current_token
        self.eat(tok.type)
        return tok.type

    def parch_val(self):
        """
        prod 107: PARCH-lit
        prod 108: id [id_tail]
        """
        prod = self.get_production('<parch-val>')
        tok = self.current_token
        if prod == 107:
            self.eat('PARCH-lit')
            return LiteralNode('PARCH', tok.value, tok)
        else:  # prod 108
            self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                return self.id_tail(tok.value, tok)
            return IdentNode(tok.value, tok)

    def scroll_val(self):
        """
        prod 132: SCROLL-lit [scr_char] [scroll_exp]
        prod 133: id [id_tail] [scroll_exp]
        prod 134: (scroll_grp_val)
        """
        prod = self.get_production('<scroll-val>')
        tok = self.current_token
        if prod == 132:
            self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            first = self.scr_char_opt(base, tok)
        elif prod == 133:
            self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                first = self.id_tail(tok.value, tok)
            else:
                first = IdentNode(tok.value, tok)
        else:  # prod 134
            self.eat('(')
            first = self.scroll_val()
            self.eat(')')
        return self.scroll_concat_fold(first)

    def scr_char_opt(self, base, tok):
        """
        prod 135: {index}  → ScrollCharAccessNode
        prod 136: λ        → base unchanged
        """
        prod = self.get_production('<scr-char>')
        if prod == 135:
            self.eat('{')
            idx = self.index_expr()
            self.eat('}')
            return ScrollCharAccessNode(base, idx, tok)
        return base  # prod 136: λ

    def scroll_concat_fold(self, left):
        """& scroll_val & scroll_val ... — left-associative concat."""
        if self.current_token and self.current_token.type == '&':
            tok = self.current_token
            operands = [left]
            while self.current_token and self.current_token.type == '&':
                self.eat('&')
                operands.append(self.scroll_val())
            return StringConcatNode(operands, tok)
        return left

    def var_digit(self):
        """prod 191/192/193: COIN-lit | DIME-lit | - neg_digit"""
        prod = self.get_production('<digit>')
        tok = self.current_token
        if prod == 191:
            self.eat('COIN-lit')
            return LiteralNode('COIN', int(tok.value), tok)
        elif prod == 192:
            self.eat('DIME-lit')
            return LiteralNode('DIME', float(tok.value), tok)
        else:  # prod 193: - neg_digit
            self.eat('-')
            inner = self.neg_digit()
            return UnaryOpNode('-', inner, tok)

    def neg_digit(self):
        """prod 194: id [id_tail] | prod 195: (dime_grp_val)"""
        prod = self.get_production('<neg-digit>')
        tok = self.current_token
        if prod == 194:
            self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                return self.id_tail(tok.value, tok)
            return IdentNode(tok.value, tok)
        else:  # prod 195
            self.eat('(')
            val = self.dime_val()
            self.eat(')')
            return val

    # ─────────────────────────────────────────────────────────────────────────
    # BOOLEAN EXPRESSIONS
    # ─────────────────────────────────────────────────────────────────────────

    def bool_val(self):
        """Main entry for a boolean value (used in conditions, initialisers, etc.)
        Delegates to bool_grp_val or the simpler bool_ope path as context demands.
        For non-condition contexts we use bool_ope + bool_exp_fold."""
        left = self.bool_ope()
        return self.bool_exp_fold(left)

    def bool_grp_val(self):
        """
        prod 231: bool_ope_grp bool_exp_grp
        Used as condition() entry point.
        """
        left = self.bool_grp_ope()
        return self._bool_exp_grp(left)

    def bool_grp_ope(self):
        """
        prod 232: id [id_tail] bool_exp2_grp
        prod 233: (value_grp) bool_exp2_grp
        prod 234: bool bool_eq_grp
        prod 235: digit bool_arith releq_grp
        prod 236: PARCH-lit eq_op parch_val
        prod 237: SCROLL-lit [scr_char] eq_op scroll_val
        """
        prod = self.get_production('<bool-ope-grp>')
        tok = self.current_token
        if prod == 232:
            self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                node = self.id_tail(tok.value, tok)
            else:
                node = IdentNode(tok.value, tok)
            return self._bool_exp2_grp(node)
        elif prod == 233:
            self.eat('(')
            node = self.value_grp()
            self.eat(')')
            return self._bool_exp2_grp(node)
        elif prod == 234:
            node = self._bool_literal()
            return self._bool_eq_grp(node)
        elif prod == 235:
            left = self.var_digit()
            left = self.arith_fold(left)
            return self._releq_grp(left)
        elif prod == 236:
            self.eat('PARCH-lit')
            left = LiteralNode('PARCH', tok.value, tok)
            op_tok = self.current_token; op = self.eq_op()
            right = self.parch_val()
            return BinaryOpNode(left, op, right, op_tok)
        elif prod == 237:
            self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            left = self.scr_char_opt(base, tok)
            op_tok = self.current_token; op = self.eq_op()
            right = self.scroll_val()
            return BinaryOpNode(left, op, right, op_tok)

    def _bool_exp2_grp(self, left):
        """bool_exp2_grp: prod 246–249"""
        prod = self.get_production('<bool-exp2-grp>')
        if prod == 246:
            left = self.arith_fold(left)
            return self._releq_grp(left)
        elif prod == 247:
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_val(); right = self.arith_fold(right)
            node = BinaryOpNode(left, op, right, op_tok)
            return self._bool_eq_grp(node)
        elif prod == 248:
            op_tok = self.current_token; op = self.eq_op()
            right = self._eq_ope_grp()
            return BinaryOpNode(left, op, right, op_tok)
        return left  # prod 249: λ

    def _bool_eq_grp(self, left):
        """bool_eq_grp: prod 238 — eq_op bool_ope_grp"""
        prod = self.get_production('<bool-eq-grp>')
        if prod == 238:
            op_tok = self.current_token; op = self.eq_op()
            right = self.bool_grp_ope()
            return BinaryOpNode(left, op, right, op_tok)
        return left

    def _releq_grp(self, left):
        """releq_grp: prod 240/241"""
        prod = self.get_production('<releq-grp>')
        if prod == 240:
            op_tok = self.current_token; op = self.rel_op()
            right = self.dime_val(); right = self.arith_fold(right)
            node = BinaryOpNode(left, op, right, op_tok)
            return self._bool_eq_grp(node)
        elif prod == 241:
            op_tok = self.current_token; op = self.eq_op()
            right = self.dime_val(); right = self.arith_fold(right)
            return BinaryOpNode(left, op, right, op_tok)
        return left

    def bool_ope(self):
        """
        prod 232–237 (same as bool_grp_ope but in non-condition context).
        For simplicity, delegate to bool_grp_ope since the AST structure is the same.
        """
        return self.bool_grp_ope()

    def _bool_literal(self):
        """AYE → True, NAY → False"""
        tok = self.current_token
        if tok.type == 'AYE':
            self.eat('AYE')
            return LiteralNode('BOOL', True, tok)
        else:
            self.eat('NAY')
            return LiteralNode('BOOL', False, tok)

    def bool_exp_fold(self, left):
        """
        prod 227: log_op bool_val bool_exp
        prod 228: λ
        """
        prod = self.get_production('<bool-exp>')
        if prod == 227:
            op_tok = self.current_token
            op = self.log_op()
            right = self.bool_val()
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)
        return left  # prod 228: λ

    def rel_op(self):
        """prods 201–204: <, >, <=, >="""
        tok = self.current_token
        self.eat(tok.type)
        return tok.type

    def eq_op(self):
        """prods 208/209: ==, !="""
        tok = self.current_token
        self.eat(tok.type)
        return tok.type

    def log_op(self):
        """prods 229/230: ||, &&"""
        tok = self.current_token
        self.eat(tok.type)
        return tok.type