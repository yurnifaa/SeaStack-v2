# Semantic Analysis — SeaStack Compiler

## Overview

The semantic analysis phase is the **third stage** of the SeaStack compiler pipeline. It takes the AST produced by `ast_parser.py` and enforces all rules that the grammar alone cannot express — type correctness, scope, initialization, const protection, and structural constraints.

At the end of this phase, the AST is not only validated but **annotated** — every expression node has its resolved type stamped onto it via `node.resolved_type`, making the type information available to all downstream phases without re-derivation.

---

## Files

| File | Responsibility |
|---|---|
| `semantic_analyzer.py` | Walks the AST via visitor pattern; enforces all semantic rules |
| `symbol_table.py` | Scope-stack symbol registry; tracks all declared names |
| `ast_nodes.py` | AST node class definitions; carries `resolved_type` on expression nodes |
| `sem_error_msg.py` | Centralized semantic error message construction |

---

## `ast_nodes.py` — Node Definitions

Every node class inherits from `ASTNode`:

```python
class ASTNode:
    resolved_type: str = None  # Filled in by SemanticAnalyzer for expression nodes
```

The `resolved_type` class attribute is `None` by default on every node. The semantic analyzer stamps a dtype string (e.g. `'COIN'`, `'BOOL'`, `'SCROLL'`) onto expression nodes as it visits them. Statement nodes intentionally remain `None` — only expressions have types.

### Node Categories

| Category | Nodes |
|---|---|
| Program structure | `ProgramNode`, `AhoyNode` |
| Constants | `ConstDeclNode` |
| Variables | `VarDeclNode`, `ArrayDeclNode` |
| Structs | `StructDefNode`, `MemberDeclNode`, `StructVarDeclNode`, `PositionalInitNode`, `NamedInitNode` |
| Functions | `FuncDefNode`, `ParamNode` |
| Statements | `AssignNode`, `CompoundAssignNode`, `AskNode`, `AddressNode`, `EchoNode`, `LookNode`, `ChartNode`, `CourseNode`, `HoistNode`, `HoistInitNode`, `HoistUpdateNode`, `HeaveNode`, `HaulHeaveNode`, `SailNode`, `LandNode`, `ReturnNode`, `BackNode`, `UnaryStmtNode`, `FuncCallStmtNode` |
| Expressions | `LiteralNode`, `IdentNode`, `ArrayAccessNode`, `MemberAccessNode`, `ScrollCharAccessNode`, `StringConcatNode`, `FuncCallNode`, `BinaryOpNode`, `UnaryOpNode` |

---

## `symbol_table.py` — The Symbol Registry

### Symbol Classes

Each kind of declared name has its own symbol class:

| Class | `kind` | Used for |
|---|---|---|
| `Symbol` | `'var'` `'const'` `'param'` | Plain variables, LOCKE constants, function parameters |
| `ArraySymbol` | `'array'` | Array declarations; carries `dimensions` and `is_2d` |
| `FunctionSymbol` | `'func'` | Function definitions; carries `return_type` and `params` |
| `StructTypeSymbol` | `'struct'` | Struct type definitions (the `MAST` blueprint); carries `members` dict and `member_order` |
| `StructVarSymbol` | `'struct_var'` | Struct variable instances; carries `struct_type_name` |

All symbols carry `name`, `dtype`, `kind`, `token`, `is_initialized`, and `init_expr`.

### `SymbolTable` — Scope Stack

The table is implemented as a stack of dictionaries. Index 0 is global scope; index -1 is always the innermost (current) scope.

```python
self._scopes: list = [{}]  # starts with one global scope
```

| Method | Purpose |
|---|---|
| `push_scope()` | Enter a new scope (function body, loop, conditional) |
| `pop_scope()` | Leave the current scope |
| `declare(symbol)` | Insert into current scope; returns `False` if name already exists |
| `lookup(name)` | Search from innermost to outermost — returns first match or `None` |
| `lookup_current_scope(name)` | Search only the current scope (for duplicate detection) |
| `lookup_global_scope(name)` | Search only global scope (for LOCKE validation) |
| `update_initialized(name)` | Mark a variable as initialized after assignment or ASK |
| `scope_level()` | Returns current depth (1 = global) |
| `is_global_scope()` | Returns `True` when depth is 1 |
| `dump()` | Returns a human-readable string of all scopes and their symbols |

