# generate_predict_set.py
# Reads the grammar TSV and automatically computes FIRST, FOLLOW, and PREDICT
# sets using standard LL(1) table construction, then outputs a Predict_Set.py.

# ALGORITHM:
#  FIRST(A)  → terminals that can start any string derived from A
#              λ is added to FIRST(A) if A can produce the empty string
#  FOLLOW(A) → terminals that can appear immediately after A in any sentential form
#              only computed for nullable non-terminals (those with a λ production)
#  PREDICT(A → α):
#              = FIRST(α)           if α cannot derive λ
#              = FIRST(α) ∪ FOLLOW(A) if α can derive λ  (λ itself is excluded)

# The production numbers from the TSV are used directly as predict table values,
# matching exactly how the hand-written Predict_Set.py maps terminals → prod_num.

# USAGE:
#  python generate_predict_set.py grammar.tsv

import csv
import re
import argparse
from collections import defaultdict

LAMBDA = 'λ'


# ─────────────────────────────────────────────
# TSV Parsing  (handles multi-line quoted cells)
# ─────────────────────────────────────────────

TOKEN_RE = re.compile(
    r'<[^>]+>'                                       # <non-terminal>
    r'|λ|lambda'                                     # lambda symbols
    r'|!!'                                           # !! (before single !)
    r'|\+#|-#|!#'                                    # unary ops
    r'|&&|\|\|'                                      # logical
    r'|\+#|-#'
    r'|[+\-*/%^]=|[=!<>]='                          # compound/compare ops
    r'|[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*'     # word tokens
    r'|[^\s]'                                        # any single non-space char
)


def parse_body(body_str: str) -> list:
    """
    Parse a production body into a list of symbol dicts.
    Supports both unquoted (Google Sheets native) and "quoted" terminal formats.
    Returns: [{"kind": "terminal"|"non_terminal"|"lambda", "value": ...}, ...]
    """
    body_str = body_str.strip()

    # Lambda / empty
    if not body_str or body_str in ('λ', 'lambda', 'Λ', 'λ '):
        return [{'kind': 'lambda'}]

    # Quoted-terminal format ("COIN" "id" <non-term>)
    if '"' in body_str:
        symbols = []
        for terminal, non_term in re.findall(r'"([^"]+)"|(<[^>]+>)', body_str):
            if terminal:
                symbols.append({'kind': 'terminal', 'value': terminal})
            elif non_term:
                symbols.append({'kind': 'non_terminal', 'value': non_term})
        return symbols or [{'kind': 'lambda'}]

    # Unquoted format (Google Sheets native)
    symbols = []
    for m in TOKEN_RE.finditer(body_str):
        tok = m.group(0)
        if tok in ('λ', 'lambda'):
            return [{'kind': 'lambda'}]
        elif tok.startswith('<') and tok.endswith('>'):
            symbols.append({'kind': 'non_terminal', 'value': tok})
        else:
            symbols.append({'kind': 'terminal', 'value': tok})

    return symbols or [{'kind': 'lambda'}]


def parse_tsv(filepath: str):
    """
    Returns:
      grammar  : {non_terminal: [(prod_num, [symbols])]}  ordered dict-like
      nt_order : list of non-terminals in first-seen order
    Uses csv.reader so multi-line quoted cells (from Google Sheets) are handled.
    """
    grammar  = defaultdict(list)
    nt_order = []
    seen_nt  = set()

    with open(filepath, encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter='\t')
        for lineno, row in enumerate(reader, 1):
            if len(row) < 3:
                continue

            prod_num_str = row[0].strip()
            non_terminal = row[1].strip()
            # Column 3 is strictly the body; column 4 (override_expected) is
            # for the parser generator only and must NOT be included here.
            body_str = row[2].strip()

            if not prod_num_str.isdigit():
                continue  # header or blank

            prod_num = int(prod_num_str)

            if non_terminal not in seen_nt:
                seen_nt.add(non_terminal)
                nt_order.append(non_terminal)

            grammar[non_terminal].append((prod_num, parse_body(body_str)))

    return grammar, nt_order


