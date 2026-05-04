# SeaStack Compiler - AI Assistant Context

## What is SeaStack?
 
SeaStack is a custom programming language with a direct-execution interpreter. It is not compiled to bytecode or another language — source files are parsed and executed immediately at runtime. The project is split into two parts:
 
- **Backend** — the interpreter engine, written in Python
- **Frontend** — the user-facing interface (web-based), powered by Node.js / npm

## Language Specification
The full SeaStack language rules are documented in [`seastack-rules.md`](seastack-rules.md).
Claude Code can read this file directly — if you need to understand syntax rules,
token definitions, or language behaviour, refer to this document before making changes.

## 1. Project Overview
* Target Language: SeaStack (a custom, C-inspired programming language).
* Compiler Type: Full 6-phase compiler.
* Key Language Features:
  * Statement terminator is `!!` instead of the traditional semicolon.
  * Strict Scoping: Local variable declarations *must* be placed at the absolute top of function bodies.

## 2. Project Architecture & Structure
The project operates as a flattened, desktop-style application divided into distinct frontend and backend domains.
* Backend (Compiler Core): Written in Python. Handles all six compiler phases.
* Frontend: Separate folder housing the UI/desktop application layer.
* Parser Design: A handmade LL(1) Predictive Parser driven by rigorously pre-calculated Predict sets.
* AST Generation: We use an automated generator for the AST parser to streamline node creation and traversal.

## 3. Directory Structure (Expected)
```text
seastack/
├── backend/                # Python compiler core
│   ├── lexer/              # Tokenizer
│   ├── parser/             # LL(1) Predictive Parser & First/Follow/Predict sets
│   ├── codegen/            # Automated AST generator and node definitions
│   ├── semantic/           # Type checking, scope resolution (High Priority)
│   └── code_generator/     # Target code emission
├── frontend/               # Desktop application UI
└── README.md

## 4. Coding Style Preferences
- Backend (Python): Strict typing (using the typing module) is highly encouraged, especially for AST nodes, tokens, and compiler passes.
- Keep parsing logic strictly isolated from semantic checks. The LL(1) parser should only care about syntax; leave meaning and validation to the semantic analyzer.
- AST Node Generation: When creating new language features, update the automated AST generator scripts rather than hand-coding repetitive node classes.
- First/Follow/Predict Sets: Keep these cleanly separated and documented, as the handmade LL(1) parser heavily relies on their accuracy for state transitions.

- Use inline comments with # not """

## Naming Conventions
 
### Python
| Element | Convention | Example |
|---|---|---|
| Files / modules | `snake_case` | `lexer.py`, `runtime.py` |
| Classes | `PascalCase` | `Lexer`, `ASTNode`, `RuntimeError` |
| Functions / methods | `snake_case` | `parse_expression()`, `eval_node()` |
| Variables | `snake_case` | `current_token`, `scope_stack` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_DEPTH`, `TOKEN_EOF` |
| Private members | `_leading_underscore` | `_advance()`, `_current` |

## 6. Constraints & Operating Rules
- LL(1) Compliance: Any new grammar rules proposed must be strictly LL(1) compatible (no left recursion, fully left-factored).
- Scope Enforcement: The semantic analyzer must strictly enforce the rule that all local declarations reside at the top of a function body. Generate clear, descriptive compilation errors if a user violates this.
- Statement Termination: Always enforce the !! terminator in the lexer and parser phases. Do not default to ;.
- No External Parser Generators: Do not suggest using tools like Yacc, Bison, or ANTLR. The predictive parser is strictly handmade.
- **Do not introduce new third-party Python packages** without discussion — the backend must remain lightweight and easy to run with a plain `pip install -r requirements.txt`.
- **Do not modify the public-facing language syntax** without updating the lexer, parser, and any documentation in lockstep.
- **Errors must be user-friendly** — all runtime and parse errors must include a line number and a clear message. Never expose a raw Python traceback to the end user.
- **Interpreter state must be fully reset between executions** — no leaked globals between runs.

## 7. Interpreter Architecture
 
SeaStack uses a classic pipeline:
 
```
Source Code
    │
    ▼
[Lexer]  →  Token stream
    │
    ▼
[Parser]  →  Abstract Syntax Tree (AST)
    │
    ▼
[Interpreter]  →  Direct execution (tree-walk interpreter)
    │
    ▼
Output / Side effects
```
 
- The interpreter is a **tree-walk interpreter**.
- Errors are caught at each stage (lex errors, parse errors, runtime errors) and reported with line/column info.

## 8. Key Concepts Claude Should Know
 
- **Token** — the smallest unit produced by the lexer (e.g. `NUMBER`, `IDENT`, `PLUS`)
- **AST Node** — a Python object representing a syntactic construct (e.g. `BinOp`, `IfStmt`, `FuncDef`)
- **Environment / Scope** — a dictionary (or chain of dicts) mapping variable names to values at runtime