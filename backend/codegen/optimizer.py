# Called in: server.py — Optimisation phase, between IR generation and code generation
# Applies 6 transformation passes over the IRProgram to reduce instruction count and simplify expressions.

import math
from codegen.ir_instructions import (
    Quad, IRProgram,
    LITERAL, ASSIGN, NOP, LABEL, JUMP, JUMP_FALSE, JUMP_TRUE,
    ADD, SUB, MUL, DIV, MOD, POW,
    LT, GT, LE, GE, EQ, NE,
    LOG_AND, LOG_OR, LOG_NOT, LOG_DNOT,
    UNARY_NEG, UNARY_INC, UNARY_DEC,
    CONCAT,
    DECL_VAR, DECL_CONST, DECL_ARR,
    FUNC_BEGIN, FUNC_END, PARAM_DECL,
    PROGRAM_START, PROGRAM_END, AHOY_BEGIN, AHOY_END,
    LOAD_ARR, LOAD_ARR2, LOAD_MEMBER,
    ASSIGN_ARR, ASSIGN_ARR2, ASSIGN_MEMBER,
    ARR_INIT_1D, ARR_INIT_2D, STRUCT_INIT,
    INPUT, OUTPUT, CALL, CALL_VOID, ARG,
    RETURN, RETURN_VOID, BREAK, CONTINUE,
    DECL_STRUCT_TYPE, DECL_STRUCT_VAR,
    SCROLL_CHAR, COMPOUND_ASSIGN,
)


