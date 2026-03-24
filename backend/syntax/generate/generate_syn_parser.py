# Reads a grammar TSV file and generates a syn_parser.py-style recursive descent parser.

# TSV FORMAT (save from Google Sheets as .tsv):
# ----------------------------------------------
#  Column 1 (prod_num)    : integer production number
#  Column 2 (non_terminal): e.g.  <program>  or  <coin-var>
#  Column 3 (body)        : space-separated list of symbols:
#                             - Non-terminals → <angle-brackets>
#                             - Terminals     → "quoted-strings"  e.g. "COIN"  "id"  "!!"
#                             - Lambda/empty  → the word:  lambda

# EXAMPLE ROWS:
#  1   <program>       <global-dec> "AHOY" "(" ")" "[" <ahoy-local-dec> <ahoy-stmnts> "]"
#  2   <global-dec>    <var-arr-func>

#USAGE:
#  python generate_syn_parser.py grammar.tsv
#  python generate_syn_parser.py grammar.tsv --out my_parser.py

import sys
import re
import argparse
from collections import defaultdict


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def nt_to_method(non_terminal: str) -> str:
    """Convert <coin-var-arr> → coin_var_arr"""
    name = non_terminal.strip().lstrip("<").rstrip(">")
    return name.replace("-", "_")


def parse_body(body_str: str) -> list:
    """
    Parse a body string into a list of symbol dicts.
    Each symbol is:
      {"kind": "terminal",    "value": "COIN"}
      {"kind": "non_terminal","value": "<coin-var>"}
      {"kind": "lambda"}

    Handles TWO input formats:
      1. Unquoted (from Google Sheets directly):
            COIN id <coin-var-arr-func>
            <coin-var>!!
            =<coin-init-val>
      2. Quoted terminals (original sample format):
            "COIN" "id" <coin-var-arr-func>
    """
    body_str = body_str.strip()

    # Lambda / empty production — handle both λ and the word "lambda"
    if not body_str or body_str in ("λ", "lambda", "Λ"):
        return [{"kind": "lambda"}]

    # ── FORMAT 1: quoted terminals ─────────────────────────────────────────
    # If any "quoted" token appears, use the original quoted-string approach.
    if '"' in body_str:
        symbols = []
        tokens = re.findall(r'"([^"]+)"|(<[^>]+>)', body_str)
        for terminal, non_term in tokens:
            if terminal:
                symbols.append({"kind": "terminal", "value": terminal})
            elif non_term:
                symbols.append({"kind": "non_terminal", "value": non_term})
        return symbols or [{"kind": "lambda"}]

    # ── FORMAT 2: unquoted (real Google Sheets export) ─────────────────────
    # Tokenise with a priority-ordered regex so that multi-char tokens like
    # "!!", "+=", "COIN-lit", "id" are matched before single characters.
    TOKEN_RE = re.compile(
        r'<[^>]+>'                                  # <non-terminal>
        r'|λ|lambda'                                # lambda symbols
        r'|!!'                                      # !! terminator  (before single !)
        r'|\+#|-#|!#'                               # unary ops: +# -# !#
        r'|&&|\|\|'                                 # logical:  && ||
        r'|[+\-*/%^]=|[=!<>]='                     # compound: += -= == != <= >= etc.
        r'|[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*' # word tokens: COIN, COIN-lit, id, AYE
        r'|[^\s]'                                   # any remaining single non-space char
    )

    symbols = []
    for m in TOKEN_RE.finditer(body_str):
        tok = m.group(0)
        if tok in ("λ", "lambda"):
            # inline lambda — treat the whole body as lambda
            return [{"kind": "lambda"}]
        elif tok.startswith("<") and tok.endswith(">"):
            symbols.append({"kind": "non_terminal", "value": tok})
        else:
            symbols.append({"kind": "terminal", "value": tok})

    return symbols or [{"kind": "lambda"}]


