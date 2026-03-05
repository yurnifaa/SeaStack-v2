# =============================================================================
# symbol_table.py — SeaStack Symbol Table
# Scope stack implementation for semantic analysis.
# =============================================================================


# =============================================================================
# SYMBOL CLASSES
# =============================================================================

class Symbol:
    """Base symbol entry."""
    def __init__(self, name, dtype, kind, token, is_initialized=False, init_expr=None):
        self.name = name
        self.dtype = dtype
        self.kind = kind           # 'var'|'const'|'array'|'func'|'struct'|'struct_var'|'param'
        self.token = token
        self.is_initialized = is_initialized
        self.init_expr = init_expr  # Store the initialization expression (AST node) for bounds checking

    def __repr__(self):
        return (f"Symbol(name={self.name!r}, dtype={self.dtype!r}, "
                f"kind={self.kind!r}, init={self.is_initialized})")


class ArraySymbol(Symbol):
    """Array declaration symbol."""
    def __init__(self, name, dtype, dimensions, is_2d, token):
        super().__init__(name, dtype, 'array', token, is_initialized=True)
        self.dimensions = dimensions   # list[int]
        self.is_2d = is_2d

    def __repr__(self):
        dims = 'x'.join(str(d) for d in self.dimensions)
        return (f"ArraySymbol(name={self.name!r}, dtype={self.dtype!r}, "
                f"dims={dims}, is_2d={self.is_2d})")


class FunctionSymbol(Symbol):
    """Function definition symbol."""
    def __init__(self, name, return_type, params, token):
        super().__init__(name, return_type, 'func', token, is_initialized=True)
        self.return_type = return_type
        self.params = params   # list[ParamNode]

    def __repr__(self):
        param_types = ', '.join(p.dtype for p in self.params)
        return (f"FunctionSymbol(name={self.name!r}, "
                f"return={self.return_type!r}, params=[{param_types}])")


class StructTypeSymbol(Symbol):
    """Struct TYPE definition (MAST Ship [...])."""
    def __init__(self, name, members, member_order, token):
        super().__init__(name, 'struct_type', 'struct', token, is_initialized=True)
        self.members = members           # dict[name → dtype]
        self.member_order = member_order # list[str] in declaration order

    def __repr__(self):
        mem_str = ', '.join(f'{k}:{v}' for k, v in self.members.items())
        return f"StructTypeSymbol(name={self.name!r}, members={{{mem_str}}})"


class StructVarSymbol(Symbol):
    """Struct VARIABLE instance (MAST Ship s1)."""
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
    """Scope-stack symbol table."""

    def __init__(self):
        self._scopes: list = [{}]   # index 0 = global, index -1 = current

    # --- Scope Management ---

    def push_scope(self):
        self._scopes.append({})

    def pop_scope(self):
        if len(self._scopes) <= 1:
            raise RuntimeError("Cannot pop global scope.")
        self._scopes.pop()

    def scope_level(self) -> int:
        return len(self._scopes)

    def is_global_scope(self) -> bool:
        return len(self._scopes) == 1

    # --- Declaration ---

    def declare(self, symbol: Symbol) -> bool:
        """Insert into current scope. Returns False if duplicate."""
        current = self._scopes[-1]
        if symbol.name in current:
            return False
        current[symbol.name] = symbol
        return True

    # --- Lookup ---

    def lookup(self, name: str):
        """Search from innermost to outermost scope."""
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_current_scope(self, name: str):
        """Search only the current (innermost) scope."""
        return self._scopes[-1].get(name)

    def lookup_global_scope(self, name: str):
        """Search only the global (outermost) scope."""
        return self._scopes[0].get(name)

    # --- Mutation ---

    def update_initialized(self, name: str):
        """Mark a variable as initialized (after assignment)."""
        for scope in reversed(self._scopes):
            if name in scope:
                scope[name].is_initialized = True
                return

    # --- Diagnostics ---

    def dump(self) -> str:
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
