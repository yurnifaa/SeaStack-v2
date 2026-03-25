# =============================================================================
# ast_nodes.py — SeaStack AST Node Definitions
# Every class maps to a meaningful grammar construct that the semantic
# analyzer must reason about. Pure syntax (keywords, delimiters, !!) is
# consumed by the AST parser and NOT stored in nodes.
# =============================================================================


# =============================================================================
# BASE NODE - Base class for all AST nodes.
# =============================================================================

class ASTNode:
    resolved_type: str = None

    def __repr__(self):
        attrs = ', '.join(f'{k}={v!r}' for k, v in self.__dict__.items() if k != 'token')
        return f'{self.__class__.__name__}({attrs})'


# =============================================================================
# PROGRAM STRUCTURE
# =============================================================================

#Root node — global_decls + ahoy_body.
class ProgramNode(ASTNode):
    def __init__(self, global_decls, ahoy_body, token=None):
        self.global_decls = global_decls  # list[ASTNode]
        self.ahoy_body = ahoy_body        # AhoyNode
        self.token = token

# AHOY() [ local_decls statements ].
class AhoyNode(ASTNode):
    def __init__(self, local_decls, statements, token=None):
        self.local_decls = local_decls    # list[ASTNode]
        self.statements = statements      # list[ASTNode]
        self.token = token


# =============================================================================
# CONSTANTS
# =============================================================================

# one node per (name, value) pair.
class ConstDeclNode(ASTNode):
    def __init__(self, dtype, name, value, token=None):
        self.dtype = dtype      # str: COIN|DIME|PARCH|SCROLL|BOOL
        self.name = name        # str
        self.value = value      # LiteralNode
        self.token = token


# =============================================================================
# VARIABLE DECLARATIONS
# =============================================================================

# one node per declared identifier.
class VarDeclNode(ASTNode):
    def __init__(self, dtype, name, init_value, token=None):
        self.dtype = dtype            # str
        self.name = name              # str
        self.init_value = init_value  # ASTNode | None
        self.token = token


# =============================================================================
# ARRAY DECLARATIONS
# =============================================================================

# 1D or 2D array declaration.
class ArrayDeclNode(ASTNode):
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
    def __init__(self, name, members, token=None):
        self.name = name          # str
        self.members = members    # list[MemberDeclNode]
        self.token = token

# One member in a MAST definition — one node per id.
class MemberDeclNode(ASTNode):
    def __init__(self, dtype, name, token=None):
        self.dtype = dtype   # str
        self.name = name     # str
        self.token = token


# =============================================================================
# STRUCT VARIABLE DECLARATIONS
# =============================================================================

class StructVarDeclNode(ASTNode):
    def __init__(self, struct_type, var_name, inits, token=None):
        self.struct_type = struct_type  # str
        self.var_name = var_name        # str
        self.inits = inits              # list[PositionalInitNode|NamedInitNode] | None
        self.token = token

# Positional value in struct initializer list.
class PositionalInitNode(ASTNode):
    def __init__(self, value, token=None):
        self.value = value   # expression node
        self.token = token

# Named member assignment: $member = value.
class NamedInitNode(ASTNode):
    def __init__(self, member_name, value, token=None):
        self.member_name = member_name  # str (without $)
        self.value = value              # expression node
        self.token = token


# =============================================================================
# FUNCTION DEFINITIONS
# =============================================================================

# Returning or non-returning function definition.
class FuncDefNode(ASTNode):
    def __init__(self, return_type, name, params, local_decls, body, return_expr, token=None):
        self.return_type = return_type    # str: COIN|DIME|PARCH|SCROLL|BOOL|ABYSS
        self.name = name                  # str
        self.params = params              # list[ParamNode]
        self.local_decls = local_decls   # list[ASTNode]
        self.body = body                  # list[ASTNode]
        self.return_expr = return_expr   # ASTNode | None (None for ABYSS)
        self.token = token

# Single parameter in a function signature.
class ParamNode(ASTNode):
    def __init__(self, dtype, name, token=None):
        self.dtype = dtype   # str
        self.name = name     # str
        self.token = token


# =============================================================================
# STATEMENTS
# =============================================================================

class AssignNode(ASTNode):
    def __init__(self, var_name, target_kind, index1, index2, member, value, token=None):
        self.var_name = var_name        # str
        self.target_kind = target_kind  # 'var' | 'array1d' | 'array2d' | 'member'
        self.index1 = index1            # ASTNode | None
        self.index2 = index2            # ASTNode | None
        self.member = member            # str | None
        self.value = value              # ASTNode
        self.token = token

# compound assignment (numeric only).
class CompoundAssignNode(ASTNode):
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
    def __init__(self, format_string, targets, token=None):
        self.format_string = format_string  # str
        self.targets = targets              # list[AddressNode]
        self.token = token

# Single @id target inside ASK.
class AddressNode(ASTNode):
    def __init__(self, var_name, target_kind, index1, index2, member, token=None):
        self.var_name = var_name
        self.target_kind = target_kind
        self.index1 = index1
        self.index2 = index2
        self.member = member
        self.token = token