---

## `sem_error_msg.py` — Centralized Error Messages

### Class: `SemanticErrorHandler`

```python
self.err = SemanticErrorHandler(source_code)
```

Owns all semantic error message construction. Every method takes a `token` (for line/col extraction) plus context-specific arguments, and returns a fully-formed error dict:

```python
{
    'line':        int | '?',
    'col':         int | '?',
    'error_type':  str,   # Category label shown in bold in the UI
    'message':     str,   # Full human-readable description
    'actual_line': str,   # Trimmed source line for context
}
```

### Error Categories and Methods

| Category | Key Methods |
|---|---|
| **Undeclared / Undefined** | `undeclared_variable`, `undeclared_variable_in_context`, `undeclared_function`, `undefined_struct_type`, `not_a_function`, `not_an_array`, `not_a_struct_variable`, `unresolvable_struct_type` |
| **Duplicate Declaration** | `duplicate_variable`, `duplicate_array`, `duplicate_function`, `duplicate_const`, `duplicate_identifier`, `duplicate_parameter`, `duplicate_struct_member`, `function_name_conflict`, `loop_variable_conflict` |
| **Uninitialized Variable** | `uninitialized_variable` |
| **LOCKE Modification** | `locke_assignment`, `locke_operator`, `locke_ask_target`, `locke_hoist_init`, `locke_hoist_update` |
| **Invalid LOCKE Scope** | `locke_not_global` |
| **Type Mismatch** | `type_mismatch_init`, `type_mismatch_assign`, `type_mismatch_array_element`, `type_mismatch_struct_member`, `type_mismatch_return`, `type_mismatch_hoist_init`, `type_mismatch_hoist_var` |
| **Invalid Operand Type** | `invalid_operand_binary`, `invalid_operand_relational`, `invalid_operand_logical`, `invalid_operand_unary_neg`, `invalid_operand_not`, `invalid_operand_unary_stmt`, `incompatible_comparison`, `compound_assign_not_numeric`, `compound_assign_rhs_not_numeric`, `hoist_update_unary_not_coin`, `hoist_update_compound_not_numeric`, `hoist_update_value_not_numeric` |
| **Array Index** | `array_index_not_coin`, `array_index_out_of_bounds`, `array_init_too_many_rows`, `array_init_row_too_long`, `array_init_too_many_elements`, `ask_array_index_not_coin`, `scroll_char_index_not_coin`, `scroll_char_index_out_of_bounds`, `scroll_char_requires_scroll`, `scroll_concat_requires_scroll` |
| **Struct Members** | `no_such_member`, `struct_too_many_inits`, `struct_positional_overflow` |
| **Function Calls** | `arg_count_mismatch`, `arg_type_mismatch`, `abyss_in_expression` |
| **Return Statements** | `back_outside_function`, `back_value_in_abyss`, `back_missing_value` |
| **Jump Statements** | `sail_outside_loop`, `sail_inside_adrift`, `land_outside_loop` |
| **Condition Type** | `condition_not_bool` |
| **CHART / COURSE** | `chart_invalid_expr_type`, `course_type_mismatch`, `course_duplicate_label` |
| **Format Specifiers** | `ask_specifier_count_mismatch`, `ask_specifier_type_mismatch`, `echo_specifier_count_mismatch`, `echo_specifier_type_mismatch` |
| **Internal** | `internal_no_visitor` |

---

## `semantic_analyzer.py` — The Analyzer

### Class: `SemanticAnalyzer`

```python
analyzer = SemanticAnalyzer(ast, source_code)
errors = analyzer.analyze()
```

**`analyze()`** calls `self.visit(self.ast)` and returns `self.errors` — a list of error dicts. If the list is empty, the AST passed all semantic checks.

### Context Tracking

The analyzer maintains runtime context flags that change as the visitor descends into different AST regions:

