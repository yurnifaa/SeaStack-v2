"""
generate_ast_parser.py
======================
Reads a grammar TSV file and generates a scaffold ast_parser.py.

Unlike generate_syn_parser.py (which produces a fully mechanical parser),
this generator produces a SCAFFOLD that you fill in:

  ✅ Full ASTParser class boilerplate (constructor, eat, advance, build)
  ✅ Every grammar method with correct production dispatch
  ✅ self.eat('TOKEN') for every terminal in every production
  ✅ result = self.sub_method() for every non-terminal call
  ✅ Smart return stubs:  [] for list-style NTs, None for node-style NTs
  ✅ # TODO markers show exactly where AST node construction goes
  ✅ Token-capture lines  (tok = self.current_token) before key eat() calls

You then replace the TODO stubs with the actual ASTNode instantiations.

TSV FORMAT (identical to generate_syn_parser.py):
  Column 1: production number (int)
  Column 2: non-terminal  e.g.  <coin-var>
  Column 3: body          e.g.  COIN id <coin-var-arr> !!

USAGE:
  python generate_ast_parser.py cfg.tsv
  python generate_ast_parser.py cfg.tsv --out ast_parser_NEW.py
"""

import sys
import re
import argparse
from collections import defaultdict


# =============================================================================
# HEURISTICS — which non-terminals return lists vs single nodes
# =============================================================================

# Non-terminal name fragments that strongly suggest "this method returns a list".
# Extend this list if your grammar uses other naming patterns.
LIST_NT_HINTS = (
    "mult",   # <coin-init-mult>, <param-mult>, …
    "tail",   # <cav-tail>, <course-tail>, …
    "list",   # <str-val-list>, …
    "stmnts", # <ahoy-stmnts>, <ret-stmnts>, …
    "stmnt",  # statement collectors
    "body",   # <look-body>, <course-body>, …
    "dec",    # <local-dec>, <mem-dec>, …  (declarations accumulate)
    "params", # <params>
    "args",   # <args>
    "struct", # <struct>  (returns a list of StructDefNode)
)

# Non-terminals whose lambda production should silently return an empty list
# (a subset of LIST_NT_HINTS where an empty list is the right default)
LAMBDA_EMPTY_LIST = LIST_NT_HINTS  # same set for now


def is_list_nt(name: str) -> bool:
    """Return True when the NT conventionally returns a list of nodes."""
    lower = name.lower()
    return any(h in lower for h in LIST_NT_HINTS)


# =============================================================================
# TSV PARSING  (identical logic to generate_syn_parser.py)
# =============================================================================

def nt_to_method(non_terminal: str) -> str:
    """<coin-var-arr> → coin_var_arr"""
    name = non_terminal.strip().lstrip("<").rstrip(">")
    return name.replace("-", "_")


TOKEN_RE = re.compile(
    r'<[^>]+>'
    r'|λ|lambda'
    r'|!!'
    r'|\+#|-#|!#'
    r'|&&|\|\|'
    r'|[+\-*/%^]=|[=!<>]='
    r'|[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*'
    r'|[^\s]'
)


def parse_body(body_str: str) -> list:
    """
    Parse a production body string into a list of symbol dicts.
    Each symbol: {"kind": "terminal"|"non_terminal"|"lambda", "value": str}
    """
    body_str = body_str.strip()
    if not body_str or body_str in ("λ", "lambda", "Λ"):
        return [{"kind": "lambda"}]

    if '"' in body_str:
        symbols = []
        tokens = re.findall(r'"([^"]+)"|(<[^>]+>)', body_str)
        for terminal, non_term in tokens:
            if terminal:
                symbols.append({"kind": "terminal", "value": terminal})
            elif non_term:
                symbols.append({"kind": "non_terminal", "value": non_term})
        return symbols or [{"kind": "lambda"}]

    symbols = []
    for m in TOKEN_RE.finditer(body_str):
        tok = m.group(0)
        if tok in ("λ", "lambda"):
            return [{"kind": "lambda"}]
        elif tok.startswith("<") and tok.endswith(">"):
            symbols.append({"kind": "non_terminal", "value": tok})
        else:
            symbols.append({"kind": "terminal", "value": tok})

    return symbols or [{"kind": "lambda"}]


