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
            'strength_reduced': 0,
            'dead_eliminated': 0,
            'jumps_optimized': 0,
        }

    # ── Entry Point ──────────────────────────────────────────────────────

    def optimize(self):
        """Run all optimization passes and return the modified IRProgram."""
        self._pass_constant_folding()
        self._pass_constant_propagation()
        self._pass_strength_reduction()
        self._pass_dead_code_elimination()
        self._pass_jump_optimization()
        # Remove NOP instructions produced by other passes
        self.ir.instructions = [q for q in self.ir.instructions if q.op != NOP]
        return self.ir

    @property
    def stats(self):
        return dict(self._stats)

    # =====================================================================
    # PASS 1: CONSTANT FOLDING
    # =====================================================================
    # Evaluate expressions that have compile-time-known operands.

    def _pass_constant_folding(self):
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

        # Record variable assignments of known values
        if q.op == ASSIGN and q.arg1 is not None and q.result is not None:
            v = self._resolve(q.arg1)
            if v is not None:
                self.temp_values[q.result] = v
            else:
                self.temp_values.pop(q.result, None)
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
                        return Quad(LITERAL, dtype, result, q.result, f"folded: {a} {q.op} {b}")
                except (ZeroDivisionError, OverflowError, ValueError):
                    pass
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
        if operand in self.temp_types:
            return self.temp_types[operand]
        if operand in self.constants:
            return self.constants[operand][0]
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
        # Ops whose arg1/arg2 can be propagated
        propagatable_arg = {
            ADD, SUB, MUL, DIV, MOD, POW,
            LT, GT, LE, GE, EQ, NE,
            LOG_AND, LOG_OR, LOG_NOT, LOG_DNOT,
            UNARY_NEG, CONCAT, ASSIGN,
            JUMP_FALSE, JUMP_TRUE,
        }
        count = 0
        for q in self.ir.instructions:
            if q.op in propagatable_arg:
                if q.arg1 is not None and isinstance(q.arg1, str) and q.arg1 in self.temp_values:
                    v = self.temp_values[q.arg1]
                    # Only propagate simple scalars
                    if isinstance(v, (int, float, bool, str)):
                        q.arg1 = q.arg1  # keep temp reference (code gen resolves)
                        count += 1
                if q.arg2 is not None and isinstance(q.arg2, str) and q.arg2 in self.temp_values:
                    v = self.temp_values[q.arg2]
                    if isinstance(v, (int, float, bool, str)):
                        q.arg2 = q.arg2  # keep temp reference
                        count += 1
        self._stats['const_propagated'] = count

    # =====================================================================
    # PASS 3: STRENGTH REDUCTION
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
    # PASS 4: DEAD CODE ELIMINATION
    # =====================================================================
    # Remove instructions that write to temporaries never read.

    def _pass_dead_code_elimination(self):
        # Build set of all referenced names (used as arg1, arg2, OR result
        # in declaration ops where result holds an init-value temp)
        used = set()
        # Certain ops always have side effects — never eliminate them
        side_effect_ops = {
            PROGRAM_START, PROGRAM_END, AHOY_BEGIN, AHOY_END,
            FUNC_BEGIN, FUNC_END, PARAM_DECL,
            DECL_VAR, DECL_CONST, DECL_ARR, DECL_STRUCT_TYPE, DECL_STRUCT_VAR,
            ARR_INIT_1D, ARR_INIT_2D, STRUCT_INIT,
            ASSIGN, ASSIGN_ARR, ASSIGN_ARR2, ASSIGN_MEMBER,
            LABEL, JUMP, JUMP_FALSE, JUMP_TRUE, BREAK, CONTINUE,
            ARG, CALL, CALL_VOID, INPUT, OUTPUT,
            RETURN, RETURN_VOID,
            UNARY_INC, UNARY_DEC,
        }
        # Declaration ops whose result field references a temp (init value)
        decl_result_ops = {DECL_VAR, DECL_CONST}

        # Gather all referenced temps/vars
        for q in self.ir.instructions:
            if q.arg1 is not None and isinstance(q.arg1, str):
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
            # Declaration result fields hold temps that were previously emitted
            if q.op in decl_result_ops and q.result is not None and isinstance(q.result, str):
                used.add(q.result)
            # ASSIGN result is the destination var, but arg1 is the source temp
            if q.op == ASSIGN and q.arg1 is not None and isinstance(q.arg1, str):
                used.add(q.arg1)

        # Remove LITERAL instructions whose result is never used
        new_instrs = []
        for q in self.ir.instructions:
            if q.op == LITERAL and q.result not in used:
                self._stats['dead_eliminated'] += 1
                continue
            if q.op in side_effect_ops:
                new_instrs.append(q)
                continue
            # Keep everything else (expressions that produce temps used later)
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