class IROptimizer:

    def __init__(self, ir_program: IRProgram):
        self.ir = ir_program
        self.constants = {}       # temp_name → (dtype, value)
        self.temp_values = {}     # temp_name → resolved value (for propagation)
        self.temp_types = {}      # temp_name → dtype
        self._stats = {
            'const_folded': 0,
            'const_propagated': 0,
            'copy_propagated': 0,
            'strength_reduced': 0,
            'dead_eliminated': 0,
            'jumps_optimized': 0,
        }

    # Entry point

    def optimize(self):
        # passes loop until fixpoint: each pass feeds the next
        changed = True
        while changed:
            before = len(self.ir.instructions)
            before_stats = dict(self._stats)

            self._pass_constant_folding()
            self._pass_constant_propagation()
            self._pass_copy_propagation()
            self._pass_strength_reduction()
            self._pass_dead_code_elimination()

            after_stats = dict(self._stats)
            changed = (
                len(self.ir.instructions) != before or
                any(after_stats[k] != before_stats[k] for k in after_stats)
            )

        # jump optimization is a single structural cleanup — run once at the end
        self._pass_jump_optimization()

        # remove NOP instructions produced by other passes
        self.ir.instructions = [q for q in self.ir.instructions if q.op != NOP]

        # sync locally-discovered types back into ir.temp_types for the code generator
        for temp, dtype in self.temp_types.items():
            if temp not in self.ir.temp_types and dtype:
                self.ir.temp_types[temp] = dtype

        return self.ir

    @property
    def stats(self):
        return dict(self._stats)

    # =======================
    # PASS 1: CONSTANT FOLDING
    # =======================
    # Evaluate expressions with compile-time-known operands.

    def _pass_constant_folding(self):
        # Pre-scan: find all variables modified after initial declaration
        # (loop counters, ASK targets, compound assigns, array/struct stores).
        # These must NOT be folded — their initial value is not their runtime value.
        self._mutable_vars = set()
        for q in self.ir.instructions:
            if q.op in (UNARY_INC, UNARY_DEC) and isinstance(q.arg1, str):
                self._mutable_vars.add(q.arg1)
            if q.op == ASSIGN and isinstance(q.result, str) and not q.result.startswith('_t'):
                self._mutable_vars.add(q.result)
            if q.op == COMPOUND_ASSIGN and isinstance(q.result, str):
                self._mutable_vars.add(q.result)
            if q.op == INPUT and q.arg2:
                for tgt in q.arg2:
                    if isinstance(tgt, dict) and 'var_name' in tgt:
                        self._mutable_vars.add(tgt['var_name'])
            if q.op in (ASSIGN_ARR, ASSIGN_ARR2, ASSIGN_MEMBER):
                if isinstance(q.arg1, str):
                    self._mutable_vars.add(q.arg1)

        changed = True
        while changed:
            changed = False
            new_instrs = []
            for q in self.ir.instructions:
                folded = self._try_fold(q)
                if folded is not q:
                    changed = True
                    self._stats['const_folded'] += 1
                new_instrs.append(folded)
            self.ir.instructions = new_instrs

    def _try_fold(self, q):
        # Record literal values
        if q.op == LITERAL:
            self.constants[q.result] = (q.arg1, q.arg2)
            self.temp_values[q.result] = q.arg2
            self.temp_types[q.result] = q.arg1
            return q

        # Record constant declarations
        if q.op == DECL_CONST and q.result is not None:
            v = self._resolve(q.result)
            if v is not None:
                self.constants[q.arg1] = (q.arg2, v)
                self.temp_values[q.arg1] = v
                self.temp_types[q.arg1] = q.arg2
            return q

        # Record variable assignments; skip mutable vars (loop counters etc.)
        if q.op == ASSIGN and q.arg1 is not None and q.result is not None:
            if hasattr(self, '_mutable_vars') and q.result in self._mutable_vars:
                self.temp_values.pop(q.result, None)
                self.constants.pop(q.result, None)
            else:
                v = self._resolve(q.arg1)
                if v is not None:
                    self.temp_values[q.result] = v
                else:
                    self.temp_values.pop(q.result, None)
            return q

        # DECL_VAR: skip mutable vars — initial value would be incorrectly frozen
        if q.op == DECL_VAR and q.arg1 is not None:
            if hasattr(self, '_mutable_vars') and q.arg1 in self._mutable_vars:
                self.temp_values.pop(q.arg1, None)
                self.constants.pop(q.arg1, None)
            return q

        # COMPOUND_ASSIGN invalidates the target's cached value
        if q.op == COMPOUND_ASSIGN and isinstance(q.result, str):
            self.temp_values.pop(q.result, None)
            self.constants.pop(q.result, None)
            return q

        # Fold arithmetic binary ops
        if q.op in (ADD, SUB, MUL, DIV, MOD, POW):
            a = self._resolve(q.arg1)
            b = self._resolve(q.arg2)
            if a is not None and b is not None:
                try:
                    result = self._compute_arith(q.op, a, b)
                    if result is not None:
                        dtype = self._result_dtype(q.arg1, q.arg2)
                        self.constants[q.result] = (dtype, result)
                        self.temp_values[q.result] = result
                        self.temp_types[q.result] = dtype
                        self.ir.temp_types[q.result] = dtype
                        return Quad(LITERAL, dtype, result, q.result, f"folded: {a} {q.op} {b}")
                except (ZeroDivisionError, OverflowError, ValueError):
                    pass
            # Cannot fold — still record inferred result type for the code generator
            if q.result is not None and q.result not in self.ir.temp_types:
                dtype = self._result_dtype(q.arg1, q.arg2)
                if dtype:
                    self.temp_types[q.result] = dtype
                    self.ir.temp_types[q.result] = dtype
            return q

        # Fold relational ops
        if q.op in (LT, GT, LE, GE, EQ, NE):
            a = self._resolve(q.arg1)
            b = self._resolve(q.arg2)
            if a is not None and b is not None:
                result = self._compute_rel(q.op, a, b)
                if result is not None:
                    self.constants[q.result] = ('BOOL', result)
                    self.temp_values[q.result] = result
                    return Quad(LITERAL, 'BOOL', result, q.result, f"folded: {a} {q.op} {b}")
            return q

        # Fold logical ops
        if q.op in (LOG_AND, LOG_OR):
            a = self._resolve(q.arg1)
            b = self._resolve(q.arg2)
            if a is not None and b is not None:
                if q.op == LOG_AND:
                    result = bool(a) and bool(b)
                else:
                    result = bool(a) or bool(b)
                self.constants[q.result] = ('BOOL', result)
                self.temp_values[q.result] = result
                return Quad(LITERAL, 'BOOL', result, q.result, f"folded logical")

        if q.op == LOG_NOT:
            a = self._resolve(q.arg1)
            if a is not None:
                result = not bool(a)
                self.constants[q.result] = ('BOOL', result)
                self.temp_values[q.result] = result
                return Quad(LITERAL, 'BOOL', result, q.result, "folded NOT")

        if q.op == LOG_DNOT:
            a = self._resolve(q.arg1)
            if a is not None:
                result = bool(a)  # double not = identity for booleans
                self.constants[q.result] = ('BOOL', result)
                self.temp_values[q.result] = result
                return Quad(LITERAL, 'BOOL', result, q.result, "folded DNOT")

        # Fold unary negation
        if q.op == UNARY_NEG:
            a = self._resolve(q.arg1)
            if a is not None and isinstance(a, (int, float)):
                result = -a
                dtype = self._get_type(q.arg1) or ('DIME' if isinstance(result, float) else 'COIN')
                self.constants[q.result] = (dtype, result)
                self.temp_values[q.result] = result
                return Quad(LITERAL, dtype, result, q.result, f"folded: -{a}")

        # Fold string concatenation
        if q.op == CONCAT:
            a = self._resolve(q.arg1)
            b = self._resolve(q.arg2)
            if a is not None and b is not None and isinstance(a, str) and isinstance(b, str):
                result = a + b
                self.constants[q.result] = ('SCROLL', result)
                self.temp_values[q.result] = result
                return Quad(LITERAL, 'SCROLL', result, q.result, "folded concat")

        return q

    def _resolve(self, operand):
        if operand is None:
            return None
        if isinstance(operand, (int, float, bool)):
            return operand
        if isinstance(operand, str):
            if operand in self.temp_values:
                return self.temp_values[operand]
            if operand in self.constants:
                return self.constants[operand][1]
        return None

    def _get_type(self, operand):
        if isinstance(operand, bool):  return 'BOOL'
        if isinstance(operand, int):   return 'COIN'
        if isinstance(operand, float): return 'DIME'
        if isinstance(operand, str):
            if operand in self.temp_types:
                return self.temp_types[operand]
            if operand in self.constants:
                return self.constants[operand][0]
            # fallback: types written by IR generator or a prior optimizer pass
            if operand in self.ir.temp_types:
                return self.ir.temp_types[operand]
        return None

    def _result_dtype(self, arg1, arg2):
        t1 = self._get_type(arg1)
        t2 = self._get_type(arg2)
        if t1 == 'DIME' or t2 == 'DIME':
            return 'DIME'
        return 'COIN'

    def _compute_arith(self, op, a, b):
        if op == ADD: return a + b
        if op == SUB: return a - b
        if op == MUL: return a * b
        if op == DIV:
            if b == 0:
                return None  # don't fold division by zero
            if isinstance(a, int) and isinstance(b, int):
                return a // b  # integer division for COIN/COIN
            return a / b
        if op == MOD:
            if b == 0:
                return None
            return a % b
        if op == POW:
            result = a ** b
            # guard against extremely large results
            if isinstance(result, (int, float)) and not math.isinf(result):
                return result
            return None
        return None

    def _compute_rel(self, op, a, b):
        try:
            if op == LT: return a < b
            if op == GT: return a > b
            if op == LE: return a <= b
            if op == GE: return a >= b
            if op == EQ: return a == b
            if op == NE: return a != b
        except TypeError:
            return None
        return None

    # =======================
    # PASS 2: CONSTANT PROPAGATION
    # =======================
    # Replace temp references with their known compile-time literal values.

    def _pass_constant_propagation(self):
        propagatable_ops = {
            ADD, SUB, MUL, DIV, MOD, POW,
            LT, GT, LE, GE, EQ, NE,
            LOG_AND, LOG_OR, LOG_NOT, LOG_DNOT,
            UNARY_NEG, CONCAT, ASSIGN,
            JUMP_FALSE, JUMP_TRUE,
        }
        count = 0
        for q in self.ir.instructions:
            if q.op == ASSIGN and isinstance(q.result, str):
                self.temp_values.pop(q.result, None)

            # UNARY_INC/DEC target is arg1 (not result); invalidate or loop conditions fold incorrectly
            if q.op in (UNARY_INC, UNARY_DEC) and isinstance(q.arg1, str):
                self.temp_values.pop(q.arg1, None)

            # INPUT writes at runtime — invalidate cached values
            if q.op == INPUT:
                for tgt in (q.arg2 or []):
                    if isinstance(tgt, dict) and tgt.get('target_kind') == 'var':
                        self.temp_values.pop(tgt['var_name'], None)

            # COMPOUND_ASSIGN modifies in place — invalidate
            if q.op == COMPOUND_ASSIGN and isinstance(q.result, str):
                self.temp_values.pop(q.result, None)

            # array/struct stores mutate the container — invalidate
            if q.op in (ASSIGN_ARR, ASSIGN_ARR2, ASSIGN_MEMBER):
                if isinstance(q.arg1, str):
                    self.temp_values.pop(q.arg1, None)

            if q.op not in propagatable_ops:
                continue

            if isinstance(q.arg1, str) and q.arg1 in self.temp_values:
                # never propagate values for user variables that are mutated at runtime
                if not (hasattr(self, '_mutable_vars') and q.arg1 in self._mutable_vars):
                    v = self.temp_values[q.arg1]
                    if isinstance(v, (int, float, bool, str)):
                        q.arg1 = v
                        count += 1

            if isinstance(q.arg2, str) and q.arg2 in self.temp_values:
                if not (hasattr(self, '_mutable_vars') and q.arg2 in self._mutable_vars):
                    v = self.temp_values[q.arg2]
                    if isinstance(v, (int, float, bool, str)):
                        q.arg2 = v
                        count += 1

        self._stats['const_propagated'] += count

    # =======================
    # PASS 3: COPY PROPAGATION
    # =======================
    # Replace reads of a copied temp with the original source directly.

    def _pass_copy_propagation(self):
        # copy_map: dest → source  (e.g. '_t3' → '_t1')
        copy_map = {}
        count = 0

        write_result_ops = {
            ADD, SUB, MUL, DIV, MOD, POW,
            LT, GT, LE, GE, EQ, NE,
            LOG_AND, LOG_OR, LOG_NOT, LOG_DNOT,
            UNARY_NEG, CONCAT, LITERAL,
            LOAD_ARR, LOAD_ARR2, LOAD_MEMBER, SCROLL_CHAR,
            CALL,
        }

        def _resolve_copy(name):
            # chase copy chain: a→b→c returns c
            seen = set()
            while name in copy_map and name not in seen:
                seen.add(name)
                name = copy_map[name]
            return name

        for q in self.ir.instructions:
            # Record new copy relationships
            if q.op == ASSIGN and isinstance(q.arg1, str) and isinstance(q.result, str):
                src = _resolve_copy(q.arg1)
                if q.result.startswith('_t'):
                    copy_map[q.result] = src

            # Invalidate stale copies when a variable is written
            if q.result is not None and isinstance(q.result, str):
                if q.op in write_result_ops:
                    copy_map.pop(q.result, None)
                    stale = [k for k, v in copy_map.items() if v == q.result]
                    for k in stale:
                        del copy_map[k]

            if q.op in (ASSIGN, ASSIGN_ARR, ASSIGN_ARR2, ASSIGN_MEMBER,
                        UNARY_INC, UNARY_DEC):
                if isinstance(q.result, str):
                    stale = [k for k, v in copy_map.items()
                             if k == q.result or v == q.result]
                    for k in stale:
                        del copy_map[k]

            # UNARY_INC/DEC target is arg1 (result is None) — invalidate both sides
            if q.op in (UNARY_INC, UNARY_DEC) and isinstance(q.arg1, str):
                stale = [k for k, v in copy_map.items()
                         if k == q.arg1 or v == q.arg1]
                for k in stale:
                    del copy_map[k]

            # COMPOUND_ASSIGN modifies in place — invalidate
            if q.op == COMPOUND_ASSIGN and isinstance(q.result, str):
                stale = [k for k, v in copy_map.items()
                         if k == q.result or v == q.result]
                for k in stale:
                    del copy_map[k]

            # INPUT writes at runtime — invalidate
            if q.op == INPUT and q.arg2:
                for tgt in q.arg2:
                    if isinstance(tgt, dict) and 'var_name' in tgt:
                        vname = tgt['var_name']
                        stale = [k for k, v in copy_map.items()
                                 if k == vname or v == vname]
                        for k in stale:
                            del copy_map[k]

            # Substitute copies in arg1/arg2
            if isinstance(q.arg1, str) and q.arg1 in copy_map:
                new_val = copy_map[q.arg1]
                if new_val != q.arg1:
                    q.arg1 = new_val
                    count += 1

            if isinstance(q.arg2, str) and q.arg2 in copy_map:
                new_val = copy_map[q.arg2]
                if new_val != q.arg2:
                    q.arg2 = new_val
                    count += 1

        self._stats['copy_propagated'] += count

    # =======================
    # PASS 4: STRENGTH REDUCTION
    # =======================
    # Replace expensive operations with cheaper equivalents.

    def _pass_strength_reduction(self):
        new_instrs = []
        for q in self.ir.instructions:
            reduced = self._try_reduce(q)
            new_instrs.append(reduced)
        self.ir.instructions = new_instrs

    def _try_reduce(self, q):
        # x ** 2 → x * x
        if q.op == POW:
            b = self._resolve(q.arg2)
            if b == 2:
                self._stats['strength_reduced'] += 1
                return Quad(MUL, q.arg1, q.arg1, q.result,
                            "strength reduction: x^2 → x*x")
            if b == 1:
                self._stats['strength_reduced'] += 1
                return Quad(ASSIGN, q.arg1, None, q.result,
                            "strength reduction: x^1 → x")
            if b == 0:
                self._stats['strength_reduced'] += 1
                return Quad(LITERAL, 'COIN', 1, q.result,
                            "strength reduction: x^0 → 1")

        # x * 2 → x + x
        if q.op == MUL:
            b = self._resolve(q.arg2)
            a = self._resolve(q.arg1)
            if b == 2:
                self._stats['strength_reduced'] += 1
                return Quad(ADD, q.arg1, q.arg1, q.result,
                            "strength reduction: x*2 → x+x")
            if a == 2:
                self._stats['strength_reduced'] += 1
                return Quad(ADD, q.arg2, q.arg2, q.result,
                            "strength reduction: 2*x → x+x")
            # x * 1 → x
            if b == 1:
                self._stats['strength_reduced'] += 1
                return Quad(ASSIGN, q.arg1, None, q.result,
                            "strength reduction: x*1 → x")
            if a == 1:
                self._stats['strength_reduced'] += 1
                return Quad(ASSIGN, q.arg2, None, q.result,
                            "strength reduction: 1*x → x")
            # x * 0 → 0
            if b == 0 or a == 0:
                self._stats['strength_reduced'] += 1
                return Quad(LITERAL, 'COIN', 0, q.result,
                            "strength reduction: x*0 → 0")

        # x + 0 → x, x - 0 → x
        if q.op == ADD:
            b = self._resolve(q.arg2)
            a = self._resolve(q.arg1)
            if b == 0:
                self._stats['strength_reduced'] += 1
                return Quad(ASSIGN, q.arg1, None, q.result, "x+0 → x")
            if a == 0:
                self._stats['strength_reduced'] += 1
                return Quad(ASSIGN, q.arg2, None, q.result, "0+x → x")

        if q.op == SUB:
            b = self._resolve(q.arg2)
            if b == 0:
                self._stats['strength_reduced'] += 1
                return Quad(ASSIGN, q.arg1, None, q.result, "x-0 → x")

        # x / 1 → x
        if q.op == DIV:
            b = self._resolve(q.arg2)
            if b == 1:
                self._stats['strength_reduced'] += 1
                return Quad(ASSIGN, q.arg1, None, q.result, "x/1 → x")

        return q

    # =======================
    # PASS 5: DEAD CODE ELIMINATION
    # =======================
    # Remove instructions whose results are never read downstream.

    def _pass_dead_code_elimination(self):
        # always keep — observable side effects beyond writing a result temp
        side_effect_ops = {
            PROGRAM_START, PROGRAM_END, AHOY_BEGIN, AHOY_END,
            FUNC_BEGIN, FUNC_END, PARAM_DECL,
            DECL_VAR, DECL_CONST, DECL_ARR, DECL_STRUCT_TYPE, DECL_STRUCT_VAR,
            ARR_INIT_1D, ARR_INIT_2D, STRUCT_INIT,
            ASSIGN, ASSIGN_ARR, ASSIGN_ARR2, ASSIGN_MEMBER,
            LABEL, JUMP, JUMP_FALSE, JUMP_TRUE, BREAK, CONTINUE,
            ARG, CALL_VOID, INPUT, OUTPUT,
            RETURN, RETURN_VOID,
            UNARY_INC, UNARY_DEC,
            COMPOUND_ASSIGN,
        }

        # result holds an init-value temp consumed by the declaration itself
        decl_result_ops = {DECL_VAR, DECL_CONST}

        # Build the used-temps set
        used = set()
        for q in self.ir.instructions:
            if isinstance(q.arg1, str):
                used.add(q.arg1)
            if q.arg2 is not None:
                if isinstance(q.arg2, str):
                    used.add(q.arg2)
                elif isinstance(q.arg2, tuple):
                    for item in q.arg2:
                        if isinstance(item, str):
                            used.add(item)
                elif isinstance(q.arg2, list):
                    for item in q.arg2:
                        if isinstance(item, str):
                            used.add(item)
                        elif isinstance(item, list):
                            for sub in item:
                                if isinstance(sub, str):
                                    used.add(sub)
                        elif isinstance(item, dict):
                            for v in item.values():
                                if isinstance(v, str):
                                    used.add(v)
                elif isinstance(q.arg2, dict):
                    for v in q.arg2.values():
                        if isinstance(v, str):
                            used.add(v)
            if q.op in decl_result_ops and isinstance(q.result, str):
                used.add(q.result)
            # store ops: result holds the VALUE temp being stored — it is an input
            if q.op in (ASSIGN_ARR, ASSIGN_ARR2, ASSIGN_MEMBER):
                if isinstance(q.result, str):
                    used.add(q.result)

        # Eliminate dead instructions
        pure_expr_ops = {
            LITERAL, ADD, SUB, MUL, DIV, MOD, POW,
            LT, GT, LE, GE, EQ, NE,
            LOG_AND, LOG_OR, LOG_NOT, LOG_DNOT,
            UNARY_NEG, CONCAT, SCROLL_CHAR,
            LOAD_ARR, LOAD_ARR2, LOAD_MEMBER,
            CALL,  # CALL result may be unused (void-use pattern)
        }

        new_instrs = []
        for q in self.ir.instructions:
            if q.op in side_effect_ops:
                new_instrs.append(q)
                continue
            if q.op in pure_expr_ops:
                if q.result is not None and q.result not in used:
                    self._stats['dead_eliminated'] += 1
                    continue
            new_instrs.append(q)

        self.ir.instructions = new_instrs

    # =======================
    # PASS 6: JUMP OPTIMIZATION
    # =======================
    # Remove jumps that target the immediately following label.

    def _pass_jump_optimization(self):
        instrs = self.ir.instructions
        new_instrs = []
        i = 0
        while i < len(instrs):
            q = instrs[i]
            if q.op == JUMP and i + 1 < len(instrs):
                nxt = instrs[i + 1]
                if nxt.op == LABEL and nxt.arg1 == q.arg1:
                    # jump to the next instruction — eliminate
                    self._stats['jumps_optimized'] += 1
                    i += 1
                    continue
            new_instrs.append(q)
            i += 1
        self.ir.instructions = new_instrs
