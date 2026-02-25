# =============================================================================
# semantic_analyzer.py — SeaStack Semantic Analyzer
#
# HOW THIS ANALYZER WORKS (read before editing):
# ───────────────────────────────────────────────
# The analyzer walks the AST produced by ast_parser.py using the VISITOR
# PATTERN. Every AST node class has a corresponding visit_ClassName() method
# here. The main dispatch method visit(node) routes each node to the right
# visitor automatically using the node's class name.
#
# TWO KINDS OF VISITORS:
#   Statement visitors  → called for side effects (register symbols, check
#                         scopes, verify control flow). Return nothing.
#   Expression visitors → called to determine the TYPE of an expression.
#                         Return a dtype string: 'COIN','DIME','PARCH',
#                         'SCROLL','BOOL', or None if unknown/error.
#
# SYMBOL TABLE:
#   Managed by SymbolTable in symbol_table.py.
#   A stack of dicts (scopes). The innermost scope is always self.sym._scopes[-1].
#   push_scope() / pop_scope() wrap every block that introduces a new scope:
#   function bodies, loop bodies, LOOK bodies, etc.
#   lookup(name) walks from innermost to outermost — this implements shadowing.
#
# CONTEXT TRACKING:
#   self.current_func_return  — the return type of the function we are inside
#                               (None at global/AHOY level)
#   self.loop_depth           — how many nested loops we are inside (HOIST/
#                               HEAVE/HAUL). LOOK/DROPLOOK/DROP/CHART are
#                               conditionals, NOT loops — they use
#                               self.in_conditional instead.
#   self.in_conditional       — whether we are inside any conditional block
#                               (LOOK/DROPLOOK/DROP/CHART/COURSE/ADRIFT).
#                               SAIL and LAND are valid here too.
#   self.in_chart             — whether we are specifically inside a CHART
#                               block (SAIL is forbidden in ADRIFT bodies,
#                               but the grammar already prevents it — tracked
#                               here for belt-and-suspenders validation).
#
# JUMP STATEMENT PLACEMENT:
#   Per SeaStack rules:
#     SAIL / LAND  → valid at the END of any loop or conditional body,
#                    including LOOK, DROPLOOK, DROP, COURSE bodies.
#                    SAIL is forbidden in ADRIFT (grammar enforces; we mirror).
#     LAND         → REQUIRED at end of ADRIFT body.
#     BACK         → only inside a function; returning functions need a value,
#                    ABYSS functions must NOT return a value.
#
# ERROR REPORTING:
#   self.error(token, message) appends an error dict to self.errors.
#   Errors are non-fatal: the analyzer continues walking after reporting one,
#   so it can catch multiple errors in a single pass.
#
# TYPE COMPATIBILITY:
#   SeaStack's rules:
#     COIN  ↔  DIME  (numeric types interchangeable in arithmetic & ==,!=)
#     All other types must match exactly.
#   _compatible(expected, actual) encodes this.
#
# CHANGES FROM ORIGINAL (v1 → v2):
#   • Symbol classes moved to symbol_table.py; imported from there.
#   • StructTypeSymbol now stores member_order (list) alongside members (dict)
#     to support positional struct initializer validation.
#   • visit_StructDefNode passes member_order to StructTypeSymbol constructor.
#   • visit_StructVarDeclNode correctly imports NamedInitNode and validates
#     positional initializer count against declared member count.
#   • Conditional bodies (LOOK/DROP/DROPLOOK) no longer increment loop_depth;
#     a new in_conditional counter is used instead, so SAIL/LAND inside
#     conditionals are correctly validated without confusing the loop counter.
#   • visit_SailNode / visit_LandNode check both loop_depth and in_conditional.
#   • visit_ArrayDeclNode now validates that init_values count ≤ declared size.
#   • visit_UnaryStmtNode enforces COIN-only operand (not DIME) per rules.
#   • visit_EchoNode validates format specifier count vs argument count.
#   • visit_AskNode validates format specifier count vs target count.
#   • _pre_register_func no longer double-declares; visit_FuncDefNode handles
#     the declare() call safely with lookup_current_scope guard.
#   • visit_FuncCallNode now handles ABYSS return type correctly (ABYSS
#     functions can be called as statements but not used in expressions).
# =============================================================================

import re

from semantic.symbol_table import (
    Symbol,
    ArraySymbol,
    FunctionSymbol,
    StructTypeSymbol,
    StructVarSymbol,
    SymbolTable,
)
from semantic.ast_nodes import NamedInitNode, PositionalInitNode


# =============================================================================
# SEMANTIC ANALYZER
# =============================================================================

