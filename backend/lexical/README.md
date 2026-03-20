# Lexical Analysis — SeaStack Compiler

## Overview

The lexical analysis phase is the **first stage** of the SeaStack compiler pipeline. It reads raw `.sea` source code as a plain string and converts it into a flat list of **Token** objects that every subsequent phase depends on.

The lexer is implemented as a **state-machine** — characters are consumed one at a time and routed through numbered transition states (State 0 → State N) that mirror the formal transition diagram for the SeaStack language.

---

## Files

| File | Responsibility |
|---|---|
| `lexer.py` | Main lexer class and state dispatcher (State 0) |
| `lexer_token.py` | `Token` data class |
| `handlers/comment_hndlr.py` | Single-line and multi-line comment tokenization |
| `handlers/digit_hndlr.py` | Integer (`COIN`) and float (`DIME`) literal tokenization |
| `handlers/identifier_hndlr.py` | Identifier tokenization and identifier table |
| `handlers/resword_hndlr.py` | Reserved word recognition |
| `handlers/sp_lits_hndlr.py` | `PARCH` (char) and `SCROLL` (string) literal tokenization |
| `handlers/symbol_hndlr.py` | Operators, delimiters, and punctuation tokenization |
| `handlers/delimiters.py` | Delimiter sets used for post-token validation |

---

## The Token Class (`lexer_token.py`)

Every character sequence recognized by the lexer is wrapped into a `Token`:

```python
Token(type, value, line, col, error_msg=None)
```

| Field | Type | Description |
|---|---|---|
| `type` | `str` | Category of the token (e.g. `COIN-lit`, `id`, `AHOY`, `+`) |
| `value` | `str` | Exact character sequence from the source |
| `line` | `int` | Source line number (1-indexed) |
| `col` | `int` | Source column number (1-indexed) |
| `error_msg` | `str \| None` | Set only on `ERROR` tokens; `None` for valid tokens |

Tokens also carry an optional `expected` list, attached by the error path in `_add_or_error()`, which lists valid delimiter characters for the context where the error occurred.

---

## The Lexer Class (`lexer.py`)

### Inheritance

`Lexer` inherits from all handler classes via Python's multiple inheritance:

```python
class Lexer(
    CommentHandler,
    DigitHandler,
    IdentifierHandler,
    ReservedWordHandler,
    LiteralHandler,
    SymbolHandler
):
```

This means every handler's state methods are directly accessible on `self` inside the lexer without any explicit delegation.

### State

| Attribute | Purpose |
|---|---|
| `self.text` | Full source code string |
| `self.pos` | Current character index |
| `self.line` | Current line number |
| `self.col` | Current column number |
| `self.current_char` | Character at `pos`, or `None` at EOF |
| `self.tokens` | Accumulated list of valid `Token` objects |
| `self.errors` | Accumulated list of `ERROR` `Token` objects |
| `self.identifier_table` | Registry of all identifiers seen |
| `self.token_start_*` | Snapshot of `pos/line/col` at the start of the current token |

### Core Methods

**`advance()`** — moves `pos` forward by one character. Handles newlines by incrementing `line` and resetting `col` to 1.

**`peek()`** — returns the character at `pos + 1` without consuming it. Used by symbol handlers to decide between single-character and two-character tokens (e.g. `=` vs `==`, `!` vs `!=`).

**`save()` / `restore(state)`** — snapshots and restores the full lexer state `(pos, line, col, current_char)`. Used when a handler needs to look ahead and backtrack if the lookahead fails.

**`mark_token_start()`** — records the current position as the beginning of the next token, used by `current_token_text()` to slice the lexeme from source.

**`_add_or_error(token_type, token_value, line, col, delim_set_name)`** — called at the end of every handler to finalize a token. It validates that the character immediately following the token belongs to the correct delimiter set for that token type. If the delimiter is invalid, an `ERROR` token is created instead of a valid one.

---

## State 0 — The Main Dispatcher

`state0()` is the entry point for every character. It examines `self.current_char` and routes to the appropriate handler state:

