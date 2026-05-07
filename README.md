# 🌊 SeaStack | Programming Language and Compiler
A C-inspired programming language with an oceanic twist — built from scratch for automata theory and formal languages. SeaStack is a high-level programming language designed to combine structured programming principles with a thematic and engaging syntax inspired by the Ocean Voyager theme. It takes its foundation from the C language, adapting familiar constructs such as functions, loops, conditionals, and data type.  This built as part of an academic project in automata theory and formal languages, SeaStack includes its own lexer, parser, and GUI-based IDE.

### 🌕 IDE - Light Mode
![Light Mode](frontend/public/GitHub_shots/Light_Mode3.png)

### 🌑 IDE - Dark Mode
![Dark Mode](frontend/public/GitHub_shots/Dark_Mode3.png)

## Language Rules (to be added in the future)

## 📂 Project Structure
```plaintext
SEASTACK_PROJ/
├── backend/
│ ├── codegen/
│ │ ├── code_generator.py
│ │ ├── ir_generator.py
│ │ ├── optimizer.py
│ │ └── ir_instructions.py
│ ├── lexical/
│ │ ├── handlers/
│ │ ├── lexer_token.py
│ │ ├── lexer_errors.py
│ │ └── lexer.py
│ ├── semantic/
│ │ ├── ast_nodes.py
│ │ ├── ast_parser.py
│ │ ├── sem_error_msg.py
│ │ ├── symbol_table.py
│ │ └── semantic_analyzer.py
│ ├── syntax/
│ │ ├── generate/
│ │ ├── syn_error_msg.py
│ │ ├── Predict_Set.py
│ │ └── syn_parser.py
│ ├── run_error_msg.py
│ ├── README.md
│ └── server.py
├── frontend/
│   ├── .next/
│   ├── node_modules/
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── favicon.ico
│   │   │   ├── globals.css
│   │   │   ├── layout.js
│   │   │   └── page.js
│   │   └── components/
│   │       ├── CodeEditor.js
│   │       └── seaStackLang.ts
│   ├── .gitignore
│   ├── eslint.config.mjs
│   ├── jsconfig.json
│   ├── next.config.mjs
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.mjs
│   └── README.md
├── node_modules/
├── package-lock.json
├── package.json
└── README.md
 ```

## 🖥️ How to Run
Follow these steps to set up and run SeaStack locally on your computer.

### 🔑 Prerequisites
Ensure you have the following installed:
- Node.js (v18 or higher recommended)
- Python (v3.10 or higher recommended)

Navigate to the root directory and install the required Python libraries:
```plaintext 
pip install -r requirements.txt
```

**▶️ Frontend & Root Setup (Node.js)**<br>
Install dependencies for the root project (to run the scripts) and the frontend interface:
```plaintext 
# 1. Install root dependencies (for the 'concurrently' script)
npm install

# 2. Install frontend dependencies (for React/Next.js)
cd frontend
npm install
cd ..
```

**▶️ Run the Application**<br>
Start both servers with one command from the root directory:
```plaintext 
npm run dev
```

## 👥 Contributors
- ALISWAG, K. V. J.
- CAYACAP, F. A. S.
- DEL ROSARIO, J. M. A.
- MAGAAN, F. M. V.
- MULLENO, J. M. A.

# DEFENSE NOTES:
# SeaStack Pipeline Walkthrough: `AHOY() [ ECHO("Test")!! ]`

## Context

This document traces exactly how the program below moves through every stage of the SeaStack compiler — from raw characters to console output — using the actual code in the `backend/` directory.

```
AHOY() [
ECHO("Test")!!
]
```

---

## Phase 1 — Lexical Analysis (`backend/lexical/`)

**Entry point:** `lexer.py` → `state0()` dispatcher

The lexer reads the source character-by-character and routes each character to a handler based on its first character.

### Character-by-character trace

