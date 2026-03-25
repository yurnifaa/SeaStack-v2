# =============================================================================
# ast_parser.py — SeaStack AST-Building Parser
#
# Runs AFTER syn_parser validates the token stream. Builds AST from tokens.
# Uses the same PREDICT table as syn_parser.py.
#
# KEY FIXES from original:
#   - Removed double sub_func call in return_func for SCROLL (prod 482)
#   - Added missing boolean continuations in multiple expression tails:
#     _parch_tail_as, _scroll_tail_as, _parch_tail_str, _scroll_tail_str,
#     _releq_str, _releq_as, _releqvar_grp
#   - hoist_init/init1_mult/init2_mult now use coin_val() instead of
#     eating COIN-lit directly, to support variable/element/member/arith
#     expressions in HOIST initialization
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
        ignored_types = ['whitespace', 'newline', 'single-comment', 'multi-comment']
        self.tokens = [t for t in tokens if t.type not in ignored_types]
        for t in self.tokens:
            if t.type.startswith('id') and t.type[2:].isdigit():
                t.type = 'id'
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

    # ── Utility ──────────────────────────────────────────────────────────

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            found = self.current_token.type if self.current_token else 'EOF'
            raise RuntimeError(
                f'ASTParser bug: expected {token_type!r}, got {found!r} '
                f'at line {getattr(self.current_token, "line", "?")}')

    def get_production(self, non_terminal):
        if not self.current_token:
            return None
        return PREDICT.get(non_terminal, {}).get(self.current_token.type)

    # ── Entry Point ──────────────────────────────────────────────────────

    def build(self):
        return self.program()

    # =====================================================================
    # PROGRAM STRUCTURE  (prod 1)
    # =====================================================================

    def program(self):
        tok = self.current_token
        global_decls = self.global_dec()
        self.eat('AHOY'); self.eat('('); self.eat(')'); self.eat('[')
        local_decls = self.ahoy_local_dec()
        statements = self.ahoy_stmnts()
        self.eat(']')
        return ProgramNode(global_decls, AhoyNode(local_decls, statements, tok), tok)

    # ── Global Declarations (prods 2-6) ──────────────────────────────────

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

    # ── Var/Arr/Func dispatch (prods 7-11) ───────────────────────────────

    def var_arr_func(self):
        prod = self.get_production('<var-arr-func>')
        if prod == 7:
            self.eat('COIN'); nt = self.current_token; self.eat('id')
            return self.coin_var_arr_func('COIN', nt)
        elif prod == 8:
            self.eat('DIME'); nt = self.current_token; self.eat('id')
            return self.dime_var_arr_func('DIME', nt)
        elif prod == 9:
            self.eat('PARCH'); nt = self.current_token; self.eat('id')
            return self.parch_var_arr_func('PARCH', nt)
        elif prod == 10:
            self.eat('SCROLL'); nt = self.current_token; self.eat('id')
            return self.scroll_var_arr_func('SCROLL', nt)
        elif prod == 11:
            self.eat('BOOL'); nt = self.current_token; self.eat('id')
            return self.bool_var_arr_func('BOOL', nt)
        return []

    # ── Type-specific global dispatch ────────────────────────────────────

    def coin_var_arr_func(self, dtype, nt):
        prod = self.get_production('<coin-var-arr-func>')
        nodes = []
        if prod == 12:
            nodes.extend(self.coin_var_arr(dtype, nt))
            self.eat('!!'); nodes.extend(self.global_dec())
        elif prod == 13:
            nodes.append(self.coin_func(dtype, nt))
        return nodes

    def dime_var_arr_func(self, dtype, nt):
        prod = self.get_production('<dime-var-arr-func>')
        nodes = []
        if prod == 58:
            nodes.extend(self.dime_var_arr(dtype, nt))
            self.eat('!!'); nodes.extend(self.global_dec())
        elif prod == 59:
            nodes.append(self.dime_func(dtype, nt))
        return nodes

    def parch_var_arr_func(self, dtype, nt):
        prod = self.get_production('<parch-var-arr-func>')
        nodes = []
        if prod == 98:
            nodes.extend(self.parch_var_arr(dtype, nt))
            self.eat('!!'); nodes.extend(self.global_dec())
        elif prod == 99:
            nodes.append(self.parch_func(dtype, nt))
        return nodes

    def scroll_var_arr_func(self, dtype, nt):
        # NOTE: prod 123 has an extra sub_func per the grammar
        prod = self.get_production('<scroll-var-arr-func>')
        nodes = []
        if prod == 122:
            nodes.extend(self.scroll_var_arr(dtype, nt))
            self.eat('!!'); nodes.extend(self.global_dec())
        elif prod == 123:
            nodes.append(self.scroll_func(dtype, nt))
            nodes.extend(self.sub_func())   # extra sub_func per grammar
        return nodes

    def bool_var_arr_func(self, dtype, nt):
        prod = self.get_production('<bool-var-arr-func>')
        nodes = []
        if prod == 164:
            nodes.extend(self.bool_var_arr(dtype, nt))
            self.eat('!!'); nodes.extend(self.global_dec())
        elif prod == 165:
            nodes.append(self.bool_func(dtype, nt))
        return nodes

    # =====================================================================
    # COIN VAR/ARR  (prods 14-53)
    # =====================================================================

    def coin_var_arr(self, dtype, nt):
        prod = self.get_production('<coin-var-arr>')
        if prod == 14: return self.coin_var(dtype, nt)
        elif prod == 15: return [self.coin_arr(dtype, nt)]
        return []

    def coin_var(self, dtype, nt):
        init = self.coin_init()
        return [VarDeclNode(dtype, nt.value, init, nt)] + self.coin_init_mult(dtype)

    def coin_init(self):
        prod = self.get_production('<coin-init>')
        if prod == 17:
            self.eat('='); return self.coin_val()
        return None  # prod 18: λ

    def coin_init_mult(self, dtype):
        prod = self.get_production('<coin-init-mult>')
        if prod == 19:
            self.eat(','); nt = self.current_token; self.eat('id')
            init = self.coin_init()
            return [VarDeclNode(dtype, nt.value, init, nt)] + self.coin_init_mult(dtype)
        return []  # prod 20: λ

    def coin_arr(self, dtype, nt):
        self.eat('{'); d1t = self.current_token; self.eat('COIN-lit'); self.eat('}')
        return self.coin_arr_tail(dtype, nt, int(d1t.value))

    def coin_arr_tail(self, dtype, nt, d1):
        prod = self.get_production('<coin-arr-tail>')
        if prod == 40:
            self.eat('='); self.eat('['); vals = self.coin_arr1(); self.eat(']')
            return ArrayDeclNode(dtype, nt.value, [d1], False, vals, nt)
        elif prod == 41:
            self.eat('{'); d2t = self.current_token; self.eat('COIN-lit'); self.eat('}')
            return self.coin_arr2_tail(dtype, nt, d1, int(d2t.value))
        else:  # prod 42: λ
            return ArrayDeclNode(dtype, nt.value, [d1], False, None, nt)

    def coin_arr2_tail(self, dtype, nt, d1, d2):
        prod = self.get_production('<coin-arr2-tail>')
        if prod == 49:
            self.eat('='); self.eat('['); rows = self.coin_arr2(); self.eat(']')
            return ArrayDeclNode(dtype, nt.value, [d1, d2], True, rows, nt)
        else:  # prod 50: λ
            return ArrayDeclNode(dtype, nt.value, [d1, d2], True, None, nt)

    def coin_arr1(self):
        val = self.coin_arr_val()
        return [val] + self.cav_tail()

    def coin_arr_val(self):
        return self.coin_val()  # coin_val includes arith_fold

    def cav_tail(self):
        prod = self.get_production('<cav-tail>')
        if prod == 47: self.eat(','); return self.coin_arr1()
        return []

    def coin_arr2(self):
        self.eat('['); row = self.coin_arr1(); self.eat(']')
        return [row] + self.cav2_tail()

    def cav2_tail(self):
        prod = self.get_production('<cav2-tail>')
        if prod == 52: self.eat(','); return self.coin_arr2()
        return []

    # =====================================================================
    # DIME VAR/ARR  (prods 60-93)
    # =====================================================================

    def dime_var_arr(self, dtype, nt):
        prod = self.get_production('<dime-var-arr>')
        if prod == 60: return self.dime_var(dtype, nt)
        elif prod == 61: return [self.dime_arr(dtype, nt)]
        return []

    def dime_var(self, dtype, nt):
        init = self.dime_init()
        return [VarDeclNode(dtype, nt.value, init, nt)] + self.dime_init_mult(dtype)

    def dime_init(self):
        prod = self.get_production('<dime-init>')
        if prod == 63: self.eat('='); return self.dime_val()
        return None

    def dime_init_mult(self, dtype):
        prod = self.get_production('<dime-init-mult>')
        if prod == 65:
            self.eat(','); nt = self.current_token; self.eat('id')
            init = self.dime_init()
            return [VarDeclNode(dtype, nt.value, init, nt)] + self.dime_init_mult(dtype)
        return []

    def dime_arr(self, dtype, nt):
        self.eat('{'); d1t = self.current_token; self.eat('COIN-lit'); self.eat('}')
        return self.dime_arr_tail(dtype, nt, int(d1t.value))

    def dime_arr_tail(self, dtype, nt, d1):
        prod = self.get_production('<dime-arr-tail>')
        if prod == 80:
            self.eat('='); self.eat('['); vals = self._arr1_values(self.dime_val); self.eat(']')
            return ArrayDeclNode(dtype, nt.value, [d1], False, vals, nt)
        elif prod == 81:
            self.eat('{'); d2t = self.current_token; self.eat('COIN-lit'); self.eat('}')
            return self.dime_arr2_tail(dtype, nt, d1, int(d2t.value))
        else:
            return ArrayDeclNode(dtype, nt.value, [d1], False, None, nt)

    def dime_arr2_tail(self, dtype, nt, d1, d2):
        prod = self.get_production('<dime-arr2-tail>')
        if prod == 89:
            self.eat('='); self.eat('['); rows = self._arr2_rows(self.dime_val); self.eat(']')
            return ArrayDeclNode(dtype, nt.value, [d1, d2], True, rows, nt)
        else:
            return ArrayDeclNode(dtype, nt.value, [d1, d2], True, None, nt)

    # =====================================================================
    # PARCH VAR/ARR  (prods 100-120)
    # =====================================================================

    def parch_var_arr(self, dtype, nt):
        prod = self.get_production('<parch-var-arr>')
        if prod == 100: return self.parch_var(dtype, nt)
        elif prod == 101: return [self.parch_arr(dtype, nt)]
        return []

    def parch_var(self, dtype, nt):
        init = self.parch_init()
        return [VarDeclNode(dtype, nt.value, init, nt)] + self.parch_init_mult(dtype)

    def parch_init(self):
        prod = self.get_production('<parch-init>')
        if prod == 103: self.eat('='); return self.parch_val()
        return None

    def parch_init_mult(self, dtype):
        prod = self.get_production('<parch-init-mult>')
        if prod == 105:
            self.eat(','); nt = self.current_token; self.eat('id')
            init = self.parch_init()
            return [VarDeclNode(dtype, nt.value, init, nt)] + self.parch_init_mult(dtype)
        return []

    def parch_arr(self, dtype, nt):
        self.eat('{'); d1t = self.current_token; self.eat('COIN-lit'); self.eat('}')
        return self.parch_arr_tail(dtype, nt, int(d1t.value))

    def parch_arr_tail(self, dtype, nt, d1):
        prod = self.get_production('<parch-arr-tail>')
        if prod == 110:
            self.eat('='); self.eat('['); vals = self._arr1_values(self.parch_val); self.eat(']')
            return ArrayDeclNode(dtype, nt.value, [d1], False, vals, nt)
        elif prod == 111:
            self.eat('{'); d2t = self.current_token; self.eat('COIN-lit'); self.eat('}')
            return self.parch_arr2_tail(dtype, nt, d1, int(d2t.value))
        else:
            return ArrayDeclNode(dtype, nt.value, [d1], False, None, nt)

    def parch_arr2_tail(self, dtype, nt, d1, d2):
        prod = self.get_production('<parch-arr2-tail>')
        if prod == 116:
            self.eat('='); self.eat('['); rows = self._arr2_rows(self.parch_val); self.eat(']')
            return ArrayDeclNode(dtype, nt.value, [d1, d2], True, rows, nt)
        else:
            return ArrayDeclNode(dtype, nt.value, [d1, d2], True, None, nt)

    # =====================================================================
    # SCROLL VAR/ARR  (prods 124-159)
    # =====================================================================

    def scroll_var_arr(self, dtype, nt):
        prod = self.get_production('<scroll-var-arr>')
        if prod == 124: return self.scroll_var(dtype, nt)
        elif prod == 125: return [self.scroll_arr(dtype, nt)]
        return []

    def scroll_var(self, dtype, nt):
        init = self.scroll_init()
        return [VarDeclNode(dtype, nt.value, init, nt)] + self.scroll_init_mult(dtype)

    def scroll_init(self):
        prod = self.get_production('<scroll-init>')
        if prod == 127: self.eat('='); return self.scroll_val()
        return None

    def scroll_init_mult(self, dtype):
        prod = self.get_production('<scroll-init-mult>')
        if prod == 129:
            self.eat(','); nt = self.current_token; self.eat('id')
            init = self.scroll_init()
            return [VarDeclNode(dtype, nt.value, init, nt)] + self.scroll_init_mult(dtype)
        return []

    def scroll_arr(self, dtype, nt):
        self.eat('{'); d1t = self.current_token; self.eat('COIN-lit'); self.eat('}')
        return self.scroll_arr_tail(dtype, nt, int(d1t.value))

    def scroll_arr_tail(self, dtype, nt, d1):
        prod = self.get_production('<scroll-arr-tail>')
        if prod == 146:
            self.eat('='); self.eat('['); vals = self._arr1_values(self.scroll_val); self.eat(']')
            return ArrayDeclNode(dtype, nt.value, [d1], False, vals, nt)
        elif prod == 147:
            self.eat('{'); d2t = self.current_token; self.eat('COIN-lit'); self.eat('}')
            return self.scroll_arr2_tail(dtype, nt, d1, int(d2t.value))
        else:
            return ArrayDeclNode(dtype, nt.value, [d1], False, None, nt)

    def scroll_arr2_tail(self, dtype, nt, d1, d2):
        prod = self.get_production('<scroll-arr2-tail>')
        if prod == 155:
            self.eat('='); self.eat('['); rows = self._arr2_rows(self.scroll_val); self.eat(']')
            return ArrayDeclNode(dtype, nt.value, [d1, d2], True, rows, nt)
        else:
            return ArrayDeclNode(dtype, nt.value, [d1, d2], True, None, nt)

    # =====================================================================
    # BOOL VAR/ARR  (prods 166-172, 260-300)
    # =====================================================================

    def bool_var_arr(self, dtype, nt):
        prod = self.get_production('<bool-var-arr>')
        if prod == 166: return self.bool_var(dtype, nt)
        elif prod == 167: return [self.bool_arr(dtype, nt)]
        return []

    def bool_var(self, dtype, nt):
        init = self.bool_init()
        return [VarDeclNode(dtype, nt.value, init, nt)] + self.bool_init_mult(dtype)

    def bool_init(self):
        prod = self.get_production('<bool-init>')
        if prod == 169: self.eat('='); return self.bool_val()
        return None

    def bool_init_mult(self, dtype):
        prod = self.get_production('<bool-init-mult>')
        if prod == 171:
            self.eat(','); nt = self.current_token; self.eat('id')
            init = self.bool_init()
            return [VarDeclNode(dtype, nt.value, init, nt)] + self.bool_init_mult(dtype)
        return []

    def bool_arr(self, dtype, nt):
        self.eat('{'); d1t = self.current_token; self.eat('COIN-lit'); self.eat('}')
        return self.bool_arr_tail(dtype, nt, int(d1t.value))

    def bool_arr_tail(self, dtype, nt, d1):
        prod = self.get_production('<bool-arr-tail>')
        if prod == 261:
            self.eat('='); self.eat('['); vals = self._arr1_values(self.bool_val); self.eat(']')
            return ArrayDeclNode(dtype, nt.value, [d1], False, vals, nt)
        elif prod == 262:
            self.eat('{'); d2t = self.current_token; self.eat('COIN-lit'); self.eat('}')
            return self.bool_arr2_tail(dtype, nt, d1, int(d2t.value))
        else:
            return ArrayDeclNode(dtype, nt.value, [d1], False, None, nt)

    def bool_arr2_tail(self, dtype, nt, d1, d2):
        prod = self.get_production('<bool-arr2-tail>')
        if prod == 296:
            self.eat('='); self.eat('['); rows = self._arr2_rows(self.bool_val); self.eat(']')
            return ArrayDeclNode(dtype, nt.value, [d1, d2], True, rows, nt)
        else:
            return ArrayDeclNode(dtype, nt.value, [d1, d2], True, None, nt)

    # ── Generic array helpers ────────────────────────────────────────────

    def _arr1_values(self, val_method):
        values = [val_method()]
        while self.current_token and self.current_token.type == ',':
            self.eat(','); values.append(val_method())
        return values

    def _arr2_rows(self, val_method):
        rows = []
        while self.current_token and self.current_token.type == '[':
            self.eat('['); rows.append(self._arr1_values(val_method)); self.eat(']')
            if self.current_token and self.current_token.type == ',':
                self.eat(',')
        return rows

    # =====================================================================
    # CONSTANTS (LOCKE)  (prod 442-468)
    # =====================================================================

    def const(self):
        self.eat('LOCKE'); nodes = self.const_init(); self.eat('!!'); return nodes

    def const_init(self):
        prod = self.get_production('<const-init>')
        if prod == 443: self.eat('COIN'); return self.coin_locke_list('COIN')
        elif prod == 444: self.eat('DIME'); return self.dime_locke_list('DIME')
        elif prod == 445: self.eat('PARCH'); return self.parch_locke_list('PARCH')
        elif prod == 446: self.eat('SCROLL'); return self.scroll_locke_list('SCROLL')
        elif prod == 447: self.eat('BOOL'); return self.bool_locke_list('BOOL')
        return []

    def coin_locke_list(self, dtype):
        nodes = []
        nt = self.current_token; self.eat('id'); self.eat('=')
        vt = self.current_token; self.eat('COIN-lit')
        nodes.append(ConstDeclNode(dtype, nt.value, LiteralNode('COIN', int(vt.value), vt), nt))
        while self.get_production('<coin-locke-mult>') == 449:
            self.eat(','); nt = self.current_token; self.eat('id'); self.eat('=')
            vt = self.current_token; self.eat('COIN-lit')
            nodes.append(ConstDeclNode(dtype, nt.value, LiteralNode('COIN', int(vt.value), vt), nt))
        return nodes

    def dime_locke_list(self, dtype):
        nodes = []
        nt = self.current_token; self.eat('id'); self.eat('=')
        vt = self.current_token
        if vt.type == 'COIN-lit':
            self.eat('COIN-lit'); lit = LiteralNode('COIN', int(vt.value), vt)
        else:
            self.eat('DIME-lit'); lit = LiteralNode('DIME', float(vt.value), vt)
        nodes.append(ConstDeclNode(dtype, nt.value, lit, nt))
        while self.get_production('<dime-locke-mult>') == 454:
            self.eat(','); nt = self.current_token; self.eat('id'); self.eat('=')
            vt = self.current_token
            if vt.type == 'COIN-lit':
                self.eat('COIN-lit'); lit = LiteralNode('COIN', int(vt.value), vt)
            else:
                self.eat('DIME-lit'); lit = LiteralNode('DIME', float(vt.value), vt)
            nodes.append(ConstDeclNode(dtype, nt.value, lit, nt))
        return nodes

    def parch_locke_list(self, dtype):
        nodes = []
        nt = self.current_token; self.eat('id'); self.eat('=')
        vt = self.current_token; self.eat('PARCH-lit')
        nodes.append(ConstDeclNode(dtype, nt.value, LiteralNode('PARCH', vt.value, vt), nt))
        while self.get_production('<parch-locke-mult>') == 457:
            self.eat(','); nt = self.current_token; self.eat('id'); self.eat('=')
            vt = self.current_token; self.eat('PARCH-lit')
            nodes.append(ConstDeclNode(dtype, nt.value, LiteralNode('PARCH', vt.value, vt), nt))
        return nodes

    def scroll_locke_list(self, dtype):
        nodes = []
        nt = self.current_token; self.eat('id'); self.eat('=')
        st = self.current_token; self.eat('SCROLL-lit')
        base = LiteralNode('SCROLL', st.value, st)
        val = self._scr_id_const(base, st)
        nodes.append(ConstDeclNode(dtype, nt.value, val, nt))
        while self.get_production('<scroll-locke-mult>') == 462:
            self.eat(','); nt = self.current_token; self.eat('id'); self.eat('=')
            st = self.current_token; self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', st.value, st)
            val = self._scr_id_const(base, st)
            nodes.append(ConstDeclNode(dtype, nt.value, val, nt))
        return nodes

    def _scr_id_const(self, base, tok):
        """Optional {COIN-lit} after SCROLL-lit in LOCKE context."""
        if self.current_token and self.current_token.type == '{':
            self.eat('{'); it = self.current_token; self.eat('COIN-lit'); self.eat('}')
            return ScrollCharAccessNode(base, LiteralNode('COIN', int(it.value), it), tok)
        return base

    def bool_locke_list(self, dtype):
        nodes = []
        nt = self.current_token; self.eat('id'); self.eat('=')
        vt = self.current_token
        if vt.type == 'AYE': self.eat('AYE'); lit = LiteralNode('BOOL', True, vt)
        else: self.eat('NAY'); lit = LiteralNode('BOOL', False, vt)
        nodes.append(ConstDeclNode(dtype, nt.value, lit, nt))
        while self.get_production('<bool-locke-mult>') == 467:
            self.eat(','); nt = self.current_token; self.eat('id'); self.eat('=')
            vt = self.current_token
            if vt.type == 'AYE': self.eat('AYE'); lit = LiteralNode('BOOL', True, vt)
            else: self.eat('NAY'); lit = LiteralNode('BOOL', False, vt)
            nodes.append(ConstDeclNode(dtype, nt.value, lit, nt))
        return nodes

    # =====================================================================
    # STRUCT DEFINITIONS  (prod 469-475)
    # =====================================================================

    def struct(self):
        nodes = []
        while self.current_token and self.current_token.type == 'MAST':
            prod = self.get_production('<struct>')
            if prod != 469: break
            self.eat('MAST'); nt = self.current_token; self.eat('id'); self.eat('[')
            members = self.mem_dec() + self.mem_dec_tail()
            self.eat(']'); self.eat('!!')
            nodes.append(StructDefNode(nt.value, members, nt))
        return nodes

    def mem_dec(self):
        dtype = self.d_type(); nt = self.current_token; self.eat('id')
        members = [MemberDeclNode(dtype, nt.value, nt)] + self.mem_mult(dtype)
        self.eat('!!'); return members

    def mem_mult(self, dtype):
        prod = self.get_production('<mem-mult>')
        if prod == 472:
            self.eat(','); nt = self.current_token; self.eat('id')
            return [MemberDeclNode(dtype, nt.value, nt)] + self.mem_mult(dtype)
        return []

    def mem_dec_tail(self):
        prod = self.get_production('<mem-dec-tail>')
        if prod == 474: return self.mem_dec() + self.mem_dec_tail()
        return []

    # =====================================================================
    # FUNCTION DEFINITIONS
    # =====================================================================

    def sub_func(self):
        prod = self.get_production('<sub-func>')
        if prod == 476: return [self.return_func()]
        elif prod == 477: return [self.nonreturn_func()]
        return []  # prod 478: λ

    def return_func(self):
        # FIX: No extra sub_func for any type — _build_return_func handles it
        prod = self.get_production('<return-func>')
        dtype_map = {479: 'COIN', 480: 'DIME', 481: 'PARCH', 482: 'SCROLL', 483: 'BOOL'}
        dtype = dtype_map[prod]
        self.eat(dtype); nt = self.current_token; self.eat('id')
        return self._build_return_func(dtype, nt)

    def _build_return_func(self, dtype, nt):
        """Shared body for all returning function definitions."""
        self.eat('('); params = self.params(); self.eat(')'); self.eat('[')
        local_decls = self.local_dec()
        body = self.ret_stmnts()
        self.eat('BACK'); return_expr = self._return_val_for(dtype)
        self.eat('!!'); self.eat(']')
        more = self.sub_func()  # chained function definitions
        node = FuncDefNode(dtype, nt.value, params, local_decls, body, return_expr, nt)
        return node  # caller (sub_func) wraps in list; more functions are siblings

    def coin_func(self, dtype, nt): return self._build_return_func(dtype, nt)
    def dime_func(self, dtype, nt): return self._build_return_func(dtype, nt)
    def parch_func(self, dtype, nt): return self._build_return_func(dtype, nt)
    def scroll_func(self, dtype, nt): return self._build_return_func(dtype, nt)
    def bool_func(self, dtype, nt): return self._build_return_func(dtype, nt)

    def _return_val_for(self, dtype):
        if dtype == 'COIN':   return self.coin_val()
        if dtype == 'DIME':   return self.dime_val()
        if dtype == 'PARCH':  return self.parch_val()
        if dtype == 'SCROLL': return self.scroll_val()
        if dtype == 'BOOL':   return self.bool_val()

    def nonreturn_func(self):
        tok = self.current_token; self.eat('ABYSS')
        nt = self.current_token; self.eat('id')
        self.eat('('); params = self.params(); self.eat(')'); self.eat('[')
        local_decls = self.local_dec()
        body = self.nonret_stmnts()
        back = self.nonret_back()
        if back: body.append(back)
        self.eat(']'); self.sub_func()
        return FuncDefNode('ABYSS', nt.value, params, local_decls, body, None, tok)

    def nonret_stmnts(self):
        first = self.nonret_stmnt()
        return [first] + self.nonret_tail()

    def nonret_tail(self):
        prod = self.get_production('<nonret-tail>')
        if prod == 486: return self.nonret_stmnts()
        return []

    def nonret_back(self):
        prod = self.get_production('<nonret-back>')
        if prod == 488:
            tok = self.current_token; self.eat('BACK'); self.eat('!!')
            return BackNode(tok)
        return None

    # ── Parameters ───────────────────────────────────────────────────────

    def params(self):
        prod = self.get_production('<params>')
        if prod == 331:
            dtype = self.d_type(); nt = self.current_token; self.eat('id')
            return [ParamNode(dtype, nt.value, nt)] + self.param_mult()
        return []

    def param_mult(self):
        prod = self.get_production('<param-mult>')
        if prod == 333: self.eat(','); return self.params()
        return []

    def d_type(self):
        tok = self.current_token; self.eat(tok.type); return tok.type

    # =====================================================================
    # LOCAL DECLARATIONS
    # =====================================================================

    def local_dec(self):
        nodes = []
        prod = self.get_production('<local-dec>')
        while prod == 502:
            nodes.extend(self.var_arr()); prod = self.get_production('<local-dec>')
        if prod == 503: nodes.extend(self.struct_dec())
        return nodes

    def ahoy_local_dec(self):
        nodes = []
        prod = self.get_production('<ahoy-local-dec>')
        while prod == 666:
            nodes.extend(self.var_arr()); prod = self.get_production('<ahoy-local-dec>')
        if prod == 667: nodes.extend(self.ahoy_struct_dec())
        return nodes

    def var_arr(self):
        prod = self.get_production('<var-arr>')
        if prod == 505:
            self.eat('COIN'); nt = self.current_token; self.eat('id')
            n = self.coin_var_arr('COIN', nt); self.eat('!!'); return n
        elif prod == 506:
            self.eat('DIME'); nt = self.current_token; self.eat('id')
            n = self.dime_var_arr('DIME', nt); self.eat('!!'); return n
        elif prod == 507:
            self.eat('PARCH'); nt = self.current_token; self.eat('id')
            n = self.parch_var_arr('PARCH', nt); self.eat('!!'); return n
        elif prod == 508:
            self.eat('SCROLL'); nt = self.current_token; self.eat('id')
            n = self.scroll_var_arr('SCROLL', nt); self.eat('!!'); return n
        elif prod == 509:
            self.eat('BOOL'); nt = self.current_token; self.eat('id')
            n = self.bool_var_arr('BOOL', nt); self.eat('!!'); return n
        return []

    def struct_dec(self):
        nodes = []
        prod = self.get_production('<struct-dec>')
        while prod == 510:
            self.eat('MAST'); tt = self.current_token; self.eat('id')
            vt = self.current_token; self.eat('id')
            inits, extras = self.str_dec_init(); self.eat('!!')
            nodes.append(StructVarDeclNode(tt.value, vt.value, inits, vt))
            for en in extras: nodes.append(StructVarDeclNode(tt.value, en, None, vt))
            prod = self.get_production('<struct-dec>')
        return nodes

    def ahoy_struct_dec(self):
        nodes = []
        prod = self.get_production('<ahoy-struct-dec>')
        while prod == 669:
            self.eat('MAST'); tt = self.current_token; self.eat('id')
            vt = self.current_token; self.eat('id')
            inits, extras = self.str_dec_init(); self.eat('!!')
            nodes.append(StructVarDeclNode(tt.value, vt.value, inits, vt))
            for en in extras: nodes.append(StructVarDeclNode(tt.value, en, None, vt))
            prod = self.get_production('<ahoy-struct-dec>')
        return nodes

    def str_dec_init(self):
        prod = self.get_production('<str-dec-init>')
        if prod == 512:
            extras = []; self.eat(',')
            nt = self.current_token; self.eat('id'); extras.append(nt.value)
            extras.extend(self.str_dec_tail()); return None, extras
        elif prod == 513:
            self.eat('='); self.eat('['); inits = self.str_val_list(); self.eat(']')
            return inits, []
        return None, []

    def str_dec_tail(self):
        prod = self.get_production('<str-dec-tail>')
        if prod == 515:
            self.eat(','); nt = self.current_token; self.eat('id')
            return [nt.value] + self.str_dec_tail()
        return []

    def str_val_list(self):
        inits = [self.str_val()]
        prod = self.get_production('<str-val-tail>')
        while prod == 519:
            self.eat(','); inits.append(self.str_val())
            prod = self.get_production('<str-val-tail>')
        return inits

    def str_val(self):
        prod = self.get_production('<str-val>')
        if prod == 518:
            self.eat('$'); nt = self.current_token; self.eat('id'); self.eat('=')
            return NamedInitNode(nt.value, self.value_str(), nt)
        else:
            return PositionalInitNode(self.value_str(), self.current_token)

    def value_str(self):
        """Expression in struct initializer context."""
        prod = self.get_production('<value-str>')
        if prod == 521:
            tok = self.current_token; self.eat('id')
            node = self.id_tail(tok.value, tok)
            return self._exp_str(node)
        elif prod == 522:
            self.eat('('); node = self.value_grp(); self.eat(')')
            return self._exp_str(node)
        elif prod == 523:
            node = self.var_digit()
            return self._digit_tail_str(node)
        elif prod == 524:
            tok = self.current_token; self.eat('PARCH-lit')
            return self._parch_tail_str(LiteralNode('PARCH', tok.value, tok))
        elif prod == 525:
            tok = self.current_token; self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            return self._scroll_tail_str(self.scr_char_opt(base, tok))
        else:  # prod 526: bool
            return self.bool_val()

    def _exp_str(self, left):
        return self._exp_shared(left)

    def _digit_tail_str(self, node):
        prod = self.get_production('<digit-tail-str>')
        if prod == 527:
            node = self.arith_fold(node)
            return self._releq_str(node)
        return node

    def _releq_str(self, left):
        prod = self.get_production('<releq-str>')
        if prod == 531:
            op_tok = self.current_token; op = self.rel_op()
            right = self.arith_fold(self.dime_ope())
            node = BinaryOpNode(left, op, right, op_tok)
            return self._logeq_str(node)
        elif prod == 532:
            # FIX: added bool_exp_fold continuation (syn_parser calls bool_exp_arr)
            op_tok = self.current_token; op = self.eq_op()
            right = self.arith_fold(self.dime_ope())
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)
        return left

    def _logeq_str(self, left):
        prod = self.get_production('<logeq-str>')
        if prod == 538:
            op_tok = self.current_token; op = self._logeq_op()
            right = self.bool_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)  # FIX: added continuation
        return left

    def _parch_tail_str(self, left):
        prod = self.get_production('<parch-tail-str>')
        if prod == 540:
            op_tok = self.current_token; op = self.eq_op()
            rt = self.current_token; self.eat('PARCH-lit')
            node = BinaryOpNode(left, op, LiteralNode('PARCH', rt.value, rt), op_tok)
            return self.bool_exp_fold(node)  # FIX: added continuation
        return left

    def _scroll_tail_str(self, left):
        prod = self.get_production('<scroll-tail-str>')
        if prod == 542: return self.scroll_concat_fold(left)
        elif prod == 543:
            op_tok = self.current_token; op = self.eq_op()
            right = self.scroll_val()
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)  # FIX: added continuation
        return left

    # =====================================================================
    # STATEMENTS
    # =====================================================================

    def ret_stmnts(self):
        stmts = []
        prod = self.get_production('<ret-stmnts>')
        while prod == 340:
            stmts.append(self.statements()); prod = self.get_production('<ret-stmnts>')
        return stmts

    def ahoy_stmnts(self):
        stmts = []
        prod = self.get_production('<ahoy-stmnts>')
        if prod == 671:
            stmts.append(self.ahoy_stmnt()); stmts.extend(self.ahoy_tail())
        return stmts

    def ahoy_tail(self):
        prod = self.get_production('<ahoy-tail>')
        if prod == 672: return self.ahoy_stmnts()
        return []

    def ahoy_stmnt(self):
        prod = self.get_production('<ahoy-stmnt>')
        if prod == 674:
            nt = self.current_token; self.eat('id')
            n = self.assign_tail(nt); self.eat('!!'); return n
        elif prod == 675: return self.ask_stmnt()
        elif prod == 676: return self.echo_stmnt()
        elif prod == 677: return self._look_stmnt_with_tail('ahoy')
        elif prod == 678: return self.chart_stmnt()
        elif prod == 679: return self.hoist_stmnt()
        elif prod == 680: return self.heave_stmnt()
        elif prod == 681: return self.haul_stmnt()
        elif prod == 682:
            n = self.unary_exp(); self.eat('!!'); return n

    def nonret_stmnt(self):
        prod = self.get_production('<nonret-stmnt>')
        if prod == 490:
            nt = self.current_token; self.eat('id')
            n = self.assign_tail(nt); self.eat('!!'); return n
        elif prod == 491: return self.ask_stmnt()
        elif prod == 492: return self.echo_stmnt()
        elif prod == 493: return self._look_stmnt_with_tail('nonret')
        elif prod == 494: return self.chart_stmnt()
        elif prod == 495: return self.hoist_stmnt()
        elif prod == 496: return self.heave_stmnt()
        elif prod == 497: return self.haul_stmnt()
        elif prod == 498:
            n = self.unary_exp(); self.eat('!!'); return n

    def statements(self):
        prod = self.get_production('<statements>')
        if prod == 553: return self.assign_stmnt()
        elif prod == 554: return self.ask_stmnt()
        elif prod == 555: return self.echo_stmnt()
        elif prod == 556: return self.look_stmnt()
        elif prod == 557: return self.chart_stmnt()
        elif prod == 558: return self.hoist_stmnt()
        elif prod == 559: return self.heave_stmnt()
        elif prod == 560: return self.haul_stmnt()
        elif prod == 561:
            n = self.unary_exp(); self.eat('!!'); return n

    # ── Assignment ───────────────────────────────────────────────────────

    def assign_stmnt(self):
        nt = self.current_token; self.eat('id')
        n = self.assign_tail(nt); self.eat('!!'); return n

    def assign_tail(self, nt):
        prod = self.get_production('<assign-tail>')
        if prod == 563:
            if self.current_token and self.current_token.type in ('{', '$'):
                tk, i1, i2, m = self.arr_str()
            else:
                tk, i1, i2, m = 'var', None, None, None
            return self.assign_body(nt, tk, i1, i2, m)
        elif prod == 564:
            self.eat('('); args = self.args(); self.eat(')')
            return FuncCallStmtNode(FuncCallNode(nt.value, args, nt), nt)

    def arr_str(self):
        prod = self.get_production('<arr-str>')
        if prod == 565:
            self.eat('{'); idx1 = self.index_expr(); self.eat('}')
            prod2 = self.get_production('<arr-str-tail>')
            if prod2 == 568:
                self.eat('{'); idx2 = self.index_expr(); self.eat('}')
                return 'array2d', idx1, idx2, None
            return 'array1d', idx1, None, None
        elif prod == 566:
            self.eat('$'); mt = self.current_token; self.eat('id')
            return 'member', None, None, mt.value
        return 'var', None, None, None

    def assign_body(self, nt, tk, i1, i2, m):
        prod = self.get_production('<assign-body>')
        if prod == 570:
            self.eat('='); val = self.value_as()
            return AssignNode(nt.value, tk, i1, i2, m, val, nt)
        elif prod == 571:
            ot = self.current_token; op = self.arith_assign_op()
            val = self.dime_val()
            return CompoundAssignNode(nt.value, tk, i1, i2, m, op, val, ot)

    def value_as(self):
        """RHS of assignment — mirrors value() with as-context tails."""
        prod = self.get_production('<value-as>')
        if prod == 572:
            tok = self.current_token; self.eat('id')
            node = self.id_tail(tok.value, tok)
            return self._exp_as(node)
        elif prod == 573:
            self.eat('('); node = self.value_grp(); self.eat(')')
            return self._exp_as(node)
        elif prod == 574:
            return self._digit_tail_as(self.var_digit())
        elif prod == 575:
            tok = self.current_token; self.eat('PARCH-lit')
            return self._parch_tail_as(LiteralNode('PARCH', tok.value, tok))
        elif prod == 576:
            tok = self.current_token; self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            return self._scroll_tail_as(self.scr_char_opt(base, tok))
        else:  # prod 577: bool
            return self.bool_val()

    def _exp_as(self, left):
        return self._exp_shared(left)

    def _digit_tail_as(self, node):
        prod = self.get_production('<digit-tail-as>')
        if prod == 578:
            node = self.arith_fold(node)
            return self._releq_as(node)
        return node

    def _releq_as(self, left):
        prod = self.get_production('<releq-as>')
        if prod == 582:
            op_tok = self.current_token; op = self.rel_op()
            right = self.arith_fold(self.dime_ope())
            node = BinaryOpNode(left, op, right, op_tok)
            return self._logeq_as(node)
        elif prod == 583:
            # FIX: added bool_exp_fold continuation (syn_parser calls bool_exp_ret)
            op_tok = self.current_token; op = self.eq_op()
            right = self.arith_fold(self.dime_ope())
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)
        return left

    def _logeq_as(self, left):
        prod = self.get_production('<logeq-as>')
        if prod == 589:
            op_tok = self.current_token; op = self._logeq_op()
            right = self.bool_ope()
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)
        return left

    def _parch_tail_as(self, left):
        prod = self.get_production('<parch-tail-as>')
        if prod == 591:
            op_tok = self.current_token; op = self.eq_op()
            rt = self.current_token; self.eat('PARCH-lit')
            node = BinaryOpNode(left, op, LiteralNode('PARCH', rt.value, rt), op_tok)
            return self.bool_exp_fold(node)  # FIX: added continuation
        return left

    def _scroll_tail_as(self, left):
        prod = self.get_production('<scroll-tail-as>')
        if prod == 593: return self.scroll_concat_fold(left)
        elif prod == 594:
            op_tok = self.current_token; op = self.eq_op()
            right = self.scroll_val()
            node = BinaryOpNode(left, op, right, op_tok)
            return self.bool_exp_fold(node)  # FIX: added continuation
        return left

    def arith_assign_op(self):
        tok = self.current_token; self.eat(tok.type); return tok.type

    # ── I/O ──────────────────────────────────────────────────────────────

    def ask_stmnt(self):
        tok = self.current_token
        self.eat('ASK'); self.eat('(')
        ft = self.current_token; self.eat('SCROLL-lit'); self.eat(',')
        targets = self.addr_list()
        self.eat(')'); self.eat('!!')
        return AskNode(ft.value, targets, tok)

    def addr_list(self):
        targets = [self.addr()]
        while self.get_production('<addr-tail>') == 612:
            self.eat(','); targets.append(self.addr())
        return targets

    def addr(self):
        tok = self.current_token; self.eat('@')
        nt = self.current_token; self.eat('id')
        if self.current_token and self.current_token.type in ('{', '$'):
            tk, i1, i2, m = self.arr_str()
        else:
            tk, i1, i2, m = 'var', None, None, None
        return AddressNode(nt.value, tk, i1, i2, m, tok)

    def echo_stmnt(self):
        tok = self.current_token
        self.eat('ECHO'); self.eat('(')
        ft = self.current_token; self.eat('SCROLL-lit')
        args = self._echo_args()
        self.eat(')'); self.eat('!!')
        return EchoNode(ft.value, args, tok)

    def _echo_args(self):
        args = []
        while self.get_production('<args-mult>') == 350:
            self.eat(','); args.append(self.value())
        return args

    # ── Conditional: LOOK ────────────────────────────────────────────────

    def look_stmnt(self):
        return self._look_stmnt_with_tail('ret')

    def _look_stmnt_with_tail(self, ctx):
        tok = self.current_token
        self.eat('LOOK'); self.eat('('); cond = self.condition(); self.eat(')'); self.eat('[')
        body = self.look_body(); jump = self.jump_stmnt()
        if jump: body.append(jump)
        self.eat(']')
        if ctx == 'ahoy':   dl, db = self.ahoy_look_tail()
        elif ctx == 'nonret': dl, db = self.nonret_look_tail()
        else:                dl, db = self.look_tail()
        return LookNode(cond, body, dl, db, tok)

    def condition(self):
        return self.bool_grp_val()

    def look_body(self):
        stmts = []
        prod = self.get_production('<look-body>')
        while prod == 617:
            stmts.append(self.statements()); prod = self.get_production('<look-body>')
        return stmts

    def jump_stmnt(self):
        prod = self.get_production('<jump-stmnt>')
        tok = self.current_token
        if prod == 619: self.eat('SAIL'); self.eat('!!'); return SailNode(tok)
        elif prod == 620: self.eat('LAND'); self.eat('!!'); return LandNode(tok)
        return None

    def look_tail(self):
        droplooks, drop = [], None
        prod = self.get_production('<look-tail>')
        while prod == 622:
            self.eat('DROPLOOK'); self.eat('('); c = self.condition(); self.eat(')'); self.eat('[')
            b = self.look_body(); j = self.jump_stmnt()
            if j: b.append(j)
            self.eat(']'); droplooks.append((c, b))
            prod = self.get_production('<look-tail>')
        if prod == 623:
            self.eat('DROP'); self.eat('[')
            drop = self.look_body(); j = self.jump_stmnt()
            if j: drop.append(j)
            self.eat(']')
        return droplooks, drop

    def ahoy_look_tail(self):
        droplooks, drop = [], None
        prod = self.get_production('<ahoy-look-tail>')
        while prod == 683:
            self.eat('DROPLOOK'); self.eat('('); c = self.condition(); self.eat(')'); self.eat('[')
            b = self.look_body(); j = self.jump_stmnt()
            if j: b.append(j)
            self.eat(']'); droplooks.append((c, b))
            prod = self.get_production('<ahoy-look-tail>')
        if prod == 684:
            self.eat('DROP'); self.eat('[')
            drop = self.look_body(); j = self.jump_stmnt()
            if j: drop.append(j)
            self.eat(']')
        return droplooks, drop

    def nonret_look_tail(self):
        droplooks, drop = [], None
        prod = self.get_production('<nonret-look-tail>')
        while prod == 499:
            self.eat('DROPLOOK'); self.eat('('); c = self.condition(); self.eat(')'); self.eat('[')
            b = self.look_body(); j = self.jump_stmnt()
            if j: b.append(j)
            self.eat(']'); droplooks.append((c, b))
            prod = self.get_production('<nonret-look-tail>')
        if prod == 500:
            self.eat('DROP'); self.eat('[')
            drop = self.look_body(); j = self.jump_stmnt()
            if j: drop.append(j)
            self.eat(']')
        return droplooks, drop

    # ── Switch: CHART ────────────────────────────────────────────────────

    def chart_stmnt(self):
        tok = self.current_token
        self.eat('CHART'); self.eat('('); expr = self.chart_cond(); self.eat(')'); self.eat('[')
        courses = [self.courses()] + self.course_tail()
        adrift = self.adrift_case(); self.eat(']')
        return ChartNode(expr, courses, adrift, tok)

    def chart_cond(self):
        prod = self.get_production('<chart-cond>')
        if prod == 626:
            tok = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                return self.id_tail(tok.value, tok)
            return IdentNode(tok.value, tok)
        else:
            return self.chart_const()

    def chart_const(self):
        prod = self.get_production('<chart-const>')
        tok = self.current_token
        if prod == 628:
            self.eat('COIN-lit'); return LiteralNode('COIN', int(tok.value), tok)
        elif prod == 629:
            self.eat('PARCH-lit'); return LiteralNode('PARCH', tok.value, tok)
        else:  # prod 630
            self.eat('SCROLL-lit'); base = LiteralNode('SCROLL', tok.value, tok)
            if self.current_token and self.current_token.type == '{':
                self.eat('{'); it = self.current_token; self.eat('COIN-lit'); self.eat('}')
                return ScrollCharAccessNode(base, LiteralNode('COIN', int(it.value), it), tok)
            return base

    def courses(self):
        tok = self.current_token; self.eat('COURSE')
        val = self.chart_const(); self.eat(':')
        body = self.course_body(); jump = self.course_jmp()
        if jump: body.append(jump)
        jname = jump.__class__.__name__.replace('Node', '') if jump else None
        return CourseNode(val, body, jname, tok)

    def course_body(self):
        stmts = []
        prod = self.get_production('<course-body>')
        while prod == 632:
            stmts.append(self.statements()); prod = self.get_production('<course-body>')
        return stmts

    def course_jmp(self):
        prod = self.get_production('<course-jmp>')
        tok = self.current_token
        if prod == 634: self.eat('SAIL'); self.eat('!!'); return SailNode(tok)
        elif prod == 635: self.eat('LAND'); self.eat('!!'); return LandNode(tok)
        return None

    def course_tail(self):
        courses = []
        prod = self.get_production('<course-tail>')
        while prod == 637:
            courses.append(self.courses()); prod = self.get_production('<course-tail>')
        return courses

    def adrift_case(self):
        prod = self.get_production('<adrift-case>')
        if prod == 639:
            self.eat('ADRIFT'); self.eat(':')
            body = self.adrift_body(); self.eat('LAND'); self.eat('!!')
            return body
        return None

    def adrift_body(self):
        stmts = []
        prod = self.get_production('<adrift-body>')
        while prod == 641:
            stmts.append(self.statements()); prod = self.get_production('<adrift-body>')
        return stmts

    # ── Loops ────────────────────────────────────────────────────────────

    def hoist_stmnt(self):
        tok = self.current_token
        self.eat('HOIST'); self.eat('(')
        inits = self.hoist_init(); self.eat('!!')
        cond = self.hoist_cond(); self.eat('!!')
        updates = self.hoist_upd(); self.eat(')'); self.eat('[')
        body = self.look_body(); jump = self.jump_stmnt()
        if jump: body.append(jump)
        self.eat(']')
        return HoistNode(inits, cond, updates, body, None, tok)

    def hoist_init(self):
        """Parse HOIST initializer(s).

        Now uses coin_val() instead of eating a bare COIN-lit, so the
        init value can be a variable, array element, struct member,
        function call, or arithmetic expression — as long as the
        overall type is COIN.
        """
        prod = self.get_production('<hoist-init>')
        inits = []
        if prod == 644:
            # COIN id = <coin-val> ...
            self.eat('COIN'); nt = self.current_token; self.eat('id')
            self.eat('='); val = self.coin_val()
            inits.append(HoistInitNode(True, nt.value, val, nt))
            inits.extend(self.init1_mult())
        elif prod == 645:
            # id [arr_str] = <coin-val> ...
            nt = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$'):
                self.arr_str()
            self.eat('='); val = self.coin_val()
            inits.append(HoistInitNode(False, nt.value, val, nt))
            inits.extend(self.init2_mult())
        return inits  # prod 646: λ

    def init1_mult(self):
        """Multiple new-variable HOIST inits: , id = <coin-val> ..."""
        inits = []
        while self.get_production('<init1-mult>') == 647:
            self.eat(','); nt = self.current_token; self.eat('id')
            self.eat('='); val = self.coin_val()
            inits.append(HoistInitNode(True, nt.value, val, nt))
        return inits

    def init2_mult(self):
        """Multiple existing-variable HOIST inits: , id [arr_str] = <coin-val> ..."""
        inits = []
        while self.get_production('<init2-mult>') == 649:
            self.eat(','); nt = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$'):
                self.arr_str()
            self.eat('='); val = self.coin_val()
            inits.append(HoistInitNode(False, nt.value, val, nt))
        return inits

    def hoist_cond(self):
        left = self.dime_val()
        op_tok = self.current_token; op = self.releq_op()
        right = self.dime_val()
        node = BinaryOpNode(left, op, right, op_tok)
        return self._hoist_log_fold(node)

    def releq_op(self):
        tok = self.current_token; self.eat(tok.type); return tok.type

    def _hoist_log_fold(self, node):
        prod = self.get_production('<hoist-log>')
        if prod == 654:
            op_tok = self.current_token; op = self.log_op()
            right = self.hoist_cond()
            return BinaryOpNode(node, op, right, op_tok)
        return node

    def hoist_upd(self):
        updates = [self.upd()]
        while self.get_production('<upd-mult>') == 659:
            self.eat(','); updates.append(self.upd())
        return updates

    def upd(self):
        prod = self.get_production('<upd>')
        if prod == 657:
            ot = self.current_token; op = '+#' if ot.type == '+#' else '-#'
            self.eat(ot.type); nt = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$'):
                tk, i1, _, m = self.arr_str()
            else: tk, i1, m = 'var', None, None
            return HoistUpdateNode('unary', nt.value, tk, i1, m, op, None, None, ot)
        else:  # prod 658
            nt = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$'):
                tk, i1, _, m = self.arr_str()
            else: tk, i1, m = 'var', None, None
            ot = self.current_token; op = self.arith_assign_op()
            val = self.dime_val()
            return HoistUpdateNode('compound', nt.value, tk, i1, m, None, op, val, ot)

    def heave_stmnt(self):
        tok = self.current_token
        self.eat('HEAVE'); self.eat('('); cond = self.condition(); self.eat(')'); self.eat('[')
        body = self.look_body(); jump = self.jump_stmnt()
        if jump: body.append(jump)
        self.eat(']')
        return HeaveNode(cond, body, None, tok)

    def haul_stmnt(self):
        tok = self.current_token
        self.eat('HAUL'); self.eat('[')
        body = self.look_body(); jump = self.jump_stmnt()
        if jump: body.append(jump)
        self.eat(']'); self.eat('HEAVE'); self.eat('(')
        cond = self.condition(); self.eat(')'); self.eat('!!')
        return HaulHeaveNode(body, cond, None, tok)

    def unary_exp(self):
        ot = self.current_token; op = self.unary_op()
        nt = self.current_token; self.eat('id')
        if self.current_token and self.current_token.type in ('{', '$'):
            tk, i1, i2, m = self.arr_str()
        else: tk, i1, i2, m = 'var', None, None, None
        return UnaryStmtNode(op, nt.value, tk, i1, i2, m, ot)

    def unary_op(self):
        tok = self.current_token; self.eat(tok.type); return tok.type

    # =====================================================================
    # EXPRESSIONS
    # =====================================================================

    # ── value() — universal expression entry ─────────────────────────────

    def value(self):
        prod = self.get_production('<value>')
        if prod == 352:
            tok = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                node = self.id_tail(tok.value, tok)
            else: node = IdentNode(tok.value, tok)
            return self._exp_shared(node)
        elif prod == 353:
            self.eat('('); node = self.value_grp(); self.eat(')')
            return self._exp_shared(node)
        elif prod == 354:
            return self._digit_tail_var(self.var_digit())
        elif prod == 355:
            tok = self.current_token; self.eat('PARCH-lit')
            return self._parch_tail_var(LiteralNode('PARCH', tok.value, tok))
        elif prod == 356:
            tok = self.current_token; self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            return self._scroll_tail_var(self.scr_char_opt(base, tok))
        else:  # prod 357: bool
            return self.bool_val()

    def _digit_tail_var(self, node):
        prod = self.get_production('<digit-tail>')
        if prod == 358:
            node = self.arith_fold(node)
            return self._releq_var(node)
        return node

    def _releq_var(self, left):
        prod = self.get_production('<releq-var>')
        if prod == 362:
            op_tok = self.current_token; op = self.rel_op()
            right = self.arith_fold(self.dime_ope())
            return self._logeq_var(BinaryOpNode(left, op, right, op_tok))
        elif prod == 363:
            op_tok = self.current_token; op = self.eq_op()
            right = self.arith_fold(self.dime_ope())
            return self._log_var(BinaryOpNode(left, op, right, op_tok))
        return left

    def _logeq_var(self, left):
        prod = self.get_production('<logeq-var>')
        if prod == 369:
            op_tok = self.current_token; op = self._logeq_op()
            right = self.bool_ope()
            return self._log_var(BinaryOpNode(left, op, right, op_tok))
        return left

    def _log_var(self, left):
        prod = self.get_production('<log-var>')
        if prod == 373:
            op_tok = self.current_token; op = self.log_op()
            right = self.bool_ope()
            return self._log_var(BinaryOpNode(left, op, right, op_tok))
        return left

    def _parch_tail_var(self, left):
        prod = self.get_production('<parch-tail>')
        if prod == 375:
            op_tok = self.current_token; op = self.eq_op()
            rt = self.current_token; self.eat('PARCH-lit')
            return self._log_var(BinaryOpNode(left, op,
                LiteralNode('PARCH', rt.value, rt), op_tok))
        return left

    def _scroll_tail_var(self, left):
        prod = self.get_production('<scroll-tail>')
        if prod == 377: return self.scroll_concat_fold(left)
        elif prod == 378:
            op_tok = self.current_token; op = self.eq_op()
            right = self.scroll_val()
            return self._log_var(BinaryOpNode(left, op, right, op_tok))
        return left

    def _exp_shared(self, left):
        """Shared exp handler for id/grouped expressions in var/as/str contexts."""
        prod = self.get_production('<exp>')
        if prod == 382:
            left = self.arith_fold(left); return self._releq_var(left)
        elif prod == 383:
            op_tok = self.current_token; op = self.rel_op()
            right = self.arith_fold(self.dime_ope())
            return self._logeq_var(BinaryOpNode(left, op, right, op_tok))
        elif prod == 384:
            op_tok = self.current_token; op = self.log_op()
            right = self.bool_ope()
            return self._log_var(BinaryOpNode(left, op, right, op_tok))
        elif prod == 385:
            op_tok = self.current_token; op = self.eq_op()
            right = self._eq_var()
            return self._log_var(BinaryOpNode(left, op, right, op_tok))
        elif prod == 386:
            return self.scroll_concat_fold(left)
        return left  # prod 387: λ

    def _eq_var(self):
        prod = self.get_production('<eq-var>')
        if prod == 402:
            tok = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                node = self.id_tail(tok.value, tok)
            else: node = IdentNode(tok.value, tok)
            node = self.arith_fold(node); return self._rel_var(node)
        elif prod == 403:
            self.eat('('); node = self.value_grp(); self.eat(')')
            node = self.arith_fold(node); return self._rel_var(node)
        elif prod == 404:
            node = self.arith_fold(self.var_digit()); return self._rel_var(node)
        else:
            return self._eq_ope1()

    def _rel_var(self, left):
        prod = self.get_production('<rel-var>')
        if prod == 408:
            op_tok = self.current_token; op = self.rel_op()
            right = self.arith_fold(self.dime_ope())
            return BinaryOpNode(left, op, right, op_tok)
        return left

    # ── value_grp() — inside parentheses ─────────────────────────────────

    def value_grp(self):
        prod = self.get_production('<value-grp>')
        if prod == 410:
            tok = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                node = self.id_tail(tok.value, tok)
            else: node = IdentNode(tok.value, tok)
            return self._exp_grp(node)
        elif prod == 411:
            self.eat('('); node = self.value_grp(); self.eat(')')
            return self._exp_grp(node)
        elif prod == 412:
            return self._digit_tail_grp(self.var_digit())
        elif prod == 413:
            tok = self.current_token; self.eat('PARCH-lit')
            return self._parch_tail_grp(LiteralNode('PARCH', tok.value, tok))
        elif prod == 414:
            tok = self.current_token; self.eat('SCROLL-lit')
            base = LiteralNode('SCROLL', tok.value, tok)
            return self._scroll_tail_grp(self.scr_char_opt(base, tok))
        else:
            return self.bool_val()

    def _exp_grp(self, left):
        prod = self.get_production('<exp-grp>')
        if prod == 436:
            left = self.arith_fold(left); return self._releqvar_grp(left)
        elif prod == 437:
            op_tok = self.current_token; op = self.rel_op()
            right = self.arith_fold(self.dime_ope())
            return self._logeq_grp(BinaryOpNode(left, op, right, op_tok))
        elif prod == 438:
            op_tok = self.current_token; op = self.log_op()
            right = self.bool_grp_ope()
            return self._bool_exp_grp(BinaryOpNode(left, op, right, op_tok))
        elif prod == 439:
            op_tok = self.current_token; op = self.eq_op()
            right = self._eq_ope_grp()
            return self._bool_exp_grp(BinaryOpNode(left, op, right, op_tok))
        elif prod == 440:
            return self.scroll_concat_fold(left)
        return left

    def _digit_tail_grp(self, node):
        prod = self.get_production('<digit-tail-grp>')
        if prod == 416:
            node = self.arith_fold(node); return self._releqvar_grp(node)
        return node

    def _releqvar_grp(self, left):
        prod = self.get_production('<releqvar-grp>')
        if prod == 420:
            op_tok = self.current_token; op = self.rel_op()
            right = self.arith_fold(self.dime_ope())
            return self._logeq_grp(BinaryOpNode(left, op, right, op_tok))
        elif prod == 421:
            # FIX: added _bool_exp_grp continuation (syn_parser calls bool_exp_grp)
            op_tok = self.current_token; op = self.eq_op()
            right = self.arith_fold(self.dime_ope())
            node = BinaryOpNode(left, op, right, op_tok)
            return self._bool_exp_grp(node)
        return left

    def _logeq_grp(self, left):
        prod = self.get_production('<logeq-grp>')
        if prod == 427:
            op_tok = self.current_token; op = self._logeq_op()
            right = self.bool_grp_ope()
            return self._bool_exp_grp(BinaryOpNode(left, op, right, op_tok))
        return left

    def _bool_exp_grp(self, left):
        prod = self.get_production('<bool-exp-grp>')
        if prod == 258:
            op_tok = self.current_token; op = self.log_op()
            right = self.bool_grp_ope()
            return self._bool_exp_grp(BinaryOpNode(left, op, right, op_tok))
        return left

    def _parch_tail_grp(self, left):
        prod = self.get_production('<parch-tail-grp>')
        if prod == 429:
            op_tok = self.current_token; op = self.eq_op()
            rt = self.current_token; self.eat('PARCH-lit')
            return self._bool_exp_grp(BinaryOpNode(left, op,
                LiteralNode('PARCH', rt.value, rt), op_tok))
        return left

    def _scroll_tail_grp(self, left):
        prod = self.get_production('<scroll-tail-grp>')
        if prod == 431: return self.scroll_concat_fold(left)
        elif prod == 432:
            op_tok = self.current_token; op = self.eq_op()
            right = self.scroll_val()
            return self._bool_exp_grp(BinaryOpNode(left, op, right, op_tok))
        return left

    def _eq_ope_grp(self):
        prod = self.get_production('<eq-ope-grp>')
        if prod == 250:
            tok = self.current_token; self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                node = self.id_tail(tok.value, tok)
            else: node = IdentNode(tok.value, tok)
            return self.arith_fold(node)
        elif prod == 251:
            self.eat('('); node = self.value_grp(); self.eat(')')
            return self.arith_fold(node)
        elif prod == 252:
            return self.arith_fold(self.var_digit())
        else:
            return self._eq_ope1()

    def _eq_ope1(self):
        prod = self.get_production('<eq-ope1>')
        tok = self.current_token
        if prod == 220:
            self.eat('PARCH-lit'); return LiteralNode('PARCH', tok.value, tok)
        elif prod == 221:
            self.eat('SCROLL-lit'); base = LiteralNode('SCROLL', tok.value, tok)
            return self.scr_char_opt(base, tok)
        else:
            return self._bool_literal()

    # ── ID Tail ──────────────────────────────────────────────────────────

    def id_tail(self, name, tok):
        prod = self.get_production('<id-tail>')
        if prod == 342:
            self.eat('{'); idx1 = self.index_expr(); self.eat('}')
            prod2 = self.get_production('<elmt2>')
            if prod2 == 346:
                self.eat('{'); idx2 = self.index_expr(); self.eat('}')
                return ArrayAccessNode(name, [idx1, idx2], tok)
            return ArrayAccessNode(name, [idx1], tok)
        elif prod == 343:
            self.eat('$'); mt = self.current_token; self.eat('id')
            return MemberAccessNode(name, mt.value, tok)
        elif prod == 344:
            self.eat('('); args = self.args(); self.eat(')')
            return FuncCallNode(name, args, tok)
        else:
            return IdentNode(name, tok)

    def index_expr(self):
        prod = self.get_production('<index>')
        tok = self.current_token
        if prod == 137: self.eat('id'); return IdentNode(tok.value, tok)
        else: self.eat('COIN-lit'); return LiteralNode('COIN', int(tok.value), tok)

    def args(self):
        prod = self.get_production('<args>')
        if prod == 348:
            first = self.value()
            rest = self._args_mult()
            return [first] + rest
        return []

    def _args_mult(self):
        prod = self.get_production('<args-mult>')
        if prod == 350: self.eat(','); return self.args()
        return []

    # ── Type-specific expression builders ────────────────────────────────

    def coin_val(self):
        prod = self.get_production('<coin-val>')
        tok = self.current_token
        if prod == 21:
            self.eat('COIN-lit'); node = LiteralNode('COIN', int(tok.value), tok)
        else:
            has_neg = (self.current_token.type == '-')
            if has_neg: self.eat('-')
            node = self.neg_coin_val()
            if has_neg: node = UnaryOpNode('-', node, tok)
        return self.arith_fold(node)

    def neg_coin_val(self):
        prod = self.get_production('<neg-coin-val>')
        tok = self.current_token
        if prod == 25:
            self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                return self.id_tail(tok.value, tok)
            return IdentNode(tok.value, tok)
        else:
            self.eat('('); val = self.coin_val(); self.eat(')'); return val

    def dime_val(self):
        prod = self.get_production('<dime-val>')
        tok = self.current_token
        if prod == 68:
            self.eat('DIME-lit'); node = LiteralNode('DIME', float(tok.value), tok)
        elif prod == 69:
            self.eat('COIN-lit'); node = LiteralNode('COIN', int(tok.value), tok)
        else:
            has_neg = (self.current_token.type == '-')
            if has_neg: self.eat('-')
            node = self.neg_dime_val()
            if has_neg: node = UnaryOpNode('-', node, tok)
        return self.arith_fold(node)

    def neg_dime_val(self):
        prod = self.get_production('<neg-dime-val>')
        tok = self.current_token
        if prod == 71:
            self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                return self.id_tail(tok.value, tok)
            return IdentNode(tok.value, tok)
        else:
            self.eat('('); val = self.dime_val(); self.eat(')'); return val

    def dime_ope(self):
        return self.dime_val()

    def _dime_atom(self):
        """Parse a single atomic term without arith continuation.
        Used by arith_fold so that a - b - c stays left-associative:
        arith_fold consumes one atom at a time instead of letting
        dime_val() greedily consume the entire right-hand chain."""
        prod = self.get_production('<dime-val>')
        tok = self.current_token
        if prod == 68:
            self.eat('DIME-lit'); return LiteralNode('DIME', float(tok.value), tok)
        elif prod == 69:
            self.eat('COIN-lit'); return LiteralNode('COIN', int(tok.value), tok)
        else:
            has_neg = (self.current_token.type == '-')
            if has_neg: self.eat('-')
            node = self.neg_dime_val()
            if has_neg: return UnaryOpNode('-', node, tok)
            return node

    def arith_fold(self, left):
        """Left-associative fold of arith_op dime_val chains."""
        while self.current_token and self.current_token.type in ('+', '-', '*', '/', '%', '^'):
            op_tok = self.current_token; op = self.arith_op()
            right = self._dime_atom()
            left = BinaryOpNode(left, op, right, op_tok)
        return left

    def arith_op(self):
        tok = self.current_token; self.eat(tok.type); return tok.type

    def parch_val(self):
        prod = self.get_production('<parch-val>')
        tok = self.current_token
        if prod == 107:
            self.eat('PARCH-lit'); return LiteralNode('PARCH', tok.value, tok)
        else:
            self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                return self.id_tail(tok.value, tok)
            return IdentNode(tok.value, tok)

    def scroll_val(self):
        prod = self.get_production('<scroll-val>')
        tok = self.current_token
        if prod == 132:
            self.eat('SCROLL-lit')
            first = self.scr_char_opt(LiteralNode('SCROLL', tok.value, tok), tok)
        elif prod == 133:
            self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                first = self.id_tail(tok.value, tok)
            else: first = IdentNode(tok.value, tok)
        else:  # prod 134
            self.eat('('); first = self.scroll_val(); self.eat(')')
        return self.scroll_concat_fold(first)

    def scr_char_opt(self, base, tok):
        if self.current_token and self.current_token.type == '{':
            prod = self.get_production('<scr-char>')
            if prod == 135:
                self.eat('{'); idx = self.index_expr(); self.eat('}')
                return ScrollCharAccessNode(base, idx, tok)
        return base

    def scroll_concat_fold(self, left):
        """& concat fold — produces StringConcatNode."""
        if self.current_token and self.current_token.type == '&':
            tok = self.current_token; operands = [left]
            while self.current_token and self.current_token.type == '&':
                self.eat('&'); operands.append(self.scroll_val())
            return StringConcatNode(operands, tok)
        return left

    def var_digit(self):
        prod = self.get_production('<digit>')
        tok = self.current_token
        if prod == 191:
            self.eat('COIN-lit'); return LiteralNode('COIN', int(tok.value), tok)
        elif prod == 192:
            self.eat('DIME-lit'); return LiteralNode('DIME', float(tok.value), tok)
        else:
            self.eat('-'); inner = self.neg_digit()
            return UnaryOpNode('-', inner, tok)

    def neg_digit(self):
        prod = self.get_production('<neg-digit>')
        tok = self.current_token
        if prod == 194:
            self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                return self.id_tail(tok.value, tok)
            return IdentNode(tok.value, tok)
        else:
            self.eat('('); val = self.dime_val(); self.eat(')'); return val

    # ── Boolean expressions ──────────────────────────────────────────────

    def bool_val(self):
        """Bool value entry — used in init/general contexts."""
        left = self.bool_ope()
        return self.bool_exp_fold(left)

    def bool_grp_val(self):
        """Bool value in condition context — uses grp PREDICT entries."""
        left = self.bool_grp_ope()
        return self._bool_exp_grp(left)

    def bool_grp_ope(self):
        prod = self.get_production('<bool-ope-grp>')
        tok = self.current_token
        if prod == 232:
            self.eat('id')
            if self.current_token and self.current_token.type in ('{', '$', '('):
                node = self.id_tail(tok.value, tok)
            else: node = IdentNode(tok.value, tok)
            return self._bool_exp2_grp(node)
        elif prod == 233:
            self.eat('('); node = self.value_grp(); self.eat(')')
            return self._bool_exp2_grp(node)
        elif prod == 234:
            node = self._bool_literal()
            return self._bool_eq_grp(node)
        elif prod == 235:
            left = self.arith_fold(self.var_digit())
            return self._releq_grp(left)
        elif prod == 236:
            self.eat('PARCH-lit')
            left = LiteralNode('PARCH', tok.value, tok)
            op_tok = self.current_token; op = self.eq_op()
            return BinaryOpNode(left, op, self.parch_val(), op_tok)
        elif prod == 237:
            self.eat('SCROLL-lit')
            left = self.scr_char_opt(LiteralNode('SCROLL', tok.value, tok), tok)
            op_tok = self.current_token; op = self.eq_op()
            return BinaryOpNode(left, op, self.scroll_val(), op_tok)

    def _bool_exp2_grp(self, left):
        prod = self.get_production('<bool-exp2-grp>')
        if prod == 246:
            left = self.arith_fold(left); return self._releq_grp(left)
        elif prod == 247:
            op_tok = self.current_token; op = self.rel_op()
            right = self.arith_fold(self.dime_val())
            return self._bool_eq_grp(BinaryOpNode(left, op, right, op_tok))
        elif prod == 248:
            op_tok = self.current_token; op = self.eq_op()
            right = self._eq_ope_grp()
            return BinaryOpNode(left, op, right, op_tok)
        return left

    def _bool_eq_grp(self, left):
        prod = self.get_production('<bool-eq-grp>')
        if prod == 238:
            op_tok = self.current_token; op = self.eq_op()
            return BinaryOpNode(left, op, self.bool_grp_ope(), op_tok)
        return left

    def _releq_grp(self, left):
        prod = self.get_production('<releq-grp>')
        if prod == 240:
            op_tok = self.current_token; op = self.rel_op()
            right = self.arith_fold(self.dime_val())
            return self._bool_eq_grp(BinaryOpNode(left, op, right, op_tok))
        elif prod == 241:
            op_tok = self.current_token; op = self.eq_op()
            right = self.arith_fold(self.dime_val())
            return BinaryOpNode(left, op, right, op_tok)
        return left

    def bool_ope(self):
        """Same as bool_grp_ope — AST structure is identical."""
        return self.bool_grp_ope()

    def _bool_literal(self):
        tok = self.current_token
        if tok.type == 'AYE':
            self.eat('AYE'); return LiteralNode('BOOL', True, tok)
        elif tok.type == 'NAY':
            self.eat('NAY'); return LiteralNode('BOOL', False, tok)
        else:
            # NOT operator (! or !#)
            op_tok = self.current_token; op = op_tok.type; self.eat(op_tok.type)
            not_prod = self.get_production('<not-ope>')
            inner_tok = self.current_token
            if not_prod == 186:
                self.eat('id')
                if self.current_token and self.current_token.type in ('{', '$', '('):
                    operand = self.id_tail(inner_tok.value, inner_tok)
                else: operand = IdentNode(inner_tok.value, inner_tok)
            elif not_prod == 187:
                self.eat('('); operand = self.value_grp(); self.eat(')')
            else:
                if inner_tok.type == 'AYE':
                    self.eat('AYE'); operand = LiteralNode('BOOL', True, inner_tok)
                else:
                    self.eat('NAY'); operand = LiteralNode('BOOL', False, inner_tok)
            return UnaryOpNode(op, operand, op_tok)

    def bool_exp_fold(self, left):
        """Fold && || bool_val chains."""
        prod = self.get_production('<bool-exp>')
        if prod == 227:
            op_tok = self.current_token; op = self.log_op()
            right = self.bool_val()
            return self.bool_exp_fold(BinaryOpNode(left, op, right, op_tok))
        return left

    def _logeq_op(self):
        tok = self.current_token; self.eat(tok.type); return tok.type

    def rel_op(self):
        tok = self.current_token; self.eat(tok.type); return tok.type

    def eq_op(self):
        tok = self.current_token; self.eat(tok.type); return tok.type

    def log_op(self):
        tok = self.current_token; self.eat(tok.type); return tok.type