# ─────────────────────────────────────────────
# FIRST / FOLLOW / PREDICT
# ─────────────────────────────────────────────

def first_of_sequence(body: list, first_sets: dict) -> set:
    """
    Compute FIRST of a sequence of symbols (body of one production).
    Returns a set of terminals; includes LAMBDA if the whole sequence can derive ε.
    """
    result = set()
    for sym in body:
        kind = sym['kind']
        if kind == 'lambda':
            result.add(LAMBDA)
            return result
        elif kind == 'terminal':
            result.add(sym['value'])
            return result
        elif kind == 'non_terminal':
            nt_first = first_sets.get(sym['value'], set())
            result.update(nt_first - {LAMBDA})
            if LAMBDA not in nt_first:
                return result
    # Fell through: entire body derives λ
    result.add(LAMBDA)
    return result


def compute_first_sets(grammar: dict) -> dict:
    """Iterative fixpoint computation of FIRST sets."""
    first = defaultdict(set)

    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for _prod_num, body in productions:
                new = first_of_sequence(body, first)
                if not new.issubset(first[nt]):
                    first[nt].update(new)
                    changed = True

    return dict(first)


def compute_follow_sets(grammar: dict, first_sets: dict) -> dict:
    """
    Iterative fixpoint computation of FOLLOW sets.
    Only non-terminals that appear in some RHS get entries here,
    plus any nullable non-terminal needs its FOLLOW set for predict table.
    No EOF/$ is added — the parser handles end-of-input separately.
    """
    follow = defaultdict(set)

    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for _prod_num, body in productions:
                # Walk each position looking for non-terminals
                for i, sym in enumerate(body):
                    if sym['kind'] != 'non_terminal':
                        continue
                    B = sym['value']
                    rest = body[i + 1:]

                    # FOLLOW(B) ⊇ FIRST(rest) − {λ}
                    rest_first = first_of_sequence(rest, first_sets) if rest else {LAMBDA}
                    added = (rest_first - {LAMBDA}) - follow[B]
                    if added:
                        follow[B].update(added)
                        changed = True

                    # If rest can derive λ, FOLLOW(B) ⊇ FOLLOW(nt)
                    if LAMBDA in rest_first:
                        added = follow[nt] - follow[B]
                        if added:
                            follow[B].update(added)
                            changed = True

    return dict(follow)


def build_predict_table(grammar: dict, first_sets: dict, follow_sets: dict) -> dict:
    """
    Build PREDICT table.
    Returns: {non_terminal: {terminal_token: prod_num}}
    """
    predict = {}

    for nt, productions in grammar.items():
        entries = {}
        for prod_num, body in productions:
            prod_first = first_of_sequence(body, first_sets)

            # Terminals in FIRST(body) → this prod
            for terminal in prod_first - {LAMBDA}:
                if terminal in entries and entries[terminal] != prod_num:
                    print(f'[WARN] CONFLICT on <{nt}> token "{terminal}": '
                          f'prod {entries[terminal]} vs {prod_num}. Grammar may not be LL(1).')
                entries[terminal] = prod_num

            # If body can derive λ, FOLLOW(nt) tokens → this prod
            if LAMBDA in prod_first:
                for terminal in follow_sets.get(nt, set()):
                    if terminal in entries and entries[terminal] != prod_num:
                        print(f'[WARN] CONFLICT on <{nt}> token "{terminal}" (follow): '
                              f'prod {entries[terminal]} vs {prod_num}.')
                    entries[terminal] = prod_num

        if entries:
            predict[nt] = entries

    return predict


# ─────────────────────────────────────────────
# Output formatting
# ─────────────────────────────────────────────