| Character class | Routed to |
|---|---|
| Uppercase letter (`A-Z`) | `_make_keyword()` in `ReservedWordHandler` |
| Lowercase letter (`a-z`) | `id196()` in `IdentifierHandler` |
| Digit (`0-9`) | `c236()` in `DigitHandler` |
| `'` | `p285()` — PARCH literal |
| `"` | `s290()` — SCROLL literal |
| `~` | `cm295()` — comment |
| Arithmetic (`+ - * / % ^`) | `rs120()` through `rs145()` in `SymbolHandler` |
| Assignment / equality (`= !`) | `rs149()`, `rs153()` |
| Relational (`< > & \|`) | `rs161()` through `rs173()` |
| Special (`@ $ , :`) | `rs176()` through `rs182()` |
| Brackets (`{ } ( ) [ ]`) | `rs184()` through `rs194()` |
| Whitespace | Emits a `whitespace` token directly |
| Anything else | Emits an `ERROR` token — Unknown Character |

---

## Token Types

### Primitive Types
| Token type | Example lexeme | Produced by |
|---|---|---|
| `COIN-lit` | `42`, `-7` | `DigitHandler` |
| `DIME-lit` | `3.14` | `DigitHandler` |
| `PARCH-lit` | `'a'` | `LiteralHandler` |
| `SCROLL-lit` | `"hello"` | `LiteralHandler` |
| `AYE` | `AYE` | `ReservedWordHandler` |
| `NAY` | `NAY` | `ReservedWordHandler` |

### Keywords (Reserved Words)
All uppercase sequences are checked against the reserved word list. If matched, a keyword token is emitted (e.g. `AHOY`, `COIN`, `DIME`, `LOOK`, `HOIST`, `HEAVE`, `HAUL`, `CHART`, `COURSE`, `MAST`, `LOCKE`, `BACK`, `SAIL`, `LAND`, `ECHO`, `ASK`, `ABYSS`). Unmatched uppercase sequences become `ERROR` tokens.

### Identifiers
Lowercase-starting sequences. Stored in `identifier_table` with a numeric suffix on the type (e.g. `id0`, `id1`). The parser normalizes these back to the generic `id` type by stripping the numeric suffix.

### Operators and Symbols
| Token type | Lexeme |
|---|---|
| `+` | `+` |
| `-` | `-` |
| `*` | `*` |
| `/` | `/` |
| `%` | `%` |
| `^` | `^` |
| `+#` | `+#` (increment) |
| `-#` | `-#` (decrement) |
| `=` | `=` |
| `==` | `==` |
| `!=` | `!=` |
| `!` | `!` |
| `!#` | `!#` (double-not) |
| `<` | `<` |
| `<=` | `<=` |
| `>` | `>` |
| `>=` | `>=` |
| `&&` | `&&` |
| `\|\|` | `\|\|` |
| `!!` | `!!` (statement terminator) |
| `@` | `@` |
| `$` | `$` |
| `&` | `&` (string concat) |
| `,` | `,` |
| `{` `}` `(` `)` `[` `]` | brackets |

### Ignored Tokens
`whitespace`, `newline`, `single-comment`, `multi-comment` tokens are produced by the lexer but filtered out by the parser before processing begins.

---

## Error Handling

The lexer uses **non-fatal error collection** — it never throws an exception. Instead, it appends `ERROR` tokens to `self.errors` and continues tokenizing. This allows multiple lexical errors to be reported in a single pass.

Two error paths exist:

**`_add_or_error()`** — triggered when a valid token is fully recognized but is followed by an invalid delimiter character. Example: an identifier immediately followed by a digit (`abc3`) would fail the `ID_DELIM` check.

**`state0()` catch-all** — triggered when `current_char` does not match any known character class. Produces an `Unknown Character` error and advances past the bad character.

Error tokens carry:
- `type = "ERROR"`
- `value` = the offending lexeme
- `error_msg` = human-readable description
- `expected` = list of valid delimiter characters (sanitized — whitespace characters are replaced with the string `"whitespace"`)

---

## Public Interface

```python
lexer = Lexer(source_code)
tokens, errors = lexer.tokenize()
```

`tokenize()` runs `state0()` in a loop until `current_char` is `None` (EOF). Returns a tuple of `(tokens, errors)` — both lists are always returned regardless of whether errors occurred.

---

## Pipeline Position

```
Source Code (.sea)
        ↓
[ Lexer ] — produces tokens + errors
        ↓
[ syn_parser.py ] — validates token stream (uses tokens)
        ↓
[ ast_parser.py ] — builds AST (uses tokens)
        ↓
        ...
```

If `errors` is non-empty after `tokenize()`, the compiler halts and reports lexical errors before invoking either parser.