| Input chars | Handler invoked | Token emitted |
|---|---|---|
| `A H O Y` | `rw1()` → reserved word states | `Token(type='AHOY', value='AHOY', line=1)` |
| `(` | Symbol handler | `Token(type='(', value='(', line=1)` |
| `)` | Symbol handler | `Token(type=')', value=')', line=1)` |
| ` ` | Whitespace | (whitespace token, skipped by parser) |
| `[` | Symbol handler | `Token(type='[', value='[', line=1)` |
| `\n` | Whitespace | (skipped) |
| `E C H O` | `rw1()` → reserved word states | `Token(type='ECHO', value='ECHO', line=2)` |
| `(` | Symbol handler | `Token(type='(', value='(', line=2)` |
| `"Test"` | `s292()` → SCROLL text handler | `Token(type='SCROLL-lit', value='Test', line=2)` |
| `)` | Symbol handler | `Token(type=')', value=')', line=2)` |
| `!!` | Symbol handler → two-char check | `Token(type='!!', value='!!', line=2)` |
| `\n` | Whitespace | (skipped) |
| `]` | Symbol handler | `Token(type=']', value=']', line=3)` |
| (end) | — | `Token(type='EOF')` |

### Final token stream (after whitespace removal)
```
AHOY  (  )  [  ECHO  (  SCROLL-lit:"Test"  )  !!  ]  EOF
```

**Key detail:** The lexer uses delimiter validation — after scanning `AHOY`, it checks that the next character is in `OPENP_DELIM` (which includes `(`). This prevents malformed identifiers from slipping through.

---

## Phase 2 — Syntax Analysis (`backend/syntax/`)

**Entry point:** `syn_parser.py` — an LL(1) predictive parser driven by `predict_set.py`

The parser calls `get_production(non_terminal)` at each step, looking up the current lookahead token in the PREDICT table to decide which grammar rule to apply. No backtracking — fully deterministic.

### Parse trace

```
<program>
  lookahead = AHOY → production 1: global_dec* then AHOY() [ ahoy_local_dec ahoy_stmnts ]

  <global-dec>* (loop)
    lookahead = AHOY → not a type keyword → zero global declarations

  eat('AHOY')          ✓  consumes AHOY
  eat('(')             ✓  consumes (
  eat(')')             ✓  consumes )
  eat('[')             ✓  consumes [

  <ahoy_local_dec> (loop)
    lookahead = ECHO → not COIN/DIME/PARCH/SCROLL/BOOL/LOCKE/MAST → zero local declarations

  <ahoy_stmnts> (loop)
    lookahead = ECHO → matches echo statement production

    <echo-stmnt>
      eat('ECHO')      ✓  consumes ECHO
      eat('(')         ✓  consumes (
      <value>          → lookahead = SCROLL-lit → literal production
        eat('SCROLL-lit')  ✓  consumes "Test"
      eat(')')         ✓  consumes )
      eat('!!')        ✓  consumes !!

    lookahead = ] → end of ahoy_stmnts

  eat(']')             ✓  consumes ]
  lookahead = EOF      ✓  program complete
```

**Parse succeeds.** The LL(1) parser never had to guess — every token matched its expected production exactly.

---

## Phase 3 — Semantic Analysis (`backend/semantic/`)

### Step 3a: AST Construction (`ast_parser.py`)

The AST parser mirrors the syntax parser but produces node objects instead of consuming tokens silently.

```
ProgramNode(
  global_decls = [],
  ahoy = AhoyNode(
    local_decls = [],
    statements = [
      EchoNode(
        format_string = LiteralNode(dtype='SCROLL', value='Test'),
        args = []
      )
    ]
  )
)
```

### Step 3b: Semantic Validation (`semantic_analyzer.py`)

The analyzer does a visitor-pattern walk, using the SymbolTable scope stack.

```
visit_ProgramNode()
  → Pass 1: scan for function/struct names to pre-register (none here)
  → Pass 2: visit everything

  visit_AhoyNode()
    → push_scope()          # enter AHOY block scope

    → visit local_decls     # empty, nothing to do

    → visit_EchoNode()
        format_string = "Test"
        _parse_specs("Test") → []     # no %C / %D / %S / %P / %B specifiers found
        args = []                     # 0 specifiers, 0 args → counts match ✓
        No type checking needed (no args)
        → EchoNode is valid ✓

    → pop_scope()           # exit AHOY block scope

errors = []   # zero semantic errors
```

**The AST is annotated and ready.** No symbols were declared, no type mismatches, no scope violations.

---

## Phase 4 — IR Generation / TAC (`backend/codegen/ir_generator.py`)

