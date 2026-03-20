# =============================================================================
# ir_instructions.py — SeaStack Intermediate Representation (TAC / Quadruples)
#
# Every IR instruction is a Quadruple: (op, arg1, arg2, result)
# Fields that are unused for a given opcode are set to None.
#
# Temporaries:  _t0, _t1, …
# Labels:       _L0, _L1, …
# =============================================================================

from dataclasses import dataclass, field
from typing import Any, Optional, List


# ─── Quadruple ───────────────────────────────────────────────────────────────

@dataclass
class Quad:
    """Three-Address Code represented as a Quadruple.

    Attributes:
        op      – operation code (string)
        arg1    – first operand  (str | int | float | bool | None)
        arg2    – second operand (str | int | float | bool | None)
        result  – destination    (str | None)
        comment – optional human-readable note (not emitted in code)
        line    – source line number for traceability (optional)
    """
    op: str
    arg1: Any = None
    arg2: Any = None
    result: Any = None
    comment: str = ""
    line: Optional[int] = None

    def __repr__(self):
        parts = [f"{self.op:18s}"]
        parts.append(f"{_fmt(self.arg1):20s}")
        parts.append(f"{_fmt(self.arg2):20s}")
        parts.append(f"{_fmt(self.result):20s}")
        base = " | ".join(parts)
        if self.comment:
            base += f"  # {self.comment}"
        return base


def _fmt(v):
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "True" if v else "False"
    return str(v)


# ─── Opcode Constants ────────────────────────────────────────────────────────
# Grouped by category for readability.

# --- Program structure ---
PROGRAM_START    = "PROG_START"
PROGRAM_END      = "PROG_END"
FUNC_BEGIN       = "FUNC_BEGIN"       # arg1=name, arg2=return_type
FUNC_END         = "FUNC_END"         # arg1=name
PARAM_DECL       = "PARAM_DECL"       # arg1=name, arg2=dtype
AHOY_BEGIN       = "AHOY_BEGIN"
AHOY_END         = "AHOY_END"

# --- Declarations ---
DECL_VAR         = "DECL_VAR"         # arg1=name, arg2=dtype, result=init_temp|None
DECL_CONST       = "DECL_CONST"       # arg1=name, arg2=dtype, result=value_temp
DECL_ARR         = "DECL_ARR"         # arg1=name, arg2=dtype, result=dims (tuple)
DECL_STRUCT_TYPE = "DECL_STRUCT_TYPE" # arg1=name, arg2=members_dict
DECL_STRUCT_VAR  = "DECL_STRUCT_VAR"  # arg1=var_name, arg2=struct_type

# --- Initialization helpers ---
ARR_INIT_1D      = "ARR_INIT_1D"      # arg1=arr_name, arg2=values_list
ARR_INIT_2D      = "ARR_INIT_2D"      # arg1=arr_name, arg2=rows_list
STRUCT_INIT      = "STRUCT_INIT"      # arg1=var_name, arg2=init_dict

# --- Assignment / copy ---
ASSIGN           = "ASSIGN"           # result = arg1
ASSIGN_ARR       = "ASSIGN_ARR"       # arg1=arr, arg2=index_temp, result=val_temp  (1D)
ASSIGN_ARR2      = "ASSIGN_ARR2"      # arg1=arr, arg2=(i,j), result=val_temp       (2D)
ASSIGN_MEMBER    = "ASSIGN_MEMBER"    # arg1=var, arg2=member, result=val_temp

# --- Compound assignment ---
COMPOUND_ASSIGN  = "COMP_ASSIGN"      # arg1=target_temp, arg2=op, result=val_temp

# --- Arithmetic binary ops ---
ADD              = "ADD"              # result = arg1 + arg2
SUB              = "SUB"              # result = arg1 - arg2
MUL              = "MUL"              # result = arg1 * arg2
DIV              = "DIV"              # result = arg1 / arg2
MOD              = "MOD"              # result = arg1 % arg2
POW              = "POW"              # result = arg1 ** arg2

# --- Relational ops ---
LT               = "LT"              # result = arg1 < arg2
GT               = "GT"              # result = arg1 > arg2
LE               = "LE"              # result = arg1 <= arg2
GE               = "GE"              # result = arg1 >= arg2
EQ               = "EQ"              # result = arg1 == arg2
NE               = "NE"              # result = arg1 != arg2