class EchoNode(ASTNode):
    def __init__(self, format_string, args, token=None):
        self.format_string = format_string  # str
        self.args = args                    # list[ASTNode]
        self.token = token


class LookNode(ASTNode):
    def __init__(self, condition, body, droplooks, drop_body, token=None):
        self.condition = condition    # ASTNode (BOOL)
        self.body = body              # list[ASTNode]
        self.droplooks = droplooks   # list[(condition, body)]
        self.drop_body = drop_body   # list[ASTNode] | None
        self.token = token


class ChartNode(ASTNode):
    def __init__(self, expr, courses, adrift_body, token=None):
        self.expr = expr              # ASTNode (COIN|PARCH|SCROLL)
        self.courses = courses        # list[CourseNode]
        self.adrift_body = adrift_body  # list[ASTNode] | None
        self.token = token


class CourseNode(ASTNode):
    def __init__(self, value, body, jump, token=None):
        self.value = value   # ASTNode (literal)
        self.body = body     # list[ASTNode]
        self.jump = jump     # 'SAIL' | 'LAND' | None
        self.token = token


class HoistNode(ASTNode):
    def __init__(self, inits, condition, updates, body, jump, token=None):
        self.inits = inits          # list[HoistInitNode]
        self.condition = condition  # ASTNode
        self.updates = updates      # list[HoistUpdateNode]
        self.body = body            # list[ASTNode]
        self.jump = jump            # str | None
        self.token = token

# One HOIST initializer — new var or existing var assignment.
class HoistInitNode(ASTNode):
    def __init__(self, declares_new, var_name, value, token=None):
        self.declares_new = declares_new  # bool
        self.var_name = var_name          # str
        self.value = value                # LiteralNode (COIN-lit)
        self.token = token

# One HOIST update — unary or compound.
class HoistUpdateNode(ASTNode):
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
    def __init__(self, condition, body, jump, token=None):
        self.condition = condition
        self.body = body
        self.jump = jump
        self.token = token


class HaulHeaveNode(ASTNode):
    def __init__(self, body, condition, jump, token=None):
        self.body = body
        self.condition = condition
        self.jump = jump
        self.token = token


class SailNode(ASTNode):
    def __init__(self, token=None):
        self.token = token


class LandNode(ASTNode):
    def __init__(self, token=None):
        self.token = token

# return with value (returning functions).
class ReturnNode(ASTNode):
    def __init__(self, value, token=None):
        self.value = value
        self.token = token

# bare return (ABYSS functions).
class BackNode(ASTNode):
    def __init__(self, token=None):
        self.token = token


class UnaryStmtNode(ASTNode):
    def __init__(self, operator, var_name, target_kind, index1, index2, member, token=None):
        self.operator = operator
        self.var_name = var_name
        self.target_kind = target_kind
        self.index1 = index1
        self.index2 = index2
        self.member = member
        self.token = token

# func()!! — function call as statement (discards return).
class FuncCallStmtNode(ASTNode):
    def __init__(self, call_expr, token=None):
        self.call_expr = call_expr  # FuncCallNode
        self.token = token


# =============================================================================
# EXPRESSIONS
# =============================================================================

# COIN-lit, DIME-lit, PARCH-lit, SCROLL-lit, AYE, NAY.
class LiteralNode(ASTNode):
    def __init__(self, dtype, value, token=None):
        self.dtype = dtype    # str
        self.value = value    # Python value
        self.token = token


class IdentNode(ASTNode):
    def __init__(self, name, token=None):
        self.name = name
        self.token = token

# arr{i} or arr{i}{j} — 1D or 2D array element access.
class ArrayAccessNode(ASTNode):
    def __init__(self, name, indices, token=None):
        self.name = name        # str
        self.indices = indices  # list[ASTNode] (length 1 or 2)
        self.token = token


class MemberAccessNode(ASTNode):
    def __init__(self, var_name, member_name, token=None):
        self.var_name = var_name
        self.member_name = member_name
        self.token = token


class ScrollCharAccessNode(ASTNode):
    def __init__(self, scroll_expr, index, token=None):
        self.scroll_expr = scroll_expr  # ASTNode
        self.index = index              # ASTNode (must be COIN)
        self.token = token


class StringConcatNode(ASTNode):
    def __init__(self, operands, token=None):
        self.operands = operands  # list[ASTNode] (all SCROLL)
        self.token = token

# func(arg1, arg2) — function call expression.
class FuncCallNode(ASTNode):
    def __init__(self, name, args, token=None):
        self.name = name   # str
        self.args = args   # list[ASTNode]
        self.token = token

# left OP right — arithmetic, relational, equality, logical.
class BinaryOpNode(ASTNode):
    def __init__(self, left, operator, right, token=None):
        self.left = left
        self.operator = operator  # str
        self.right = right
        self.token = token


class UnaryOpNode(ASTNode):
    def __init__(self, operator, operand, token=None):
        self.operator = operator
        self.operand = operand
        self.token = token