**Entry point:** `IRGenerator.generate()` → `visit(ast)`

The generator walks the annotated AST and emits `Quad` objects (Three-Address Code instructions). Each `Quad` has: `(op, arg1, arg2, result)`.

### Quads emitted (raw TAC)

```
#  op              arg1       arg2    result    comment
─────────────────────────────────────────────────────────
1  PROGRAM_START   –          –       –
2  AHOY_BEGIN      –          –       –
3  OUTPUT          "Test"     –       –         # ECHO("Test")!!
4  AHOY_END        –          –       –
5  PROGRAM_END     –          –       –
```

**Why no temporaries?** Temporaries (`_t0`, `_t1`, …) are created when an expression needs an intermediate result (e.g., `"a" & "b"` → `CONCAT "a" "b" _t0`). Here the ECHO argument is a plain string literal — the format string itself IS the value — so the generator passes it directly to `OUTPUT` without creating a temp.

---

## Phase 5 — Optimization (`backend/codegen/optimizer.py`)

The optimizer runs 6 passes in a loop until no more changes occur.

### Pass-by-pass for this program

| Pass | What it does | Effect here |
|---|---|---|
| 1 Constant Folding | Fold `_t0 = 1 + 2` → `_t0 = 3` | Nothing to fold (no arithmetic) |
| 2 Constant Propagation | Replace temp refs with known literals | No temps exist |
| 3 Copy Propagation | Replace `_t1 = _t0` chains | No copies |
| 4 Strength Reduction | `x^2` → `x*x`, `x*1` → `x` | No arithmetic |
| 5 Dead Code Elimination | Remove unused pure-expression temps | No temps to eliminate |
| 6 Jump Optimization | Remove `JUMP` to immediately next label | No jumps |

**Optimized TAC = Raw TAC** (unchanged — the program is already minimal).

---

## Phase 6 — Code Generation (`backend/codegen/code_generator.py`)

The code generator translates each Quad into Python source code.

### `OUTPUT` quad → Python

For `Quad(op='OUTPUT', arg1='"Test"', arg2=None, result=None)`:

1. Parse format string `"Test"` — look for `%C`, `%S`, `%D`, `%P`, `%B` specifiers → none found
2. No format substitution needed → format string stays as `"Test"`
3. No numeric args → no `_ss_check_overflow()` calls needed
4. Emit: `print("Test", end='')`

### Full generated Python (simplified)

```python
# --- preamble helpers ---
def _ss_display(val): ...
def _ss_check_overflow(val, dtype): ...
# ... (other helpers)

# --- main entry ---
def _ss_ahoy():
    print("Test", end='')

_ss_ahoy()
```

---

## Phase 7 — Execution (`backend/server.py`)

The server runs the generated Python inside an isolated `exec()` namespace with a patched `print()`.

### Execution trace

```
server.py: _compile() runs phases 1–6, returns python_code string

exec(python_code, namespace)
  → namespace['print'] = captured_print   # print is replaced

_ss_ahoy() is called
  → print("Test", end='')
      ↓
  captured_print("Test", end='')
      → output_q.put(('output', 'Test'))

SSE generator reads output_q:
  → yields:  data: {"type": "output", "text": "Test"}\n\n

Frontend receives SSE event
  → appends "Test" to the console display
```

**Console shows:** `Test`

---

## End-to-End Summary

```
Source:  AHOY() [\n  ECHO("Test")\n]

Lexer    → [AHOY] [(] [)] [[] [ECHO] [(] [SCROLL-lit:"Test"] [)] [!!] []]

Parser   → parse tree: program → ahoy_block → echo_stmt → scroll_literal

AST      → ProgramNode → AhoyNode → EchoNode(fmt="Test", args=[])

Semantic → EchoNode validated: 0 specifiers, 0 args — OK. No errors.

IR/TAC   →  PROGRAM_START
            AHOY_BEGIN
            OUTPUT  "Test"  –  –
            AHOY_END
            PROGRAM_END

Optimize →  (no changes — single OUTPUT, no temporaries, no dead code)

Codegen  →  def _ss_ahoy():
                print("Test", end='')
            _ss_ahoy()

Runtime  →  captured_print → output_q → SSE → frontend console: "Test"
```