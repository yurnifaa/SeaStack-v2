from dataclasses import dataclass, field
from typing import Any, Optional, List


# =======================
# QUAD CLASS
# =======================

@dataclass
class Quad:
    op: str
    arg1: Any = None
    arg2: Any = None
    result: Any = None
    comment: str = ""
    line: Optional[int] = None
    col: Optional[int] = None

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


# =======================
# OPCODE CONSTANTS
# =======================

# Program structure
PROGRAM_START    = "PROG_START"
PROGRAM_END      = "PROG_END"
FUNC_BEGIN       = "FUNC_BEGIN"       # arg1=name, arg2=return_type
FUNC_END         = "FUNC_END"         # arg1=name
PARAM_DECL       = "PARAM_DECL"       # arg1=name, arg2=dtype
AHOY_BEGIN       = "AHOY_BEGIN"
AHOY_END         = "AHOY_END"

# Declarations
DECL_VAR         = "DECL_VAR"         # arg1=name, arg2=dtype, result=init_temp|None
DECL_CONST       = "DECL_CONST"       # arg1=name, arg2=dtype, result=value_temp
DECL_ARR         = "DECL_ARR"         # arg1=name, arg2=dtype, result=dims (tuple)
DECL_STRUCT_TYPE = "DECL_STRUCT_TYPE" # arg1=name, arg2=members_dict
DECL_STRUCT_VAR  = "DECL_STRUCT_VAR"  # arg1=var_name, arg2=struct_type

# Initialization
ARR_INIT_1D      = "ARR_INIT_1D"      # arg1=arr_name, arg2=values_list
ARR_INIT_2D      = "ARR_INIT_2D"      # arg1=arr_name, arg2=rows_list
STRUCT_INIT      = "STRUCT_INIT"      # arg1=var_name, arg2=init_dict

# Assignment
ASSIGN           = "ASSIGN"           # result = arg1
ASSIGN_ARR       = "ASSIGN_ARR"       # arg1=arr, arg2=index_temp, result=val_temp
ASSIGN_ARR2      = "ASSIGN_ARR2"      # arg1=arr, arg2=(i,j), result=val_temp
ASSIGN_MEMBER    = "ASSIGN_MEMBER"    # arg1=var, arg2=member, result=val_temp
COMPOUND_ASSIGN  = "COMP_ASSIGN"      # arg1=target_temp, arg2=op, result=val_temp

# Arithmetic
ADD              = "ADD"
SUB              = "SUB"
MUL              = "MUL"
DIV              = "DIV"
MOD              = "MOD"
POW              = "POW"

# Relational
LT               = "LT"
GT               = "GT"
LE               = "LE"
GE               = "GE"
EQ               = "EQ"
NE               = "NE"

# Logical
LOG_AND          = "LOG_AND"
LOG_OR           = "LOG_OR"
LOG_NOT          = "LOG_NOT"
LOG_DNOT         = "LOG_DNOT"         # not not arg1

# Unary
UNARY_NEG        = "UNARY_NEG"
UNARY_INC        = "UNARY_INC"
UNARY_DEC        = "UNARY_DEC"

# String (SCROLL)
CONCAT           = "CONCAT"           # result = arg1 + arg2
SCROLL_CHAR      = "SCROLL_CHAR"      # result = arg1[arg2]

# Array / member access
LOAD_ARR         = "LOAD_ARR"         # result = arg1[arg2]
LOAD_ARR2        = "LOAD_ARR2"        # result = arg1[i][j]
LOAD_MEMBER      = "LOAD_MEMBER"      # result = arg1.arg2

# Control flow
LABEL            = "LABEL"            # arg1=label_name
JUMP             = "JUMP"             # arg1=target_label
JUMP_FALSE       = "JUMP_FALSE"       # jump to arg2 if arg1 is false
JUMP_TRUE        = "JUMP_TRUE"        # jump to arg2 if arg1 is true
BREAK            = "BREAK"
CONTINUE         = "CONTINUE"

# Functions
ARG              = "ARG"              # arg1=value to push
CALL             = "CALL"             # arg1=func_name, arg2=n_args, result=dest_temp
CALL_VOID        = "CALL_VOID"        # arg1=func_name, arg2=n_args
RETURN           = "RETURN"           # arg1=return value
RETURN_VOID      = "RETURN_VOID"

# I/O
INPUT            = "INPUT"            # arg1=fmt, arg2=targets_list
OUTPUT           = "OUTPUT"           # arg1=fmt, arg2=args_list

# Misc
NOP              = "NOP"
LITERAL          = "LITERAL"          # result=value, arg1=dtype, arg2=value
COMMENT          = "COMMENT"          # arg1=comment text


# =======================
# OPERATOR MAPPING
# =======================

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


# =======================
# IR PROGRAM CLASS
# =======================

@dataclass
class IRProgram:
    instructions: List[Quad] = field(default_factory=list)
    struct_types: dict = field(default_factory=dict)    # name → {member: dtype}
    struct_orders: dict = field(default_factory=dict)   # name → [member_names]
    func_signatures: dict = field(default_factory=dict) # name → (ret_type, [(p_dtype, p_name)])
    temp_types: dict = field(default_factory=dict)      # temp_name → dtype

    def emit(self, op, arg1=None, arg2=None, result=None, comment="", line=None, col=None):
        q = Quad(op, arg1, arg2, result, comment, line, col)
        self.instructions.append(q)
        return q

    def dump(self):
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
