# =============================================================================
# symbol_table.py — SeaStack Symbol Table
#
# HOW THE SYMBOL TABLE WORKS (read before editing):
# ──────────────────────────────────────────────────
# The symbol table is a SCOPE STACK — a list of dicts, where each dict
# represents one lexical scope. The innermost (most-recently-pushed) scope
# is always at index -1.
#
# SCOPE LIFECYCLE:
#   Global scope    → created at construction, never popped.
#   Function scope  → pushed on entry to a function body, popped on exit.
#   Block scope     → pushed for LOOK/HOIST/HEAVE/HAUL/CHART bodies, popped on exit.
#
# SHADOWING:
#   SeaStack explicitly allows a local identifier to shadow a global one.
#   lookup() walks from innermost to outermost — the first match wins.
#   lookup_current_scope() only checks the innermost dict, used for duplicate
#   detection within the same scope.
#
# SYMBOL KINDS:
#   'var'        → regular variable (VarDeclNode)
#   'const'      → LOCKE constant (ConstDeclNode) — cannot be reassigned
#   'array'      → array variable (ArrayDeclNode) — uses ArraySymbol subclass
#   'func'       → subfunction (FuncDefNode) — uses FunctionSymbol subclass
#   'struct'     → struct TYPE definition (StructDefNode) — uses StructTypeSymbol
#   'struct_var' → struct VARIABLE instance (StructVarDeclNode) — uses StructVarSymbol
#   'param'      → function parameter — treated like an initialized var
#
# INITIALIZATION TRACKING:
#   Variables declared without an initializer (e.g. "COIN x!!") start with
#   is_initialized = False. The analyzer flags any read of an uninitialized
#   variable. Calling update_initialized() after an assignment sets it True.
#   Constants, arrays, params, functions, and struct vars are always
#   considered initialized from the moment of declaration.
#
# SCOPE LEVELS:
#   scope_level() returns the current nesting depth (1 = global only).
#   is_global_scope() returns True when only the global scope is active.
#   is_function_scope() returns True when exactly one function scope has been
#   pushed on top of global (depth == 2). Used to distinguish local-of-function
#   vs local-of-nested-block.
# =============================================================================


# =============================================================================
# SYMBOL CLASSES
# =============================================================================

class Symbol:
    """
    Base class for every entry in the symbol table.

    Attributes:
        name           : the identifier string
        dtype          : the SeaStack type ('COIN','DIME','PARCH','SCROLL',
                         'BOOL','ABYSS', or a struct type name)
        kind           : one of the kind strings listed above
        token          : the lexer Token at the declaration site (for error
                         location reporting)
        is_initialized : False for uninitialized variables; True for everything
                         else
    """
    def __init__(self, name, dtype, kind, token, is_initialized=False):
        self.name           = name
        self.dtype          = dtype
        self.kind           = kind
        self.token          = token
        self.is_initialized = is_initialized

    def __repr__(self):
        return (f"Symbol(name={self.name!r}, dtype={self.dtype!r}, "
                f"kind={self.kind!r}, init={self.is_initialized})")


class ArraySymbol(Symbol):
    """
    Symbol for an array declaration.

    Extra attributes:
        dimensions : list[int] — declared sizes, e.g. [5] for 1D or [3,4] for 2D
        is_2d      : bool
    """
    def __init__(self, name, dtype, dimensions, is_2d, token):
        super().__init__(name, dtype, 'array', token, is_initialized=True)
        self.dimensions = dimensions   # list[int]
        self.is_2d      = is_2d        # bool

    def __repr__(self):
        dims = 'x'.join(str(d) for d in self.dimensions)
        return (f"ArraySymbol(name={self.name!r}, dtype={self.dtype!r}, "
                f"dims={dims}, is_2d={self.is_2d})")


class FunctionSymbol(Symbol):
    """
    Symbol for a subfunction definition.

    Extra attributes:
        return_type : the declared return type string
        params      : list[ParamNode] — the original parameter nodes are kept
                      so the analyzer can check argument compatibility at call
                      sites (type, count, and order).
    """
    def __init__(self, name, return_type, params, token):
        super().__init__(name, return_type, 'func', token, is_initialized=True)
        self.return_type = return_type
        self.params      = params        # list[ParamNode]

    def __repr__(self):
        param_types = ', '.join(p.dtype for p in self.params)
        return (f"FunctionSymbol(name={self.name!r}, "
                f"return={self.return_type!r}, params=[{param_types}])")


class StructTypeSymbol(Symbol):
    """
    Symbol for a struct TYPE definition (MAST Ship [...]).

    Extra attributes:
        members      : dict[str, str] — maps member_name → dtype.
                       Insertion order is preserved (Python 3.7+) so
                       positional struct initialization can iterate in
                       declaration order.
        member_order : list[str] — member names in declaration order.
                       Kept separately for safe positional-init indexing
                       without relying on dict ordering in older Pythons.
    """
    def __init__(self, name, members, member_order, token):
        super().__init__(name, 'struct_type', 'struct', token, is_initialized=True)
        self.members      = members       # dict[member_name → dtype]
        self.member_order = member_order  # list[str] preserves declaration order

    def __repr__(self):
        mem_str = ', '.join(f'{k}:{v}' for k, v in self.members.items())
        return f"StructTypeSymbol(name={self.name!r}, members={{{mem_str}}})"


class StructVarSymbol(Symbol):
    """
    Symbol for a struct VARIABLE instance (MAST Ship s1).

    Extra attributes:
        struct_type_name : str — the name of the MAST struct definition.
                           Used to look up the StructTypeSymbol when
                           checking member accesses.
    """
    def __init__(self, name, struct_type_name, token):
        super().__init__(name, struct_type_name, 'struct_var', token,
                         is_initialized=True)
        self.struct_type_name = struct_type_name

    def __repr__(self):
        return (f"StructVarSymbol(name={self.name!r}, "
                f"struct_type={self.struct_type_name!r})")