def parse_tsv(filepath: str):
    """
    Returns:
      productions  — list of {"prod_num": int, "non_terminal": str, "body": [...]}
      nt_order     — list of unique NTs in first-seen order
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
                print(f"[WARN] Line {lineno}: fewer than 3 tab-separated columns – skipping")
                continue
            prod_num_str = parts[0].strip()
            non_terminal = parts[1].strip()
            body_str     = "\t".join(parts[2:]).strip()

            if not prod_num_str.isdigit():
                continue  # header row

            prod_num = int(prod_num_str)
            if non_terminal not in seen_nt_set:
                seen_nt_set.add(non_terminal)
                seen_nt_order.append(non_terminal)

            productions.append({
                "prod_num":     prod_num,
                "non_terminal": non_terminal,
                "body":         parse_body(body_str),
            })

    return productions, seen_nt_order


# =============================================================================
# CODE GENERATION
# =============================================================================

HEADER = '''\
# =============================================================================
# ast_parser.py — SeaStack AST-Building Parser  (AUTO-GENERATED SCAFFOLD)
#
# Generated by generate_ast_parser.py — DO NOT edit the scaffold structure.
# Your job: replace every  # TODO  comment with actual ASTNode construction.
#
# Workflow:
#   1. Every method is a stub that calls eat() / sub-methods correctly.
#   2. Find the TODO lines and return the right ASTNode (or list of nodes).
#   3. Methods whose name contains list-style hints already return [].
#      Change those to build and return real node lists.
# =============================================================================

from syntax.Predict_Set import PREDICT
from semantic.ast_nodes import (
    # TODO: import every ASTNode class you need, e.g.:
    # ProgramNode, AhoyNode,
    # ConstDeclNode, VarDeclNode, ArrayDeclNode,
    # StructDefNode, MemberDeclNode,
    # StructVarDeclNode, PositionalInitNode, NamedInitNode,
    # FuncDefNode, ParamNode,
    # AssignNode, CompoundAssignNode,
    # AskNode, AddressNode, EchoNode,
    # LookNode, ChartNode, CourseNode,
    # HoistNode, HoistInitNode, HoistUpdateNode,
    # HeaveNode, HaulHeaveNode,
    # SailNode, LandNode, ReturnNode, BackNode,
    # UnaryStmtNode, FuncCallStmtNode,
    # LiteralNode, IdentNode,
    # ArrayAccessNode, MemberAccessNode,
    # ScrollCharAccessNode, StringConcatNode,
    # FuncCallNode, BinaryOpNode, UnaryOpNode,
)


class ASTParser:
    def __init__(self, tokens, source_code):
        ignored_types = [\'whitespace\', \'newline\', \'single-comment\', \'multi-comment\']
        self.tokens = [t for t in tokens if t.type not in ignored_types]
        for t in self.tokens:
            if t.type.startswith(\'id\') and t.type[2:].isdigit():
                t.type = \'id\'
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

    # ── Utility ──────────────────────────────────────────────────────────

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            found = self.current_token.type if self.current_token else \'EOF\'
            raise RuntimeError(
                f\'ASTParser bug: expected {token_type!r}, got {found!r} \'
                f\'at line {getattr(self.current_token, "line", "?")}\')

    def get_production(self, non_terminal):
        if not self.current_token:
            return None
        return PREDICT.get(non_terminal, {}).get(self.current_token.type)

    # ── Entry Point ──────────────────────────────────────────────────────

    def build(self):
        return self.program()

    # =========================================================================
    # GRAMMAR PRODUCTIONS  (auto-generated scaffold)
    # =========================================================================
'''


def _var_name_for(sym: dict, used: set) -> str:
    """
    Choose a local variable name for a non-terminal call result.
    Avoids clashes within the same production branch.
    """
    base = nt_to_method(sym["value"])          # e.g. "coin_val"
    # Shorten common long bases for readability
    short_map = {
        "coin_val": "cv", "dime_val": "dv", "parch_val": "pv",
        "scroll_val": "sv", "bool_val": "bv",
        "coin_var_arr": "cva", "dime_var_arr": "dva",
        "statements": "stmt", "local_dec": "ldec",
        "params": "params", "args": "args",
    }
    candidate = short_map.get(base, base[:8]) if len(base) > 8 else base
    # Ensure uniqueness
    name = candidate
    i = 2
    while name in used:
        name = f"{candidate}{i}"
        i += 1
    used.add(name)
    return name


def _is_significant_terminal(val: str) -> bool:
    """
    Returns True for terminals whose token we want to capture
    (identifiers, literals, operators) vs purely structural ones.
    """
    structural = {"!!", "(", ")", "[", "]", "{", "}", ",", ":", "@", "$",
                  "=", "+", "-", "*", "/", "%", "^",
                  "+=", "-=", "*=", "/=", "%=", "^=",
                  "==", "!=", "<", ">", "<=", ">=",
                  "&&", "||", "!", "!#", "+#", "-#", "&"}
    return val not in structural


def generate_method(non_terminal: str, prods: list) -> str:
    """Generate a single ASTParser method for one non-terminal."""
    method_name = nt_to_method(non_terminal)
    returns_list = is_list_nt(non_terminal)

    lines = []
    lines.append(f"    def {method_name}(self):")
    lines.append(f"        # {non_terminal}")
    lines.append(f"        prod = self.get_production({non_terminal!r})")

    prods_sorted = sorted(prods, key=lambda p: p["prod_num"])

    for i, prod in enumerate(prods_sorted):
        num  = prod["prod_num"]
        body = prod["body"]
        keyword = "if" if i == 0 else "elif"
        lines.append(f"        {keyword} prod == {num}:")

        is_lambda = len(body) == 1 and body[0]["kind"] == "lambda"

        if is_lambda:
            if returns_list:
                lines.append(f"            return []  # λ — empty list")
            else:
                lines.append(f"            return None  # λ — no node")
        else:
            used_vars: set = set()

            for sym in body:
                if sym["kind"] == "terminal":
                    val = sym["value"]
                    if _is_significant_terminal(val):
                        # Capture the token before eating (useful for node construction)
                        var = val.lower().replace("-", "_").replace(".", "_")
                        var = re.sub(r'[^a-z0-9_]', '_', var)
                        if var in used_vars:
                            var = f"{var}_tok"
                        used_vars.add(var)
                        lines.append(f"            {var}_tok = self.current_token  # capture {val!r} token")
                    lines.append(f"            self.eat({val!r})")

                elif sym["kind"] == "non_terminal":
                    sub = nt_to_method(sym["value"])
                    var = _var_name_for(sym, used_vars)
                    lines.append(f"            {var} = self.{sub}()")

            # Close the branch with a TODO stub
            if returns_list:
                lines.append(f"            # TODO: build node(s) using captured tokens/sub-results above")
                lines.append(f"            return []  # TODO: replace with real node list")
            else:
                lines.append(f"            # TODO: build node using captured tokens/sub-results above")
                lines.append(f"            return None  # TODO: replace with real ASTNode")

    # Final else: error
    lines.append(f"        else:")
    lines.append(f"            raise RuntimeError(")
    lines.append(f"                f'ASTParser bug: unexpected token {{self.current_token!r}}'")
    lines.append(f"                f' in {method_name} (non-terminal {non_terminal!r})')")
    lines.append("")

    return "\n".join(lines)


def generate_ast_parser(productions: list, nt_order: list) -> str:
    """Build the full ASTParser source as a string."""
    grouped = defaultdict(list)
    for prod in productions:
        grouped[prod["non_terminal"]].append(prod)

    parts = [HEADER]
    for nt in nt_order:
        parts.append(generate_method(nt, grouped[nt]))

    return "\n".join(parts)


# =============================================================================
# MAIN
# =============================================================================

def main():
    ap = argparse.ArgumentParser(
        description="Generate an ast_parser.py scaffold from a grammar TSV.")
    ap.add_argument("tsv", help="Path to the .tsv grammar file")
    ap.add_argument("--out", default="ast_parser_NEW.py",
                    help="Output file path (default: ast_parser_NEW.py)")
    args = ap.parse_args()

    print(f"[INFO] Reading grammar from: {args.tsv}")
    productions, nt_order = parse_tsv(args.tsv)
    print(f"[INFO] Found {len(productions)} productions across {len(nt_order)} non-terminals.")

    source = generate_ast_parser(productions, nt_order)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(source)

    print(f"[INFO] Scaffold written to: {args.out}")
    print(f"[INFO] Non-terminal order:")
    for nt in nt_order:
        marker = " [LIST]" if is_list_nt(nt) else ""
        print(f"         {nt}{marker}")
    print()
    print("[INFO] Next steps:")
    print("  1. Open the generated file.")
    print("  2. Search for '# TODO' — each one is a spot where you build/return an ASTNode.")
    print("  3. Methods marked [LIST] above already return []; replace with real node lists.")
    print("  4. Add any needed arguments to method signatures (e.g. dtype, nt).")
    print("  5. Uncomment and fill in the import block at the top.")


if __name__ == "__main__":
    main()