| Attribute | Type | Purpose |
|---|---|---|
| `current_func_return` | `str \| None` | Return type of the function currently being analyzed; `None` outside any function |
| `loop_depth` | `int` | Incremented inside `HOIST`, `HEAVE`, `HAUL` bodies; guards `SAIL`/`LAND` usage |
| `in_conditional` | `int` | Incremented inside `LOOK`, `DROPLOOK`, `DROP`, `CHART`, `COURSE` bodies |
| `in_chart` | `bool` | `True` while inside a `CHART` block |
| `in_adrift` | `bool` | `True` while inside an `ADRIFT` body; guards `SAIL` usage |
| `known_values` | `dict` | Maps `var_name → (dtype, value)` for compile-time constant propagation |

### Visitor Pattern

Dispatch uses Python's `getattr` to find the right method by node class name:

```python
def visit(self, node):
    method = f'visit_{type(node).__name__}'
    return getattr(self, method, self._visit_unknown)(node)
```

**Statement visitors** return `None`. **Expression visitors** return a dtype string and stamp it onto the node:

```python
def visit_BinaryOpNode(self, node):
    lt = self.visit(node.left)
    rt = self.visit(node.right)
    # ... checks ...
    node.resolved_type = result   # ← annotate
    return node.resolved_type
```

Errors are appended via the thin `_e()` helper:

```python
def _e(self, error_dict):
    self.errors.append(error_dict)
```

---

## Type System

### SeaStack Types

| Type keyword | Python equivalent | Notes |
|---|---|---|
| `COIN` | `int` | Integer; 16-digit max |
| `DIME` | `float` | Float; 16-digit integer part, 8-digit decimal part |
| `PARCH` | `str` (single char) | Single character literal |
| `SCROLL` | `str` | String |
| `BOOL` | `bool` | `AYE` = True, `NAY` = False |
| `ABYSS` | `None` | Void; only valid as a function return type |

### Type Compatibility Rules

**Assignment compatibility** (`_compatible`):
- Exact type match always passes
- `COIN` → `DIME` promotion is allowed (integer assigned to float variable)
- All other combinations are rejected

**Expression compatibility** (`_compatible_expr`):
- `COIN` and `DIME` are interchangeable in expressions (e.g. comparing int and float is valid)
- All other type pairs must match exactly

**Arithmetic result type**:
- `COIN op COIN` → `COIN`
- `DIME op anything` or `anything op DIME` → `DIME`

**Format specifier mapping** (`_SPEC_MAP`):
| Specifier | Expected type |
|---|---|
| `%C` | `COIN` |
| `%D` | `DIME` |
| `%P` | `PARCH` |
| `%S` | `SCROLL` |
| `%B` | `BOOL` |

---

## Semantic Rules Enforced

### Declarations

- Variables, arrays, constants, structs, and functions cannot be declared with the same name in the same scope
- `LOCKE` constants may only be declared at global scope
- Array initializer element count cannot exceed the declared dimension size
- Array initializer element types must match the array's declared type
- Struct initializer count cannot exceed the number of members
- Struct member initializer types must match the member's declared type
- Function parameter names must be unique within the parameter list

### Variables and Constants

- Variables must be declared before use
- Variables may not be read before they are initialized (`is_initialized` check)
- `LOCKE` constants are read-only — assignment, compound assignment, unary operators, ASK targets, and HOIST init/update are all rejected
- Identifiers that resolve to functions cannot be used as plain variable references (parentheses required for calls)

### Functions

- Functions are pre-registered in a first pass to support forward references and mutual recursion
- Function calls must match the declared parameter count exactly
- Each argument type must be compatible with the corresponding parameter type
- `ABYSS` functions cannot be used in expression context — only as standalone call statements
- Returning functions must have a `BACK` expression matching the declared return type
- `ABYSS` functions must use bare `BACK!!` and cannot return a value
- `BACK` is illegal outside any function body

### Control Flow

