# =============================================================================
# semantic_analyzer.py — SeaStack Semantic Analyzer
#
# Walks AST via visitor pattern. Expression visitors return dtype strings.
# Statement visitors return None. Non-fatal errors are collected.
#
# =============================================================================

import re
from semantic.symbol_table import ( Symbol, ArraySymbol, FunctionSymbol, StructTypeSymbol, StructVarSymbol, SymbolTable, )
from semantic.ast_nodes import NamedInitNode, PositionalInitNode
from backend.semantic.sem_error_msg import SemanticErrorHandler

class SemanticAnalyzer:
    def __init__(self, ast, source_code):
        self.ast = ast
        self.source_code = source_code
        self.sym = SymbolTable()
        self.errors = []
        self.err = SemanticErrorHandler(source_code)

        # Context tracking
        self.current_func_return = None
        self.loop_depth = 0
        self.in_conditional = 0
        self.in_chart = False
        self.in_adrift = False
        self.known_values = {}

    # ── Entry Point ──────────────────────────────────────────────────────

    def analyze(self):
        self.visit(self.ast)
        return self.errors

    # ── Visitor Dispatch ─────────────────────────────────────────────────

    def visit(self, node):
        if node is None: return None
        method = f'visit_{type(node).__name__}'
        return getattr(self, method, self._visit_unknown)(node)

    def _visit_unknown(self, node):
        self._e(self.err.internal_no_visitor(type(node).__name__))

    # ── Error Helper ─────────────────────────────────────────────────────

    # Append a pre-built error dict from SemanticErrorHandler.
    def _e(self, error_dict):
        self.errors.append(error_dict)

    # ── Type Helpers ─────────────────────────────────────────────────────

    # Assignment compatibility: exact match or COIN → DIME promotion.
    def _compatible(self, expected, actual):
        if expected == actual: return True
        if expected == 'DIME' and actual == 'COIN': return True
        return False

    # Expression compatibility: COIN ↔ DIME are compatible.
    def _compatible_expr(self, left, right):
        if left == right: return True
        if left in ('COIN', 'DIME') and right in ('COIN', 'DIME'): return True
        return False

    def _is_numeric(self, dtype): return dtype in ('COIN', 'DIME')
    def _is_bool(self, dtype): return dtype == 'BOOL'
    def _type_name(self, dtype): return dtype if dtype else 'unknown'

    # ── Bounds Checking ──────────────────────────────────────────────────

    # Get compile-time COIN int value, or None for runtime values.
    def _literal_int(self, node):
        if type(node).__name__ == 'LiteralNode':
            if getattr(node, 'dtype', None) != 'COIN': return None
            try: return int(getattr(node, 'value', None))
            except (TypeError, ValueError): return None
        if type(node).__name__ == 'IdentNode':
            name = getattr(node, 'name', None)
            if name and name in self.known_values:
                dtype, val = self.known_values[name]
                if dtype == 'COIN':
                    try: return int(val)
                    except (TypeError, ValueError): return None
        return None

    # Get compile-time SCROLL string length, or None for runtime values.
    def _known_scroll_length(self, node):
        if type(node).__name__ == 'LiteralNode' and getattr(node, 'dtype', None) == 'SCROLL':
            raw = getattr(node, 'value', None)
            if raw is not None: return len(str(raw))
        if type(node).__name__ == 'IdentNode':
            name = getattr(node, 'name', None)
            if name and name in self.known_values:
                dtype, val = self.known_values[name]
                if dtype == 'SCROLL' and val is not None:
                    return len(str(val))
        return None

    def _check_bounds(self, arr_name, dim_label, idx_expr, size, token):
        v = self._literal_int(idx_expr)
        if v is not None and (v < 0 or v >= size):
            self._e(self.err.array_index_out_of_bounds(token, arr_name, dim_label, v, size))

    # ── Format Specifiers ────────────────────────────────────────────────

    _SPEC_MAP = {'C': 'COIN', 'D': 'DIME', 'P': 'PARCH', 'S': 'SCROLL', 'B': 'BOOL'}

    def _parse_specs(self, fmt):
        return [self._SPEC_MAP[ch] for ch in re.findall(r'%([CDPSB])', fmt)]

    # =====================================================================
    # PROGRAM STRUCTURE
    # =====================================================================

    def visit_ProgramNode(self, node):
        # Pass 1: pre-register functions and struct types for forward refs
        for d in node.global_decls:
            cn = type(d).__name__
            if cn == 'FuncDefNode': self._pre_register_func(d)
            elif cn == 'StructDefNode': self._pre_register_struct(d)
        # Pass 2: full analysis
        for d in node.global_decls: self.visit(d)
        self.visit(node.ahoy_body)

    def _pre_register_func(self, node):
        if not self.sym.lookup_current_scope(node.name):
            self.sym.declare(FunctionSymbol(node.name, node.return_type, node.params, node.token))

    def _pre_register_struct(self, node):
        if not self.sym.lookup_current_scope(node.name):
            members = {m.name: m.dtype for m in node.members}
            order = [m.name for m in node.members]
            self.sym.declare(StructTypeSymbol(node.name, members, order, node.token))

    def visit_AhoyNode(self, node):
        self.sym.push_scope()
        for d in node.local_decls: self.visit(d)
        for s in node.statements: self.visit(s)
        self.sym.pop_scope()

    # =====================================================================
    # DECLARATIONS
    # =====================================================================

    def visit_ConstDeclNode(self, node):
        # LOCKE can only be declared globally
        if not self.sym.is_global_scope():
            self._e(self.err.locke_not_global(node.token, node.name))
            return
        if self.sym.lookup_current_scope(node.name):
            self._e(self.err.duplicate_const(node.token, node.name))
            return
        self.sym.declare(Symbol(node.name, node.dtype, 'const', node.token, is_initialized=True))

    def visit_VarDeclNode(self, node):
        if self.sym.lookup_current_scope(node.name):
            self._e(self.err.duplicate_variable(node.token, node.name))
            return
        if node.init_value is not None:
            init_type = self.visit(node.init_value)
            if init_type and not self._compatible(node.dtype, init_type):
                self._e(self.err.type_mismatch_init(node.token, node.name, node.dtype, self._type_name(init_type)))
            # Track compile-time known value for constant propagation
            if type(node.init_value).__name__ == 'LiteralNode':
                self.known_values[node.name] = (node.dtype, node.init_value.value)
        self.sym.declare(Symbol(node.name, node.dtype, 'var', node.token,
                                is_initialized=(node.init_value is not None)))

    def visit_ArrayDeclNode(self, node):
        if self.sym.lookup_current_scope(node.name):
            self._e(self.err.duplicate_array(node.token, node.name))
            return
        if node.init_values is not None:
            if node.is_2d:
                dr, dc = node.dimensions[0], node.dimensions[1]
                if len(node.init_values) > dr:
                    self._e(self.err.array_init_too_many_rows(node.token, node.name, len(node.init_values), dr))
                for ri, row in enumerate(node.init_values):
                    if len(row) > dc:
                        self._e(self.err.array_init_row_too_long(node.token, node.name, ri, len(row), dc))
                    for ci, elem in enumerate(row):
                        et = self.visit(elem)
                        if et and not self._compatible(node.dtype, et):
                            self._e(self.err.type_mismatch_array_element(node.token, node.name, f'[{ri}][{ci}]', node.dtype, self._type_name(et)))
            else:
                ds = node.dimensions[0]
                if len(node.init_values) > ds:
                    self._e(self.err.array_init_too_many_elements(node.token, node.name, len(node.init_values), ds))
                for i, elem in enumerate(node.init_values):
                    et = self.visit(elem)
                    if et and not self._compatible(node.dtype, et):
                        self._e(self.err.type_mismatch_array_element(node.token, node.name, f'[{i}]', node.dtype, self._type_name(et)))
        self.sym.declare(ArraySymbol(node.name, node.dtype, node.dimensions, node.is_2d, node.token))

    def visit_StructDefNode(self, node):
        existing = self.sym.lookup_current_scope(node.name)
        if existing and existing.kind == 'struct':
            # Already pre-registered — just validate members
            seen = set()
            for m in node.members:
                if m.name in seen:
                    self._e(self.err.duplicate_struct_member(m.token, m.name, node.name))
                seen.add(m.name)
            return
        if existing:
            self._e(self.err.duplicate_identifier(node.token, node.name))
            return
        members, order = {}, []
        for m in node.members:
            if m.name in members:
                self._e(self.err.duplicate_struct_member(m.token, m.name, node.name))
            else:
                members[m.name] = m.dtype; order.append(m.name)
        self.sym.declare(StructTypeSymbol(node.name, members, order, node.token))

    def visit_MemberDeclNode(self, node): pass

    def visit_StructVarDeclNode(self, node):
        type_sym = self.sym.lookup(node.struct_type)
        if type_sym is None or type_sym.kind != 'struct':
            self._e(self.err.undefined_struct_type(node.token, node.struct_type)); return
        members, order = type_sym.members, type_sym.member_order
        if self.sym.lookup_current_scope(node.var_name):
            self._e(self.err.duplicate_variable(node.token, node.var_name)); return
        if node.inits:
            if len(node.inits) > len(order):
                self._e(self.err.struct_too_many_inits(node.token, node.struct_type, len(order), len(node.inits)))
            else:
                pos = 0
                for init in node.inits:
                    if isinstance(init, NamedInitNode):
                        if init.member_name not in members:
                            self._e(self.err.no_such_member(init.token, node.struct_type, init.member_name))
                        else:
                            actual = self.visit(init.value)
                            if actual and not self._compatible(members[init.member_name], actual):
                                self._e(self.err.type_mismatch_struct_member(init.token, init.member_name, node.struct_type, members[init.member_name], self._type_name(actual)))
                        if init.member_name in order:
                            pos = order.index(init.member_name) + 1
                    elif isinstance(init, PositionalInitNode):
                        if pos >= len(order):
                            self._e(self.err.struct_positional_overflow(node.token, node.struct_type)); break
                        mname = order[pos]; expected = members[mname]
                        actual = self.visit(init.value)
                        if actual and not self._compatible(expected, actual):
                            self._e(self.err.type_mismatch_struct_member(node.token, mname, node.struct_type, expected, self._type_name(actual)))
                        pos += 1
        self.sym.declare(StructVarSymbol(node.var_name, node.struct_type, node.token))

    def visit_PositionalInitNode(self, node): return self.visit(node.value)
    def visit_NamedInitNode(self, node): return self.visit(node.value)

    def visit_FuncDefNode(self, node):
        existing = self.sym.lookup_current_scope(node.name)
        if existing is None:
            if not self.sym.declare(FunctionSymbol(node.name, node.return_type, node.params, node.token)):
                self._e(self.err.duplicate_function(node.token, node.name)); return
        elif existing.kind != 'func':
            self._e(self.err.function_name_conflict(node.token, node.name, existing.kind)); return

        outer_ret = self.current_func_return
        self.current_func_return = node.return_type
        self.sym.push_scope()

        for p in node.params:
            if self.sym.lookup_current_scope(p.name):
                self._e(self.err.duplicate_parameter(p.token, p.name, node.name))
            else:
                self.sym.declare(Symbol(p.name, p.dtype, 'param', p.token, is_initialized=True))

        for d in node.local_decls: self.visit(d)
        for s in node.body: self.visit(s)

        if node.return_type != 'ABYSS' and node.return_expr is not None:
            rt = self.visit(node.return_expr)
            if rt and not self._compatible(node.return_type, rt):
                self._e(self.err.type_mismatch_return(node.token, node.name, node.return_type, self._type_name(rt)))

        self.sym.pop_scope()
        self.current_func_return = outer_ret

    def visit_ParamNode(self, node): pass

    # =====================================================================
    # STATEMENTS
    # =====================================================================

    def _target_label(self, var_name, target_kind, index1, index2, member):
        if target_kind == 'member' and member:
            return f"{var_name}${member}"
        elif target_kind == 'array2d' and index1 is not None and index2 is not None:
            i1 = getattr(index1, 'value', '?')
            i2 = getattr(index2, 'value', '?')
            return f"{var_name}{{{i1}}}{{{i2}}}"
        elif target_kind == 'array1d' and index1 is not None:
            i1 = getattr(index1, 'value', '?')
            return f"{var_name}{{{i1}}}"
        return var_name

    def visit_AssignNode(self, node):
        target_dtype = self._resolve_target(
            node.var_name, node.target_kind, node.index1, node.index2, node.member, node.token)
        if target_dtype is not None:
            val_type = self.visit(node.value)
            if val_type and not self._compatible(target_dtype, val_type):
                label = self._target_label(
                    node.var_name, node.target_kind, node.index1, node.index2, node.member)
                self._e(self.err.type_mismatch_assign(node.token, label, target_dtype, self._type_name(val_type)))
            # Mark initialized
            self.sym.update_initialized(node.var_name)
            # Track compile-time known value for simple variable assignments
            if node.target_kind == 'var':
                if type(node.value).__name__ == 'LiteralNode':
                    self.known_values[node.var_name] = (target_dtype, node.value.value)
                else:
                    # Value is now runtime-determined; remove from known values
                    self.known_values.pop(node.var_name, None)

    def visit_CompoundAssignNode(self, node):
        target_dtype = self._resolve_target(
            node.var_name, node.target_kind, node.index1, node.index2, node.member, node.token)
        if target_dtype is not None:
            label = self._target_label(
                node.var_name, node.target_kind, node.index1, node.index2, node.member)
            if not self._is_numeric(target_dtype):
                self._e(self.err.compound_assign_not_numeric(node.token, node.operator, label, target_dtype))
            val_type = self.visit(node.value)
            if val_type and not self._is_numeric(val_type):
                self._e(self.err.compound_assign_rhs_not_numeric(node.token, node.operator, self._type_name(val_type)))
            # Mark the variable as initialized after compound assignment
            self.sym.update_initialized(node.var_name)
            # Value is now runtime-determined; remove from known values
            self.known_values.pop(node.var_name, None)

    # Resolve assignment target dtype. Returns None on error.
    def _resolve_target(self, var_name, target_kind, index1, index2, member, token):
        sym = self.sym.lookup(var_name)
        if sym is None:
            self._e(self.err.undeclared_variable(token, var_name)); return None
        if sym.kind == 'const':
            self._e(self.err.locke_assignment(token, var_name)); return None

        if target_kind == 'var':
            return sym.dtype
        elif target_kind in ('array1d', 'array2d'):
            if sym.kind != 'array':
                self._e(self.err.not_an_array(token, var_name)); return None
            if index1 is not None:
                it = self.visit(index1)
                if it and it != 'COIN':
                    self._e(self.err.array_index_not_coin(token, var_name, 0, self._type_name(it)))
                lbl = 'row index' if sym.is_2d else 'index'
                self._check_bounds(var_name, lbl, index1, sym.dimensions[0], token)
            if index2 is not None:
                it = self.visit(index2)
                if it and it != 'COIN':
                    self._e(self.err.array_index_not_coin(token, var_name, 1, self._type_name(it)))
                if len(sym.dimensions) > 1:
                    self._check_bounds(var_name, 'column index', index2, sym.dimensions[1], token)
            return sym.dtype
        elif target_kind == 'member':
            if sym.kind != 'struct_var':
                self._e(self.err.not_a_struct_variable(token, var_name)); return None
            ts = self.sym.lookup(sym.struct_type_name)
            if ts is None or ts.kind != 'struct':
                self._e(self.err.unresolvable_struct_type(token, sym.struct_type_name)); return None
            if member not in ts.members:
                self._e(self.err.no_such_member(token, sym.struct_type_name, member)); return None
            return ts.members[member]
        return None

    def visit_AskNode(self, node):
        specs = self._parse_specs(node.format_string)
        if len(specs) != len(node.targets):
            self._e(self.err.ask_specifier_count_mismatch(node.token, len(specs), len(node.targets)))
        for i, tgt in enumerate(node.targets):
            tgt_dtype = self._resolve_addr_target(tgt)
            if i < len(specs) and tgt_dtype:
                if not self._compatible(specs[i], tgt_dtype):
                    spec_ch = [k for k, v in self._SPEC_MAP.items() if v == specs[i]]
                    self._e(self.err.ask_specifier_type_mismatch(tgt.token, spec_ch[0] if spec_ch else '?', specs[i], tgt.var_name, tgt_dtype))
            # ASK reads input into the target, so mark it as initialized
            self.sym.update_initialized(tgt.var_name)
            # Value is now runtime-determined; remove from known values
            self.known_values.pop(tgt.var_name, None)

    def _resolve_addr_target(self, node):
        sym = self.sym.lookup(node.var_name)
        if sym is None:
            self._e(self.err.undeclared_variable_in_context(node.token, node.var_name, 'ASK target')); return None
        if sym.kind == 'const':
            self._e(self.err.locke_ask_target(node.token, node.var_name)); return None
        if node.target_kind in ('array1d', 'array2d'):
            if sym.kind != 'array':
                self._e(self.err.not_an_array(node.token, node.var_name)); return None
            if node.index1 is not None:
                it = self.visit(node.index1)
                if it and it != 'COIN':
                    self._e(self.err.ask_array_index_not_coin(node.token, node.var_name, 0, self._type_name(it)))
                lbl = 'row index' if sym.is_2d else 'index'
                self._check_bounds(node.var_name, lbl, node.index1, sym.dimensions[0], node.token)
            if getattr(node, 'index2', None) is not None:
                it = self.visit(node.index2)
                if it and it != 'COIN':
                    self._e(self.err.ask_array_index_not_coin(node.token, node.var_name, 1, self._type_name(it)))
                if len(sym.dimensions) > 1:
                    self._check_bounds(node.var_name, 'column index', node.index2, sym.dimensions[1], node.token)
            return sym.dtype
        elif node.target_kind == 'member':
            if sym.kind != 'struct_var':
                self._e(self.err.not_a_struct_variable(node.token, node.var_name)); return None
            ts = self.sym.lookup(sym.struct_type_name)
            if ts and node.member in ts.members: return ts.members[node.member]
            self._e(self.err.no_such_member(node.token, sym.struct_type_name, node.member)); return None
        return sym.dtype

    def visit_AddressNode(self, node): self._resolve_addr_target(node)

    def visit_EchoNode(self, node):
        specs = self._parse_specs(node.format_string)
        if len(specs) != len(node.args):
            self._e(self.err.echo_specifier_count_mismatch(node.token, len(specs), len(node.args)))
        for i, arg in enumerate(node.args):
            at = self.visit(arg)
            if i < len(specs) and at:
                if not self._compatible(specs[i], at):
                    sc = [k for k, v in self._SPEC_MAP.items() if v == specs[i]]
                    self._e(self.err.echo_specifier_type_mismatch(node.token, sc[0] if sc else '?', specs[i], self._type_name(at)))

    # ── Conditionals ─────────────────────────────────────────────────────

    def visit_LookNode(self, node):
        ct = self.visit(node.condition)
        if ct and not self._is_bool(ct):
            self._e(self.err.condition_not_bool(node.token, 'LOOK', self._type_name(ct)))
        self.sym.push_scope(); self.in_conditional += 1
        for s in node.body: self.visit(s)
        self.in_conditional -= 1; self.sym.pop_scope()
        for (dc, db) in node.droplooks:
            dt = self.visit(dc)
            if dt and not self._is_bool(dt):
                self._e(self.err.condition_not_bool(node.token, 'DROPLOOK', self._type_name(dt)))
            self.sym.push_scope(); self.in_conditional += 1
            for s in db: self.visit(s)
            self.in_conditional -= 1; self.sym.pop_scope()
        if node.drop_body is not None:
            self.sym.push_scope(); self.in_conditional += 1
            for s in node.drop_body: self.visit(s)
            self.in_conditional -= 1; self.sym.pop_scope()

    def visit_ChartNode(self, node):
        expr_type = self.visit(node.expr)
        if expr_type and expr_type not in ('COIN', 'PARCH', 'SCROLL'):
            self._e(self.err.chart_invalid_expr_type(node.token, self._type_name(expr_type)))
        outer_chart = self.in_chart; self.in_chart = True
        # duplicate COURSE label check using value+dtype
        seen = {}
        for course in node.courses:
            case_type = self.visit(course.value)
            if expr_type and case_type and not self._compatible(expr_type, case_type):
                self._e(self.err.course_type_mismatch(course.token, self._type_name(case_type), self._type_name(expr_type)))
            # Build label key from dtype+value for reliable comparison
            label_key = self._course_label_key(course.value)
            if label_key in seen:
                self._e(self.err.course_duplicate_label(course.token))
            else:
                seen[label_key] = True

            self.sym.push_scope(); self.in_conditional += 1
            for s in course.body: self.visit(s)
            self.in_conditional -= 1; self.sym.pop_scope()

        if node.adrift_body is not None:
            outer_adrift = self.in_adrift; self.in_adrift = True
            self.sym.push_scope(); self.in_conditional += 1
            for s in node.adrift_body: self.visit(s)
            self.in_conditional -= 1; self.sym.pop_scope()
            self.in_adrift = outer_adrift
        self.in_chart = outer_chart

    # Generate a reliable key for COURSE label duplicate detection.
    def _course_label_key(self, node):
        cn = type(node).__name__
        if cn == 'LiteralNode': return (node.dtype, node.value)
        if cn == 'ScrollCharAccessNode':
            inner = getattr(node.scroll_expr, 'value', '?')
            idx = getattr(node.index, 'value', '?')
            return ('SCROLL_CHAR', inner, idx)
        return id(node)  # fallback

    def visit_CourseNode(self, node): pass

    # ── Loops ────────────────────────────────────────────────────────────

    def visit_HoistNode(self, node):
        self.sym.push_scope()
        for init in node.inits: self.visit(init)
        ct = self.visit(node.condition)
        if ct and not self._is_bool(ct):
            self._e(self.err.condition_not_bool(node.token, 'HOIST', self._type_name(ct)))
        for upd in node.updates: self.visit(upd)
        self.loop_depth += 1
        for s in node.body: self.visit(s)
        self.loop_depth -= 1
        self.sym.pop_scope()

    def visit_HoistInitNode(self, node):
        # Visit the init value expression and type-check it.
        # The value can now be a literal, variable, element, member, function call, or arithmetic expression — but must resolve to COIN.
        val_type = None
        if node.value is not None:
            val_type = self.visit(node.value)

        if node.declares_new:
            # COIN id = <coin-val>  — declares a new loop variable
            if self.sym.lookup_current_scope(node.var_name):
                self._e(self.err.loop_variable_conflict(node.token, node.var_name))
            else:
                self.sym.declare(Symbol(node.var_name, 'COIN', 'var', node.token, is_initialized=True))
            # Type-check the init value: must be COIN (or compatible)
            if val_type and not self._compatible('COIN', val_type):
                self._e(self.err.type_mismatch_hoist_init(node.token, node.var_name, self._type_name(val_type)))
        else:
            # id = <coin-val>  — assigns to an existing variable
            sym = self.sym.lookup(node.var_name)
            if sym is None:
                self._e(self.err.undeclared_variable_in_context(node.token, node.var_name, 'HOIST init'))
            elif sym.kind == 'const':
                self._e(self.err.locke_hoist_init(node.token, node.var_name))
            elif sym.dtype != 'COIN':
                self._e(self.err.type_mismatch_hoist_var(node.token, node.var_name, sym.dtype))
            else:
                # Type-check the init value: must be COIN
                if val_type and not self._compatible('COIN', val_type):
                    self._e(self.err.type_mismatch_hoist_init(node.token, node.var_name, self._type_name(val_type)))
                # Mark the variable as initialized
                self.sym.update_initialized(node.var_name)

    def visit_HoistUpdateNode(self, node):
        sym = self.sym.lookup(node.var_name)
        if sym is None:
            self._e(self.err.undeclared_variable_in_context(node.token, node.var_name, 'HOIST update')); return
        if sym.kind == 'const':
            self._e(self.err.locke_hoist_update(node.token, node.var_name)); return
        if node.update_kind == 'unary':
            if sym.dtype != 'COIN':
                self._e(self.err.hoist_update_unary_not_coin(node.token, node.unary_op, node.var_name, sym.dtype))
        elif node.update_kind == 'compound':
            if not self._is_numeric(sym.dtype):
                self._e(self.err.hoist_update_compound_not_numeric(node.token, node.var_name, sym.dtype))
            if node.value is not None:
                vt = self.visit(node.value)
                if vt and not self._is_numeric(vt):
                    self._e(self.err.hoist_update_value_not_numeric(node.token, self._type_name(vt)))

    def visit_HeaveNode(self, node):
        ct = self.visit(node.condition)
        if ct and not self._is_bool(ct):
            self._e(self.err.condition_not_bool(node.token, 'HEAVE', self._type_name(ct)))
        self.sym.push_scope(); self.loop_depth += 1
        for s in node.body: self.visit(s)
        self.loop_depth -= 1; self.sym.pop_scope()

    def visit_HaulHeaveNode(self, node):
        self.sym.push_scope(); self.loop_depth += 1
        for s in node.body: self.visit(s)
        self.loop_depth -= 1; self.sym.pop_scope()
        ct = self.visit(node.condition)
        if ct and not self._is_bool(ct):
            self._e(self.err.condition_not_bool(node.token, 'HAUL-HEAVE', self._type_name(ct)))

    # ── Jump Statements ──────────────────────────────────────────────────

    def visit_SailNode(self, node):
        if self.in_adrift:
            self._e(self.err.sail_inside_adrift(node.token)); return
        if self.loop_depth == 0:
            self._e(self.err.sail_outside_loop(node.token))

    def visit_LandNode(self, node):
        if self.loop_depth == 0 and not self.in_chart:
            self._e(self.err.land_outside_loop(node.token))

    def visit_ReturnNode(self, node):
        if self.current_func_return is None:
            self._e(self.err.back_outside_function(node.token)); return
        if self.current_func_return == 'ABYSS':
            self._e(self.err.back_value_in_abyss(node.token)); return
        rt = self.visit(node.value)
        if rt and not self._compatible(self.current_func_return, rt):
            self._e(self.err.type_mismatch_return(node.token, '(current function)', self.current_func_return, self._type_name(rt)))

    def visit_BackNode(self, node):
        if self.current_func_return is None:
            self._e(self.err.back_outside_function(node.token))
        elif self.current_func_return != 'ABYSS':
            self._e(self.err.back_missing_value(node.token, self.current_func_return))

    def visit_UnaryStmtNode(self, node):
        sym = self.sym.lookup(node.var_name)
        if sym is None:
            self._e(self.err.undeclared_variable(node.token, node.var_name)); return
        if sym.kind == 'const':
            self._e(self.err.locke_operator(node.token, node.operator, node.var_name)); return
        # Unary +# -# operates on COIN only (rule p.38)
        if sym.dtype != 'COIN':
            self._e(self.err.invalid_operand_unary_stmt(node.token, node.operator, node.var_name, sym.dtype))
        # Value is now runtime-determined; remove from known values
        self.known_values.pop(node.var_name, None)

    # Validate the call directly so that ABYSS-returning functions are allowed.
    def visit_FuncCallStmtNode(self, node):
        call = node.call_expr
        sym = self.sym.lookup(call.name)
        if sym is None:
            self._e(self.err.undeclared_function(call.token, call.name)); return
        if sym.kind != 'func':
            self._e(self.err.not_a_function(call.token, call.name)); return
        exp_cnt, act_cnt = len(sym.params), len(call.args)
        if exp_cnt != act_cnt:
            self._e(self.err.arg_count_mismatch(call.token, call.name, exp_cnt, act_cnt))
        else:
            for idx, (p, a) in enumerate(zip(sym.params, call.args)):
                at = self.visit(a)
                if at and not self._compatible(p.dtype, at):
                    self._e(self.err.arg_type_mismatch(call.token, call.name, idx+1, p.dtype, self._type_name(at)))
        # Non-ABYSS functions may also be called as statements (return value is discarded).
        # ABYSS functions are intentionally allowed here and nowhere else.

    # =====================================================================
    # EXPRESSIONS
    # =====================================================================

    def visit_LiteralNode(self, node): return node.dtype

    def visit_IdentNode(self, node):
        sym = self.sym.lookup(node.name)
        if sym is None:
            self._e(self.err.undeclared_variable(node.token, node.name)); return None
        # A lone identifier (no parentheses) is ONLY a variable or constant.
        # If the name resolves to a function, it must be treated as undeclared
        # because function references require parentheses: greet() not greet.
        if sym.kind == 'func':
            self._e(self.err.undeclared_variable(node.token, node.name)); return None
        if not sym.is_initialized:
            self._e(self.err.uninitialized_variable(node.token, node.name))
        return sym.dtype

    def visit_ArrayAccessNode(self, node):
        sym = self.sym.lookup(node.name)
        if sym is None:
            self._e(self.err.undeclared_variable(node.token, node.name)); return None

        # SCROLL character indexing: scroll{n} yields a single PARCH character.
        # The parser emits ArrayAccessNode for all {}-indexing, so we redirect
        # here instead of raising "not an array" for SCROLL variables.
        if sym.kind == 'var' and sym.dtype == 'SCROLL':
            if not sym.is_initialized:
                self._e(self.err.uninitialized_variable(node.token, node.name))
            if len(node.indices) != 1:
                self._e(self.err.scroll_char_requires_scroll(node.token, node.name))
                return None
            it = self.visit(node.indices[0])
            if it and it != 'COIN':
                self._e(self.err.scroll_char_index_not_coin(node.token, self._type_name(it)))
            # Compile-time bounds check using known SCROLL length
            # Look up the variable name directly, since _known_scroll_length
            # expects a LiteralNode or IdentNode, not an ArrayAccessNode.
            str_len = None
            if node.name in self.known_values:
                kv_dtype, kv_val = self.known_values[node.name]
                if kv_dtype == 'SCROLL' and kv_val is not None:
                    str_len = len(str(kv_val))
            if str_len is not None:
                idx_val = self._literal_int(node.indices[0])
                if idx_val is not None and (idx_val < 0 or idx_val >= str_len):
                    self._e(self.err.scroll_char_index_out_of_bounds(node.token, idx_val, str_len))
            # Stamp resolved type on the node for the IR generator
            node.resolved_type = 'SCROLL'
            return 'SCROLL'

        if sym.kind != 'array':
            self._e(self.err.not_an_array(node.token, node.name)); return None
        for i, idx in enumerate(node.indices):
            it = self.visit(idx)
            if it and it != 'COIN':
                self._e(self.err.array_index_not_coin(node.token, node.name, i, self._type_name(it)))
            if i < len(sym.dimensions):
                lbl = 'column index' if (sym.is_2d and i == 1) else 'row index' if (sym.is_2d and i == 0) else 'index'
                self._check_bounds(node.name, lbl, idx, sym.dimensions[i], node.token)
        return sym.dtype

    def visit_MemberAccessNode(self, node):
        sym = self.sym.lookup(node.var_name)
        if sym is None:
            self._e(self.err.undeclared_variable(node.token, node.var_name)); return None
        if sym.kind != 'struct_var':
            self._e(self.err.not_a_struct_variable(node.token, node.var_name)); return None
        ts = self.sym.lookup(sym.struct_type_name)
        if ts is None or ts.kind != 'struct':
            self._e(self.err.unresolvable_struct_type(node.token, sym.struct_type_name)); return None
        if node.member_name not in ts.members:
            self._e(self.err.no_such_member(node.token, sym.struct_type_name, node.member_name)); return None
        return ts.members[node.member_name]

    def visit_ScrollCharAccessNode(self, node):
        st = self.visit(node.scroll_expr)
        if st and st != 'SCROLL':
            self._e(self.err.scroll_char_requires_scroll(node.token, self._type_name(st)))
        it = self.visit(node.index)
        if it and it != 'COIN':
            self._e(self.err.scroll_char_index_not_coin(node.token, self._type_name(it)))
        # Compile-time bounds check (works for both literals and known variables)
        str_len = self._known_scroll_length(node.scroll_expr)
        if str_len is not None:
            idx_val = self._literal_int(node.index)
            if idx_val is not None:
                if idx_val < 0 or idx_val >= str_len:
                    self._e(self.err.scroll_char_index_out_of_bounds(node.token, idx_val, str_len))
        return 'SCROLL'  # SCROLL char access returns a single-char SCROLL

    def visit_StringConcatNode(self, node):
        for op in node.operands:
            ot = self.visit(op)
            if ot and ot != 'SCROLL':
                self._e(self.err.scroll_concat_requires_scroll(node.token, self._type_name(ot)))
        return 'SCROLL'

    def visit_FuncCallNode(self, node):
        sym = self.sym.lookup(node.name)
        if sym is None:
            self._e(self.err.undeclared_function(node.token, node.name)); return None
        if sym.kind != 'func':
            self._e(self.err.not_a_function(node.token, node.name)); return None
        exp_cnt, act_cnt = len(sym.params), len(node.args)
        if exp_cnt != act_cnt:
            self._e(self.err.arg_count_mismatch(node.token, node.name, exp_cnt, act_cnt))
        else:
            for i, (p, a) in enumerate(zip(sym.params, node.args)):
                at = self.visit(a)
                if at and not self._compatible(p.dtype, at):
                    self._e(self.err.arg_type_mismatch(node.token, node.name, i+1, p.dtype, self._type_name(at)))
        if sym.return_type == 'ABYSS':
            self._e(self.err.abyss_in_expression(node.token, node.name))
            return None
        return sym.return_type

    def visit_BinaryOpNode(self, node):
        lt = self.visit(node.left); rt = self.visit(node.right)
        op = node.operator
        if op in ('+', '-', '*', '/', '%', '^'):
            if lt and not self._is_numeric(lt):
                self._e(self.err.invalid_operand_binary(node.token, op, 'left', self._type_name(lt)))
            if rt and not self._is_numeric(rt):
                self._e(self.err.invalid_operand_binary(node.token, op, 'right', self._type_name(rt)))
            return 'DIME' if (lt == 'DIME' or rt == 'DIME') else 'COIN'
        elif op in ('<', '>', '<=', '>='):
            if lt and not self._is_numeric(lt):
                self._e(self.err.invalid_operand_relational(node.token, op, 'left', self._type_name(lt)))
            if rt and not self._is_numeric(rt):
                self._e(self.err.invalid_operand_relational(node.token, op, 'right', self._type_name(rt)))
            return 'BOOL'
        elif op in ('==', '!='):
            if lt and rt and not self._compatible_expr(lt, rt):
                self._e(self.err.incompatible_comparison(node.token, op, self._type_name(lt), self._type_name(rt)))
            return 'BOOL'
        elif op in ('&&', '||'):
            if lt and not self._is_bool(lt):
                self._e(self.err.invalid_operand_logical(node.token, op, 'left', self._type_name(lt)))
            if rt and not self._is_bool(rt):
                self._e(self.err.invalid_operand_logical(node.token, op, 'right', self._type_name(rt)))
            return 'BOOL'
        return None

    def visit_UnaryOpNode(self, node):
        ot = self.visit(node.operand); op = node.operator
        if op == '-':
            if ot and not self._is_numeric(ot):
                self._e(self.err.invalid_operand_unary_neg(node.token, self._type_name(ot)))
            return ot
        elif op in ('!', '!#'):
            if ot and not self._is_bool(ot):
                self._e(self.err.invalid_operand_not(node.token, op, self._type_name(ot)))
            return 'BOOL'
        return None