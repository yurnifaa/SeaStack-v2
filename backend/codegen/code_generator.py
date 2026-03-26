# =============================================================================
# code_generator.py — SeaStack Code Generator (Optimized IR → Python)
#
# Walks the optimized IR instruction list and emits clean, executable
# Python code as a string.  The generated code can be exec()'d to run
# the SeaStack program.
#
# SeaStack type mapping:
#   COIN   → int          DIME  → float       PARCH  → str (1 char)
#   SCROLL → str          BOOL  → bool        ABYSS  → None (void)
#
# SeaStack escape sequences:
#   PARCH:  \s→'  \n→\n  \t→\t  \0→\0  \\→\\
#   SCROLL: \d→"  \n→\n  \t→\t  \0→\0  \\→\\
# =============================================================================

import re
from codegen.ir_instructions import (
    IRProgram, Quad,
    PROGRAM_START, PROGRAM_END, FUNC_BEGIN, FUNC_END, PARAM_DECL,
    AHOY_BEGIN, AHOY_END,
    DECL_VAR, DECL_CONST, DECL_ARR, DECL_STRUCT_TYPE, DECL_STRUCT_VAR,
    ARR_INIT_1D, ARR_INIT_2D, STRUCT_INIT,
    ASSIGN, ASSIGN_ARR, ASSIGN_ARR2, ASSIGN_MEMBER,
    ADD, SUB, MUL, DIV, MOD, POW,
    LT, GT, LE, GE, EQ, NE,
    LOG_AND, LOG_OR, LOG_NOT, LOG_DNOT,
    UNARY_NEG, UNARY_INC, UNARY_DEC,
    CONCAT, SCROLL_CHAR,
    LOAD_ARR, LOAD_ARR2, LOAD_MEMBER,
    LABEL, JUMP, JUMP_FALSE, JUMP_TRUE, BREAK, CONTINUE,
    ARG, CALL, CALL_VOID, RETURN, RETURN_VOID,
    INPUT, OUTPUT, NOP, LITERAL, COMMENT,
    COMPOUND_ASSIGN,
)


# ─── SeaStack escape conversion ─────────────────────────────────────────────

def _convert_parch_escapes(raw):
    """Convert SeaStack PARCH escape sequences to Python equivalents."""
    if raw is None:
        return "''"
    s = str(raw)
    # Remove surrounding single quotes if present
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        s = s[1:-1]
    s = s.replace('\\\\', '\x00BACKSLASH\x00')
    s = s.replace('\\s', "'")
    s = s.replace('\\n', '\n')
    s = s.replace('\\t', '\t')
    s = s.replace('\\0', '\0')
    s = s.replace('\x00BACKSLASH\x00', '\\')
    return s


def _convert_scroll_escapes(raw):
    """Convert SeaStack SCROLL escape sequences to Python equivalents."""
    if raw is None:
        return '""'
    s = str(raw)
    # Remove surrounding double quotes if present
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    s = s.replace('\\\\', '\x00BACKSLASH\x00')
    s = s.replace('\\d', '"')
    s = s.replace('\\n', '\n')
    s = s.replace('\\t', '\t')
    s = s.replace('\\0', '\0')
    s = s.replace('\x00BACKSLASH\x00', '\\')
    return s


def _format_spec_to_python(fmt_str):
    """Convert SeaStack format specifiers in a SCROLL literal to Python
    format-string placeholders.

    Input:  'Hello %S, you are %C years old\\n'
    Output: ('Hello {}, you are {} years old\\n', ['SCROLL', 'COIN'])
    """
    raw = _convert_scroll_escapes(fmt_str)
    specs = []
    spec_map = {'C': 'COIN', 'D': 'DIME', 'P': 'PARCH', 'S': 'SCROLL', 'B': 'BOOL'}

    def replacer(m):
        ch = m.group(1)
        specs.append(spec_map.get(ch, 'SCROLL'))
        return '{}'

    converted = re.sub(r'%([CDPSB])', replacer, raw)
    return converted, specs


# ─── Default values ──────────────────────────────────────────────────────────

_DEFAULT_VALUES = {
    'COIN':   '0',
    'DIME':   '0.0',
    'PARCH':  "'\\x00'",  # SeaStack default: null char  '\x00'
    'SCROLL': '"\\x00"',  # SeaStack default: null string "\x00"
    'BOOL':   'False',    # SeaStack NAY
}

_INPUT_CONVERTERS = {
    'COIN': 'int',
    'DIME': 'float',
    'PARCH': 'str',
    'SCROLL': 'str',
    'BOOL': '_ss_bool_input',
}


# ─── Code Generator ─────────────────────────────────────────────────────────