def parse_tsv(filepath: str):
    """
    Returns a list of productions:
      [{"prod_num": int, "non_terminal": str, "body": [symbols]}, ...]
    and an ordered list of unique non-terminals (preserving first-seen order).
    """
    productions = []
    seen_nt_order = []
    seen_nt_set = set()

    with open(filepath, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip():
                continue

            parts = line.split("\t")
            if len(parts) < 3:
                print(f"[WARN] Line {lineno} has fewer than 3 tab-separated columns – skipping: {line!r}")
                continue

            prod_num_str = parts[0].strip()
            non_terminal = parts[1].strip()
            body_str     = "\t".join(parts[2:]).strip()   # body may contain tabs

            # Skip header row
            if not prod_num_str.isdigit():
                continue

            prod_num = int(prod_num_str)

            if non_terminal not in seen_nt_set:
                seen_nt_set.add(non_terminal)
                seen_nt_order.append(non_terminal)

            productions.append({
                "prod_num":    prod_num,
                "non_terminal": non_terminal,
                "body":        parse_body(body_str),
            })

    return productions, seen_nt_order


# ─────────────────────────────────────────────
# Code generation
# ─────────────────────────────────────────────

HEADER = '''\
import sys
from syntax.Predict_Set import PREDICT
from backend.error_msg import ErrorHandler

# ============================================================
# AUTO-GENERATED by generate_syn_parser.py
# Do NOT edit manually — edit the grammar TSV and regenerate.
# ============================================================


class Parser:
    def __init__(self, tokens, source_code):
        ignored_types = [
            "whitespace",
            "newline",
            "single-comment",
            "multi-comment",
        ]

        self.tokens = [t for t in tokens if t.type not in ignored_types]

        for t in self.tokens:
            if t.type.startswith("id") and t.type[2:].isdigit():
                t.type = "id"

        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.errors = []
        self.err_handler = ErrorHandler(source_code)

    # =========================================
    # Utility Methods
    # =========================================
    def advance(self):
        """Moves to the next token."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def eat(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            raise Exception(self.err_handler.get_missing_token_error(
                self.current_token,
                token_type,
            ))

    def get_production(self, non_terminal):
        if not self.current_token:
            return None
        productions = PREDICT.get(non_terminal, {})
        return productions.get(self.current_token.type)

    def error_invalid_token(self, non_terminal):
        expected = list(PREDICT.get(non_terminal, {}).keys())
        raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    # =========================================
    # Entry Point
    # =========================================
    def parse(self):
        try:
            if not self.tokens:
                raise Exception(self.err_handler.get_missing_start_error())

            self.program()

            if self.current_token is not None:
                raise Exception(self.err_handler.get_expected_eof_error(self.current_token))

        except Exception as e:
            if e.args and isinstance(e.args[0], dict):
                self.errors.append(e.args[0])
            else:
                self.errors.append({
                    "type": "Parser Crash",
                    "line": "?",
                    "col": "?",
                    "found": "CRASH",
                    "expected": [],
                    "message": str(e),
                })

        return self.errors

    # =========================================
    # GRAMMAR PRODUCTIONS
    # =========================================
'''


# Non-terminals that are optional (only called when the current token
# is in their FIRST set).  Maps non-terminal name → list of trigger token types.
OPTIONAL_CALL_GUARDS: dict = {
    "<id-tail>": ["{", "$", "("],
    "<arr-str>": ["{", "$"],
    "<scr-char>": ["{"],
    "<scr-id>": ["{"],
}


def generate_method(non_terminal: str, prods: list) -> str:
    """Generate a single parser method for one non-terminal."""
    method_name = nt_to_method(non_terminal)
    lines = []
    lines.append(f"    def {method_name}(self):")
    lines.append(f"        # {non_terminal}")
    lines.append(f"        prod = self.get_production({non_terminal!r})")

    # Sort by production number so output is deterministic
    prods_sorted = sorted(prods, key=lambda p: p["prod_num"])

    for i, prod in enumerate(prods_sorted):
        num  = prod["prod_num"]
        body = prod["body"]

        keyword = "if" if i == 0 else "elif"
        lines.append(f"        {keyword} prod == {num}:")

        is_lambda = len(body) == 1 and body[0]["kind"] == "lambda"

        if is_lambda:
            lines.append("            pass  # Lambda")
        else:
            for sym in body:
                if sym["kind"] == "terminal":
                    val = sym["value"]
                    lines.append(f"            self.eat({val!r})")
                elif sym["kind"] == "non_terminal":
                    sub = nt_to_method(sym["value"])
                    guard_tokens = OPTIONAL_CALL_GUARDS.get(sym["value"])
                    if guard_tokens:
                        # Emit a guarded call: only invoke when current token matches
                        tokens_repr = ", ".join(repr(t) for t in guard_tokens)
                        lines.append(f"            if self.current_token.type in [{tokens_repr}]:")
                        lines.append(f"                self.{sub}()")
                    else:
                        lines.append(f"            self.{sub}()")

    lines.append(f"        else:")
    lines.append(f"            self.error_invalid_token({non_terminal!r})")
    lines.append("")

    return "\n".join(lines)


def generate_parser(productions: list, nt_order: list) -> str:
    """Build the full parser source as a string."""
    # Group productions by non-terminal
    grouped = defaultdict(list)
    for prod in productions:
        grouped[prod["non_terminal"]].append(prod)

    parts = [HEADER]
    for nt in nt_order:
        parts.append(generate_method(nt, grouped[nt]))

    return "\n".join(parts)


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Generate syn_parser.py from a grammar TSV.")
    ap.add_argument("tsv", help="Path to the .tsv grammar file")
    ap.add_argument("--out", default="syn_parser_NEW.py",
                    help="Output file path (default: syn_parser_NEW.py)")
    args = ap.parse_args()

    print(f"[INFO] Reading grammar from: {args.tsv}")
    productions, nt_order = parse_tsv(args.tsv)
    print(f"[INFO] Found {len(productions)} productions across {len(nt_order)} non-terminals.")

    source = generate_parser(productions, nt_order)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(source)

    print(f"[INFO] Parser written to: {args.out}")
    print(f"[INFO] Non-terminal order:")
    for nt in nt_order:
        print(f"         {nt}")


if __name__ == "__main__":
    main()