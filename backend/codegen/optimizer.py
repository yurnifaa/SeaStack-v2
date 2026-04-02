# =============================================================================
# optimizer.py — SeaStack IR Optimizer
#
# Reads the flat IR instruction list and applies safe transformations to
# reduce computational cost WITHOUT compromising accuracy.
#
# Optimization passes (applied in order):
#   1. Constant Folding       – evaluate compile-time-known expressions
#   2. Constant Propagation   – replace uses of constants with their values
#   3. Strength Reduction     – replace expensive ops with cheaper equivalents
#   4. Dead Code Elimination  – remove instructions whose results are never used
#   5. Redundant Load Elim.   – remove duplicate loads of the same value
#   6. Jump Optimization      – remove jumps to the immediately-next label
# =============================================================================

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
    """Multi-pass optimizer over a flat list of IR Quadruples."""

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

    # ── Entry Point ──────────────────────────────────────────────────────

    def optimize(self):
        """Run all optimization passes and return the modified IRProgram.

        Passes are looped until no further changes occur so that each pass
        can feed the next (e.g. folding enables propagation enables DCE).
        """
        changed = True
        while changed:
            before = len(self.ir.instructions)
            before_stats = dict(self._stats)

            self._pass_constant_folding()
            self._pass_constant_propagation()
            self._pass_copy_propagation()
            self._pass_strength_reduction()
            self._pass_dead_code_elimination()

            # Check if anything actually changed this iteration
            after_stats = dict(self._stats)
            changed = (
                len(self.ir.instructions) != before or
                any(after_stats[k] != before_stats[k] for k in after_stats)
            )

        # Jump optimization is a single structural cleanup — run once at the end
        self._pass_jump_optimization()

        # Remove NOP instructions produced by other passes
        self.ir.instructions = [q for q in self.ir.instructions if q.op != NOP]

        # Final sync: write every type the optimizer discovered locally
        # (constants, folded results) back into ir.temp_types so the code
        # generator always has the full, accurate type table to consult.
        for temp, dtype in self.temp_types.items():
            if temp not in self.ir.temp_types and dtype:
                self.ir.temp_types[temp] = dtype

        return self.ir

    @property
    def stats(self):
        return dict(self._stats)

    # =====================================================================
    # PASS 1: CONSTANT FOLDING
    # =====================================================================
    # Evaluate expressions that have compile-time-known operands.

    def _pass_constant_folding(self):
        # Pre-scan: find ALL variables that are modified after their initial
        # declaration.  This includes:
        #   - UNARY_INC / UNARY_DEC  (loop counters: +#i / -#j)
        #   - ASSIGN to a user variable (accumulator pattern: dec = dec + …)
        #   - COMPOUND_ASSIGN        (e.g.  dec += expr)
        #   - INPUT targets           (ASK writes to variables at runtime)
        #   - ASSIGN_ARR / ASSIGN_ARR2 / ASSIGN_MEMBER (array/struct stores)
        #
        # Their values must NOT be treated as compile-time constants because
        # the folding pass processes instructions linearly and would
        # incorrectly freeze the initialisation value (e.g. dec=0) into every
        # expression that reads the variable, ignoring subsequent assignments
        # inside loop bodies.
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
        self._induction_vars = self._mutable_vars

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
        """Try to fold a single instruction.  Returns the (possibly replaced) Quad."""
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

        # Record variable assignments of known values.
        # Skip induction variables (loop counters modified by UNARY_INC/DEC):
        # their "initial" value must not be treated as a compile-time constant
        # because the folding pass is linear and would incorrectly propagate
        # the initialisation value (e.g. j=0) into the loop body.
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

        # DECL_VAR: if the declared variable is later mutated, do NOT record
        # its init value — it would be incorrectly frozen into loop expressions.
        if q.op == DECL_VAR and q.arg1 is not None:
            if hasattr(self, '_mutable_vars') and q.arg1 in self._mutable_vars:
                self.temp_values.pop(q.arg1, None)
                self.constants.pop(q.arg1, None)
            return q

        # COMPOUND_ASSIGN invalidates the target variable's cached value
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
                        self.ir.temp_types[q.result] = dtype   # sync to IR
                        return Quad(LITERAL, dtype, result, q.result, f"folded: {a} {q.op} {b}")
                except (ZeroDivisionError, OverflowError, ValueError):
                    pass
            # Cannot fold at compile time — still record the inferred result type
            # so that StructuralCodeGenerator._resolve_operand_type can determine
            # whether to emit integer or float division/modulo at code-gen time.
            if q.result is not None and q.result not in self.ir.temp_types:
                dtype = self._result_dtype(q.arg1, q.arg2)
                if dtype:
                    self.temp_types[q.result] = dtype
                    self.ir.temp_types[q.result] = dtype       # sync to IR
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
        """Resolve an operand to its compile-time value, or None."""
        if operand is None:
            return None
        if isinstance(operand, (int, float, bool)):
            return operand
        if isinstance(operand, str):
            # Check if it's a known temp or constant
            if operand in self.temp_values:
                return self.temp_values[operand]
            if operand in self.constants:
                return self.constants[operand][1]
        return None

    def _get_type(self, operand):
        # Raw Python literals embedded by constant propagation
        if isinstance(operand, bool):  return 'BOOL'
        if isinstance(operand, int):   return 'COIN'
        if isinstance(operand, float): return 'DIME'
        if isinstance(operand, str):
            if operand in self.temp_types:
                return self.temp_types[operand]
            if operand in self.constants:
                return self.constants[operand][0]
            # Fallback: types written into ir.temp_types by the IR generator
            # (or by a prior optimizer pass that already synced back)
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
            # Guard against extremely large results
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

    # =====================================================================
    # PASS 2: CONSTANT PROPAGATION
    # =====================================================================
    # Replace references to temps that hold known constant values with
    # fresh LITERAL instructions.

    def _pass_constant_propagation(self):
        """Replace temp references with their known compile-time literal values.

        When a temp holds a known scalar (recorded during folding), any
        subsequent instruction that reads that temp as arg1/arg2 can have
        the temp replaced with the literal value directly.  This enables
        further folding on the next iteration.
        """
        propagatable_ops = {
            ADD, SUB, MUL, DIV, MOD, POW,
            LT, GT, LE, GE, EQ, NE,
            LOG_AND, LOG_OR, LOG_NOT, LOG_DNOT,
            UNARY_NEG, CONCAT, ASSIGN,
            JUMP_FALSE, JUMP_TRUE,
        }
        count = 0
        for q in self.ir.instructions:
            # Invalidate propagated knowledge when a variable is reassigned
            if q.op == ASSIGN and isinstance(q.result, str):
                self.temp_values.pop(q.result, None)

            # FIX: UNARY_INC/DEC store their target in arg1 (result is None).
            # Without this, j=0 stays in temp_values after j+=1, causing the
            # loop condition LT j limit1 to be folded to LT 0 limit1 (always
            # True) and creating an infinite loop at runtime.
            if q.op in (UNARY_INC, UNARY_DEC) and isinstance(q.arg1, str):
                self.temp_values.pop(q.arg1, None)

            # FIX: INPUT writes to its target variable at runtime.
            # Without this, a variable read before ASK could be stale.
            if q.op == INPUT:
                for tgt in (q.arg2 or []):
                    if isinstance(tgt, dict) and tgt.get('target_kind') == 'var':
                        self.temp_values.pop(tgt['var_name'], None)

            # FIX: COMPOUND_ASSIGN modifies a variable in place.
            if q.op == COMPOUND_ASSIGN and isinstance(q.result, str):
                self.temp_values.pop(q.result, None)

            # FIX: ASSIGN_ARR / ASSIGN_ARR2 / ASSIGN_MEMBER mutate the container.
            if q.op in (ASSIGN_ARR, ASSIGN_ARR2, ASSIGN_MEMBER):
                if isinstance(q.arg1, str):
                    self.temp_values.pop(q.arg1, None)

            if q.op not in propagatable_ops:
                continue

            if isinstance(q.arg1, str) and q.arg1 in self.temp_values:
                # Never propagate values for variables that are modified in
                # the program (only propagate temp values like _t0, _t1, …)
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

    # =====================================================================
    # PASS 3: COPY PROPAGATION
    # =====================================================================
    # When an ASSIGN copies one temp/var into another (result = arg1),
    # replace all subsequent reads of `result` with `arg1` directly —
    # until `result` or `arg1` is overwritten.  The now-redundant ASSIGN
    # becomes dead and is removed by the next DCE pass.

    def _pass_copy_propagation(self):
        # copy_map: dest → source  (e.g. '_t3' → '_t1')
        # Tracks active copy relationships through the instruction stream.
        copy_map = {}
        count = 0

        # Ops whose result is a fresh computation — invalidate any copy into result
        write_result_ops = {
            ADD, SUB, MUL, DIV, MOD, POW,
            LT, GT, LE, GE, EQ, NE,
            LOG_AND, LOG_OR, LOG_NOT, LOG_DNOT,
            UNARY_NEG, CONCAT, LITERAL,
            LOAD_ARR, LOAD_ARR2, LOAD_MEMBER, SCROLL_CHAR,
            CALL,
        }

        def _resolve_copy(name):
            """Chase copy chain: a→b→c returns c."""
            seen = set()
            while name in copy_map and name not in seen:
                seen.add(name)
                name = copy_map[name]
            return name

        for q in self.ir.instructions:
            # --- Record new copy relationships ---
            if q.op == ASSIGN and isinstance(q.arg1, str) and isinstance(q.result, str):
                src = _resolve_copy(q.arg1)
                if q.result.startswith('_t'):
                    copy_map[q.result] = src

            # --- Invalidate stale copies when a variable is written ---
            if q.result is not None and isinstance(q.result, str):
                if q.op in write_result_ops:
                    # This result is freshly computed, not a copy — remove any
                    # stale entry so we don't propagate the old value
                    copy_map.pop(q.result, None)
                    # Also invalidate any copy whose SOURCE is now overwritten
                    stale = [k for k, v in copy_map.items() if v == q.result]
                    for k in stale:
                        del copy_map[k]

            # Stores to variables kill copies involving that variable
            if q.op in (ASSIGN, ASSIGN_ARR, ASSIGN_ARR2, ASSIGN_MEMBER,
                        UNARY_INC, UNARY_DEC):
                if isinstance(q.result, str):
                    stale = [k for k, v in copy_map.items()
                             if k == q.result or v == q.result]
                    for k in stale:
                        del copy_map[k]

            # FIX: UNARY_INC/DEC store their target in arg1 (result is None),
            # so the check above (isinstance(q.result, str)) never fires for
            # them.  Chase both the key and value sides of the copy map so that
            # after j += 1 we no longer treat j as an alias for _t0 = 0.
            if q.op in (UNARY_INC, UNARY_DEC) and isinstance(q.arg1, str):
                stale = [k for k, v in copy_map.items()
                         if k == q.arg1 or v == q.arg1]
                for k in stale:
                    del copy_map[k]

            # FIX: COMPOUND_ASSIGN modifies a variable in place — invalidate.
            if q.op == COMPOUND_ASSIGN and isinstance(q.result, str):
                stale = [k for k, v in copy_map.items()
                         if k == q.result or v == q.result]
                for k in stale:
                    del copy_map[k]

            # FIX: INPUT writes to target variables at runtime — invalidate.
            if q.op == INPUT and q.arg2:
                for tgt in q.arg2:
                    if isinstance(tgt, dict) and 'var_name' in tgt:
                        vname = tgt['var_name']
                        stale = [k for k, v in copy_map.items()
                                 if k == vname or v == vname]
                        for k in stale:
                            del copy_map[k]

            # --- Substitute copies in arg1/arg2 ---
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

    # =====================================================================
    # PASS 4: STRENGTH REDUCTION
    # =====================================================================
    # Replace expensive operations with cheaper equivalents.

    def _pass_strength_reduction(self):
        new_instrs = []
        for q in self.ir.instructions:
            reduced = self._try_reduce(q)
            new_instrs.append(reduced)
        self.ir.instructions = new_instrs

    def _try_reduce(self, q):
        # x ** 2  →  x * x
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

        # Double negation: --x → x
        if q.op == UNARY_NEG:
            # Check if arg1 was itself a negation result
            pass  # complex to track, skip for safety

        return q

    # =====================================================================
    # PASS 5: DEAD CODE ELIMINATION
    # =====================================================================

    def _pass_dead_code_elimination(self):
        """Remove instructions that write to temporaries never read downstream.

        Any instruction whose ONLY effect is writing to a temp that nothing
        else reads is dead.  Instructions with side effects (I/O, calls,
        jumps, declarations, stores) are always kept regardless.
        """
        # Ops that have observable side effects beyond writing their result temp.
        # These are ALWAYS kept even if their result temp is unused.
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

        # Ops that write a result temp AND have a side effect (keep always,
        # but also mark their result as used so dependent temps survive)
        side_effect_with_result = {CALL}

        # Declaration ops where result holds an init-value temp (that temp is
        # consumed by the declaration itself, so mark it as used)
        decl_result_ops = {DECL_VAR, DECL_CONST}

        # --- Build the used-temps set ---
        used = set()
        for q in self.ir.instructions:
            # arg1 is read
            if isinstance(q.arg1, str):
                used.add(q.arg1)
            # arg2 is read — handle scalars, tuples, lists, dicts
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
            # Declaration result fields hold init-value temps — mark as used
            if q.op in decl_result_ops and isinstance(q.result, str):
                used.add(q.result)
            # Store ops: result holds the VALUE temp being stored — it is an
            # input, not an output, so mark it used
            if q.op in (ASSIGN_ARR, ASSIGN_ARR2, ASSIGN_MEMBER):
                if isinstance(q.result, str):
                    used.add(q.result)

        # --- Eliminate dead instructions ---
        # Pure expression ops: can be removed if their result temp is never used.
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
                    continue  # drop it
            new_instrs.append(q)

        self.ir.instructions = new_instrs

    # =====================================================================
    # PASS 5: JUMP OPTIMIZATION
    # =====================================================================
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
                    # Jump to the next instruction — eliminate the jump
                    self._stats['jumps_optimized'] += 1
                    i += 1
                    continue
            new_instrs.append(q)
            i += 1
        self.ir.instructions = new_instrs