# =============================================================================
# SYMBOL TABLE
# =============================================================================

class SymbolTable:
    """
    A scope-stack symbol table for SeaStack semantic analysis.

    Usage pattern:
        sym = SymbolTable()           # global scope already open

        sym.push_scope()              # enter function body / block
        sym.declare(my_symbol)        # add to current scope
        sym.lookup('x')               # search outward from innermost scope
        sym.pop_scope()               # exit scope (symbols are discarded)

    Error handling:
        declare() returns False if the name already exists IN THE CURRENT
        SCOPE (duplicate declaration). The caller is responsible for
        reporting the error; the duplicate is NOT inserted.

        lookup() returns None if the name is not found in any scope. The
        caller is responsible for reporting the undeclared-identifier error.
    """

    def __init__(self):
        # Index 0 = global scope, index -1 = innermost (current) scope.
        self._scopes: list = [{}]

    # ─────────────────────────────────────────────────────────────────────────
    # SCOPE MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def push_scope(self):
        """Open a new (inner) lexical scope."""
        self._scopes.append({})

    def pop_scope(self):
        """
        Close the innermost scope, discarding all symbols declared in it.
        Raises RuntimeError if called when only the global scope is open
        (popping global scope would be a bug in the analyzer).
        """
        if len(self._scopes) <= 1:
            raise RuntimeError(
                "SymbolTable.pop_scope() called with only global scope open — "
                "this is a bug in the semantic analyzer."
            )
        self._scopes.pop()

    def scope_level(self) -> int:
        """
        Returns the current nesting depth.
          1  = global only
          2  = one function scope pushed on top of global
          3+ = nested blocks (LOOK/HOIST/HEAVE/CHART) inside a function
        """
        return len(self._scopes)

    def is_global_scope(self) -> bool:
        """True when only the global scope is active (depth == 1)."""
        return len(self._scopes) == 1

    def is_function_scope(self) -> bool:
        """
        True when exactly one scope has been pushed on top of global (depth == 2).
        This corresponds to the outermost scope of a function body — where
        local declarations and parameters live.
        """
        return len(self._scopes) == 2

    # ─────────────────────────────────────────────────────────────────────────
    # DECLARATION
    # ─────────────────────────────────────────────────────────────────────────

    def declare(self, symbol: Symbol) -> bool:
        """
        Insert a symbol into the CURRENT (innermost) scope.

        Returns:
            True  → symbol successfully declared.
            False → a symbol with the same name already exists in THIS scope
                    (duplicate declaration). The new symbol is NOT inserted;
                    the caller should report the error.

        SeaStack allows shadowing — a local name may duplicate a global name.
        That is NOT treated as a duplicate here, because the declarations
        live in different scopes.
        """
        current = self._scopes[-1]
        if symbol.name in current:
            return False          # duplicate in current scope — caller reports error
        current[symbol.name] = symbol
        return True

    # ─────────────────────────────────────────────────────────────────────────
    # LOOKUP
    # ─────────────────────────────────────────────────────────────────────────

    def lookup(self, name: str):
        """
        Search for a symbol by name, starting from the innermost scope and
        moving outward. Returns the first (innermost) match, or None.

        This implements SeaStack's shadowing rules: a local declaration of 'x'
        hides any global declaration of 'x' within the local scope.
        """
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_current_scope(self, name: str):
        """
        Search ONLY the current (innermost) scope.
        Used for duplicate-declaration checks where shadowing is allowed but
        re-declaring in the same scope is not.
        Returns the Symbol, or None if not present in the current scope.
        """
        return self._scopes[-1].get(name)

    def lookup_global_scope(self, name: str):
        """
        Search ONLY the global (outermost) scope.
        Useful when verifying that a globally-defined function or struct type
        exists regardless of any local shadowing.
        Returns the Symbol, or None if not found in global scope.
        """
        return self._scopes[0].get(name)

    # ─────────────────────────────────────────────────────────────────────────
    # MUTATION
    # ─────────────────────────────────────────────────────────────────────────

    def update_initialized(self, name: str):
        """
        Mark a variable as initialized (called after a successful assignment).
        Searches outward from the innermost scope and updates the first match.
        Does nothing if the name is not found (the undeclared error was already
        reported at the read/write site).
        """
        for scope in reversed(self._scopes):
            if name in scope:
                scope[name].is_initialized = True
                return

    # ─────────────────────────────────────────────────────────────────────────
    # DIAGNOSTICS
    # ─────────────────────────────────────────────────────────────────────────

    def dump(self) -> str:
        """
        Return a human-readable dump of the entire scope stack.
        Useful when debugging the semantic analyzer.
        """
        lines = [f"SymbolTable — {len(self._scopes)} scope(s):"]
        for depth, scope in enumerate(self._scopes):
            label = "global" if depth == 0 else f"scope[{depth}]"
            lines.append(f"  {label}:")
            if scope:
                for name, sym in scope.items():
                    lines.append(f"    {name!r:25s} → {sym!r}")
            else:
                lines.append("    (empty)")
        return "\n".join(lines)

    def all_symbols_in_current_scope(self) -> dict:
        """Return a copy of the current scope's symbol dict (for testing)."""
        return dict(self._scopes[-1])

    def all_symbols_in_global_scope(self) -> dict:
        """Return a copy of the global scope's symbol dict (for testing)."""
        return dict(self._scopes[0])
