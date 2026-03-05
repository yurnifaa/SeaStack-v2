# =============================================================================
# ast_nodes.py — SeaStack AST Node Definitions
# Every class maps to a meaningful grammar construct that the semantic
# analyzer must reason about. Pure syntax (keywords, delimiters, !!) is
# consumed by the AST parser and NOT stored in nodes.
# =============================================================================


# =============================================================================
# BASE NODE
# =============================================================================

class ASTNode:
    """Base class for all AST nodes."""
    def __repr__(self):
        attrs = ', '.join(f'{k}={v!r}' for k, v in self.__dict__.items() if k != 'token')
        return f'{self.__class__.__name__}({attrs})'


# =============================================================================
# PROGRAM STRUCTURE
# =============================================================================

class ProgramNode(ASTNode):
    """Root node — global_decls + ahoy_body."""
    def __init__(self, global_decls, ahoy_body, token=None):
        self.global_decls = global_decls  # list[ASTNode]
        self.ahoy_body = ahoy_body        # AhoyNode
        self.token = token


class AhoyNode(ASTNode):
    """AHOY() [ local_decls statements ]."""
    def __init__(self, local_decls, statements, token=None):
        self.local_decls = local_decls    # list[ASTNode]
        self.statements = statements      # list[ASTNode]
        self.token = token


# =============================================================================
# CONSTANTS
# =============================================================================

class ConstDeclNode(ASTNode):
    """LOCKE COIN x = 5!! — one node per (name, value) pair."""
    def __init__(self, dtype, name, value, token=None):
        self.dtype = dtype      # str: COIN|DIME|PARCH|SCROLL|BOOL
        self.name = name        # str
        self.value = value      # LiteralNode
        self.token = token


# =============================================================================
# VARIABLE DECLARATIONS
# =============================================================================

class VarDeclNode(ASTNode):
    """COIN x = 5!! — one node per declared identifier."""
    def __init__(self, dtype, name, init_value, token=None):
        self.dtype = dtype            # str
        self.name = name              # str
        self.init_value = init_value  # ASTNode | None
        self.token = token


# =============================================================================
# ARRAY DECLARATIONS
# =============================================================================

class ArrayDeclNode(ASTNode):
    """COIN arr{5} = [1,2,3]!! — 1D or 2D array declaration."""
    def __init__(self, dtype, name, dimensions, is_2d, init_values, token=None):
        self.dtype = dtype              # str
        self.name = name               # str
        self.dimensions = dimensions   # list[int] (1 or 2 elements)
        self.is_2d = is_2d             # bool
        self.init_values = init_values # list | list-of-lists | None
        self.token = token


# =============================================================================
# STRUCT DEFINITION
# =============================================================================

class StructDefNode(ASTNode):
    """MAST Ship [ COIN x!! SCROLL name!! ]!!"""
    def __init__(self, name, members, token=None):
        self.name = name          # str
        self.members = members    # list[MemberDeclNode]
        self.token = token


class MemberDeclNode(ASTNode):
    """One member in a MAST definition — one node per id."""
    def __init__(self, dtype, name, token=None):
        self.dtype = dtype   # str
        self.name = name     # str
        self.token = token


# =============================================================================
# STRUCT VARIABLE DECLARATIONS
# =============================================================================

class StructVarDeclNode(ASTNode):
    """MAST Ship s1 = [val1, $x = val2]!!"""
    def __init__(self, struct_type, var_name, inits, token=None):
        self.struct_type = struct_type  # str
        self.var_name = var_name        # str
        self.inits = inits              # list[PositionalInitNode|NamedInitNode] | None
        self.token = token


class PositionalInitNode(ASTNode):
    """Positional value in struct initializer list."""
    def __init__(self, value, token=None):
        self.value = value   # expression node
        self.token = token


class NamedInitNode(ASTNode):
    """Named member assignment: $member = value."""
    def __init__(self, member_name, value, token=None):
        self.member_name = member_name  # str (without $)
        self.value = value              # expression node
        self.token = token


# =============================================================================
# FUNCTION DEFINITIONS
# =============================================================================