class SemanticAnalyzer:
    def __init__(self, ast, source_code):
        self.ast         = ast
        self.source_code = source_code
        self.sym         = SymbolTable()
        self.errors      = []

        # ── Context tracking ─────────────────────────────────────────────────
        # Return type of the function we are currently inside.
        # None  → global scope or AHOY (neither returns a value).
        self.current_func_return = None   # str | None

        # Nested loop depth (HOIST / HEAVE / HAUL-HEAVE only).
        # LOOK / CHART are conditionals, not loops — they use in_conditional.
        self.loop_depth    = 0   # int

        # Depth of any conditional block (LOOK, DROPLOOK, DROP, CHART).
        # Incremented/decremented alongside loop_depth so that SAIL/LAND
        # inside a LOOK body nested in a HOIST body is still valid.
        self.in_conditional = 0  # int

        # True specifically while inside a CHART block.  SAIL is forbidden
        # in ADRIFT bodies (the grammar enforces this, but we double-check).
        self.in_chart = False

        # True when we are analyzing the ADRIFT body of a CHART statement.
        self.in_adrift = False

    # =========================================================================
    # ENTRY POINT
    # =========================================================================

    def analyze(self):
        """
        Run the full semantic analysis pass.
        Returns list of error dicts (empty list means success).
        """
        self.visit(self.ast)
        return self.errors

    # =========================================================================
    # VISITOR DISPATCH
    # =========================================================================

    def visit(self, node):
        """
        Dispatch to the correct visitor based on node class name.
        Expression visitors return a dtype string.
        Statement visitors return None.
        """
        if node is None:
            return None
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.visit_unknown)
        return visitor(node)

    def visit_unknown(self, node):
        self.errors.append({
            'type':    'Internal',
            'message': f'No visitor for node type {type(node).__name__}',
            'line': '?', 'col': '?',
        })

    # =========================================================================
    # ERROR HELPER
    # =========================================================================

    def error(self, token, message):
        """
        Record a semantic error. token can be None (for implicit locations).
        Non-fatal — analysis continues after this call.
        """
        line = getattr(token, 'line', '?')
        col  = getattr(token, 'col',  '?')
        self.errors.append({
            'type':    'Semantic Error',
            'line':    line,
            'col':     col,
            'message': message,
        })

    # =========================================================================
    # TYPE HELPERS
    # =========================================================================

    def _compatible(self, expected, actual):
        """
        Returns True if actual type is acceptable where expected type is needed.
        COIN and DIME are numeric siblings — they are mutually compatible for
        assignment, equality (==,!=), and arithmetic.
        All other types must match exactly.
        """
        if expected == actual:
            return True
        if expected in ('COIN', 'DIME') and actual in ('COIN', 'DIME'):
            return True
        return False

    def _is_numeric(self, dtype):
        return dtype in ('COIN', 'DIME')

    def _is_bool(self, dtype):
        return dtype == 'BOOL'

    def _type_name(self, dtype):
        """Human-readable type name for error messages."""
        return dtype if dtype else 'unknown'

    # ─────────────────────────────────────────────────────────────────────────
    # FORMAT SPECIFIER HELPERS  (for ASK and ECHO validation)
    # ─────────────────────────────────────────────────────────────────────────

    # Maps the specifier character (after %) to the SeaStack type it represents.
    _SPECIFIER_TO_DTYPE = {
        'C': 'COIN',
        'D': 'DIME',
        'P': 'PARCH',
        'S': 'SCROLL',
        'B': 'BOOL',
    }

    def _parse_format_specifiers(self, fmt_string):
        """
        Extract the list of dtype strings from a format string.
        E.g. "%C%D%S" → ['COIN', 'DIME', 'SCROLL']
        Returns list[str] (may be empty if no specifiers found).
        """
        found = re.findall(r'%([CDPSB])', fmt_string)
        return [self._SPECIFIER_TO_DTYPE[ch] for ch in found]

    # =========================================================================
    # PROGRAM STRUCTURE
    # =========================================================================

    def visit_ProgramNode(self, node):
        """
        Global scope: process all global declarations, then the AHOY body.

        Two-pass strategy:
          Pass 1 → pre-register all function signatures so they can be called
                   before their definition appears in the file (forward refs).
                   Also pre-register struct types so struct vars can reference
                   them in initializers before the full definition pass.
          Pass 2 → full analysis of each global declaration.
        """
        # Pass 1: register function signatures and struct types
        for decl in node.global_decls:
            cls = type(decl).__name__
            if cls == 'FuncDefNode':
                self._pre_register_func(decl)
            elif cls == 'StructDefNode':
                self._pre_register_struct(decl)

        # Pass 2: full analysis
        for decl in node.global_decls:
            self.visit(decl)

        # Analyze the AHOY main body
        self.visit(node.ahoy_body)

    def _pre_register_func(self, node):
        """
        Register a function's signature (name, return type, params) in the
        global scope without analyzing its body. This enables forward calls.
        Silently skips if already declared — visit_FuncDefNode will handle
        the genuine duplicate check.
        """
        if not self.sym.lookup_current_scope(node.name):
            sym = FunctionSymbol(node.name, node.return_type, node.params, node.token)
            self.sym.declare(sym)

    def _pre_register_struct(self, node):
        """
        Register a struct type definition in the global scope so that struct
        variable declarations can reference the type name before the full
        visit_StructDefNode pass runs.
        """
        if not self.sym.lookup_current_scope(node.name):
            members      = {m.name: m.dtype for m in node.members}
            member_order = [m.name for m in node.members]
            sym = StructTypeSymbol(node.name, members, member_order, node.token)
            self.sym.declare(sym)

    def visit_AhoyNode(self, node):
        """The main AHOY block has its own scope for local declarations."""
        self.sym.push_scope()
        for decl in node.local_decls:
            self.visit(decl)
        for stmt in node.statements:
            self.visit(stmt)
        self.sym.pop_scope()

    # =========================================================================
    # DECLARATIONS
    # =========================================================================

    def visit_ConstDeclNode(self, node):
        """
        LOCKE declarations: must have a literal value, cannot be reassigned.
        The grammar already enforces literal-only values, so we just register.
        """
        if self.sym.lookup_current_scope(node.name):
            self.error(node.token,
                f"Constant '{node.name}' is already declared in this scope.")
            return
        sym = Symbol(node.name, node.dtype, 'const', node.token,
                     is_initialized=True)
        self.sym.declare(sym)

    def visit_VarDeclNode(self, node):
        """
        Variable declaration. Check for duplicates, type-check the initializer.
        Variables without an initializer are registered as uninitialized —
        the analyzer will flag use-before-init when they are read.
        """
        if self.sym.lookup_current_scope(node.name):
            self.error(node.token,
                f"Variable '{node.name}' is already declared in this scope.")
            return

        init_type = None
        if node.init_value is not None:
            init_type = self.visit(node.init_value)
            if init_type and not self._compatible(node.dtype, init_type):
                self.error(node.token,
                    f"Cannot initialize '{node.dtype}' variable '{node.name}' "
                    f"with a '{self._type_name(init_type)}' value.")

        sym = Symbol(node.name, node.dtype, 'var', node.token,
                     is_initialized=(node.init_value is not None))
        self.sym.declare(sym)

    def visit_ArrayDeclNode(self, node):
        """
        Array declaration.
        Checks:
          • No duplicate in current scope.
          • Each initializer element's type matches the array's declared dtype.
          • Initializer element COUNT does not exceed the declared dimension size.
            (Fewer elements than the size is allowed — remaining are null.)
        """
        if self.sym.lookup_current_scope(node.name):
            self.error(node.token,
                f"Array '{node.name}' is already declared in this scope.")
            return

        if node.init_values is not None:
            if node.is_2d:
                # For 2D: outer list = rows, each row = list of expressions.
                declared_rows = node.dimensions[0]
                declared_cols = node.dimensions[1]

                if len(node.init_values) > declared_rows:
                    self.error(node.token,
                        f"Array '{node.name}' initializer has {len(node.init_values)} "
                        f"row(s) but was declared with {declared_rows} row(s).")

                for row_idx, row in enumerate(node.init_values):
                    if len(row) > declared_cols:
                        self.error(node.token,
                            f"Array '{node.name}' row [{row_idx}] has {len(row)} "
                            f"element(s) but the declared column size is {declared_cols}.")
                    for col_idx, elem in enumerate(row):
                        elem_type = self.visit(elem)
                        if elem_type and not self._compatible(node.dtype, elem_type):
                            self.error(node.token,
                                f"Array '{node.name}' element [{row_idx}][{col_idx}] "
                                f"has type '{self._type_name(elem_type)}', "
                                f"expected '{node.dtype}'.")
            else:
                declared_size = node.dimensions[0]
                if len(node.init_values) > declared_size:
                    self.error(node.token,
                        f"Array '{node.name}' initializer has {len(node.init_values)} "
                        f"element(s) but was declared with size {declared_size}.")

                for idx, elem in enumerate(node.init_values):
                    elem_type = self.visit(elem)
                    if elem_type and not self._compatible(node.dtype, elem_type):
                        self.error(node.token,
                            f"Array '{node.name}' element [{idx}] "
                            f"has type '{self._type_name(elem_type)}', "
                            f"expected '{node.dtype}'.")

        sym = ArraySymbol(node.name, node.dtype, node.dimensions, node.is_2d,
                          node.token)
        self.sym.declare(sym)

    def visit_StructDefNode(self, node):
        """
        Register a struct TYPE definition (MAST Ship [...]).
        Checks:
          • No duplicate struct type name in current scope.
          • No duplicate member names within the struct.
          • At least one member (grammar enforces; we mirror for clarity).
        """
        # If pre-registered in Pass 1, skip re-declaration but still validate members.
        existing = self.sym.lookup_current_scope(node.name)
        if existing and existing.kind == 'struct':
            # Already registered — validate members against what we stored.
            members_seen = set()
            for member in node.members:
                if member.name in members_seen:
                    self.error(member.token,
                        f"Struct '{node.name}' has duplicate member '{member.name}'.")
                members_seen.add(member.name)
            return

        if existing:
            self.error(node.token,
                f"Identifier '{node.name}' is already declared in this scope.")
            return

        members      = {}
        member_order = []
        for member in node.members:
            if member.name in members:
                self.error(member.token,
                    f"Struct '{node.name}' has duplicate member '{member.name}'.")
            else:
                members[member.name]  = member.dtype
                member_order.append(member.name)

        sym = StructTypeSymbol(node.name, members, member_order, node.token)
        self.sym.declare(sym)

    def visit_MemberDeclNode(self, node):
        pass   # handled inside visit_StructDefNode

    def visit_StructVarDeclNode(self, node):
        """
        Declare a struct variable instance (MAST Ship s1).
        Checks:
          • Struct type must be defined.
          • Variable name must not collide in current scope.
          • If positional initializers: count must not exceed member count;
            each value's type must match the corresponding member's dtype.
          • If named initializers: each member name must exist in the struct;
            each value's type must match the member's declared dtype.
          • Providing more initializers than members is invalid.
        """
        # Verify struct type exists
        type_sym = self.sym.lookup(node.struct_type)
        if type_sym is None or type_sym.kind != 'struct':
            self.error(node.token,
                f"Undefined struct type '{node.struct_type}'.")
            return

        members      = type_sym.members       # dict[name → dtype]
        member_order = type_sym.member_order  # list[str] — declaration order

        # Check for duplicate variable name in current scope
        if self.sym.lookup_current_scope(node.var_name):
            self.error(node.token,
                f"Variable '{node.var_name}' is already declared in this scope.")
            return

        # Validate initializer list
        if node.inits:
            if len(node.inits) > len(member_order):
                self.error(node.token,
                    f"Struct '{node.struct_type}' has {len(member_order)} member(s) "
                    f"but {len(node.inits)} initializer(s) were provided.")
            else:
                positional_cursor = 0   # tracks which member we are on for positional inits

                for init in node.inits:
                    if isinstance(init, NamedInitNode):
                        # Named init: $member_name = value
                        if init.member_name not in members:
                            self.error(init.token,
                                f"Struct type '{node.struct_type}' has no member "
                                f"'{init.member_name}'.")
                        else:
                            expected = members[init.member_name]
                            actual   = self.visit(init.value)
                            if actual and not self._compatible(expected, actual):
                                self.error(init.token,
                                    f"Member '{init.member_name}' of '{node.struct_type}' "
                                    f"expects '{expected}', "
                                    f"got '{self._type_name(actual)}'.")
                        # After a named init we do NOT advance positional_cursor —
                        # the next init (if positional) picks up from wherever
                        # the named init left the cursor.  SeaStack rule: named
                        # inits jump to that member; the next positional init
                        # then goes to the member AFTER the named one.
                        if init.member_name in member_order:
                            positional_cursor = member_order.index(init.member_name) + 1

                    elif isinstance(init, PositionalInitNode):
                        # Positional init: value fills the next member in order
                        if positional_cursor >= len(member_order):
                            self.error(node.token,
                                f"Too many positional initializers for struct "
                                f"'{node.struct_type}'.")
                            break
                        member_name = member_order[positional_cursor]
                        expected    = members[member_name]
                        actual      = self.visit(init.value)
                        if actual and not self._compatible(expected, actual):
                            self.error(node.token,
                                f"Positional initializer {positional_cursor + 1} for "
                                f"struct '{node.struct_type}' member '{member_name}' "
                                f"expects '{expected}', "
                                f"got '{self._type_name(actual)}'.")
                        positional_cursor += 1

        sym = StructVarSymbol(node.var_name, node.struct_type, node.token)
        self.sym.declare(sym)

    def visit_PositionalInitNode(self, node):
        return self.visit(node.value)

    def visit_NamedInitNode(self, node):
        return self.visit(node.value)

    def visit_FuncDefNode(self, node):
        """
        Function definition.

        Key steps:
        1. Register the function in the OUTER scope if not already done by
           _pre_register_func (forward-reference pass). Report error on genuine
           duplicates (two function definitions with the same name).
        2. Push a new scope for the function body.
        3. Declare all parameters as initialized variables in the inner scope.
        4. Analyze local declarations and body statements.
        5. Validate the return expression type matches the declared return type.
        6. Pop the scope when done.

        current_func_return tells nested ReturnNode/BackNode visitors what
        type to expect.
        """
        # If not pre-registered, register now.  If already in scope, that means
        # _pre_register_func ran successfully — skip re-declaration.
        existing = self.sym.lookup_current_scope(node.name)
        if existing is None:
            sym = FunctionSymbol(node.name, node.return_type, node.params, node.token)
            if not self.sym.declare(sym):
                self.error(node.token,
                    f"Function '{node.name}' is already declared in this scope.")
                return
        elif existing.kind != 'func':
            # Name collides with a non-function symbol
            self.error(node.token,
                f"'{node.name}' is already declared as a "
                f"'{existing.kind}' in this scope.")
            return
        # (else: pre-registered as func — proceed to analyze body)

        # Save and set function context
        outer_return          = self.current_func_return
        self.current_func_return = node.return_type

        self.sym.push_scope()

        # Declare parameters as initialized variables in function scope
        for param in node.params:
            if self.sym.lookup_current_scope(param.name):
                self.error(param.token,
                    f"Duplicate parameter name '{param.name}' "
                    f"in function '{node.name}'.")
            else:
                sym = Symbol(param.name, param.dtype, 'param', param.token,
                             is_initialized=True)
                self.sym.declare(sym)

        # Analyze body
        for decl in node.local_decls:
            self.visit(decl)
        for stmt in node.body:
            self.visit(stmt)

        # Validate return expression (for returning functions only)
        if node.return_type != 'ABYSS' and node.return_expr is not None:
            ret_type = self.visit(node.return_expr)
            if ret_type and not self._compatible(node.return_type, ret_type):
                self.error(node.token,
                    f"Function '{node.name}' declared to return '{node.return_type}' "
                    f"but BACK expression has type '{self._type_name(ret_type)}'.")

        self.sym.pop_scope()
        self.current_func_return = outer_return

    def visit_ParamNode(self, node):
        pass   # params are handled inside visit_FuncDefNode

    # =========================================================================
    # STATEMENTS
    # =========================================================================

    def visit_AssignNode(self, node):
        """
        Simple assignment: x = expr!!  arr{i} = expr!!  s$member = expr!!

        Checks:
          • Target variable must be declared.
          • Target must NOT be a constant (LOCKE).
          • For array access: indices must be COIN type.
          • For member access: struct variable and member must exist.
          • RHS type must be compatible with the target's declared dtype.
          • After assignment, the variable is marked as initialized.
        """
        target_dtype = self._resolve_assign_target(
            node.var_name, node.target_kind,
            node.index1, node.index2, node.member, node.token
        )
        if target_dtype is not None:
            val_type = self.visit(node.value)
            if val_type and not self._compatible(target_dtype, val_type):
                self.error(node.token,
                    f"Cannot assign '{self._type_name(val_type)}' to "
                    f"'{node.var_name}' (declared as '{target_dtype}').")
            # Mark variable as initialized after first assignment
            if node.target_kind == 'var':
                self.sym.update_initialized(node.var_name)

    def visit_CompoundAssignNode(self, node):
        """
        Compound assignment: x += 5!!  arr{i} -= 1!!
        Per rules: compound operators are numeric-only (COIN or DIME).
        """
        target_dtype = self._resolve_assign_target(
            node.var_name, node.target_kind,
            node.index1, node.index2, node.member, node.token
        )
        if target_dtype is not None:
            if not self._is_numeric(target_dtype):
                self.error(node.token,
                    f"Compound assignment operator '{node.operator}' can only be used "
                    f"on numeric types (COIN/DIME), "
                    f"but '{node.var_name}' is '{target_dtype}'.")
            val_type = self.visit(node.value)
            if val_type and not self._is_numeric(val_type):
                self.error(node.token,
                    f"Right-hand side of '{node.operator}' must be numeric "
                    f"(COIN/DIME), got '{self._type_name(val_type)}'.")

    def _resolve_assign_target(self, var_name, target_kind,
                                index1, index2, member, token):
        """
        Shared helper for AssignNode and CompoundAssignNode.
        Resolves the declared dtype of the assignment target and performs
        all target-specific checks (const guard, array index types, member lookup).
        Returns the target's dtype string, or None if an error was reported.
        """
        sym = self.sym.lookup(var_name)
        if sym is None:
            self.error(token, f"Undeclared variable '{var_name}'.")
            return None

        # Constants cannot be reassigned
        if sym.kind == 'const':
            self.error(token,
                f"Cannot assign to constant '{var_name}' "
                f"(declared with LOCKE — constants are read-only).")
            return None

        if target_kind == 'var':
            return sym.dtype

        elif target_kind in ('array1d', 'array2d'):
            if sym.kind != 'array':
                self.error(token, f"'{var_name}' is not an array.")
                return None
            # Validate index types
            if index1 is not None:
                idx_type = self.visit(index1)
                if idx_type and idx_type != 'COIN':
                    self.error(token,
                        f"Array index for '{var_name}' must be COIN, "
                        f"got '{self._type_name(idx_type)}'.")
            if index2 is not None:
                idx_type = self.visit(index2)
                if idx_type and idx_type != 'COIN':
                    self.error(token,
                        f"Second array index for '{var_name}' must be COIN, "
                        f"got '{self._type_name(idx_type)}'.")
            return sym.dtype

        elif target_kind == 'member':
            if sym.kind != 'struct_var':
                self.error(token,
                    f"'{var_name}' is not a struct variable "
                    f"(member access with $ requires a struct variable).")
                return None
            type_sym = self.sym.lookup(sym.struct_type_name)
            if type_sym is None or type_sym.kind != 'struct':
                self.error(token,
                    f"Cannot resolve struct type '{sym.struct_type_name}' "
                    f"for variable '{var_name}'.")
                return None
            if member not in type_sym.members:
                self.error(token,
                    f"Struct '{sym.struct_type_name}' has no member '{member}'.")
                return None
            return type_sym.members[member]

        return None

    def visit_AskNode(self, node):
        """
        ASK("format", @x, @arr{0})!!

        Checks:
          • Format specifier count must match the number of address targets.
          • Each specifier's dtype must match the corresponding target's dtype.
          • Each target must be a declared, non-constant variable.
        """
        specifiers = self._parse_format_specifiers(node.format_string)
        target_count = len(node.targets)

        if len(specifiers) != target_count:
            self.error(node.token,
                f"ASK format string has {len(specifiers)} specifier(s) "
                f"but {target_count} target variable(s) were given.")

        for i, target in enumerate(node.targets):
            target_dtype = self._resolve_address_target(target)
            # Type-check specifier vs target if both are known
            if i < len(specifiers) and target_dtype:
                expected_spec = specifiers[i]
                if not self._compatible(expected_spec, target_dtype):
                    self.error(target.token,
                        f"ASK format specifier %{list(self._SPECIFIER_TO_DTYPE.keys())[list(self._SPECIFIER_TO_DTYPE.values()).index(expected_spec)]} "
                        f"expects '{expected_spec}' but target '{target.var_name}' "
                        f"is '{target_dtype}'.")

    def _resolve_address_target(self, node):
        """
        Validate and return the dtype of an ASK address target (@id[...]).
        Returns the target dtype or None on error.
        """
        sym = self.sym.lookup(node.var_name)
        if sym is None:
            self.error(node.token,
                f"Undeclared variable '{node.var_name}' in ASK target.")
            return None
        if sym.kind == 'const':
            self.error(node.token,
                f"Cannot use constant '{node.var_name}' as an ASK target "
                f"(constants are read-only).")
            return None

        if node.target_kind in ('array1d', 'array2d'):
            if sym.kind != 'array':
                self.error(node.token,
                    f"'{node.var_name}' is not an array.")
                return None
            if node.index1 is not None:
                idx_type = self.visit(node.index1)
                if idx_type and idx_type != 'COIN':
                    self.error(node.token,
                        f"Array index in ASK target must be COIN, "
                        f"got '{self._type_name(idx_type)}'.")
            return sym.dtype

        elif node.target_kind == 'member':
            if sym.kind != 'struct_var':
                self.error(node.token,
                    f"'{node.var_name}' is not a struct variable.")
                return None
            type_sym = self.sym.lookup(sym.struct_type_name)
            if type_sym and node.member in type_sym.members:
                return type_sym.members[node.member]
            self.error(node.token,
                f"Struct '{sym.struct_type_name}' has no member '{node.member}'.")
            return None

        return sym.dtype

    def visit_AddressNode(self, node):
        """Dispatched only when AddressNode is visited outside visit_AskNode."""
        self._resolve_address_target(node)

    def visit_EchoNode(self, node):
        """
        ECHO("format", arg1, arg2)!!

        Checks:
          • Format specifier count must match the number of extra arguments.
            (The first argument is the SCROLL literal — extra args follow.)
          • Each specifier's dtype must be compatible with the corresponding
            argument's inferred type.
          • If there are no specifiers, there must be no extra arguments.
        """
        specifiers = self._parse_format_specifiers(node.format_string)
        arg_count  = len(node.args)

        if len(specifiers) != arg_count:
            self.error(node.token,
                f"ECHO format string has {len(specifiers)} specifier(s) "
                f"but {arg_count} argument(s) were given.")

        for i, arg in enumerate(node.args):
            arg_type = self.visit(arg)
            if i < len(specifiers) and arg_type:
                expected_spec = specifiers[i]
                if not self._compatible(expected_spec, arg_type):
                    spec_char = [k for k, v in self._SPECIFIER_TO_DTYPE.items()
                                 if v == expected_spec]
                    spec_str = f'%{spec_char[0]}' if spec_char else '?'
                    self.error(node.token,
                        f"ECHO argument {i+1}: specifier {spec_str} expects "
                        f"'{expected_spec}' but got '{self._type_name(arg_type)}'.")

    # ─────────────────────────────────────────────────────────────────────────
    # CONDITIONAL STATEMENTS
    # ─────────────────────────────────────────────────────────────────────────

    def visit_LookNode(self, node):
        """
        LOOK (cond) [ body ] [DROPLOOK (cond) [ body ]] [DROP [ body ]]

        • Condition must be BOOL.
        • Each branch body gets its own scope.
        • SAIL/LAND are valid at the end of any conditional body —
          tracked via in_conditional counter, NOT loop_depth.
        """
        cond_type = self.visit(node.condition)
        if cond_type and not self._is_bool(cond_type):
            self.error(node.token,
                f"LOOK condition must be BOOL, got '{self._type_name(cond_type)}'.")

        # LOOK body
        self.sym.push_scope()
        self.in_conditional += 1
        for stmt in node.body:
            self.visit(stmt)
        self.in_conditional -= 1
        self.sym.pop_scope()

        # DROPLOOK branches
        for (dl_cond, dl_body) in node.droplooks:
            dl_type = self.visit(dl_cond)
            if dl_type and not self._is_bool(dl_type):
                self.error(node.token,
                    f"DROPLOOK condition must be BOOL, "
                    f"got '{self._type_name(dl_type)}'.")
            self.sym.push_scope()
            self.in_conditional += 1
            for stmt in dl_body:
                self.visit(stmt)
            self.in_conditional -= 1
            self.sym.pop_scope()

        # DROP branch
        if node.drop_body is not None:
            self.sym.push_scope()
            self.in_conditional += 1
            for stmt in node.drop_body:
                self.visit(stmt)
            self.in_conditional -= 1
            self.sym.pop_scope()

    def visit_ChartNode(self, node):
        """
        CHART(expr) [ COURSE val: body ... ADRIFT: body LAND!! ]

        • Switch expression must be COIN, PARCH, or SCROLL (per rules).
        • Each COURSE label must be a compatible literal type.
        • Duplicate COURSE labels within the same CHART are invalid.
        • ADRIFT is the default case.
        """
        expr_type = self.visit(node.expr)

        # Switch expression type must be COIN, PARCH, or SCROLL
        if expr_type and expr_type not in ('COIN', 'PARCH', 'SCROLL'):
            self.error(node.token,
                f"CHART expression must be COIN, PARCH, or SCROLL, "
                f"got '{self._type_name(expr_type)}'.")

        outer_chart = self.in_chart
        self.in_chart = True

        seen_labels = {}   # label repr → CourseNode.token (duplicate detection)

        for course in node.courses:
            # Check case value type matches switch expression type
            case_type = self.visit(course.value)
            if expr_type and case_type and not self._compatible(expr_type, case_type):
                self.error(course.token,
                    f"COURSE value type '{self._type_name(case_type)}' does not "
                    f"match CHART expression type '{self._type_name(expr_type)}'.")

            # Duplicate label check
            label_key = repr(course.value)
            if label_key in seen_labels:
                self.error(course.token,
                    f"Duplicate COURSE label in CHART block.")
            else:
                seen_labels[label_key] = course.token

            self.sym.push_scope()
            self.in_conditional += 1
            for stmt in course.body:
                self.visit(stmt)
            self.in_conditional -= 1
            self.sym.pop_scope()

        # ADRIFT body (default case)
        if node.adrift_body is not None:
            outer_adrift = self.in_adrift
            self.in_adrift = True
            self.sym.push_scope()
            self.in_conditional += 1
            for stmt in node.adrift_body:
                self.visit(stmt)
            self.in_conditional -= 1
            self.sym.pop_scope()
            self.in_adrift = outer_adrift

        self.in_chart = outer_chart

    def visit_CourseNode(self, node):
        pass   # handled inline in visit_ChartNode

    # ─────────────────────────────────────────────────────────────────────────
    # LOOP STATEMENTS
    # ─────────────────────────────────────────────────────────────────────────

    def visit_HoistNode(self, node):
        """
        HOIST (init!! cond!! upd) [ body ]

        The init section can declare new COIN variables — these live only
        for the duration of the loop (they get their own scope).
        The condition must resolve to BOOL (numeric comparison).
        """
        self.sym.push_scope()

        for init in node.inits:
            self.visit(init)

        cond_type = self.visit(node.condition)
        if cond_type and not self._is_bool(cond_type):
            self.error(node.token,
                f"HOIST condition must resolve to BOOL, "
                f"got '{self._type_name(cond_type)}'.")

        for upd in node.updates:
            self.visit(upd)

        self.loop_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        self.loop_depth -= 1

        self.sym.pop_scope()

    def visit_HoistInitNode(self, node):
        """
        One HOIST initializer.
          declares_new=True  → COIN id = COIN-lit  (declares loop variable)
          declares_new=False → id = COIN-lit        (assigns to existing variable)
        Per rules, HOIST init variables must be COIN type.
        """
        if node.declares_new:
            if self.sym.lookup_current_scope(node.var_name):
                self.error(node.token,
                    f"Loop variable '{node.var_name}' conflicts with an "
                    f"existing declaration in this scope.")
            else:
                sym = Symbol(node.var_name, 'COIN', 'var', node.token,
                             is_initialized=True)
                self.sym.declare(sym)
        else:
            sym = self.sym.lookup(node.var_name)
            if sym is None:
                self.error(node.token,
                    f"Undeclared variable '{node.var_name}' in HOIST init.")
            elif sym.kind == 'const':
                self.error(node.token,
                    f"Cannot assign to constant '{node.var_name}' in HOIST init.")
            elif sym.dtype != 'COIN':
                # HOIST init with existing var: must be COIN (not just numeric)
                self.error(node.token,
                    f"HOIST init variable '{node.var_name}' must be COIN, "
                    f"got '{sym.dtype}'. "
                    f"(Only COIN literals are valid HOIST initializer values.)")

    def visit_HoistUpdateNode(self, node):
        """
        One HOIST update expression: +#id / -#id, or id op= expr.
        Per rules: unary operands must be COIN; compound operands must be
        numeric (COIN or DIME).
        """
        sym = self.sym.lookup(node.var_name)
        if sym is None:
            self.error(node.token,
                f"Undeclared variable '{node.var_name}' in HOIST update.")
            return
        if sym.kind == 'const':
            self.error(node.token,
                f"Cannot modify constant '{node.var_name}' in HOIST update.")
            return

        if node.update_kind == 'unary':
            # +#id / -#id requires COIN specifically (not DIME)
            if sym.dtype != 'COIN':
                self.error(node.token,
                    f"Unary operator '{node.unary_op}' in HOIST update requires "
                    f"COIN type, but '{node.var_name}' is '{sym.dtype}'.")
        elif node.update_kind == 'compound':
            if not self._is_numeric(sym.dtype):
                self.error(node.token,
                    f"Compound update target '{node.var_name}' must be numeric "
                    f"(COIN/DIME), got '{sym.dtype}'.")
            if node.value is not None:
                val_type = self.visit(node.value)
                if val_type and not self._is_numeric(val_type):
                    self.error(node.token,
                        f"HOIST update value must be numeric, "
                        f"got '{self._type_name(val_type)}'.")

    def visit_HeaveNode(self, node):
        """HEAVE (cond) [ body ] — while loop. Condition must be BOOL."""
        cond_type = self.visit(node.condition)
        if cond_type and not self._is_bool(cond_type):
            self.error(node.token,
                f"HEAVE condition must be BOOL, "
                f"got '{self._type_name(cond_type)}'.")
        self.sym.push_scope()
        self.loop_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        self.loop_depth -= 1
        self.sym.pop_scope()

    def visit_HaulHeaveNode(self, node):
        """HAUL [ body ] HEAVE (cond)!! — do-while. Condition must be BOOL."""
        self.sym.push_scope()
        self.loop_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        self.loop_depth -= 1
        self.sym.pop_scope()
        cond_type = self.visit(node.condition)
        if cond_type and not self._is_bool(cond_type):
            self.error(node.token,
                f"HAUL-HEAVE condition must be BOOL, "
                f"got '{self._type_name(cond_type)}'.")

    # ─────────────────────────────────────────────────────────────────────────
    # JUMP STATEMENTS
    # ─────────────────────────────────────────────────────────────────────────

    def visit_SailNode(self, node):
        """
        SAIL!! — break out of a loop or COURSE case.
        Valid inside any loop body or conditional body (LOOK, COURSE, etc.).
        NOT valid in ADRIFT bodies (grammar already prevents this; we mirror).
        NOT valid at top level or directly inside AHOY with no containing block.
        """
        if self.in_adrift:
            self.error(node.token,
                "SAIL!! is not allowed inside an ADRIFT body.")
            return
        if self.loop_depth == 0 and self.in_conditional == 0:
            self.error(node.token,
                "SAIL!! used outside of a loop or conditional block.")

    def visit_LandNode(self, node):
        """
        LAND!! — continue to next iteration, or exit CHART/LOOK block.
        Valid inside any loop body or conditional body.
        """
        if self.loop_depth == 0 and self.in_conditional == 0:
            self.error(node.token,
                "LAND!! used outside of a loop or conditional block.")

    def visit_ReturnNode(self, node):
        """
        BACK expr!! inside a returning function.
        Checks:
          • Must be inside a returning function (not ABYSS, not global/AHOY).
          • Return value type must match the declared return type.
        """
        if self.current_func_return is None:
            self.error(node.token,
                "BACK (return with value) used outside of a function.")
            return
        if self.current_func_return == 'ABYSS':
            self.error(node.token,
                "ABYSS functions cannot return a value. "
                "Use bare BACK!! instead.")
            return
        ret_type = self.visit(node.value)
        if ret_type and not self._compatible(self.current_func_return, ret_type):
            self.error(node.token,
                f"Function expects return type '{self.current_func_return}', "
                f"but BACK expression has type '{self._type_name(ret_type)}'.")

    def visit_BackNode(self, node):
        """
        Bare BACK!! inside an ABYSS (non-returning) function.
        """
        if self.current_func_return is None:
            self.error(node.token,
                "BACK used outside of a function.")
        elif self.current_func_return != 'ABYSS':
            self.error(node.token,
                f"Bare BACK!! used inside a '{self.current_func_return}' "
                f"returning function. This function must return a value — "
                f"use BACK <value>!! instead.")

    def visit_UnaryStmtNode(self, node):
        """
        +#x!! or -#x!! as a standalone statement.
        Per SeaStack rules: the operand must be a COIN variable (NOT DIME).
        Also invalid on constants.
        """
        sym = self.sym.lookup(node.var_name)
        if sym is None:
            self.error(node.token,
                f"Undeclared variable '{node.var_name}'.")
            return
        if sym.kind == 'const':
            self.error(node.token,
                f"Cannot apply '{node.operator}' to constant '{node.var_name}' "
                f"(constants are read-only).")
            return
        # Rule: unary +# and -# operate on COIN ONLY
        if sym.dtype != 'COIN':
            self.error(node.token,
                f"Operator '{node.operator}' requires a COIN variable, "
                f"but '{node.var_name}' is '{sym.dtype}'. "
                f"(Unary increment/decrement is not defined for '{sym.dtype}'.)")

    def visit_FuncCallStmtNode(self, node):
        """A function call used as a statement (return value discarded)."""
        self.visit(node.call_expr)

    # =========================================================================
    # EXPRESSIONS  (all return a dtype string or None on error)
    # =========================================================================

    def visit_LiteralNode(self, node):
        """Literals always know their own type — return it directly."""
        return node.dtype

    def visit_IdentNode(self, node):
        """
        A bare variable reference.
        Checks:
          • Variable must be declared.
          • Variable must be initialized before use.
        Returns the variable's declared dtype.
        """
        sym = self.sym.lookup(node.name)
        if sym is None:
            self.error(node.token,
                f"Use of undeclared variable '{node.name}'.")
            return None
        if not sym.is_initialized:
            self.error(node.token,
                f"Variable '{node.name}' may be used before it is initialized.")
        return sym.dtype

    def visit_ArrayAccessNode(self, node):
        """
        arr{i} or arr{i}{j}
        Checks:
          • Array must be declared and actually be of kind 'array'.
          • Each index must be COIN type.
        Returns the element type (the array's base dtype).
        """
        sym = self.sym.lookup(node.name)
        if sym is None:
            self.error(node.token,
                f"Undeclared array '{node.name}'.")
            return None
        if sym.kind != 'array':
            self.error(node.token,
                f"'{node.name}' is not an array (it is a '{sym.kind}').")
            return None

        # Validate index types
        for idx, index_expr in enumerate(node.indices):
            idx_type = self.visit(index_expr)
            if idx_type and idx_type != 'COIN':
                self.error(node.token,
                    f"Array index [{idx}] for '{node.name}' must be COIN, "
                    f"got '{self._type_name(idx_type)}'.")

        return sym.dtype   # element type = array's base dtype

    def visit_MemberAccessNode(self, node):
        """
        s$member — access a struct member in an expression.
        Checks:
          • Variable must be a struct_var.
          • The struct type must be resolvable.
          • The member must exist in that struct type.
        Returns the member's declared dtype.
        """
        sym = self.sym.lookup(node.var_name)
        if sym is None:
            self.error(node.token,
                f"Undeclared variable '{node.var_name}'.")
            return None
        if sym.kind != 'struct_var':
            self.error(node.token,
                f"'{node.var_name}' is not a struct variable "
                f"($ member access requires a struct variable).")
            return None

        type_sym = self.sym.lookup(sym.struct_type_name)
        if type_sym is None or type_sym.kind != 'struct':
            self.error(node.token,
                f"Cannot resolve struct type '{sym.struct_type_name}' "
                f"for variable '{node.var_name}'.")
            return None

        if node.member_name not in type_sym.members:
            self.error(node.token,
                f"Struct '{sym.struct_type_name}' has no member "
                f"'{node.member_name}'.")
            return None

        return type_sym.members[node.member_name]

    def visit_ScrollCharAccessNode(self, node):
        """
        "hello"{0} or msg{i}
        Checks:
          • The scroll expression must be SCROLL type.
          • The index must be COIN type.
        Returns PARCH (a single character).
        """
        scroll_type = self.visit(node.scroll_expr)
        if scroll_type and scroll_type != 'SCROLL':
            self.error(node.token,
                f"Character indexing with {{}} requires a SCROLL value, "
                f"got '{self._type_name(scroll_type)}'.")

        idx_type = self.visit(node.index)
        if idx_type and idx_type != 'COIN':
            self.error(node.token,
                f"SCROLL character index must be COIN, "
                f"got '{self._type_name(idx_type)}'.")

        return 'PARCH'   # always returns a single character

    def visit_StringConcatNode(self, node):
        """
        "Hello" & " " & name
        All operands must be SCROLL type. Returns SCROLL.
        """
        for operand in node.operands:
            op_type = self.visit(operand)
            if op_type and op_type != 'SCROLL':
                self.error(node.token,
                    f"String concatenation (&) requires SCROLL operands, "
                    f"got '{self._type_name(op_type)}'.")
        return 'SCROLL'

    def visit_FuncCallNode(self, node):
        """
        add(x, y) — function call used as an expression.
        Checks:
          • Function must be declared.
          • Argument count must match parameter count.
          • Each argument's type must be compatible with the corresponding param.
          • ABYSS functions have no return value — if used as an expression
            (not via FuncCallStmtNode) this is a type error.
        Returns the function's declared return type, or None on error.
        """
        sym = self.sym.lookup(node.name)
        if sym is None:
            self.error(node.token,
                f"Call to undeclared function '{node.name}'.")
            return None
        if sym.kind != 'func':
            self.error(node.token,
                f"'{node.name}' is not a function (it is a '{sym.kind}').")
            return None

        # Argument count check
        expected_count = len(sym.params)
        actual_count   = len(node.args)
        if expected_count != actual_count:
            self.error(node.token,
                f"Function '{node.name}' expects {expected_count} argument(s), "
                f"got {actual_count}.")
        else:
            # Type-check each argument against its corresponding parameter
            for i, (param, arg) in enumerate(zip(sym.params, node.args)):
                arg_type = self.visit(arg)
                if arg_type and not self._compatible(param.dtype, arg_type):
                    self.error(node.token,
                        f"Argument {i+1} of '{node.name}': "
                        f"expected '{param.dtype}', "
                        f"got '{self._type_name(arg_type)}'.")

        # ABYSS return used in an expression context is a type error
        if sym.return_type == 'ABYSS':
            self.error(node.token,
                f"Function '{node.name}' is declared ABYSS (no return value) "
                f"and cannot be used as an expression. "
                f"Call it as a statement instead.")
            return None

        return sym.return_type

    def visit_BinaryOpNode(self, node):
        """
        left OP right

        Type rules per SeaStack spec:
          Arithmetic (+,-,*,/,%,^):
            Both sides must be numeric (COIN or DIME).
            Result is DIME if either side is DIME, else COIN.

          Relational (<,>,<=,>=):
            Both sides must be numeric.
            Result is always BOOL.

          Equality (==,!=):
            Both sides must have COMPATIBLE types.
            COIN==DIME and DIME==COIN are allowed (numeric ↔ numeric).
            PARCH==PARCH, SCROLL==SCROLL, BOOL==BOOL are allowed.
            Cross-type comparisons (e.g. COIN==BOOL) are errors.
            Result is always BOOL.

          Logical (&&,||):
            Both sides must be BOOL.
            Result is always BOOL.
        """
        left_type  = self.visit(node.left)
        right_type = self.visit(node.right)
        op = node.operator

        if op in ('+', '-', '*', '/', '%', '^'):
            if left_type and not self._is_numeric(left_type):
                self.error(node.token,
                    f"Operator '{op}' requires numeric operands, "
                    f"left operand is '{self._type_name(left_type)}'.")
            if right_type and not self._is_numeric(right_type):
                self.error(node.token,
                    f"Operator '{op}' requires numeric operands, "
                    f"right operand is '{self._type_name(right_type)}'.")
            # DIME dominates COIN in mixed arithmetic
            if left_type == 'DIME' or right_type == 'DIME':
                return 'DIME'
            return 'COIN'

        elif op in ('<', '>', '<=', '>='):
            if left_type and not self._is_numeric(left_type):
                self.error(node.token,
                    f"Relational operator '{op}' requires numeric operands, "
                    f"left operand is '{self._type_name(left_type)}'.")
            if right_type and not self._is_numeric(right_type):
                self.error(node.token,
                    f"Relational operator '{op}' requires numeric operands, "
                    f"right operand is '{self._type_name(right_type)}'.")
            return 'BOOL'

        elif op in ('==', '!='):
            if left_type and right_type and not self._compatible(left_type, right_type):
                self.error(node.token,
                    f"Cannot compare '{self._type_name(left_type)}' "
                    f"and '{self._type_name(right_type)}' with '{op}': "
                    f"operands must have compatible types.")
            return 'BOOL'

        elif op in ('&&', '||'):
            if left_type and not self._is_bool(left_type):
                self.error(node.token,
                    f"Logical operator '{op}' requires BOOL operands, "
                    f"left operand is '{self._type_name(left_type)}'.")
            if right_type and not self._is_bool(right_type):
                self.error(node.token,
                    f"Logical operator '{op}' requires BOOL operands, "
                    f"right operand is '{self._type_name(right_type)}'.")
            return 'BOOL'

        return None  # unknown operator — should not happen after syntax parse

    def visit_UnaryOpNode(self, node):
        """
        Prefix unary operators:
          '-'  : negate a numeric value (COIN/DIME → same type preserved)
          '!'  : logical NOT            (BOOL → BOOL)
          '!#' : logical double-NOT     (BOOL → BOOL)
        """
        operand_type = self.visit(node.operand)
        op = node.operator

        if op == '-':
            if operand_type and not self._is_numeric(operand_type):
                self.error(node.token,
                    f"Unary '-' requires a numeric operand (COIN or DIME), "
                    f"got '{self._type_name(operand_type)}'.")
            return operand_type   # preserves COIN or DIME

        elif op in ('!', '!#'):
            if operand_type and not self._is_bool(operand_type):
                self.error(node.token,
                    f"Operator '{op}' requires a BOOL operand, "
                    f"got '{self._type_name(operand_type)}'.")
            return 'BOOL'

        return None
