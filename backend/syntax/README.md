# Syntax Analysis — SeaStack Compiler

## Overview

The syntax analysis phase is the **second stage** of the SeaStack compiler pipeline. It takes the flat token list produced by the lexer and verifies that the token sequence conforms to SeaStack's formal grammar — and if it does, builds an **Abstract Syntax Tree (AST)** from it.

This phase is split into **two separate parsers** that run in sequence:

1. **`syn_parser.py`** — a pure *recognizer* that validates the token stream and collects syntax errors
2. **`ast_parser.py`** — an *AST builder* that re-walks the same tokens and constructs the tree, but only runs if `syn_parser` found no errors

Both parsers share the same grammar and the same PREDICT table, implementing a **predictive LL(1) top-down parser**.

---

## Files

| File | Responsibility |
|---|---|
| `syn_parser.py` | Validates token stream against grammar; collects syntax errors |
| `ast_parser.py` | Builds the AST from the validated token stream |
| `syntax/Predict_Set.py` | PREDICT table mapping `(non-terminal, token)` → production number |
| `backend/error_msg.py` | Constructs all syntax error message dicts |
| `generate_syn_parser.py` | Auto-generates `syn_parser.py` from the grammar TSV — do not edit `syn_parser.py` manually |

---

## Architecture: Two-Parser Design

### Why two parsers?

A single parser that both validates and builds an AST must mix error-recovery logic with tree-construction logic, making both harder to maintain. The two-parser design keeps concerns separated:

- `syn_parser.py` focuses entirely on **error detection and reporting** with clean, user-facing messages
- `ast_parser.py` focuses entirely on **tree construction** with no error-handling clutter — it can assume the input is already valid

The tradeoff is that the token stream is walked twice, but since `ast_parser` only runs on clean input, the total cost remains acceptable.

### Important maintenance note

`syn_parser.py` is **auto-generated** from a grammar TSV file using `generate_syn_parser.py`. Do not edit it manually — any changes will be overwritten on the next regeneration. `ast_parser.py` is hand-maintained and must be updated manually whenever the grammar changes.

---

## The PREDICT Table (`syntax/Predict_Set.py`)

Both parsers share a single PREDICT table — a nested dictionary:

```python
PREDICT = {
    '<non-terminal>': {
        'token_type': production_number,
        ...
    },
    ...
}
```

Given a non-terminal and the current token type, a lookup returns which production rule to apply. If the lookup returns `None`, no valid production exists and an error is raised.

The table covers **685 productions** across the full SeaStack grammar, including lambda (empty) productions where a non-terminal can legally match nothing.

---

## Parser 1: `syn_parser.py` — The Recognizer

### Purpose

Validates the token stream. Returns a list of syntax error dicts. If the list is empty, the input is syntactically valid and `ast_parser.py` can proceed.

### Class: `Parser`

```python
parser = Parser(tokens, source_code)
errors = parser.parse()
```

**`__init__`** filters out ignored token types before storing the token list:
```python
ignored_types = ["whitespace", "newline", "single-comment", "multi-comment"]
```

It also normalizes identifier tokens — any token whose type matches `id` followed by digits (e.g. `id0`, `id12`) is normalized back to the generic type `id`. This is because the lexer assigns unique-suffixed types to each identifier, but the parser only needs the generic category.

### Core Methods

**`advance()`** — moves to the next token. Sets `current_token` to `None` at EOF.

**`eat(token_type)`** — asserts that `current_token` matches the expected type and advances. On mismatch, raises an exception with a structured error dict from `ErrorHandler`.

**`get_production(non_terminal)`** — looks up `current_token.type` in the PREDICT table for the given non-terminal. Returns the production number, or `None` if no production matches.

**`error_invalid_token(non_terminal)`** — called when `get_production` returns an unexpected value. Collects the set of expected tokens from the PREDICT table and raises an error.

**`parse()`** — entry point. Calls `self.program()` and catches any exception into `self.errors`. Also checks that no tokens remain after `program()` completes (unexpected tokens after the main block). Always returns `self.errors`.

### Production Methods

Every non-terminal in the grammar has a corresponding method (e.g. `program()`, `global_dec()`, `coin_var()`, `look_body()`, `condition()`). Each method:

1. Calls `get_production('<non-terminal>')` to determine which rule applies
2. Dispatches to the correct sequence of `eat()` calls and recursive non-terminal method calls
3. Returns `None` — the recognizer discards all values

Lambda (empty) productions are represented as `pass`:
```python
elif prod == 6:
    pass  # Lambda — this non-terminal can match nothing
```

### Error Handling

`syn_parser` uses **single-error-and-stop** — the first error encountered halts parsing. This is intentional: in a predictive parser, a single mismatched token can cascade into dozens of false errors. Reporting one clean error is more useful than reporting twenty noisy ones.

All error messages are produced by `ErrorHandler` from `backend/error_msg.py`.

---

## Error Messages (`backend/error_msg.py`)

### Class: `ErrorHandler`

```python
handler = ErrorHandler(source_code)
```

Produces structured error dicts for all syntax error cases:

| Method | Trigger |
|---|---|
| `get_missing_start_error()` | Source file is empty |
| `get_invalid_token_error(token, expected)` | PREDICT table lookup fails (unexpected token or unexpected EOF) |
| `get_missing_token_error(token, expected_type)` | `eat()` fails — token present but wrong type |
| `get_expected_eof_error(token)` | Tokens remain after `program()` completes |
| `get_program_start_error(token, expected)` | Program begins with an illegal token |
| `get_custom_error(token, message)` | Generic fallback |

All methods return the same error dict schema:

```python
{
    "type":         "Syntax Error",
    "error_header": str,      # Short label shown in bold in the UI
    "line":         int,
    "col":          int,
    "found":        str,      # The token type that caused the error
    "expected":     list,     # List of valid token types at this point
    "message":      str,      # Full formatted message with source line
}
```

### Special case: Missing `AHOY`

If `eat('AHOY')` fails, `get_missing_token_error` detects the expected type and emits a dedicated "Missing Main Function 'AHOY'" message instead of the generic misplaced-token message.

### Delimiter sanitization

Expected token lists are sanitized before display — whitespace characters (`' '`, `'\t'`, `'\n'`, etc.) are replaced with the human-readable string `"whitespace"` so they render meaningfully in the error panel.

---

## Parser 2: `ast_parser.py` — The AST Builder

### Purpose

Builds an AST from the validated token stream. Returns the root `ProgramNode`. Only called after `syn_parser` confirms zero errors.

### Class: `ASTParser`

```python
parser = ASTParser(tokens, source_code)
root = parser.build()
```

Applies the same token filtering and `id`-type normalization as `syn_parser`.

### Entry Point

```python
def build(self):
    return self.program()
```

Returns the root `ProgramNode` of the complete AST.

### Key Design Differences from `syn_parser`

| Aspect | `syn_parser` | `ast_parser` |
|---|---|---|
| Return values | All methods return `None` | All methods return nodes or node lists |
| Error handling | Full error dict construction | Raises `RuntimeError` with bug message (should never trigger on valid input) |
| Token capture | Tokens are consumed and discarded | Tokens are captured into node constructors |
| Purpose | Detect errors | Build tree |

### Node Construction Pattern

Every production method captures tokens and returns AST nodes:

```python
def coin_var(self, dtype, nt):
    init = self.coin_init()
    return [VarDeclNode(dtype, nt.value, init, nt)] + self.coin_init_mult(dtype)
```

Tokens are captured **before** being consumed so their `line` and `col` can be stored on the node for later use in semantic error reporting:

```python
nt = self.current_token   # capture token first
self.eat('id')            # then consume it
```

### Expression Folding

Arithmetic and boolean chains are built using **left-folding** — each new operator and operand wraps the accumulated left result, producing a left-associative tree:

```python
def bool_exp_fold(self, left):
    prod = self.get_production('<bool-exp>')
    if prod == 227:
        op_tok = self.current_token
        op = self.log_op()
        right = self.bool_val()
        return self.bool_exp_fold(BinaryOpNode(left, op, right, op_tok))
    return left
```

This correctly encodes operator precedence for `&&`, `||`, `+`, `-`, etc.

### String Concatenation

`SCROLL` concatenation using `&` is handled by `scroll_concat_fold()`, which collects all operands and produces a single `StringConcatNode`:

```python
def scroll_concat_fold(self, left):
    if self.current_token and self.current_token.type == '&':
        operands = [left]
        while self.current_token and self.current_token.type == '&':
            self.eat('&')
            operands.append(self.scroll_val())
        return StringConcatNode(operands, tok)
    return left
```

### Known Grammar Divergences from `syn_parser`

Due to a grammar quirk, `scroll_var_arr_func` (production 123) includes an extra `sub_func` call that was manually fixed in `ast_parser.py` but is not present in the auto-generated `syn_parser.py`. This is documented in the header comment of `ast_parser.py`. Any future grammar regeneration must be cross-checked against these manual fixes.

---

## Node Types Produced

`ast_parser.py` imports and produces nodes from `semantic/ast_nodes.py`. The full set:

**Program structure:** `ProgramNode`, `AhoyNode`

**Declarations:** `ConstDeclNode`, `VarDeclNode`, `ArrayDeclNode`, `StructDefNode`, `MemberDeclNode`, `StructVarDeclNode`, `PositionalInitNode`, `NamedInitNode`, `FuncDefNode`, `ParamNode`

**Statements:** `AssignNode`, `CompoundAssignNode`, `AskNode`, `AddressNode`, `EchoNode`, `LookNode`, `ChartNode`, `CourseNode`, `HoistNode`, `HoistInitNode`, `HoistUpdateNode`, `HeaveNode`, `HaulHeaveNode`, `SailNode`, `LandNode`, `ReturnNode`, `BackNode`, `UnaryStmtNode`, `FuncCallStmtNode`

**Expressions:** `LiteralNode`, `IdentNode`, `ArrayAccessNode`, `MemberAccessNode`, `ScrollCharAccessNode`, `StringConcatNode`, `FuncCallNode`, `BinaryOpNode`, `UnaryOpNode`

---

## Pipeline Position

```
[ Lexer ]
    ↓  tokens + errors
    
[ syn_parser.py ]
    ├── errors found → halt, report Syntax Errors to frontend
    └── no errors ↓

[ ast_parser.py ]
    ↓  ProgramNode (root of AST)

[ semantic_analyzer.py ]
    ...
```

---

## Grammar Coverage

| Construct | SeaStack keyword(s) |
|---|---|
| Entry point | `AHOY` |
| Variable declaration | `COIN`, `DIME`, `PARCH`, `SCROLL`, `BOOL` |
| Constant declaration | `LOCKE` |
| Array declaration | `COIN{n}`, `DIME{n}`, etc. |
| Struct definition | `MAST` |
| Function definition | `COIN func()`, `ABYSS func()` |
| If / else-if / else | `LOOK`, `DROPLOOK`, `DROP` |
| Switch | `CHART`, `COURSE`, `ADRIFT` |
| For loop | `HOIST` |
| While loop | `HEAVE` |
| Do-while loop | `HAUL ... HEAVE` |
| Break | `LAND` |
| Continue | `SAIL` |
| Return | `BACK` |
| Print | `ECHO` |
| Input | `ASK` |
| Statement terminator | `!!` |