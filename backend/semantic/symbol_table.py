# =============================================================================
# symbol_table.py — SeaStack Symbol Table
# Scope stack implementation for semantic analysis.
# Stores five kinds of symbols: plain variables (Symbol), arrays (ArraySymbol), 
# functions (FunctionSymbol), struct type definitions (StructTypeSymbol), struct variable instances (StructVarSymbol). 
# =============================================================================


# =============================================================================
# SYMBOL CLASSES
# =============================================================================

class Symbol:
    # Base symbol entry.
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

# Array declaration symbol.
class ArraySymbol(Symbol):
    def __init__(self, name, dtype, dimensions, is_2d, token):
        super().__init__(name, dtype, 'array', token, is_initialized=True)
        self.dimensions = dimensions   # list[int]
        self.is_2d = is_2d

    def __repr__(self):
        dims = 'x'.join(str(d) for d in self.dimensions)
        return (f"ArraySymbol(name={self.name!r}, dtype={self.dtype!r}, "
                f"dims={dims}, is_2d={self.is_2d})")

# Function definition symbol.
class FunctionSymbol(Symbol):
    def __init__(self, name, return_type, params, token):
        super().__init__(name, return_type, 'func', token, is_initialized=True)
        self.return_type = return_type
        self.params = params   # list[ParamNode]

    def __repr__(self):
        param_types = ', '.join(p.dtype for p in self.params)
        return (f"FunctionSymbol(name={self.name!r}, "
                f"return={self.return_type!r}, params=[{param_types}])")

# Struct TYPE definition (MAST Ship [...]).
class StructTypeSymbol(Symbol):
    def __init__(self, name, members, member_order, token):
        super().__init__(name, 'struct_type', 'struct', token, is_initialized=True)
        self.members = members           # dict[name → dtype]
        self.member_order = member_order # list[str] in declaration order

    def __repr__(self):
        mem_str = ', '.join(f'{k}:{v}' for k, v in self.members.items())
        return f"StructTypeSymbol(name={self.name!r}, members={{{mem_str}}})"

# Struct VARIABLE instance (MAST Ship s1).
class StructVarSymbol(Symbol):
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

# Scope-stack symbol table
class SymbolTable:

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

    # Insert into current scope. Returns False if duplicate.
    def declare(self, symbol: Symbol) -> bool:
        current = self._scopes[-1]
        if symbol.name in current:
            return False
        current[symbol.name] = symbol
        return True

    # --- Lookup ---

    # Search from innermost to outermost scope.
    def lookup(self, name: str):
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    # Search only the current (innermost) scope.
    def lookup_current_scope(self, name: str):
        return self._scopes[-1].get(name)

    # Search only the global (outermost) scope.
    def lookup_global_scope(self, name: str):
        return self._scopes[0].get(name)

    # --- Mutation ---

    # Mark a variable as initialized (after assignment).
    def update_initialized(self, name: str):
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