def _terminal_sort_key(t: str):
    """
    Sort key matching the hand-written Predict_Set.py style:
    - Special symbols first: !, !#, $, (, ), *, +, +=, etc.
    - Then alphabetical uppercase words: AYE, BOOL, COIN ...
    - Then lowercase: id
    """
    is_word = bool(re.match(r'^[A-Za-z]', t))
    is_lower = t.islower()
    return (is_word, is_lower, t)


def format_predict_entry(nt: str, entries: dict) -> str:
    """
    Format one non-terminal's entries as a Python dict literal.
    Tokens that share the same prod_num are grouped on the same line.
    Lambda-production tokens (highest prod_num, FOLLOW set) go last.
    """
    # Group tokens by prod_num
    by_prod = defaultdict(list)
    for tok, prod_num in entries.items():
        by_prod[prod_num].append(tok)

    # Sort prod_nums; put the lambda prod (FOLLOW set) last if it exists
    prod_nums = sorted(by_prod.keys())

    lines = []
    for prod_num in prod_nums:
        toks = sorted(by_prod[prod_num], key=_terminal_sort_key)
        pair_strs = [f'{t!r}: {prod_num}' for t in toks]
        lines.append('        ' + ', '.join(pair_strs))

    inner = ',\n'.join(lines)
    return f'    {nt!r}: {{\n{inner}\n    }},'


def write_predict_set(predict: dict, nt_order: list, filepath: str):
    """Write the Predict_Set.py file in TSV first-seen order."""
    lines = [
        '# AUTO-GENERATED by generate_predict_set.py',
        '# Do NOT edit manually — regenerate from the grammar TSV.',
        '',
        'PREDICT = {',
    ]

    # Use the order non-terminals first appear in the TSV
    ordered   = [nt for nt in nt_order if nt in predict]
    remainder = [nt for nt in predict   if nt not in set(nt_order)]
    for nt in ordered + remainder:
        lines.append(format_predict_entry(nt, predict[nt]))

    lines.append('}')
    lines.append('')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description='Generate Predict_Set.py from a grammar TSV using FIRST/FOLLOW sets.')
    ap.add_argument('tsv', help='Path to the .tsv grammar file')
    ap.add_argument('--out', default='Predict_Set_NEW.py',
                    help='Output file (default: Predict_Set_NEW.py)')
    ap.add_argument('--start', default=None,
                    help='Start symbol (default: first non-terminal in TSV)')
    args = ap.parse_args()

    print(f'[INFO] Reading grammar: {args.tsv}')
    grammar, nt_order = parse_tsv(args.tsv)

    start = args.start or nt_order[0]
    total_prods = sum(len(v) for v in grammar.values())
    print(f'[INFO] {total_prods} productions, {len(grammar)} non-terminals')
    print(f'[INFO] Start symbol: {start}')

    print('[INFO] Computing FIRST sets...')
    first_sets = compute_first_sets(grammar)

    print('[INFO] Computing FOLLOW sets...')
    follow_sets = compute_follow_sets(grammar, first_sets)

    print('[INFO] Building PREDICT table...')
    predict = build_predict_table(grammar, first_sets, follow_sets)

    # Print a summary of nullable non-terminals (those with FOLLOW sets in use)
    nullable = [nt for nt, prods in grammar.items()
                if any(len(b) == 1 and b[0]['kind'] == 'lambda' for _, b in prods)]
    print(f'[INFO] Nullable non-terminals: {len(nullable)}')

    write_predict_set(predict, nt_order, args.out)
    print(f'[INFO] Written to: {args.out}')

    # Show FIRST/FOLLOW for a few key non-terminals as a sanity check
    print('\n[SANITY CHECK] Sample FIRST sets:')
    for nt in list(nt_order)[:5]:
        print(f'  FIRST({nt}) = {sorted(first_sets.get(nt, set()))}')

    print('\n[SANITY CHECK] Sample FOLLOW sets (nullable only):')
    for nt in nullable[:5]:
        print(f'  FOLLOW({nt}) = {sorted(follow_sets.get(nt, set()))}')


if __name__ == '__main__':
    main()