class FuncDefNode(ASTNode):
    """Returning or non-returning function definition."""
    def __init__(self, return_type, name, params, local_decls, body, return_expr, token=None):
        self.return_type = return_type    # str: COIN|DIME|PARCH|SCROLL|BOOL|ABYSS
        self.name = name                  # str
        self.params = params              # list[ParamNode]
        self.local_decls = local_decls   # list[ASTNode]
        self.body = body                  # list[ASTNode]
        self.return_expr = return_expr   # ASTNode | None (None for ABYSS)
        self.token = token


class ParamNode(ASTNode):
    """Single parameter in a function signature."""
    def __init__(self, dtype, name, token=None):
        self.dtype = dtype   # str
        self.name = name     # str
        self.token = token


# =============================================================================
# STATEMENTS
# =============================================================================

class AssignNode(ASTNode):
    """x = 5!!  arr{0} = 5!!  s$member = val!!"""
    def __init__(self, var_name, target_kind, index1, index2, member, value, token=None):
        self.var_name = var_name        # str
        self.target_kind = target_kind  # 'var' | 'array1d' | 'array2d' | 'member'
        self.index1 = index1            # ASTNode | None
        self.index2 = index2            # ASTNode | None
        self.member = member            # str | None
        self.value = value              # ASTNode
        self.token = token


class CompoundAssignNode(ASTNode):
    """x += 5!! — compound assignment (numeric only)."""
    def __init__(self, var_name, target_kind, index1, index2, member, operator, value, token=None):
        self.var_name = var_name
        self.target_kind = target_kind
        self.index1 = index1
        self.index2 = index2
        self.member = member
        self.operator = operator        # str: +=, -=, *=, /=, %=, ^=
        self.value = value              # ASTNode (numeric expression)
        self.token = token


class AskNode(ASTNode):
    """ASK("format", @x, @arr{0})!!"""
    def __init__(self, format_string, targets, token=None):
        self.format_string = format_string  # str
        self.targets = targets              # list[AddressNode]
        self.token = token


class AddressNode(ASTNode):
    """Single @id target inside ASK."""
    def __init__(self, var_name, target_kind, index1, index2, member, token=None):
        self.var_name = var_name
        self.target_kind = target_kind
        self.index1 = index1
        self.index2 = index2
        self.member = member
        self.token = token


class EchoNode(ASTNode):
    """ECHO("Value: %C", x)!!"""
    def __init__(self, format_string, args, token=None):
        self.format_string = format_string  # str
        self.args = args                    # list[ASTNode]
        self.token = token


class LookNode(ASTNode):
    """LOOK/DROPLOOK/DROP conditional chain."""
    def __init__(self, condition, body, droplooks, drop_body, token=None):
        self.condition = condition    # ASTNode (BOOL)
        self.body = body              # list[ASTNode]
        self.droplooks = droplooks   # list[(condition, body)]
        self.drop_body = drop_body   # list[ASTNode] | None
        self.token = token


class ChartNode(ASTNode):
    """CHART(expr) [ COURSE ... ADRIFT ... ]"""
    def __init__(self, expr, courses, adrift_body, token=None):
        self.expr = expr              # ASTNode (COIN|PARCH|SCROLL)
        self.courses = courses        # list[CourseNode]
        self.adrift_body = adrift_body  # list[ASTNode] | None
        self.token = token


class CourseNode(ASTNode):
    """COURSE literal: body SAIL/LAND!!"""
    def __init__(self, value, body, jump, token=None):
        self.value = value   # ASTNode (literal)
        self.body = body     # list[ASTNode]
        self.jump = jump     # 'SAIL' | 'LAND' | None
        self.token = token


class HoistNode(ASTNode):
    """HOIST (init!! cond!! upd) [ body ]"""
    def __init__(self, inits, condition, updates, body, jump, token=None):
        self.inits = inits          # list[HoistInitNode]
        self.condition = condition  # ASTNode
        self.updates = updates      # list[HoistUpdateNode]
        self.body = body            # list[ASTNode]
        self.jump = jump            # str | None
        self.token = token


class HoistInitNode(ASTNode):
    """One HOIST initializer — new var or existing var assignment."""
    def __init__(self, declares_new, var_name, value, token=None):
        self.declares_new = declares_new  # bool
        self.var_name = var_name          # str
        self.value = value                # LiteralNode (COIN-lit)
        self.token = token


