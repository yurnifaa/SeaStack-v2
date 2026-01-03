### Overview
This module implements the Lexical Analyzer (Lexer) for the compiler. It is responsible for reading the raw source code character-by-character and grouping them into meaningful Token objects. The lexer tracks line and column numbers to provide precise error reporting.

### Core Components
## 1. Token Class
Represents a single unit of the language.
# Attributes:
- type: The category of the token (e.g., AHOY, COIN, ID).
- value: The actual text content (e.g., "variableName").
- line & col: Precise location data for debugging and error messages.

## 2. Lexer Class
Manages the state of the scanning process.
- State Management: Tracks text, pos (index), current_char, line, and col.
- Symbol Table: Initializes the identifier_table for mapping variable names (id1, id2, etc.).
# Navigation Methods:
- advance(): Moves forward one character.
- peek(): Looks ahead without moving (essential for 2-character tokens like != or ~().
- save() / restore(): Backtracking mechanism allows the lexer to attempt a match and revert if it fails.

### Current Functionality
The main entry point is the tokenize() method, which loops through the input and dispatches tasks to specific handlers based on the current_char:
- Keywords: Implements a nested decision tree (checking A, C, D...) to match reserved words like AHOY, COIN, DIME, ECHO, etc.
- Numbers (DFA Implemented):
    - COIN (Integers): Reads 1–16 digits.
    - DIME (Floats): Detects a dot . and reads 1–8 decimal digits.
- Literals:
    - Scrolls (Strings): Handles double quotes " and escape sequences (\n, \t).
    - Parch (Chars): Handles single quotes ' and escape sequences.
- Comments:
    - Single-line: Starts with ~ and ends at a newline.
    - Multi-line: Starts with ~( and ends with )~.
- Symbols & Operators: Supports Arithmetic, Assignment (+=), Logical (&&, ||), and Relational (<=, >=) operators.

### Roadmap & To-Do
Refactoring & Optimization
[ ] Strict State Machine Implementation: Refactor reservedword, symbol, identifier, scroll, and parch handlers to process input character-by-character, strictly following transitional diagrams (using state codes like s279, s280).

[ ] Literal Split: Explicitly separate literal_handler into distinct scroll_handler and parch_handler.

[ ] Delimiter Logic: Centralize delimiter checks to avoid manual updates across different DFAs.

Bug Fixes & Validation
[ ] Identifier Validation: Fix logic to strictly disallow uppercase letters in identifiers.

[ ] Error Messages: Standardize errors to "Invalid character" instead of "Invalid delimiter."

[ ] Reserved Word Validation: Ensure uppercase sequences that aren't valid keywords are flagged as invalid immediately.

[ ] Number Edge Case: Fix parsing bug where a dot after a number consumes the next character incorrectly (e.g., 6.5.!!).