class CodeGenerator:
    """Translate optimized IR quadruples into executable Python source code."""

    def __init__(self, ir_program: IRProgram):
        self.ir = ir_program
        self._lines = []          # collected Python source lines
        self._indent = 0          # current indentation level
        self._temps = {}          # temp_name → Python expression string
        self._arg_stack = []      # pushed ARG values for upcoming CALL
        self._var_types = {}      # var_name → dtype
        self._const_names = set() # names declared as LOCKE

    # ── Entry ────────────────────────────────────────────────────────────

    def generate(self):
        """Generate and return Python source code as a string."""
        self._emit_runtime_preamble()
        self._walk_instructions()
        return '\n'.join(self._lines)

    # ── Emit helpers ─────────────────────────────────────────────────────

    def _emit(self, line):
        self._lines.append('    ' * self._indent + line)

    def _emit_blank(self):
        self._lines.append('')

    def _indent_inc(self):
        self._indent += 1

    def _indent_dec(self):
        self._indent = max(0, self._indent - 1)

    def _val(self, operand):
        """Resolve an operand to its Python expression string."""
        if operand is None:
            return 'None'
        if isinstance(operand, bool):
            return 'True' if operand else 'False'
        if isinstance(operand, int):
            return str(operand)
        if isinstance(operand, float):
            return repr(operand)
        if isinstance(operand, str):
            if operand in self._temps:
                return self._temps[operand]
            # It's a variable name — return as-is
            return self._sanitize_name(operand)
        return repr(operand)

    def _sanitize_name(self, name):
        """Ensure a SeaStack identifier is a valid Python identifier."""
        # SeaStack identifiers are lowercase + digits + underscores, already Python-safe
        # But guard against Python reserved words
        py_reserved = {
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else',
            'except', 'finally', 'for', 'from', 'global', 'if', 'import',
            'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise',
            'return', 'try', 'while', 'with', 'yield',
        }
        if name in py_reserved:
            return f'_ss_{name}'
        return name

    def _python_literal(self, dtype, value):
        """Convert a SeaStack literal to its Python representation."""
        if dtype == 'COIN':
            return str(int(value))
        elif dtype == 'DIME':
            f = float(value)
            s = repr(f)
            # Guarantee a decimal point so whole numbers display as e.g. 5.0
            if '.' not in s and 'e' not in s and 'n' not in s:
                s += '.0'
            return s
        elif dtype == 'BOOL':
            return 'True' if value else 'False'
        elif dtype == 'PARCH':
            converted = _convert_parch_escapes(value)
            return repr(converted)
        elif dtype == 'SCROLL':
            converted = _convert_scroll_escapes(value)
            return repr(converted)
        return repr(value)

    # ── Runtime Preamble ─────────────────────────────────────────────────

    def _emit_runtime_preamble(self):
        """Emit Python helper functions needed at runtime."""
        self._emit("# === SeaStack Generated Python Code ===")
        self._emit("import sys")
        self._emit_blank()
        self._emit("def _ss_bool_input(s):")
        self._indent_inc()
        self._emit("s = s.strip()")
        self._emit("if s == 'AYE': return True")
        self._emit("if s == 'NAY': return False")
        self._emit("raise ValueError(f'Expected AYE or NAY, got {s!r}')")
        self._indent_dec()
        self._emit_blank()
        self._emit("def _ss_make_array(dims, default=None):")
        self._indent_inc()
        self._emit("if len(dims) == 1:")
        self._indent_inc()
        self._emit("return [default] * dims[0]")
        self._indent_dec()
        self._emit("return [[default] * dims[1] for _ in range(dims[0])]")
        self._indent_dec()
        self._emit_blank()
        self._emit("def _ss_display(val):")
        self._indent_inc()
        self._emit("if isinstance(val, bool): return 'AYE' if val else 'NAY'")
        self._emit("return str(val)")
        self._indent_dec()
        self._emit_blank()
        # SCROLL character access: index at len(s) returns the SeaStack null
        # terminator '\x00', matching the rule that the char immediately after
        # the last character of a SCROLL string is always '\x00'.
        self._emit("def _ss_scroll_char(s, idx):")
        self._indent_inc()
        self._emit("if idx == len(s): return '\\x00'")
        self._emit("return s[idx]")
        self._indent_dec()
        self._emit_blank()

    # ── Instruction Walker ───────────────────────────────────────────────

    def _walk_instructions(self):
        instrs = self.ir.instructions
        i = 0
        while i < len(instrs):
            q = instrs[i]
            handler = getattr(self, f'_gen_{q.op}', None)
            if handler:
                handler(q)
            # else: skip unknown ops silently
            i += 1

    # ── Generators per opcode ────────────────────────────────────────────

    def _gen_PROG_START(self, q):
        pass  # preamble already emitted

    def _gen_PROG_END(self, q):
        self._emit_blank()
        self._emit("# === Entry point ===")
        self._emit("if __name__ == '__main__':")
        self._indent_inc()
        self._emit("_ss_ahoy()")
        self._indent_dec()

    # --- Functions ---

    def _gen_FUNC_BEGIN(self, q):
        name = self._sanitize_name(q.arg1)
        # Collect params from subsequent PARAM_DECL instructions
        self._current_func_name = name
        self._current_params = []
        self._emit_blank()

    def _gen_PARAM_DECL(self, q):
        self._current_params.append(self._sanitize_name(q.arg1))
        self._var_types[q.arg1] = q.arg2

    def _gen_FUNC_END(self, q):
        name = getattr(self, '_current_func_name', self._sanitize_name(q.arg1))
        params = getattr(self, '_current_params', [])
        # The function definition was deferred until we see FUNC_END
        # Actually, we need to refactor: emit def at FUNC_BEGIN, buffer body
        pass

    def _gen_AHOY_BEGIN(self, q):
        self._emit("def _ss_ahoy():")
        self._indent_inc()

    def _gen_AHOY_END(self, q):
        # If no body was emitted, add pass
        self._indent_dec()
        self._emit_blank()

    # --- Declarations ---

    def _gen_DECL_VAR(self, q):
        name = self._sanitize_name(q.arg1)
        dtype = q.arg2
        self._var_types[q.arg1] = dtype
        if q.result is not None:
            self._emit(f"{name} = {self._val(q.result)}")
        else:
            self._emit(f"{name} = {_DEFAULT_VALUES.get(dtype, 'None')}")

    def _gen_DECL_CONST(self, q):
        name = self._sanitize_name(q.arg1)
        dtype = q.arg2
        self._var_types[q.arg1] = dtype
        self._const_names.add(q.arg1)
        self._emit(f"{name} = {self._val(q.result)}")

    def _gen_DECL_ARR(self, q):
        name = self._sanitize_name(q.arg1)
        dtype = q.arg2
        dims = q.result  # tuple
        self._var_types[q.arg1] = dtype
        default = _DEFAULT_VALUES.get(dtype, 'None')
        self._emit(f"{name} = _ss_make_array({list(dims)}, {default})")

    def _gen_DECL_STRUCT_TYPE(self, q):
        pass  # struct types are metadata, no Python code needed

    def _gen_DECL_STRUCT_VAR(self, q):
        name = self._sanitize_name(q.arg1)
        stype = q.arg2
        # Initialize with default values for all members
        members = self.ir.struct_types.get(stype, {})
        member_defaults = []
        for mname, mdtype in members.items():
            default = _DEFAULT_VALUES.get(mdtype, 'None')
            member_defaults.append(f"'{mname}': {default}")
        self._emit(f"{name} = {{{', '.join(member_defaults)}}}")

    def _gen_STRUCT_INIT(self, q):
        name = self._sanitize_name(q.arg1)
        init_dict = q.arg2
        if init_dict:
            for member, val_temp in init_dict.items():
                self._emit(f"{name}['{member}'] = {self._val(val_temp)}")

    def _gen_ARR_INIT_1D(self, q):
        name = self._sanitize_name(q.arg1)
        vals = q.arg2 or []
        if vals:
            dtype   = self._var_types.get(q.arg1, '')
            default = _DEFAULT_VALUES.get(dtype, 'None')
            val_strs = [self._val(v) for v in vals]
            n = len(val_strs)
            # If more init values are supplied than the declared size, extend
            # the array in-place so the index assignment never goes out of bounds.
            # (Fewer values than declared size already works — DECL_ARR pre-fills
            # every slot with the type default.)
            self._emit(
                f"if len({name}) < {n}: "
                f"{name} += [{default}] * ({n} - len({name}))"
            )
            for i, vs in enumerate(val_strs):
                self._emit(f"{name}[{i}] = {vs}")

    def _gen_ARR_INIT_2D(self, q):
        name = self._sanitize_name(q.arg1)
        rows = q.arg2 or []
        if rows:
            dtype   = self._var_types.get(q.arg1, '')
            default = _DEFAULT_VALUES.get(dtype, 'None')
            n_rows = len(rows)
            self._emit(
                f"if len({name}) < {n_rows}: "
                f"{name} += [[{default}]] * ({n_rows} - len({name}))"
            )
            for ri, row in enumerate(rows):
                n_cols = len(row)
                self._emit(
                    f"if len({name}[{ri}]) < {n_cols}: "
                    f"{name}[{ri}] += [{default}] * ({n_cols} - len({name}[{ri}]))"
                )
                for ci, v in enumerate(row):
                    self._emit(f"{name}[{ri}][{ci}] = {self._val(v)}")

    # --- Assignment ---

    def _gen_ASSIGN(self, q):
        if q.result is not None:
            dest = self._sanitize_name(q.result)
            self._emit(f"{dest} = {self._val(q.arg1)}")

    def _gen_ASSIGN_ARR(self, q):
        name = self._sanitize_name(q.arg1)
        idx = self._val(q.arg2)
        val = self._val(q.result)
        self._emit(f"{name}[{idx}] = {val}")

    def _gen_ASSIGN_ARR2(self, q):
        name = self._sanitize_name(q.arg1)
        i1, i2 = q.arg2
        val = self._val(q.result)
        self._emit(f"{name}[{self._val(i1)}][{self._val(i2)}] = {val}")

    def _gen_ASSIGN_MEMBER(self, q):
        name = self._sanitize_name(q.arg1)
        member = q.arg2
        val = self._val(q.result)
        self._emit(f"{name}['{member}'] = {val}")

    # --- Arithmetic ---

    def _gen_arith(self, q, py_op):
        a = self._val(q.arg1)
        b = self._val(q.arg2)
        result = q.result
        expr = f"({a} {py_op} {b})"
        self._temps[result] = expr
        self._emit(f"{result} = {expr}")

    def _gen_ADD(self, q):     self._gen_arith(q, '+')
    def _gen_SUB(self, q):     self._gen_arith(q, '-')
    def _gen_MUL(self, q):     self._gen_arith(q, '*')
    def _gen_POW(self, q):     self._gen_arith(q, '**')

    def _gen_DIV(self, q):
        a = self._val(q.arg1)
        b = self._val(q.arg2)
        result = q.result
        # Check if both operands are COIN for integer division
        t1 = self._var_types.get(q.arg1)
        t2 = self._var_types.get(q.arg2)
        self._emit(f"if ({b}) == 0: raise ZeroDivisionError('Division by zero is not allowed.')")
        if t1 == 'COIN' and t2 == 'COIN':
            expr = f"int(({a}) / ({b}))"
        else:
            expr = f"({a} / {b})"
        self._temps[result] = expr
        self._emit(f"{result} = {expr}")

    def _gen_MOD(self, q):
        a = self._val(q.arg1)
        b = self._val(q.arg2)
        result = q.result
        # SeaStack modulo preserves the sign of the dividend (like C's %)
        self._emit(f"if ({b}) == 0: raise ZeroDivisionError('Modulo by zero is not allowed.')")
        expr = f"int(__import__('math').fmod({a}, {b}))" if self._var_types.get(q.arg1) == 'COIN' else f"__import__('math').fmod({a}, {b})"
        self._temps[result] = expr
        self._emit(f"{result} = {expr}")

    # --- Relational ---

    def _gen_rel(self, q, py_op):
        a = self._val(q.arg1)
        b = self._val(q.arg2)
        result = q.result
        expr = f"({a} {py_op} {b})"
        self._temps[result] = expr
        self._emit(f"{result} = {expr}")

    def _gen_LT(self, q):  self._gen_rel(q, '<')
    def _gen_GT(self, q):  self._gen_rel(q, '>')
    def _gen_LE(self, q):  self._gen_rel(q, '<=')
    def _gen_GE(self, q):  self._gen_rel(q, '>=')
    def _gen_EQ(self, q):  self._gen_rel(q, '==')
    def _gen_NE(self, q):  self._gen_rel(q, '!=')

    # --- Logical ---

    def _gen_LOG_AND(self, q):
        a = self._val(q.arg1)
        b = self._val(q.arg2)
        expr = f"({a} and {b})"
        self._temps[q.result] = expr
        self._emit(f"{q.result} = {expr}")

    def _gen_LOG_OR(self, q):
        a = self._val(q.arg1)
        b = self._val(q.arg2)
        expr = f"({a} or {b})"
        self._temps[q.result] = expr
        self._emit(f"{q.result} = {expr}")

    def _gen_LOG_NOT(self, q):
        a = self._val(q.arg1)
        expr = f"(not {a})"
        self._temps[q.result] = expr
        self._emit(f"{q.result} = {expr}")

    def _gen_LOG_DNOT(self, q):
        a = self._val(q.arg1)
        expr = f"(not not {a})"
        self._temps[q.result] = expr
        self._emit(f"{q.result} = {expr}")

    # --- Unary ---

    def _gen_UNARY_NEG(self, q):
        a = self._val(q.arg1)
        expr = f"(-{a})"
        self._temps[q.result] = expr
        self._emit(f"{q.result} = {expr}")

    def _gen_UNARY_INC(self, q):
        name = self._sanitize_name(q.arg1)
        self._emit(f"{name} += 1")

    def _gen_UNARY_DEC(self, q):
        name = self._sanitize_name(q.arg1)
        self._emit(f"{name} -= 1")

    # --- String / SCROLL ---

    def _gen_CONCAT(self, q):
        a = self._val(q.arg1)
        b = self._val(q.arg2)
        expr = f"(str({a}) + str({b}))"
        self._temps[q.result] = expr
        self._emit(f"{q.result} = {expr}")

    def _gen_SCROLL_CHAR(self, q):
        s = self._val(q.arg1)
        idx = self._val(q.arg2)
        # _ss_scroll_char honours the SeaStack rule: s[len(s)] == '\x00'
        expr = f"_ss_scroll_char({s}, {idx})"
        self._temps[q.result] = expr
        self._emit(f"{q.result} = {expr}")

    # --- Array / Member loads ---

    def _gen_LOAD_ARR(self, q):
        name = self._sanitize_name(q.arg1)
        idx = self._val(q.arg2)
        expr = f"{name}[{idx}]"
        self._temps[q.result] = expr
        self._emit(f"{q.result} = {expr}")

    def _gen_LOAD_ARR2(self, q):
        name = self._sanitize_name(q.arg1)
        i1, i2 = q.arg2
        expr = f"{name}[{self._val(i1)}][{self._val(i2)}]"
        self._temps[q.result] = expr
        self._emit(f"{q.result} = {expr}")

    def _gen_LOAD_MEMBER(self, q):
        name = self._sanitize_name(q.arg1)
        member = q.arg2
        expr = f"{name}['{member}']"
        self._temps[q.result] = expr
        self._emit(f"{q.result} = {expr}")

    # --- Control flow ---

    def _gen_LABEL(self, q):
        # Labels don't directly translate to Python.
        # We use a comment marker for traceability.
        # The actual control flow is handled by if/while/for generation.
        pass  # labels are consumed by the structural code gen approach below

    def _gen_JUMP(self, q):
        pass  # handled structurally

    def _gen_JUMP_FALSE(self, q):
        cond = self._val(q.arg1)
        self._emit(f"if not ({cond}):")
        self._indent_inc()
        self._emit("pass  # branch target")
        self._indent_dec()

    def _gen_JUMP_TRUE(self, q):
        cond = self._val(q.arg1)
        self._emit(f"if ({cond}):")
        self._indent_inc()
        self._emit("pass  # branch target")
        self._indent_dec()

    def _gen_BREAK(self, q):
        self._emit("break")

    def _gen_CONTINUE(self, q):
        self._emit("continue")

    # --- Functions ---

    def _gen_ARG(self, q):
        self._arg_stack.append(self._val(q.arg1))

    def _gen_CALL(self, q):
        fname = self._sanitize_name(q.arg1)
        n = q.arg2
        args = self._arg_stack[-n:] if n else []
        self._arg_stack = self._arg_stack[:-n] if n else self._arg_stack
        args_str = ', '.join(args)
        expr = f"{fname}({args_str})"
        self._temps[q.result] = expr
        self._emit(f"{q.result} = {expr}")

    def _gen_CALL_VOID(self, q):
        fname = self._sanitize_name(q.arg1)
        n = q.arg2
        args = self._arg_stack[-n:] if n else []
        self._arg_stack = self._arg_stack[:-n] if n else self._arg_stack
        args_str = ', '.join(args)
        self._emit(f"{fname}({args_str})")

    def _gen_RETURN(self, q):
        self._emit(f"return {self._val(q.arg1)}")

    def _gen_RETURN_VOID(self, q):
        self._emit("return")

    # --- I/O ---

    def _gen_INPUT(self, q):
        fmt = q.arg1
        targets = q.arg2  # list of dicts
        spec_map = {'C': 'COIN', 'D': 'DIME', 'P': 'PARCH', 'S': 'SCROLL', 'B': 'BOOL'}
        raw = _convert_scroll_escapes(fmt) if fmt else ''
        specs = [spec_map[ch] for ch in re.findall(r'%([CDPSB])', raw)]

        # Print any literal text in the format string as a visible input prompt
        prompt = re.sub(r'%[CDPSB]', '', raw)
        if prompt:
            self._emit(f"print({repr(prompt)}, end='', flush=True)")

        for i, tgt in enumerate(targets):
            dtype = specs[i] if i < len(specs) else 'SCROLL'
            var = self._sanitize_name(tgt['var_name'])

            # Build the validated input expression for each type
            if dtype == 'COIN':
                raw_var = f"_ss_raw_{var}"
                self._emit(f"{raw_var} = input().strip()")
                self._emit(f"if not {raw_var}: raise ValueError('Input Error: Expected an integer (COIN) but received empty input.')")
                self._emit(f"try:")
                self._indent_inc()
                self._emit(f"{var}_conv = int({raw_var})")
                self._indent_dec()
                self._emit(f"except ValueError:")
                self._indent_inc()
                self._emit(f"raise ValueError(f'Input Error: Expected a whole number (COIN), got {{{raw_var}!r}}. Do not use decimals or letters.')")
                self._indent_dec()
                self._emit(f"if len({raw_var}.lstrip('-+')) > 16: raise RuntimeError('Overflow Error: COIN input exceeds 16 digits.')")
                assign_expr = f"{var}_conv"
            elif dtype == 'DIME':
                raw_var = f"_ss_raw_{var}"
                self._emit(f"{raw_var} = input().strip()")
                self._emit(f"if not {raw_var}: raise ValueError('Input Error: Expected a decimal number (DIME) but received empty input.')")
                self._emit(f"try:")
                self._indent_inc()
                self._emit(f"{var}_conv = float({raw_var})")
                self._indent_dec()
                self._emit(f"except ValueError:")
                self._indent_inc()
                self._emit(f"raise ValueError(f'Input Error: Expected a numeric value (DIME), got {{{raw_var}!r}}. Please enter a number.')")
                self._indent_dec()
                assign_expr = f"{var}_conv"
            elif dtype == 'PARCH':
                raw_var = f"_ss_raw_{var}"
                self._emit(f"{raw_var} = input().strip()")
                self._emit(f"if not {raw_var}: raise ValueError('Input Error: Expected a single character (PARCH) but received empty input.')")
                self._emit(f"if len({raw_var}) != 1: raise ValueError(f'Input Error: Expected exactly one character (PARCH), got {{{raw_var}!r}} ({{len({raw_var})}} chars).')")
                assign_expr = f"{raw_var}"
            elif dtype == 'BOOL':
                assign_expr = f"_ss_bool_input(input().strip())"
            else:
                assign_expr = "input()"

            if tgt['target_kind'] == 'var':
                self._emit(f"{var} = {assign_expr}")
            elif tgt['target_kind'] == 'array1d':
                idx = self._val(tgt['index1'])
                self._emit(f"{var}[{idx}] = {assign_expr}")
            elif tgt['target_kind'] == 'array2d':
                i1 = self._val(tgt['index1'])
                i2 = self._val(tgt['index2'])
                self._emit(f"{var}[{i1}][{i2}] = {assign_expr}")
            elif tgt['target_kind'] == 'member':
                member = tgt['member']
                self._emit(f"{var}['{member}'] = {assign_expr}")

    def _gen_OUTPUT(self, q):
        fmt_str = q.arg1
        arg_temps = q.arg2  # list of temps

        fmt_converted, specs = _format_spec_to_python(fmt_str)

        if not arg_temps:
            self._emit(f"print({repr(fmt_converted)}, end='')")
        else:
            val_strs = []
            for i, at in enumerate(arg_temps):
                v = self._val(at)
                if i < len(specs) and specs[i] == 'BOOL':
                    val_strs.append(f"_ss_display({v})")
                else:
                    val_strs.append(f"{v}")
            args = ', '.join(val_strs)
            self._emit(f"print({repr(fmt_converted)}.format({args}), end='')")

    # --- Literal ---

    def _gen_LITERAL(self, q):
        dtype = q.arg1
        value = q.arg2
        result = q.result
        py_lit = self._python_literal(dtype, value)
        self._temps[result] = py_lit
        self._emit(f"{result} = {py_lit}")

    # --- NOP ---

    def _gen_NOP(self, q):
        pass

    def _gen_COMMENT(self, q):
        self._emit(f"# {q.arg1}")