# --- Logical ops ---
LOG_AND          = "LOG_AND"          # result = arg1 and arg2
LOG_OR           = "LOG_OR"           # result = arg1 or arg2
LOG_NOT          = "LOG_NOT"          # result = not arg1
LOG_DNOT         = "LOG_DNOT"         # result = not not arg1

# --- Unary ---
UNARY_NEG        = "UNARY_NEG"        # result = -arg1
UNARY_INC        = "UNARY_INC"        # arg1 = arg1 + 1
UNARY_DEC        = "UNARY_DEC"        # arg1 = arg1 - 1

# --- String ---
CONCAT           = "CONCAT"           # result = arg1 + arg2
SCROLL_CHAR      = "SCROLL_CHAR"      # result = arg1[arg2]

# --- Array / member access (load) ---
LOAD_ARR         = "LOAD_ARR"         # result = arg1[arg2]      (1D)
LOAD_ARR2        = "LOAD_ARR2"        # result = arg1[arg2.i][arg2.j] (2D)
LOAD_MEMBER      = "LOAD_MEMBER"      # result = arg1.arg2

# --- Control flow ---
LABEL            = "LABEL"            # arg1 = label_name
JUMP             = "JUMP"             # arg1 = target_label
JUMP_FALSE       = "JUMP_FALSE"       # if arg1 is false, jump to arg2
JUMP_TRUE        = "JUMP_TRUE"        # if arg1 is true,  jump to arg2
BREAK            = "BREAK"            # LAND  — break out of loop/chart
CONTINUE         = "CONTINUE"         # SAIL  — continue to next iteration

# --- Functions ---
ARG              = "ARG"              # arg1 = value to push
CALL             = "CALL"             # arg1=func_name, arg2=n_args, result=dest_temp
CALL_VOID        = "CALL_VOID"        # arg1=func_name, arg2=n_args
RETURN           = "RETURN"           # arg1 = value
RETURN_VOID      = "RETURN_VOID"

# --- I/O ---
INPUT            = "INPUT"            # arg1=fmt, arg2=targets_list
OUTPUT           = "OUTPUT"           # arg1=fmt, arg2=args_list

# --- Misc ---
NOP              = "NOP"              # no operation
LITERAL          = "LITERAL"          # result = literal value, arg1=dtype, arg2=value
COMMENT          = "COMMENT"          # arg1 = comment text (preserved for readability)


# ─── Utility: Map SeaStack operators to IR opcodes ───────────────────────────

ARITH_OP_MAP = {
    '+': ADD, '-': SUB, '*': MUL, '/': DIV, '%': MOD, '^': POW,
}

REL_OP_MAP = {
    '<': LT, '>': GT, '<=': LE, '>=': GE, '==': EQ, '!=': NE,
}

LOG_OP_MAP = {
    '&&': LOG_AND, '||': LOG_OR,
}

COMPOUND_OP_MAP = {
    '+=': '+', '-=': '-', '*=': '*', '/=': '/', '%=': '%', '^=': '^',
}

# ─── IR Program Container ───────────────────────────────────────────────────

@dataclass
class IRProgram:
    """Container for the flat list of IR quadruples plus metadata."""
    instructions: List[Quad] = field(default_factory=list)
    struct_types: dict = field(default_factory=dict)   # name → {member: dtype}
    struct_orders: dict = field(default_factory=dict)   # name → [member_names]
    func_signatures: dict = field(default_factory=dict) # name → (ret_type, [(p_dtype, p_name)])
    temp_types: dict = field(default_factory=dict)      # temp_name → dtype (e.g. '_t0' → 'COIN')

    def emit(self, op, arg1=None, arg2=None, result=None, comment="", line=None):
        q = Quad(op, arg1, arg2, result, comment, line)
        self.instructions.append(q)
        return q

    def dump(self):
        """Return a human-readable listing of all instructions."""
        lines = []
        lines.append(f"{'#':>4}  {'OP':18s} | {'ARG1':20s} | {'ARG2':20s} | {'RESULT':20s}")
        lines.append("-" * 92)
        for i, q in enumerate(self.instructions):
            lines.append(f"{i:4d}  {q}")
        if self.temp_types:
            lines.append("")
            lines.append("Temp Types:")
            for name, dtype in sorted(self.temp_types.items(),
                                      key=lambda x: int(x[0][2:])):
                lines.append(f"  {name:10s} → {dtype}")
        return "\n".join(lines)