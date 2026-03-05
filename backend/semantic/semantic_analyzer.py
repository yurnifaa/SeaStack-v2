# =============================================================================
# semantic_analyzer.py — SeaStack Semantic Analyzer
#
# Walks AST via visitor pattern. Expression visitors return dtype strings.
# Statement visitors return None. Non-fatal errors are collected.
#
# KEY FIXES from original:
#   - Added global-scope check for LOCKE constants
#   - Compound assignment now checks target is initialized
#   - Improved COURSE duplicate label detection using value comparison
#   - Assignment marks arrays/structs as initialized at base level
# =============================================================================

import re
from semantic.symbol_table import (
    Symbol, ArraySymbol, FunctionSymbol,
    StructTypeSymbol, StructVarSymbol, SymbolTable,
)
from semantic.ast_nodes import NamedInitNode, PositionalInitNode


class SemanticAnalyzer:
    def __init__(self, ast, source_code):
        self.ast = ast
        self.source_code = source_code
        self.sym = SymbolTable()
        self.errors = []

        # Context tracking
        self.current_func_return = None  # return type of current function (None = global/AHOY)
        self.loop_depth = 0              # HOIST/HEAVE/HAUL depth
        self.in_conditional = 0          # LOOK/CHART conditional depth
        self.in_chart = False            # inside CHART block
        self.in_adrift = False           # inside ADRIFT body

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
        self.errors.append({'type': 'Internal', 'message': f'No visitor for {type(node).__name__}',
                           'line': '?', 'col': '?'})

    # ── Error Helper ─────────────────────────────────────────────────────

    def error(self, token, message):
        line = getattr(token, 'line', '?')
        col = getattr(token, 'col', '?')
        actual_line = ""
        if line != '?' and line != '-':
            try:
                ln = int(line) - 1
                src_lines = self.source_code.split('\n')
                if 0 <= ln < len(src_lines): actual_line = src_lines[ln].strip()
            except (ValueError, IndexError, AttributeError): pass

        self.errors.append({
            'line': line, 'col': col,
            'error_type': self._classify_error(message),
            'message': message, 'actual_line': actual_line,
        })

    def _classify_error(self, msg):
        m = msg.lower()
        if 'may be used before' in m: return 'Uninitialized Variable'
        if 'already declared' in m or 'duplicate' in m: return 'Duplicate Declaration'
        if 'undeclared' in m or 'undefined' in m: return 'Undeclared Variable'
        if 'locke' in m and ('assign' in m or 'modify' in m or 'apply' in m): return 'LOCKE Modification'
        if 'read-only' in m: return 'LOCKE Modification'
        if 'only be declared globally' in m: return 'Invalid LOCKE Scope'
        if 'type mismatch' in m or 'cannot initialize' in m: return 'Type Mismatch'
        if 'incompatible' in m: return 'Type Mismatch'
        if 'cannot assign' in m: return 'Invalid Assignment'
        if 'outside' in m: return 'Outside Scope'
        if 'operator' in m and ('requires' in m or 'must' in m): return 'Invalid Operand Type'
        if 'chart' in m and 'expression' in m: return 'Invalid CHART Expression'
        if 'course' in m and 'duplicate' in m: return 'Duplicate COURSE Label'
        if 'out of bounds' in m: return 'Array Index Out of Bounds'
        if 'initializer has' in m and ('row' in m or 'exceed' in m): return 'Array Bounds Exceeded'
        if 'array index' in m and 'must be coin' in m: return 'Invalid Index Type'
        if 'is not an array' in m: return 'Invalid Array'
        if 'has no member' in m: return 'Undefined Struct Member'
        if 'expects' in m and 'argument' in m: return 'Argument Count Mismatch'
        if 'specifier' in m and ('expects' in m or 'mismatch' in m): return 'Format Specifier Mismatch'
        if 'function' in m: return 'Function Error'
        if 'back' in m and ('outside' in m or 'abyss' in m or 'return' in m): return 'Invalid Return Context'
        if ('sail' in m or 'land' in m) and 'outside' in m: return 'Invalid Jump Context'
        if 'cannot be used as an expression' in m: return 'Invalid Expression Context'
        if 'condition' in m and 'must' in m: return 'Invalid Condition Type'
        return 'Semantic Error'

    # ── Type Helpers ─────────────────────────────────────────────────────

    def _compatible(self, expected, actual):
        """Assignment compatibility: exact match or COIN→DIME promotion."""
        if expected == actual: return True
        if expected == 'DIME' and actual == 'COIN': return True
        return False

    def _compatible_expr(self, left, right):
        """Expression compatibility: COIN↔DIME are compatible."""
        if left == right: return True
        if left in ('COIN', 'DIME') and right in ('COIN', 'DIME'): return True
        return False

    def _is_numeric(self, dtype): return dtype in ('COIN', 'DIME')
    def _is_bool(self, dtype): return dtype == 'BOOL'
    def _type_name(self, dtype): return dtype if dtype else 'unknown'

    # ── Bounds Checking ──────────────────────────────────────────────────

    def _literal_int(self, node):
        """Get compile-time COIN int value, or None for runtime values."""
        if type(node).__name__ != 'LiteralNode': return None
        if getattr(node, 'dtype', None) != 'COIN': return None
        try: return int(getattr(node, 'value', None))
        except (TypeError, ValueError): return None

    def _check_bounds(self, arr_name, dim_label, idx_expr, size, token):
        v = self._literal_int(idx_expr)
        if v is not None and (v < 0 or v >= size):
            self.error(token,
                f"Array '{arr_name}' {dim_label} {v} is out of bounds "
                f"(declared size {size}, valid range 0–{size - 1}).")

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
        # LOCKE can only be declared globally (rule p.11)
        if not self.sym.is_global_scope():
            self.error(node.token,
                f"LOCKE '{node.name}' can only be declared globally.")
            return
        if self.sym.lookup_current_scope(node.name):
            self.error(node.token, f"LOCKE '{node.name}' is already declared in this scope.")
            return
        self.sym.declare(Symbol(node.name, node.dtype, 'const', node.token, is_initialized=True))

    def visit_VarDeclNode(self, node):
        if self.sym.lookup_current_scope(node.name):
            self.error(node.token, f"Variable '{node.name}' is already declared in this scope.")
            return
        if node.init_value is not None:
            init_type = self.visit(node.init_value)
            if init_type and not self._compatible(node.dtype, init_type):
                self.error(node.token,
                    f"Cannot initialize '{node.dtype}' variable '{node.name}' "
                    f"with a '{self._type_name(init_type)}' value.")
        self.sym.declare(Symbol(node.name, node.dtype, 'var', node.token,
                                is_initialized=(node.init_value is not None)))

    def visit_ArrayDeclNode(self, node):
        if self.sym.lookup_current_scope(node.name):
            self.error(node.token, f"Array '{node.name}' is already declared in this scope.")
            return
        if node.init_values is not None:
            if node.is_2d:
                dr, dc = node.dimensions[0], node.dimensions[1]
                if len(node.init_values) > dr:
                    self.error(node.token,
                        f"Array '{node.name}' initializer has {len(node.init_values)} "
                        f"row(s) but was declared with {dr} row(s).")
                for ri, row in enumerate(node.init_values):
                    if len(row) > dc:
                        self.error(node.token,
                            f"Array '{node.name}' row [{ri}] has {len(row)} element(s) "
                            f"but the declared column size is {dc}.")
                    for ci, elem in enumerate(row):
                        et = self.visit(elem)
                        if et and not self._compatible(node.dtype, et):
                            self.error(node.token,
                                f"Array '{node.name}' element [{ri}][{ci}] has type "
                                f"'{self._type_name(et)}', expected '{node.dtype}'.")
            else:
                ds = node.dimensions[0]
                if len(node.init_values) > ds:
                    self.error(node.token,
                        f"Array '{node.name}' initializer has {len(node.init_values)} "
                        f"element(s) but was declared with size {ds}.")
                for i, elem in enumerate(node.init_values):
                    et = self.visit(elem)
                    if et and not self._compatible(node.dtype, et):
                        self.error(node.token,
                            f"Array '{node.name}' element [{i}] has type "
                            f"'{self._type_name(et)}', expected '{node.dtype}'.")
        self.sym.declare(ArraySymbol(node.name, node.dtype, node.dimensions, node.is_2d, node.token))

    def visit_StructDefNode(self, node):
        existing = self.sym.lookup_current_scope(node.name)
        if existing and existing.kind == 'struct':
            # Already pre-registered — just validate members
            seen = set()
            for m in node.members:
                if m.name in seen:
                    self.error(m.token, f"Struct '{node.name}' has duplicate member '{m.name}'.")
                seen.add(m.name)
            return
        if existing:
            self.error(node.token, f"Identifier '{node.name}' is already declared in this scope.")
            return
        members, order = {}, []
        for m in node.members:
            if m.name in members:
                self.error(m.token, f"Struct '{node.name}' has duplicate member '{m.name}'.")
            else:
                members[m.name] = m.dtype; order.append(m.name)
        self.sym.declare(StructTypeSymbol(node.name, members, order, node.token))

    def visit_MemberDeclNode(self, node): pass

    def visit_StructVarDeclNode(self, node):
        type_sym = self.sym.lookup(node.struct_type)
        if type_sym is None or type_sym.kind != 'struct':
            self.error(node.token, f"Undefined struct type '{node.struct_type}'."); return
        members, order = type_sym.members, type_sym.member_order
        if self.sym.lookup_current_scope(node.var_name):
            self.error(node.token, f"Variable '{node.var_name}' is already declared in this scope."); return
        if node.inits:
            if len(node.inits) > len(order):
                self.error(node.token,
                    f"Struct '{node.struct_type}' has {len(order)} member(s) "
                    f"but {len(node.inits)} initializer(s) were provided.")
            else:
                pos = 0
                for init in node.inits:
                    if isinstance(init, NamedInitNode):
                        if init.member_name not in members:
                            self.error(init.token,
                                f"Struct type '{node.struct_type}' has no member '{init.member_name}'.")
                        else:
                            actual = self.visit(init.value)
                            if actual and not self._compatible(members[init.member_name], actual):
                                self.error(init.token,
                                    f"Member '{init.member_name}' of '{node.struct_type}' "
                                    f"expects '{members[init.member_name]}', got '{self._type_name(actual)}'.")
                        if init.member_name in order:
                            pos = order.index(init.member_name) + 1
                    elif isinstance(init, PositionalInitNode):
                        if pos >= len(order):
                            self.error(node.token, f"Too many positional initializers for struct '{node.struct_type}'."); break
                        mname = order[pos]; expected = members[mname]
                        actual = self.visit(init.value)
                        if actual and not self._compatible(expected, actual):
                            self.error(node.token,
                                f"Positional initializer {pos+1} for struct '{node.struct_type}' "
                                f"member '{mname}' expects '{expected}', got '{self._type_name(actual)}'.")
                        pos += 1
        self.sym.declare(StructVarSymbol(node.var_name, node.struct_type, node.token))

    def visit_PositionalInitNode(self, node): return self.visit(node.value)
    def visit_NamedInitNode(self, node): return self.visit(node.value)

    def visit_FuncDefNode(self, node):
        existing = self.sym.lookup_current_scope(node.name)
        if existing is None:
            if not self.sym.declare(FunctionSymbol(node.name, node.return_type, node.params, node.token)):
                self.error(node.token, f"Function '{node.name}' is already declared in this scope."); return
        elif existing.kind != 'func':
            self.error(node.token, f"'{node.name}' is already declared as a '{existing.kind}' in this scope."); return

        outer_ret = self.current_func_return
        self.current_func_return = node.return_type
        self.sym.push_scope()

        for p in node.params:
            if self.sym.lookup_current_scope(p.name):
                self.error(p.token, f"Duplicate parameter name '{p.name}' in function '{node.name}'.")
            else:
                self.sym.declare(Symbol(p.name, p.dtype, 'param', p.token, is_initialized=True))

        for d in node.local_decls: self.visit(d)
        for s in node.body: self.visit(s)

        if node.return_type != 'ABYSS' and node.return_expr is not None:
            rt = self.visit(node.return_expr)
            if rt and not self._compatible(node.return_type, rt):
                self.error(node.token,
                    f"Function '{node.name}' declared to return '{node.return_type}' "
                    f"but BACK expression has type '{self._type_name(rt)}'.")

        self.sym.pop_scope()
        self.current_func_return = outer_ret

    def visit_ParamNode(self, node): pass

    # =====================================================================
    # STATEMENTS
    # =====================================================================

    def _target_label(self, var_name, target_kind, index1, index2, member):
        """Build a human-readable label for the assignment target.
        e.g. 'b1$crew', 'arr{2}', 'grid{1}{0}', or just 'x'."""
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
                self.error(node.token,
                    f"Cannot assign '{self._type_name(val_type)}' to '{label}'.")
            # Mark initialized
            self.sym.update_initialized(node.var_name)

    def visit_CompoundAssignNode(self, node):
        target_dtype = self._resolve_target(
            node.var_name, node.target_kind, node.index1, node.index2, node.member, node.token)
        if target_dtype is not None:
            # NOTE: the LHS of a compound assignment does not need to be initialized
            # beforehand — as long as it is declared, it may be assigned to.
            label = self._target_label(
                node.var_name, node.target_kind, node.index1, node.index2, node.member)
            if not self._is_numeric(target_dtype):
                self.error(node.token,
                    f"Compound assignment operator '{node.operator}' can only be used "
                    f"on numeric types, but '{label}' is '{target_dtype}'.")
            val_type = self.visit(node.value)
            if val_type and not self._is_numeric(val_type):
                self.error(node.token,
                    f"Right-hand side of '{node.operator}' must be numeric, "
                    f"got '{self._type_name(val_type)}'.")
            # Mark the variable as initialized after compound assignment
            self.sym.update_initialized(node.var_name)

    def _resolve_target(self, var_name, target_kind, index1, index2, member, token):
        """Resolve assignment target dtype. Returns None on error."""
        sym = self.sym.lookup(var_name)
        if sym is None:
            self.error(token, f"Undeclared variable '{var_name}'."); return None
        if sym.kind == 'const':
            self.error(token, f"Cannot assign to LOCKE '{var_name}'."); return None

        if target_kind == 'var':
            return sym.dtype
        elif target_kind in ('array1d', 'array2d'):
            if sym.kind != 'array':
                self.error(token, f"'{var_name}' is not an array."); return None
            if index1 is not None:
                it = self.visit(index1)
                if it and it != 'COIN':
                    self.error(token, f"Array index for '{var_name}' must be COIN, got '{self._type_name(it)}'.")
                lbl = 'row index' if sym.is_2d else 'index'
                self._check_bounds(var_name, lbl, index1, sym.dimensions[0], token)
            if index2 is not None:
                it = self.visit(index2)
                if it and it != 'COIN':
                    self.error(token, f"Second array index for '{var_name}' must be COIN, got '{self._type_name(it)}'.")
                if len(sym.dimensions) > 1:
                    self._check_bounds(var_name, 'column index', index2, sym.dimensions[1], token)
            return sym.dtype
        elif target_kind == 'member':
            if sym.kind != 'struct_var':
                self.error(token, f"'{var_name}' is not a struct variable."); return None
            ts = self.sym.lookup(sym.struct_type_name)
            if ts is None or ts.kind != 'struct':
                self.error(token, f"Cannot resolve struct type '{sym.struct_type_name}'."); return None
            if member not in ts.members:
                self.error(token, f"Struct '{sym.struct_type_name}' has no member '{member}'."); return None
            return ts.members[member]
        return None

    def visit_AskNode(self, node):
        specs = self._parse_specs(node.format_string)
        if len(specs) != len(node.targets):
            self.error(node.token,
                f"ASK format string has {len(specs)} specifier(s) "
                f"but {len(node.targets)} target variable(s) were given.")
        for i, tgt in enumerate(node.targets):
            tgt_dtype = self._resolve_addr_target(tgt)
            if i < len(specs) and tgt_dtype:
                if not self._compatible(specs[i], tgt_dtype):
                    spec_ch = [k for k, v in self._SPEC_MAP.items() if v == specs[i]]
                    self.error(tgt.token,
                        f"ASK format specifier %{spec_ch[0] if spec_ch else '?'} "
                        f"expects '{specs[i]}' but target '{tgt.var_name}' is '{tgt_dtype}'.")

    def _resolve_addr_target(self, node):
        sym = self.sym.lookup(node.var_name)
        if sym is None:
            self.error(node.token, f"Undeclared variable '{node.var_name}' in ASK target."); return None
        if sym.kind == 'const':
            self.error(node.token, f"Cannot use LOCKE '{node.var_name}' as an ASK target."); return None
        if node.target_kind in ('array1d', 'array2d'):
            if sym.kind != 'array':
                self.error(node.token, f"'{node.var_name}' is not an array."); return None
            if node.index1 is not None:
                it = self.visit(node.index1)
                if it and it != 'COIN':
                    self.error(node.token, f"Array index in ASK target must be COIN, got '{self._type_name(it)}'.")
                lbl = 'row index' if sym.is_2d else 'index'
                self._check_bounds(node.var_name, lbl, node.index1, sym.dimensions[0], node.token)
            if getattr(node, 'index2', None) is not None:
                it = self.visit(node.index2)
                if it and it != 'COIN':
                    self.error(node.token, f"Second array index in ASK target must be COIN, got '{self._type_name(it)}'.")
                if len(sym.dimensions) > 1:
                    self._check_bounds(node.var_name, 'column index', node.index2, sym.dimensions[1], node.token)
            return sym.dtype
        elif node.target_kind == 'member':
            if sym.kind != 'struct_var':
                self.error(node.token, f"'{node.var_name}' is not a struct variable."); return None
            ts = self.sym.lookup(sym.struct_type_name)
            if ts and node.member in ts.members: return ts.members[node.member]
            self.error(node.token, f"Struct '{sym.struct_type_name}' has no member '{node.member}'."); return None
        return sym.dtype

    def visit_AddressNode(self, node): self._resolve_addr_target(node)

    def visit_EchoNode(self, node):
        specs = self._parse_specs(node.format_string)
        if len(specs) != len(node.args):
            self.error(node.token,
                f"ECHO format string has {len(specs)} specifier(s) "
                f"but {len(node.args)} argument(s) were given.")
        for i, arg in enumerate(node.args):
            at = self.visit(arg)
            if i < len(specs) and at:
                if not self._compatible(specs[i], at):
                    sc = [k for k, v in self._SPEC_MAP.items() if v == specs[i]]
                    self.error(node.token,
                        f"Specifier %{sc[0] if sc else '?'} expects '{specs[i]}' "
                        f"but got '{self._type_name(at)}'.")

    # ── Conditionals ─────────────────────────────────────────────────────

    def visit_LookNode(self, node):
        ct = self.visit(node.condition)
        if ct and not self._is_bool(ct):
            self.error(node.token, f"LOOK condition must be BOOL, got '{self._type_name(ct)}'.")
        self.sym.push_scope(); self.in_conditional += 1
        for s in node.body: self.visit(s)
        self.in_conditional -= 1; self.sym.pop_scope()
        for (dc, db) in node.droplooks:
            dt = self.visit(dc)
            if dt and not self._is_bool(dt):
                self.error(node.token, f"DROPLOOK condition must be BOOL, got '{self._type_name(dt)}'.")
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
            self.error(node.token,
                f"CHART expression must be COIN, PARCH, or SCROLL, got '{self._type_name(expr_type)}'.")
        outer_chart = self.in_chart; self.in_chart = True
        # Improved duplicate COURSE label check using value+dtype
        seen = {}
        for course in node.courses:
            case_type = self.visit(course.value)
            if expr_type and case_type and not self._compatible(expr_type, case_type):
                self.error(course.token,
                    f"COURSE value type '{self._type_name(case_type)}' does not "
                    f"match CHART expression type '{self._type_name(expr_type)}'.")
            # Build label key from dtype+value for reliable comparison
            label_key = self._course_label_key(course.value)
            if label_key in seen:
                self.error(course.token, "Duplicate COURSE label in CHART block.")
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

    def _course_label_key(self, node):
        """Generate a reliable key for COURSE label duplicate detection."""
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
            self.error(node.token, f"HOIST condition must resolve to BOOL, got '{self._type_name(ct)}'.")
        for upd in node.updates: self.visit(upd)
        self.loop_depth += 1
        for s in node.body: self.visit(s)
        self.loop_depth -= 1
        self.sym.pop_scope()

    def visit_HoistInitNode(self, node):
        if node.declares_new:
            if self.sym.lookup_current_scope(node.var_name):
                self.error(node.token, f"Loop variable '{node.var_name}' conflicts with existing declaration.")
            else:
                self.sym.declare(Symbol(node.var_name, 'COIN', 'var', node.token, is_initialized=True))
        else:
            sym = self.sym.lookup(node.var_name)
            if sym is None:
                self.error(node.token, f"Undeclared variable '{node.var_name}' in HOIST init.")
            elif sym.kind == 'const':
                self.error(node.token, f"Cannot assign to LOCKE '{node.var_name}' in HOIST init.")
            elif sym.dtype != 'COIN':
                self.error(node.token,
                    f"HOIST init variable '{node.var_name}' must be COIN, got '{sym.dtype}'.")

    def visit_HoistUpdateNode(self, node):
        sym = self.sym.lookup(node.var_name)
        if sym is None:
            self.error(node.token, f"Undeclared variable '{node.var_name}' in HOIST update."); return
        if sym.kind == 'const':
            self.error(node.token, f"Cannot modify LOCKE '{node.var_name}' in HOIST update."); return
        if node.update_kind == 'unary':
            if sym.dtype != 'COIN':
                self.error(node.token,
                    f"Unary operator '{node.unary_op}' in HOIST update requires COIN type, "
                    f"but '{node.var_name}' is '{sym.dtype}'.")
        elif node.update_kind == 'compound':
            if not self._is_numeric(sym.dtype):
                self.error(node.token,
                    f"Compound update target '{node.var_name}' must be numeric, got '{sym.dtype}'.")
            if node.value is not None:
                vt = self.visit(node.value)
                if vt and not self._is_numeric(vt):
                    self.error(node.token, f"HOIST update value must be numeric, got '{self._type_name(vt)}'.")

    def visit_HeaveNode(self, node):
        ct = self.visit(node.condition)
        if ct and not self._is_bool(ct):
            self.error(node.token, f"HEAVE condition must be BOOL, got '{self._type_name(ct)}'.")
        self.sym.push_scope(); self.loop_depth += 1
        for s in node.body: self.visit(s)
        self.loop_depth -= 1; self.sym.pop_scope()

    def visit_HaulHeaveNode(self, node):
        self.sym.push_scope(); self.loop_depth += 1
        for s in node.body: self.visit(s)
        self.loop_depth -= 1; self.sym.pop_scope()
        ct = self.visit(node.condition)
        if ct and not self._is_bool(ct):
            self.error(node.token, f"HAUL-HEAVE condition must be BOOL, got '{self._type_name(ct)}'.")

    # ── Jump Statements ──────────────────────────────────────────────────

    def visit_SailNode(self, node):
        if self.in_adrift:
            self.error(node.token, "SAIL!! is not allowed inside an ADRIFT body."); return
        if self.loop_depth == 0 and self.in_conditional == 0:
            self.error(node.token, "SAIL!! used outside of a loop or conditional block.")

    def visit_LandNode(self, node):
        if self.loop_depth == 0 and self.in_conditional == 0:
            self.error(node.token, "LAND!! used outside of a loop or conditional block.")

    def visit_ReturnNode(self, node):
        if self.current_func_return is None:
            self.error(node.token, "BACK used outside of a function."); return
        if self.current_func_return == 'ABYSS':
            self.error(node.token, "ABYSS functions cannot return a value."); return
        rt = self.visit(node.value)
        if rt and not self._compatible(self.current_func_return, rt):
            self.error(node.token,
                f"Function expects return type '{self.current_func_return}', "
                f"but BACK expression has type '{self._type_name(rt)}'.")

    def visit_BackNode(self, node):
        if self.current_func_return is None:
            self.error(node.token, "BACK used outside of a function.")
        elif self.current_func_return != 'ABYSS':
            self.error(node.token,
                f"BACK!! used inside a '{self.current_func_return}' returning function. "
                f"This function must return a value.")

    def visit_UnaryStmtNode(self, node):
        sym = self.sym.lookup(node.var_name)
        if sym is None:
            self.error(node.token, f"Undeclared variable '{node.var_name}'."); return
        if sym.kind == 'const':
            self.error(node.token, f"Cannot apply '{node.operator}' to LOCKE '{node.var_name}'."); return
        # Unary +# -# operates on COIN only (rule p.38)
        if sym.dtype != 'COIN':
            self.error(node.token,
                f"Operator '{node.operator}' requires a COIN variable, "
                f"but '{node.var_name}' is '{sym.dtype}'.")

    def visit_FuncCallStmtNode(self, node):
        # Special handling for function calls in statement context.
        # ABYSS functions can only be called as statements, not expressions.
        call = node.call_expr
        sym = self.sym.lookup(call.name)
        if sym is None:
            self.error(call.token, f"Call to undeclared function '{call.name}'."); return
        if sym.kind != 'func':
            self.error(call.token, f"'{call.name}' is not a function."); return

        # Check argument count and types
        exp_cnt, act_cnt = len(sym.params), len(call.args)
        if exp_cnt != act_cnt:
            self.error(call.token,
                f"Function '{call.name}' expects '{exp_cnt}' argument(s), got '{act_cnt}'.")
        else:
            for i, (p, a) in enumerate(zip(sym.params, call.args)):
                at = self.visit(a)
                if at and not self._compatible(p.dtype, at):
                    self.error(call.token,
                        f"Argument {i+1} of '{call.name}': expected '{p.dtype}', got '{self._type_name(at)}'.")

        # ABYSS functions are allowed in statement context (this is their only valid use).
        # For non-ABYSS functions called as statements, the return value is just discarded.

    # =====================================================================
    # EXPRESSIONS
    # =====================================================================

    def visit_LiteralNode(self, node): return node.dtype

    def visit_IdentNode(self, node):
        sym = self.sym.lookup(node.name)
        if sym is None:
            self.error(node.token, f"Undeclared variable '{node.name}'."); return None
        # A lone identifier (no parentheses) is ONLY a variable or constant.
        # If the name resolves to a function, it must be treated as undeclared
        # because function references require parentheses: greet() not greet.
        if sym.kind == 'func':
            self.error(node.token, f"Undeclared variable '{node.name}'."); return None
        if not sym.is_initialized:
            self.error(node.token, f"Variable '{node.name}' may be used before it is initialized.")
        return sym.dtype

    def visit_ArrayAccessNode(self, node):
        sym = self.sym.lookup(node.name)
        if sym is None:
            self.error(node.token, f"Undeclared array '{node.name}'."); return None
        if sym.kind != 'array':
            self.error(node.token, f"'{node.name}' is not an array (it is a '{sym.kind}')."); return None
        for i, idx in enumerate(node.indices):
            it = self.visit(idx)
            if it and it != 'COIN':
                self.error(node.token, f"Array index [{i}] for '{node.name}' must be COIN, got '{self._type_name(it)}'.")
            if i < len(sym.dimensions):
                lbl = 'column index' if (sym.is_2d and i == 1) else 'row index' if (sym.is_2d and i == 0) else 'index'
                self._check_bounds(node.name, lbl, idx, sym.dimensions[i], node.token)
        return sym.dtype

    def visit_MemberAccessNode(self, node):
        sym = self.sym.lookup(node.var_name)
        if sym is None:
            self.error(node.token, f"Undeclared variable '{node.var_name}'."); return None
        if sym.kind != 'struct_var':
            self.error(node.token, f"'{node.var_name}' is not a struct variable."); return None
        ts = self.sym.lookup(sym.struct_type_name)
        if ts is None or ts.kind != 'struct':
            self.error(node.token, f"Cannot resolve struct type '{sym.struct_type_name}'."); return None
        if node.member_name not in ts.members:
            self.error(node.token, f"Struct '{sym.struct_type_name}' has no member '{node.member_name}'."); return None
        return ts.members[node.member_name]

    def visit_ScrollCharAccessNode(self, node):
        st = self.visit(node.scroll_expr)
        if st and st != 'SCROLL':
            self.error(node.token,
                f"Character indexing requires a SCROLL value, got '{self._type_name(st)}'.")
        it = self.visit(node.index)
        if it and it != 'COIN':
            self.error(node.token, f"SCROLL character index must be COIN, got '{self._type_name(it)}'.")
        # Compile-time bounds check when the SCROLL operand is a literal string
        scroll_node = node.scroll_expr
        if type(scroll_node).__name__ == 'LiteralNode' and getattr(scroll_node, 'dtype', None) == 'SCROLL':
            raw = getattr(scroll_node, 'value', None)
            if raw is not None:
                str_len = len(str(raw))
                idx_val = self._literal_int(node.index)
                if idx_val is not None:
                    if idx_val < 0 or idx_val >= str_len:
                        self.error(node.token,
                            f"SCROLL character index {idx_val} is out of bounds "
                            f"(length {str_len}, valid range 0–{str_len - 1}).")
        return 'SCROLL'  # SCROLL char access returns single-char SCROLL (rule p.16)

    def visit_StringConcatNode(self, node):
        for op in node.operands:
            ot = self.visit(op)
            if ot and ot != 'SCROLL':
                self.error(node.token,
                    f"String concatenation (&) requires SCROLL operands, got '{self._type_name(ot)}'.")
        return 'SCROLL'

    def visit_FuncCallNode(self, node):
        sym = self.sym.lookup(node.name)
        if sym is None:
            self.error(node.token, f"Call to undeclared function '{node.name}'."); return None
        if sym.kind != 'func':
            self.error(node.token, f"'{node.name}' is not a function."); return None
        exp_cnt, act_cnt = len(sym.params), len(node.args)
        if exp_cnt != act_cnt:
            self.error(node.token,
                f"Function '{node.name}' expects '{exp_cnt}' argument(s), got '{act_cnt}'.")
        else:
            for i, (p, a) in enumerate(zip(sym.params, node.args)):
                at = self.visit(a)
                if at and not self._compatible(p.dtype, at):
                    self.error(node.token,
                        f"Argument {i+1} of '{node.name}': expected '{p.dtype}', got '{self._type_name(at)}'.")
        if sym.return_type == 'ABYSS':
            self.error(node.token,
                f"Function '{node.name}' is declared ABYSS and cannot be used as an expression.")
            return None
        return sym.return_type

    def visit_BinaryOpNode(self, node):
        lt = self.visit(node.left); rt = self.visit(node.right)
        op = node.operator
        if op in ('+', '-', '*', '/', '%', '^'):
            if lt and not self._is_numeric(lt):
                self.error(node.token, f"Operator '{op}' requires numeric operands, left is '{self._type_name(lt)}'.")
            if rt and not self._is_numeric(rt):
                self.error(node.token, f"Operator '{op}' requires numeric operands, right is '{self._type_name(rt)}'.")
            return 'DIME' if (lt == 'DIME' or rt == 'DIME') else 'COIN'
        elif op in ('<', '>', '<=', '>='):
            if lt and not self._is_numeric(lt):
                self.error(node.token, f"Relational operator '{op}' requires numeric operands, left is '{self._type_name(lt)}'.")
            if rt and not self._is_numeric(rt):
                self.error(node.token, f"Relational operator '{op}' requires numeric operands, right is '{self._type_name(rt)}'.")
            return 'BOOL'
        elif op in ('==', '!='):
            if lt and rt and not self._compatible_expr(lt, rt):
                self.error(node.token,
                    f"Cannot compare '{self._type_name(lt)}' and '{self._type_name(rt)}' with '{op}'.")
            return 'BOOL'
        elif op in ('&&', '||'):
            if lt and not self._is_bool(lt):
                self.error(node.token, f"Logical operator '{op}' requires BOOL operands, left is '{self._type_name(lt)}'.")
            if rt and not self._is_bool(rt):
                self.error(node.token, f"Logical operator '{op}' requires BOOL operands, right is '{self._type_name(rt)}'.")
            return 'BOOL'
        return None

    def visit_UnaryOpNode(self, node):
        ot = self.visit(node.operand); op = node.operator
        if op == '-':
            if ot and not self._is_numeric(ot):
                self.error(node.token, f"Unary '-' requires a numeric operand, got '{self._type_name(ot)}'.")
            return ot
        elif op in ('!', '!#'):
            if ot and not self._is_bool(ot):
                self.error(node.token, f"Operator '{op}' requires a BOOL operand, got '{self._type_name(ot)}'.")
            return 'BOOL'
        return None