# =============================================================================
# HIGH-LEVEL CODE GENERATOR
# =============================================================================
# The low-level generator above emits code per-instruction.  For correct
# control flow (loops, conditionals), we need a structural approach that
# reconstructs Python's block structure from the flat IR.
#
# This class wraps the low-level approach: it scans the IR for control-flow
# patterns (LABEL/JUMP/JUMP_FALSE sequences) and emits proper Python
# if/while/for blocks.

class StructuralCodeGenerator:
    """Generates clean, well-structured Python from optimized IR."""

    def __init__(self, ir_program: IRProgram):
        self.ir = ir_program
        self._lines = []
        self._indent = 0
        self._temps = {}
        self._arg_stack = []
        self._var_types = {}
        self._const_names = set()
        self._func_bodies = {}  # func_name → list of Quad
        self._ahoy_body = []
        self._global_decls = []

    def generate(self):
        """Generate executable Python code."""
        self._partition_instructions()
        self._emit_preamble()
        self._emit_globals()
        self._emit_functions()
        self._emit_ahoy()
        self._emit_entry()
        return '\n'.join(self._lines)

    # ── Partitioning ─────────────────────────────────────────────────────

    def _partition_instructions(self):
        """Split IR into global decls, function bodies, and AHOY body."""
        instrs = self.ir.instructions
        current_func = None
        current_body = []
        in_ahoy = False

        for q in instrs:
            if q.op == PROGRAM_START:
                continue
            elif q.op == PROGRAM_END:
                continue
            elif q.op == FUNC_BEGIN:
                current_func = q.arg1
                current_body = [q]
            elif q.op == FUNC_END:
                current_body.append(q)
                self._func_bodies[current_func] = current_body
                current_func = None
                current_body = []
            elif q.op == AHOY_BEGIN:
                in_ahoy = True
                current_body = []
            elif q.op == AHOY_END:
                self._ahoy_body = current_body
                in_ahoy = False
                current_body = []
            elif current_func is not None:
                current_body.append(q)
            elif in_ahoy:
                current_body.append(q)
            else:
                self._global_decls.append(q)

    # ── Emit helpers ─────────────────────────────────────────────────────

    def _emit(self, line):
        self._lines.append('    ' * self._indent + line)

    def _emit_blank(self):
        self._lines.append('')

    def _inc(self):
        self._indent += 1

    def _dec(self):
        self._indent = max(0, self._indent - 1)

    def _val(self, operand):
        if operand is None:
            return 'None'
        if isinstance(operand, bool):
            return 'True' if operand else 'False'
        if isinstance(operand, int):
            return str(operand)
        if isinstance(operand, float):
            return repr(operand)
        if isinstance(operand, str):
            if operand in self._temps:
                return self._temps[operand]
            return self._sanitize(operand)
        return repr(operand)

    def _sanitize(self, name):
        py_reserved = {
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else',
            'except', 'finally', 'for', 'from', 'global', 'if', 'import',
            'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise',
            'return', 'try', 'while', 'with', 'yield',
        }
        return f'_ss_{name}' if name in py_reserved else name

    def _py_lit(self, dtype, value):
        if dtype == 'COIN': return str(int(value))
        if dtype == 'DIME':
            f = float(value)
            s = repr(f)
            # Guarantee a decimal point so whole numbers display as e.g. 5.0
            if '.' not in s and 'e' not in s and 'n' not in s:
                s += '.0'
            return s
        if dtype == 'BOOL': return 'True' if value else 'False'
        if dtype == 'PARCH': return repr(_convert_parch_escapes(value))
        if dtype == 'SCROLL': return repr(_convert_scroll_escapes(value))
        return repr(value)

    def _resolve_operand_type(self, operand):
        """Resolve the SeaStack type of an operand.

        After the optimizer's constant propagation, an operand that was
        originally a temp name (e.g. '_t5') may have been replaced with
        a Python literal (e.g. the integer 10).  This helper checks:
          1. Python int/bool → 'COIN'  (bool before int — bool is int subclass)
          2. Python float    → 'DIME'
          3. String key      → look up in _var_types, then ir.temp_types
        """
        if isinstance(operand, bool):
            return 'BOOL'
        if isinstance(operand, int):
            return 'COIN'
        if isinstance(operand, float):
            return 'DIME'
        if isinstance(operand, str):
            # Check code-generator local type registry first
            t = self._var_types.get(operand)
            if t:
                return t
            # Fall back to the IR program's temp-type metadata
            t = self.ir.temp_types.get(operand)
            if t:
                return t
        return None

    # ── Preamble ─────────────────────────────────────────────────────────

    def _emit_preamble(self):
        self._emit("# ═══ SeaStack → Python (Generated Code) ═══")
        self._emit("import sys, math")
        self._emit_blank()
        # Runtime line/column tracking: updated before every potentially-failing statement.
        # The execution host (server) reads _ss_line / _ss_col when catching exceptions
        # to report the correct SeaStack source location.
        self._emit("_ss_line = 0")
        self._emit("_ss_col  = 0")
        self._emit_blank()
        self._emit("def _ss_bool_input(s):")
        self._inc()
        self._emit("s = s.strip()")
        self._emit("if s == 'AYE': return True")
        self._emit("if s == 'NAY': return False")
        self._emit("raise ValueError(f'Expected AYE or NAY, got {s!r}')")
        self._dec()
        self._emit_blank()
        self._emit("def _ss_make_array(dims, default=None):")
        self._inc()
        self._emit("for _d in dims:")
        self._inc()
        self._emit("if not isinstance(_d, int) or _d <= 0:")
        self._inc()
        self._emit("raise ValueError(f'Invalid array size {_d!r}: array dimensions must be positive integers.')")
        self._dec()
        self._dec()
        self._emit("if len(dims) == 1: return [default] * dims[0]")
        self._emit("return [[default] * dims[1] for _ in range(dims[0])]")
        self._dec()
        self._emit_blank()
        self._emit("def _ss_check_div(divisor):")
        self._inc()
        self._emit("if divisor == 0:")
        self._inc()
        self._emit("raise ZeroDivisionError('Division by zero is not allowed.')")
        self._dec()
        self._dec()
        self._emit_blank()
        self._emit("def _ss_check_arr_bounds(arr, idx, arr_name='array'):")
        self._inc()
        self._emit("if not isinstance(idx, int):")
        self._inc()
        self._emit("raise TypeError(f'Array index must be an integer, got {type(idx).__name__!r}.')")
        self._dec()
        self._emit("if idx < 0:")
        self._inc()
        self._emit("raise IndexError(f'Index out of bounds: index {idx} is negative for array \\''+arr_name+'\\'')")
        self._dec()
        self._emit("if idx >= len(arr):")
        self._inc()
        self._emit("raise IndexError(f'Index out of bounds: index {idx} exceeds size {len(arr)} of array \\''+arr_name+'\\'')")
        self._dec()
        self._dec()
        self._emit_blank()
        self._emit("def _ss_display(val):")
        self._inc()
        self._emit("if isinstance(val, bool): return 'AYE' if val else 'NAY'")
        self._emit("return str(val)")
        self._dec()
        self._emit_blank()
        # SCROLL character access: index at len(s) returns the SeaStack null
        # terminator '\x00', satisfying the rule that the char immediately after
        # the last character of a SCROLL string must equal '\x00'.
        self._emit("def _ss_scroll_char(s, idx):")
        self._inc()
        self._emit("if idx == len(s): return '\\x00'")
        self._emit("return s[idx]")
        self._dec()
        self._emit_blank()
        self._emit("def _ss_parse_input(raw_line, types):")
        self._inc()
        self._emit("if len(types) == 1 and types[0] == 'SCROLL': return [raw_line]")
        self._emit("tokens = raw_line.split()")
        self._emit("results = []")
        self._emit("for i, t in enumerate(types):")
        self._inc()
        self._emit("tok = tokens[i] if i < len(tokens) else ''")
        # ── COIN (integer) ────────────────────────────────────────────────
        self._emit("if t == 'COIN':")
        self._inc()
        self._emit("if not tok:")
        self._inc()
        self._emit("raise ValueError('Input Error: Expected an integer (COIN) but received empty input.')")
        self._dec()
        self._emit("try:")
        self._inc()
        self._emit("_coin_val = int(tok)")
        self._dec()
        self._emit("except ValueError:")
        self._inc()
        self._emit("raise ValueError(f'Input Error: Expected a whole number (COIN), got {tok!r}. Do not use decimals or letters.')")
        self._dec()
        self._emit("if len(tok.lstrip('-+')) > 16:")
        self._inc()
        self._emit("raise RuntimeError('Overflow Error: COIN input exceeds 16 digits.')")
        self._dec()
        self._emit("results.append(_coin_val)")
        self._dec()
        # ── DIME (float) ──────────────────────────────────────────────────
        self._emit("elif t == 'DIME':")
        self._inc()
        self._emit("if not tok:")
        self._inc()
        self._emit("raise ValueError('Input Error: Expected a decimal number (DIME) but received empty input.')")
        self._dec()
        self._emit("try:")
        self._inc()
        self._emit("_dime_val = float(tok)")
        self._dec()
        self._emit("except ValueError:")
        self._inc()
        self._emit("raise ValueError(f'Input Error: Expected a numeric value (DIME), got {tok!r}. Please enter a number.')")
        self._dec()
        # Validate integer and decimal parts separately (max 16 and 8 digits respectively)
        self._emit("_dime_clean = tok.lstrip('-+').split('.')[0]")
        self._emit("if len(_dime_clean) > 16:")
        self._inc()
        self._emit("raise RuntimeError('Overflow Error: DIME input exceeds 16 digits in integer part.')")
        self._dec()
        self._emit("if '.' in tok:")
        self._inc()
        self._emit("_dime_dec = tok.split('.')[1]")
        self._emit("if len(_dime_dec) > 8:")
        self._inc()
        self._emit("raise RuntimeError('Overflow Error: DIME input exceeds 8 digits in decimal part.')")
        self._dec()
        self._dec()
        self._emit("results.append(_dime_val)")
        self._dec()
        # ── BOOL ─────────────────────────────────────────────────────────
        self._emit("elif t == 'BOOL':")
        self._inc()
        self._emit("if not tok:")
        self._inc()
        self._emit("raise ValueError('Input Error: Expected AYE or NAY (BOOL) but received empty input.')")
        self._dec()
        self._emit("results.append(_ss_bool_input(tok))")
        self._dec()
        # ── PARCH (single character) ──────────────────────────────────────
        self._emit("elif t == 'PARCH':")
        self._inc()
        self._emit("if not tok:")
        self._inc()
        self._emit("raise ValueError('Input Error: Expected a single character (PARCH) but received empty input.')")
        self._dec()
        self._emit("if len(tok) != 1:")
        self._inc()
        self._emit("raise ValueError(f'Input Error: Expected exactly one character (PARCH), got {tok!r} ({len(tok)} characters).')")
        self._dec()
        self._emit("results.append(tok)")
        self._dec()
        # ── SCROLL (string) ───────────────────────────────────────────────
        self._emit("else:")
        self._inc()
        self._emit("results.append(tok)")
        self._dec()
        self._dec()
        self._emit("return results")
        self._dec()
        self._emit_blank()

    # ── Line / column tracker ─────────────────────────────────────────────

    def _maybe_emit_line_tracker(self, q):
        """Emit _ss_line / _ss_col assignments if the quad carries source-location info.

        This lets the execution host (server.py) report the exact SeaStack source
        line when a runtime exception (e.g. ZeroDivisionError) is caught."""
        line = getattr(q, 'line', None)
        col  = getattr(q, 'col',  None)
        if line is not None:
            self._emit(f"_ss_line = {line}")
            self._emit(f"_ss_col  = {col if col is not None else 0}")

    # ── Globals ──────────────────────────────────────────────────────────

    def _emit_globals(self):
        if self._global_decls:
            self._emit("# --- Global Declarations ---")
            self._emit_block(self._global_decls)
            self._emit_blank()

    # ── Functions ────────────────────────────────────────────────────────

    def _emit_functions(self):
        for fname, body in self._func_bodies.items():
            self._emit_function(fname, body)

    def _emit_function(self, fname, instrs):
        # Extract params
        params = []
        body_start = 0
        ret_type = None
        for i, q in enumerate(instrs):
            if q.op == FUNC_BEGIN:
                ret_type = q.arg2
            elif q.op == PARAM_DECL:
                params.append(self._sanitize(q.arg1))
                self._var_types[q.arg1] = q.arg2
            elif q.op == FUNC_END:
                break
            else:
                if body_start == 0:
                    body_start = i
        # Find body (between last PARAM_DECL and FUNC_END)
        body_instrs = []
        found_first_non_param = False
        for q in instrs:
            if q.op in (FUNC_BEGIN, PARAM_DECL, FUNC_END):
                continue
            body_instrs.append(q)

        safe_name = self._sanitize(fname)
        params_str = ', '.join(params)
        self._emit(f"def {safe_name}({params_str}):")
        self._inc()
        self._emit("global _ss_line, _ss_col")
        if body_instrs:
            self._emit_block(body_instrs)
        else:
            self._emit("pass")
        self._dec()
        self._emit_blank()

    # ── AHOY ─────────────────────────────────────────────────────────────

    def _emit_ahoy(self):
        self._emit("def _ss_ahoy():")
        self._inc()
        self._emit("global _ss_line, _ss_col")
        if self._ahoy_body:
            self._emit_block(self._ahoy_body)
        else:
            self._emit("pass")
        self._dec()
        self._emit_blank()

    # ── Entry ────────────────────────────────────────────────────────────

    def _emit_entry(self):
        self._emit("if __name__ == '__main__':")
        self._inc()
        self._emit("_ss_ahoy()")
        self._dec()

    # ── Block Emission (main recursive logic) ────────────────────────────

    # Emit a sequence of IR instructions as Python statements. Reconstructs control flow from LABEL/JUMP patterns.
    def _emit_block(self, instrs):
        i = 0
        emitted_any = False
        while i < len(instrs):
            q = instrs[i]

            # --- LITERAL: register in temps AND emit the Python assignment ---
            # Registering in self._temps allows _val() to inline the literal
            # wherever it is later referenced.  Emitting the assignment is the
            # essential safety net: if _val() is called from a nested/recursive
            # _emit_block call that hasn't processed this LITERAL yet, the temp
            # name (e.g. '_t5') would appear as an unresolved bare variable —
            # causing the "Variable '_t5' is not defined" runtime error seen with
            # array and struct initialisation.  Always emitting the line ensures
            # the variable is unconditionally present in the generated Python scope.
            if q.op == LITERAL:
                py_val = self._py_lit(q.arg1, q.arg2)
                self._temps[q.result] = py_val
                self._emit(f"{q.result} = {py_val}")
                emitted_any = True
                i += 1
                continue

            # --- Simple assignment ---
            if q.op == ASSIGN:
                if q.result:
                    self._maybe_emit_line_tracker(q)
                    self._emit(f"{self._sanitize(q.result)} = {self._val(q.arg1)}")
                    emitted_any = True
                i += 1
                continue

            # --- Declarations ---
            if q.op == DECL_VAR:
                self._maybe_emit_line_tracker(q)
                name = self._sanitize(q.arg1)
                self._var_types[q.arg1] = q.arg2
                if q.result is not None:
                    self._emit(f"{name} = {self._val(q.result)}")
                else:
                    self._emit(f"{name} = {_DEFAULT_VALUES.get(q.arg2, 'None')}")
                emitted_any = True
                i += 1
                continue

            if q.op == DECL_CONST:
                self._maybe_emit_line_tracker(q)
                name = self._sanitize(q.arg1)
                self._var_types[q.arg1] = q.arg2
                self._const_names.add(q.arg1)
                self._emit(f"{name} = {self._val(q.result)}")
                emitted_any = True
                i += 1
                continue

            if q.op == DECL_ARR:
                self._maybe_emit_line_tracker(q)
                name = self._sanitize(q.arg1)
                self._var_types[q.arg1] = q.arg2
                dims = q.result
                default = _DEFAULT_VALUES.get(q.arg2, 'None')
                for _d in dims:
                    if isinstance(_d, int) and _d <= 0:
                        self._emit(f"raise ValueError('Invalid array size {_d} for {name!r}: dimensions must be positive integers.')")
                self._emit(f"{name} = _ss_make_array({list(dims)}, {default})")
                emitted_any = True
                i += 1
                continue

            if q.op == DECL_STRUCT_TYPE:
                i += 1
                continue

            if q.op == DECL_STRUCT_VAR:
                name = self._sanitize(q.arg1)
                members = self.ir.struct_types.get(q.arg2, {})
                md = ', '.join(f"'{m}': {_DEFAULT_VALUES.get(d, 'None')}" for m, d in members.items())
                self._emit(f"{name} = {{{md}}}")
                emitted_any = True
                i += 1
                continue

            if q.op == STRUCT_INIT:
                name = self._sanitize(q.arg1)
                if q.arg2:
                    for member, vt in q.arg2.items():
                        self._emit(f"{name}['{member}'] = {self._val(vt)}")
                emitted_any = True
                i += 1
                continue

            if q.op in (ARR_INIT_1D, ARR_INIT_2D):
                name   = self._sanitize(q.arg1)
                dtype  = self._var_types.get(q.arg1, '')
                default = _DEFAULT_VALUES.get(dtype, 'None')

                if q.op == ARR_INIT_1D:
                    vals = q.arg2 or []
                    if vals:
                        val_strs = [self._val(v) for v in vals]
                        n = len(val_strs)
                        # Extend the array when the init list is longer than the
                        # declared size so index assignment never goes out of bounds.
                        # Fewer values than declared is handled automatically:
                        # DECL_ARR already pre-fills every slot with the type default.
                        self._emit(
                            f"if len({name}) < {n}: "
                            f"{name} += [{default}] * ({n} - len({name}))"
                        )
                        for idx, vs in enumerate(val_strs):
                            self._emit(f"{name}[{idx}] = {vs}")
                else:  # ARR_INIT_2D
                    rows = q.arg2 or []
                    if rows:
                        n_rows = len(rows)
                        self._emit(
                            f"if len({name}) < {n_rows}: "
                            f"{name} += [[{default}]] * ({n_rows} - len({name}))"
                        )
                        for ri, row in enumerate(rows):
                            n_cols = len(row)
                            self._emit(
                                f"if len({name}[{ri}]) < {n_cols}: "
                                f"{name}[{ri}] += [{default}] * "
                                f"({n_cols} - len({name}[{ri}]))"
                            )
                            for ci, v in enumerate(row):
                                self._emit(f"{name}[{ri}][{ci}] = {self._val(v)}")
                emitted_any = True
                i += 1
                continue

            # --- Binary/Unary ops ---
            if q.op in (ADD, SUB, MUL, DIV, MOD, POW):
                self._maybe_emit_line_tracker(q)
                a, b = self._val(q.arg1), self._val(q.arg2)
                py_ops = {ADD: '+', SUB: '-', MUL: '*', DIV: '/', MOD: '%', POW: '**'}
                op = py_ops[q.op]
                if q.op == DIV:
                    t1 = self._resolve_operand_type(q.arg1)
                    t2 = self._resolve_operand_type(q.arg2)
                    self._emit(f"_ss_check_div({b})")
                    if t1 == 'COIN' and t2 == 'COIN':
                        expr = f"int(({a}) / ({b}))"
                    else:
                        expr = f"({a} {op} {b})"
                elif q.op == MOD:
                    self._emit(f"_ss_check_div({b})")
                    expr = f"int(math.fmod({a}, {b}))"
                else:
                    expr = f"({a} {op} {b})"
                self._temps[q.result] = expr
                self._emit(f"{q.result} = {expr}")
                emitted_any = True
                i += 1
                continue

            if q.op in (LT, GT, LE, GE, EQ, NE):
                self._maybe_emit_line_tracker(q)
                a, b = self._val(q.arg1), self._val(q.arg2)
                py_ops = {LT: '<', GT: '>', LE: '<=', GE: '>=', EQ: '==', NE: '!='}
                expr = f"({a} {py_ops[q.op]} {b})"
                self._temps[q.result] = expr
                self._emit(f"{q.result} = {expr}")
                emitted_any = True
                i += 1
                continue

            if q.op in (LOG_AND, LOG_OR):
                a, b = self._val(q.arg1), self._val(q.arg2)
                py_op = 'and' if q.op == LOG_AND else 'or'
                expr = f"({a} {py_op} {b})"
                self._temps[q.result] = expr
                self._emit(f"{q.result} = {expr}")
                emitted_any = True
                i += 1
                continue

            if q.op == LOG_NOT:
                expr = f"(not {self._val(q.arg1)})"
                self._temps[q.result] = expr
                self._emit(f"{q.result} = {expr}")
                emitted_any = True
                i += 1
                continue

            if q.op == LOG_DNOT:
                expr = f"(not not {self._val(q.arg1)})"
                self._temps[q.result] = expr
                self._emit(f"{q.result} = {expr}")
                emitted_any = True
                i += 1
                continue

            if q.op == UNARY_NEG:
                expr = f"(-{self._val(q.arg1)})"
                self._temps[q.result] = expr
                self._emit(f"{q.result} = {expr}")
                emitted_any = True
                i += 1
                continue

            if q.op == UNARY_INC:
                self._maybe_emit_line_tracker(q)
                self._emit(f"{self._sanitize(q.arg1)} += 1")
                emitted_any = True
                i += 1
                continue

            if q.op == UNARY_DEC:
                self._maybe_emit_line_tracker(q)
                self._emit(f"{self._sanitize(q.arg1)} -= 1")
                emitted_any = True
                i += 1
                continue

            # --- Compound assignment (e.g. +=, -=, *=, /=, %=) ---
            if q.op == COMPOUND_ASSIGN:
                self._maybe_emit_line_tracker(q)
                name = self._sanitize(q.result)
                py_ops = {'+': '+=', '-': '-=', '*': '*=', '/': '/=', '%': '%=', '**': '**='}
                op_str = py_ops.get(q.arg2, f'{q.arg2}=') if q.arg2 else '+='
                val = self._val(q.arg1)
                self._emit(f"{name} {op_str} {val}")
                emitted_any = True
                i += 1
                continue

            # --- String ---
            if q.op == CONCAT:
                a, b = self._val(q.arg1), self._val(q.arg2)
                expr = f"(str({a}) + str({b}))"
                self._temps[q.result] = expr
                self._emit(f"{q.result} = {expr}")
                emitted_any = True
                i += 1
                continue

            if q.op == SCROLL_CHAR:
                s, idx = self._val(q.arg1), self._val(q.arg2)
                # _ss_scroll_char honours the SeaStack rule: s[len(s)] == '\x00'
                expr = f"_ss_scroll_char({s}, {idx})"
                self._temps[q.result] = expr
                self._emit(f"{q.result} = {expr}")
                emitted_any = True
                i += 1
                continue

            # --- Loads ---
            if q.op == LOAD_ARR:
                self._maybe_emit_line_tracker(q)
                name = self._sanitize(q.arg1)
                idx  = self._val(q.arg2)
                self._emit(f"_ss_check_arr_bounds({name}, {idx}, {name!r})")
                expr = f"{name}[{idx}]"
                self._emit(f"{q.result} = {expr}")
                emitted_any = True
                i += 1
                continue

            if q.op == LOAD_ARR2:
                self._maybe_emit_line_tracker(q)
                name = self._sanitize(q.arg1)
                i1, i2 = q.arg2
                r1, r2 = self._val(i1), self._val(i2)
                self._emit(f"_ss_check_arr_bounds({name}, {r1}, {name!r})")
                self._emit(f"_ss_check_arr_bounds({name}[{r1}], {r2}, {name!r}+'[row]')")
                expr = f"{name}[{r1}][{r2}]"
                self._emit(f"{q.result} = {expr}")
                emitted_any = True
                i += 1
                continue

            if q.op == LOAD_MEMBER:
                self._maybe_emit_line_tracker(q)
                name = self._sanitize(q.arg1)
                expr = f"{name}['{q.arg2}']"
                self._emit(f"{q.result} = {expr}")
                emitted_any = True
                i += 1
                continue

            # --- Stores ---
            if q.op == ASSIGN_ARR:
                self._maybe_emit_line_tracker(q)
                name = self._sanitize(q.arg1)
                idx  = self._val(q.arg2)
                self._emit(f"_ss_check_arr_bounds({name}, {idx}, {name!r})")
                self._emit(f"{name}[{idx}] = {self._val(q.result)}")
                emitted_any = True
                i += 1
                continue

            if q.op == ASSIGN_ARR2:
                self._maybe_emit_line_tracker(q)
                name = self._sanitize(q.arg1)
                i1, i2 = q.arg2
                r1, r2 = self._val(i1), self._val(i2)
                self._emit(f"_ss_check_arr_bounds({name}, {r1}, {name!r})")
                self._emit(f"_ss_check_arr_bounds({name}[{r1}], {r2}, {name!r}+'[row]')")
                self._emit(f"{name}[{r1}][{r2}] = {self._val(q.result)}")
                emitted_any = True
                i += 1
                continue

            if q.op == ASSIGN_MEMBER:
                self._maybe_emit_line_tracker(q)
                name = self._sanitize(q.arg1)
                self._emit(f"{name}['{q.arg2}'] = {self._val(q.result)}")
                emitted_any = True
                i += 1
                continue

            # --- I/O ---
            if q.op == INPUT:
                self._maybe_emit_line_tracker(q)
                self._gen_input(q)
                emitted_any = True
                i += 1
                continue

            if q.op == OUTPUT:
                self._maybe_emit_line_tracker(q)
                self._gen_output(q)
                emitted_any = True
                i += 1
                continue

            # --- Control flow ---
            if q.op == LABEL:
                # Check if this label is a loop start (jumped back to later)
                label_name = q.arg1
                is_loop_target = False
                for k in range(i + 1, len(instrs)):
                    if instrs[k].op == JUMP and instrs[k].arg1 == label_name:
                        is_loop_target = True
                        break
                    if instrs[k].op == JUMP_TRUE and instrs[k].arg2 == label_name:
                        is_loop_target = True
                        break

                if is_loop_target:
                    # Collect the entire loop body up to and including the back-jump
                    loop_body = []
                    j = i + 1
                    end_label = None
                    while j < len(instrs):
                        if instrs[j].op == JUMP and instrs[j].arg1 == label_name:
                            # This is the back-edge — loop ends here
                            j += 1
                            # Next should be the end label
                            if j < len(instrs) and instrs[j].op == LABEL:
                                end_label = instrs[j].arg1
                                j += 1
                            break
                        if instrs[j].op == JUMP_TRUE and instrs[j].arg2 == label_name:
                            # do-while back-edge
                            # The condition is in arg1
                            cond = self._val(instrs[j].arg1)
                            j += 1
                            if j < len(instrs) and instrs[j].op == LABEL:
                                j += 1
                            # Emit do-while as while True + break
                            self._emit("while True:")
                            self._inc()
                            if loop_body:
                                self._emit_block(loop_body)
                            self._emit(f"if not ({cond}):")
                            self._inc()
                            self._emit("break")
                            self._dec()
                            self._dec()
                            emitted_any = True
                            i = j
                            break
                        loop_body.append(instrs[j])
                        j += 1
                    else:
                        # Reached end without finding back-jump
                        i += 1
                        continue

                    if instrs[j - 1].op != JUMP_TRUE or instrs[j - 1].arg2 != label_name:
                        # while-loop pattern: first check for JUMP_FALSE in body
                        # Pattern: condition_calc → JUMP_FALSE end → body
                        cond_instrs = []
                        body_instrs_loop = []
                        found_jf = False
                        jf_end = None
                        for bi, bq in enumerate(loop_body):
                            if bq.op == JUMP_FALSE and not found_jf:
                                found_jf = True
                                jf_end = bq.arg2
                                cond_instrs = loop_body[:bi]
                                body_instrs_loop = loop_body[bi + 1:]
                                cond_val = self._val(bq.arg1)
                                break
                        if found_jf:
                            # Emit condition calculations before the while
                            if cond_instrs:
                                self._emit_block(cond_instrs)
                            self._emit(f"while {cond_val}:")
                            self._inc()
                            if body_instrs_loop:
                                self._emit_block(body_instrs_loop)
                                # Re-evaluate condition
                                if cond_instrs:
                                    self._emit_block(cond_instrs)
                            else:
                                self._emit("pass")
                            self._dec()
                        else:
                            # Infinite loop
                            self._emit("while True:")
                            self._inc()
                            if loop_body:
                                self._emit_block(loop_body)
                            else:
                                self._emit("pass")
                            self._dec()
                        emitted_any = True
                    i = j
                    continue
                else:
                    i += 1
                    continue

            if q.op == JUMP:
                # Unconditional jump — handled by control flow structures
                i += 1
                continue

            if q.op == JUMP_FALSE:
                # If-block: collect body up to target label
                cond_val = self._val(q.arg1)
                target_label = q.arg2
                # Find the target label index
                body_instrs_inner = []
                j = i + 1
                while j < len(instrs):
                    if instrs[j].op == LABEL and instrs[j].arg1 == target_label:
                        break
                    body_instrs_inner.append(instrs[j])
                    j += 1
                # Check if the last body instruction is a JUMP (→ else branch)
                else_instrs = []
                if body_instrs_inner and body_instrs_inner[-1].op == JUMP:
                    else_label = body_instrs_inner[-1].arg1
                    body_instrs_inner = body_instrs_inner[:-1]  # remove the JUMP
                    # Skip past the target label and collect until the else-end label
                    k = j + 1  # past the LABEL
                    while k < len(instrs):
                        if instrs[k].op == LABEL and instrs[k].arg1 == else_label:
                            break
                        else_instrs.append(instrs[k])
                        k += 1
                    j = k + 1  # skip past the else-end label
                else:
                    j = j + 1  # skip past the target label

                self._emit(f"if {cond_val}:")
                self._inc()
                if body_instrs_inner:
                    self._emit_block(body_instrs_inner)
                else:
                    self._emit("pass")
                self._dec()
                if else_instrs:
                    self._emit("else:")
                    self._inc()
                    self._emit_block(else_instrs)
                    self._dec()
                emitted_any = True
                i = j
                continue

            if q.op == JUMP_TRUE:
                # Used in do-while (HAUL-HEAVE): just skip - handled by loop pattern
                i += 1
                continue

            if q.op == BREAK:
                self._emit("break")
                emitted_any = True
                i += 1
                continue

            if q.op == CONTINUE:
                self._emit("continue")
                emitted_any = True
                i += 1
                continue

            # --- Functions ---
            if q.op == ARG:
                self._arg_stack.append(self._val(q.arg1))
                i += 1
                continue

            if q.op == CALL:
                self._maybe_emit_line_tracker(q)
                fname = self._sanitize(q.arg1)
                n = q.arg2 or 0
                args = self._arg_stack[-n:] if n else []
                self._arg_stack = self._arg_stack[:-n] if n else self._arg_stack
                expr = f"{fname}({', '.join(args)})"
                self._temps[q.result] = expr
                self._emit(f"{q.result} = {expr}")
                emitted_any = True
                i += 1
                continue

            if q.op == CALL_VOID:
                self._maybe_emit_line_tracker(q)
                fname = self._sanitize(q.arg1)
                n = q.arg2 or 0
                args = self._arg_stack[-n:] if n else []
                self._arg_stack = self._arg_stack[:-n] if n else self._arg_stack
                self._emit(f"{fname}({', '.join(args)})")
                emitted_any = True
                i += 1
                continue

            if q.op == RETURN:
                self._emit(f"return {self._val(q.arg1)}")
                emitted_any = True
                i += 1
                continue

            if q.op == RETURN_VOID:
                self._emit("return")
                emitted_any = True
                i += 1
                continue

            # --- NOP / COMMENT ---
            if q.op == NOP:
                i += 1
                continue

            if q.op == COMMENT:
                self._emit(f"# {q.arg1}")
                i += 1
                continue

            # --- Fallthrough ---
            i += 1

        if not emitted_any:
            self._emit("pass")

    # ── I/O helpers ──────────────────────────────────────────────────────

    def _gen_input(self, q):
        fmt = q.arg1
        targets = q.arg2
        spec_map = {'C': 'COIN', 'D': 'DIME', 'P': 'PARCH', 'S': 'SCROLL', 'B': 'BOOL'}
        raw = _convert_scroll_escapes(fmt) if fmt else ''
        specs = [spec_map[ch] for ch in re.findall(r'%([CDPSB])', raw)]

        prompt = re.sub(r'%[CDPSB]', '', raw)
        if prompt:
            self._emit(f"print({repr(prompt)}, end='', flush=True)")

        # Ask the server for one full line of input
        self._emit(f"_ss_raw_in = input('__ss:LINE:')")
        # Let the injected parser split it according to the format specs
        self._emit(f"_ss_parsed = _ss_parse_input(_ss_raw_in, {repr(specs)})")

        for i, tgt in enumerate(targets):
            var = self._sanitize(tgt['var_name'])
            val_expr = f"_ss_parsed[{i}]"

            if tgt['target_kind'] == 'var':
                self._emit(f"{var} = {val_expr}")
            elif tgt['target_kind'] == 'array1d':
                idx = self._val(tgt['index1'])
                self._emit(f"{var}[{idx}] = {val_expr}")
            elif tgt['target_kind'] == 'array2d':
                i1 = self._val(tgt['index1'])
                i2 = self._val(tgt['index2'])
                self._emit(f"{var}[{i1}][{i2}] = {val_expr}")
            elif tgt['target_kind'] == 'member':
                member = tgt['member']
                self._emit(f"{var}['{member}'] = {val_expr}")

    def _gen_output(self, q):
        fmt_str = q.arg1
        arg_temps = q.arg2

        fmt_converted, specs = _format_spec_to_python(fmt_str)

        if not arg_temps:
            self._emit(f"print({repr(fmt_converted)}, end='')")
        else:
            val_strs = []
            for i, at in enumerate(arg_temps):
                v = self._val(at)
                if i < len(specs) and specs[i] == 'BOOL':
                    val_strs.append(f"_ss_display({v})")
                else:
                    val_strs.append(str(v))
            args = ', '.join(val_strs)
            self._emit(f"print({repr(fmt_converted)}.format({args}), end='')")