class HoistUpdateNode(ASTNode):
    """One HOIST update — unary or compound."""
    def __init__(self, update_kind, var_name, target_kind, index1, member,
                 unary_op, compound_op, value, token=None):
        self.update_kind = update_kind  # 'unary' | 'compound'
        self.var_name = var_name
        self.target_kind = target_kind  # 'var' | 'array1d' | 'member'
        self.index1 = index1
        self.member = member
        self.unary_op = unary_op        # '+#' | '-#' | None
        self.compound_op = compound_op  # str | None
        self.value = value              # ASTNode | None
        self.token = token


class HeaveNode(ASTNode):
    """HEAVE (cond) [ body ] — while loop."""
    def __init__(self, condition, body, jump, token=None):
        self.condition = condition
        self.body = body
        self.jump = jump
        self.token = token


class HaulHeaveNode(ASTNode):
    """HAUL [ body ] HEAVE (cond)!! — do-while loop."""
    def __init__(self, body, condition, jump, token=None):
        self.body = body
        self.condition = condition
        self.jump = jump
        self.token = token


class SailNode(ASTNode):
    """SAIL!! — continue/break."""
    def __init__(self, token=None):
        self.token = token


class LandNode(ASTNode):
    """LAND!! — break."""
    def __init__(self, token=None):
        self.token = token


class ReturnNode(ASTNode):
    """BACK value!! — return with value (returning functions)."""
    def __init__(self, value, token=None):
        self.value = value
        self.token = token


class BackNode(ASTNode):
    """BACK!! — bare return (ABYSS functions)."""
    def __init__(self, token=None):
        self.token = token


class UnaryStmtNode(ASTNode):
    """+#x!! or -#x!! as standalone statement."""
    def __init__(self, operator, var_name, target_kind, index1, index2, member, token=None):
        self.operator = operator
        self.var_name = var_name
        self.target_kind = target_kind
        self.index1 = index1
        self.index2 = index2
        self.member = member
        self.token = token


class FuncCallStmtNode(ASTNode):
    """func()!! — function call as statement (discards return)."""
    def __init__(self, call_expr, token=None):
        self.call_expr = call_expr  # FuncCallNode
        self.token = token


# =============================================================================
# EXPRESSIONS
# =============================================================================

class LiteralNode(ASTNode):
    """Literal value: COIN-lit, DIME-lit, PARCH-lit, SCROLL-lit, AYE, NAY."""
    def __init__(self, dtype, value, token=None):
        self.dtype = dtype    # str
        self.value = value    # Python value
        self.token = token


class IdentNode(ASTNode):
    """Bare variable reference."""
    def __init__(self, name, token=None):
        self.name = name
        self.token = token


class ArrayAccessNode(ASTNode):
    """arr{i} or arr{i}{j} — 1D or 2D array element access."""
    def __init__(self, name, indices, token=None):
        self.name = name        # str
        self.indices = indices  # list[ASTNode] (length 1 or 2)
        self.token = token


class MemberAccessNode(ASTNode):
    """ship$speed — struct member access."""
    def __init__(self, var_name, member_name, token=None):
        self.var_name = var_name
        self.member_name = member_name
        self.token = token


class ScrollCharAccessNode(ASTNode):
    """
    "hello"{0} or msg{i} — SCROLL character index.
    Returns a single-char SCROLL (not PARCH per SeaStack rules p.16).
    """
    def __init__(self, scroll_expr, index, token=None):
        self.scroll_expr = scroll_expr  # ASTNode
        self.index = index              # ASTNode (must be COIN)
        self.token = token


class StringConcatNode(ASTNode):
    """SCROLL & concatenation: "a" & "b" & name."""
    def __init__(self, operands, token=None):
        self.operands = operands  # list[ASTNode] (all SCROLL)
        self.token = token


class FuncCallNode(ASTNode):
    """func(arg1, arg2) — function call expression."""
    def __init__(self, name, args, token=None):
        self.name = name   # str
        self.args = args   # list[ASTNode]
        self.token = token


class BinaryOpNode(ASTNode):
    """left OP right — arithmetic, relational, equality, logical."""
    def __init__(self, left, operator, right, token=None):
        self.left = left
        self.operator = operator  # str
        self.right = right
        self.token = token


class UnaryOpNode(ASTNode):
    """Prefix unary: - (negate), ! (NOT), !# (double NOT)."""
    def __init__(self, operator, operand, token=None):
        self.operator = operator
        self.operand = operand
        self.token = token