- `LOOK`, `DROPLOOK`, `HEAVE`, `HAUL-HEAVE`, and `HOIST` conditions must resolve to `BOOL`
- `CHART` expression must be `COIN`, `PARCH`, or `SCROLL`
- `COURSE` values must match the `CHART` expression type
- Duplicate `COURSE` labels within the same `CHART` block are rejected
- `SAIL!!` and `LAND!!` are illegal outside a loop or conditional block
- `SAIL!!` is additionally illegal inside an `ADRIFT` (default) body

### Arrays

- Array indices must be `COIN` type
- Compile-time bounds checking: if both the index and array size are known at compile time, out-of-bounds access is reported as an error
- `SCROLL` character indexing requires a `COIN` index; the indexed value must be `SCROLL`
- Compile-time SCROLL character bounds checking uses the same known-value mechanism

### Operators

- Arithmetic operators (`+ - * / % ^`) require numeric operands (`COIN` or `DIME`)
- Relational operators (`< > <= >=`) require numeric operands
- Equality operators (`== !=`) require operands of compatible types
- Logical operators (`&& ||`) require `BOOL` operands
- Unary `-` requires a numeric operand
- Unary `!` and `!#` require a `BOOL` operand
- Unary `+#` and `-#` (increment/decrement) require a `COIN` variable and cannot be applied to `LOCKE`
- Compound assignment operators (`+= -= *= /= %= ^=`) require numeric targets and numeric right-hand sides
- String concatenation `&` requires all operands to be `SCROLL`

---

## Compile-Time Propagation

The analyzer maintains a `known_values` dictionary that tracks variables whose values are known at compile time (assigned from a literal). This enables two important checks without runtime information:

**Array bounds checking** — if an array index is a known integer or a `LOCKE` constant holding a known integer, the analyzer checks it against the array's declared size.

**SCROLL character bounds checking** — if the string being indexed is a known literal or a variable holding a known string, the character index is validated against the string's length.

`known_values` is invalidated for a variable whenever it receives a non-literal assignment (including `ASK` input, compound assignment, or unary update), since the value is no longer compile-time-known.

---

## AST Annotation

After `analyze()` completes, every expression node in the AST carries a `resolved_type`:

| Node | `resolved_type` set to |
|---|---|
| `LiteralNode` | `node.dtype` |
| `IdentNode` | `sym.dtype` from symbol table |
| `ArrayAccessNode` | `sym.dtype` of the array |
| `MemberAccessNode` | `ts.members[member_name]` |
| `ScrollCharAccessNode` | `'SCROLL'` (always) |
| `StringConcatNode` | `'SCROLL'` (always) |
| `FuncCallNode` | `sym.return_type` |
| `BinaryOpNode` | `'COIN'`/`'DIME'` for arithmetic; `'BOOL'` for relational/logical |
| `UnaryOpNode` | Propagated operand type for `-`; `'BOOL'` for `!`/`!#` |

The IR generator reads `node.resolved_type` directly from these nodes rather than re-deriving types, and registers each temporary's type in `IRProgram.temp_types`.

---

## Two-Pass Strategy for Functions and Structs

`visit_ProgramNode` runs two passes over global declarations:

**Pass 1** — pre-registers all `FuncDefNode` and `StructDefNode` names into the symbol table without fully analyzing their bodies. This allows functions to call each other regardless of declaration order (forward references).

**Pass 2** — fully visits every declaration, now with all function and struct names already in scope.

---

## Non-Fatal Error Collection

The semantic analyzer uses **non-fatal error collection** — it never throws an exception. All errors are appended to `self.errors` and analysis continues. This allows multiple independent errors to be reported in a single compilation run.

The one exception is when an error makes further analysis of a subtree meaningless (e.g. an undeclared variable — its type is unknown, so type-checking its usage would produce cascading false errors). In these cases the visitor returns `None` early, and downstream visitors guard against `None` types before reporting further errors.

---

## Pipeline Position

```
[ ast_parser.py ]
    ↓  ProgramNode (unannotated AST)

[ semantic_analyzer.py ]
    ├── errors found → halt, report Semantic Errors to frontend
    └── no errors ↓
    
    ↓  ProgramNode (annotated AST — resolved_type on all expression nodes)

[ ir_generator.py ]
    ...
```