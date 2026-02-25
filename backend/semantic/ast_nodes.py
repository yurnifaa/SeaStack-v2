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
# prod 1: <program> → <global-dec> AHOY() [ <ahoy-local-dec> <ahoy-stmnts> ]
# =============================================================================

class ProgramNode(ASTNode):
    """Root node of the entire program."""
    def __init__(self, global_decls, ahoy_body, token=None):
        self.global_decls = global_decls  # list[ASTNode] — consts, vars, arrays, funcs, structs
        self.ahoy_body = ahoy_body        # AhoyNode
        self.token = token


class AhoyNode(ASTNode):
    """The main AHOY() [ ... ] block."""
    def __init__(self, local_decls, statements, token=None):
        self.local_decls = local_decls    # list[ASTNode] — local vars/arrays/struct vars
        self.statements = statements      # list[ASTNode] — statements
        self.token = token


# =============================================================================
# CONSTANTS
# prod 265–291: LOCKE <const-init>!!
# One ConstDeclNode per id inside a LOCKE declaration.
# =============================================================================

class ConstDeclNode(ASTNode):
    """
    LOCKE COIN x = 5, y = 10!!
    One node per (name, value) pair.
    dtype: 'COIN' | 'DIME' | 'PARCH' | 'SCROLL' | 'BOOL'
    value: LiteralNode (always a literal — grammar enforces this)
    """
    def __init__(self, dtype, name, value, token=None):
        self.dtype = dtype      # str
        self.name = name        # str
        self.value = value      # LiteralNode
        self.token = token


# =============================================================================
# VARIABLE DECLARATIONS
# prods 7–11 (global), 328–332 (local)
# One VarDeclNode per declared identifier, even when comma-separated.
# =============================================================================

class VarDeclNode(ASTNode):
    """
    COIN x = 5, y!!   →   two VarDeclNodes: (COIN, x, LiteralNode(5)), (COIN, y, None)
    dtype: 'COIN' | 'DIME' | 'PARCH' | 'SCROLL' | 'BOOL'
    init_value: expression node or None (uninitialized)
    """
    def __init__(self, dtype, name, init_value, token=None):
        self.dtype = dtype            # str
        self.name = name              # str
        self.init_value = init_value  # ASTNode | None
        self.token = token


# =============================================================================
# ARRAY DECLARATIONS
# prods 36–47 (COIN), 66–77 (DIME), 90–101 (PARCH), 122–133 (SCROLL), 202–213 (BOOL)
# =============================================================================

class ArrayDeclNode(ASTNode):
    """
    COIN arr{5}!!           →  1D, no init
    COIN arr{5} = [1,2,3]!! →  1D, with init
    COIN arr{3}{3}!!        →  2D, no init
    COIN arr{3}{3} = [[...],[...]]!! → 2D, with init

    dimensions: list[int | str]  — sizes (COIN-lit or id)
    is_2d: bool
    init_values: list of expression nodes (1D) or list-of-lists (2D), or None
    """
    def __init__(self, dtype, name, dimensions, is_2d, init_values, token=None):
        self.dtype = dtype              # str
        self.name = name               # str
        self.dimensions = dimensions   # list (1 element for 1D, 2 for 2D)
        self.is_2d = is_2d             # bool
        self.init_values = init_values # list | list-of-lists | None
        self.token = token


# =============================================================================
# STRUCT DEFINITION
# prod 292–298: MAST id [ <mem-dec> <mem-dec-tail> ]!!
# =============================================================================

class StructDefNode(ASTNode):
    """
    MAST Ship [ COIN x, y!! SCROLL name!! ]!!
    members: list[MemberDeclNode]
    """
    def __init__(self, name, members, token=None):
        self.name = name          # str — struct type name
        self.members = members    # list[MemberDeclNode]
        self.token = token


class MemberDeclNode(ASTNode):
    """
    One member declaration inside a MAST block.
    prod 294: <mem-dec> → <d-type> id <mem-mult>!!
    One node per id — a single line 'COIN x, y!!' produces two MemberDeclNodes.
    """
    def __init__(self, dtype, name, token=None):
        self.dtype = dtype   # str
        self.name = name     # str
        self.token = token


# =============================================================================
# STRUCT VARIABLE DECLARATIONS
# prods 333–343: MAST id id <str-dec-init>!!
# =============================================================================

class StructVarDeclNode(ASTNode):
    """
    MAST Ship s1!!
    MAST Ship s2 = [val1, val2]!!
    MAST Ship s3 = [$x = val1, $y = val2]!!
    MAST Ship s4, s5!!  → two StructVarDeclNodes

    struct_type: str — the MAST type name
    var_name: str
    inits: list[ PositionalInitNode | NamedInitNode ] | None
    """
    def __init__(self, struct_type, var_name, inits, token=None):
        self.struct_type = struct_type  # str
        self.var_name = var_name        # str
        self.inits = inits              # list | None
        self.token = token


class PositionalInitNode(ASTNode):
    """
    A positional value in a struct initializer list.
    prod 340: <str-val> → <value>
    """
    def __init__(self, value, token=None):
        self.value = value   # expression node
        self.token = token


class NamedInitNode(ASTNode):
    """
    A named member assignment in a struct initializer list.
    prod 341: <str-val> → $id = <value>
    """
    def __init__(self, member_name, value, token=None):
        self.member_name = member_name  # str (without $)
        self.value = value              # expression node
        self.token = token


# =============================================================================
# FUNCTION DEFINITIONS
# Returning:    prods 48, 78, 102, 134, 214
# Non-returning: prod 307 (ABYSS)
# =============================================================================

class FuncDefNode(ASTNode):
    """
    COIN add(COIN a, COIN b) [ ... BACK a + b!! ]
    ABYSS print(SCROLL msg) [ ... ]

    return_type: 'COIN'|'DIME'|'PARCH'|'SCROLL'|'BOOL'|'ABYSS'
    params: list[ParamNode]
    local_decls: list[ASTNode]
    body: list[ASTNode] — statements
    return_expr: ASTNode | None  (None for ABYSS)
    """
    def __init__(self, return_type, name, params, local_decls, body, return_expr, token=None):
        self.return_type = return_type    # str
        self.name = name                  # str
        self.params = params              # list[ParamNode]
        self.local_decls = local_decls   # list[ASTNode]
        self.body = body                  # list[ASTNode]
        self.return_expr = return_expr   # ASTNode | None
        self.token = token


class ParamNode(ASTNode):
    """
    A single parameter in a function signature.
    prod 215: <params> → <d-type> id <param-mult>
    """
    def __init__(self, dtype, name, token=None):
        self.dtype = dtype   # str
        self.name = name     # str
        self.token = token


# =============================================================================
# STATEMENTS
# =============================================================================

# --- Assignment ---
# prod 353–359: id <arr-str> = <value>!!

class AssignNode(ASTNode):
    """
    Simple assignment: x = 5!!  arr{0} = 5!!  s$member = val!!

    target_kind: 'var' | 'array1d' | 'array2d' | 'member'
    var_name: str
    index1: ASTNode | None   (array row index)
    index2: ASTNode | None   (array column index, 2D only)
    member: str | None       (struct member name, without $)
    value: ASTNode           (right-hand side expression)
    """
    def __init__(self, var_name, target_kind, index1, index2, member, value, token=None):
        self.var_name = var_name        # str
        self.target_kind = target_kind  # 'var' | 'array1d' | 'array2d' | 'member'
        self.index1 = index1            # ASTNode | None
        self.index2 = index2            # ASTNode | None
        self.member = member            # str | None
        self.value = value              # ASTNode
        self.token = token


class CompoundAssignNode(ASTNode):
    """
    Compound assignment: x += 5!!  arr{0} -= 1!!
    prods 360–366: <assign-body> → <arith-assign-op> <dime-ope> <dime-arith>

    operator: '+=', '-=', '*=', '/=', '%=', '^='
    Right-hand side is always numeric (COIN or DIME).
    target_kind, var_name, index1, index2, member: same as AssignNode
    """
    def __init__(self, var_name, target_kind, index1, index2, member, operator, value, token=None):
        self.var_name = var_name        # str
        self.target_kind = target_kind  # 'var' | 'array1d' | 'array2d' | 'member'
        self.index1 = index1            # ASTNode | None
        self.index2 = index2            # ASTNode | None
        self.member = member            # str | None
        self.operator = operator        # str (e.g. '+=')
        self.value = value              # ASTNode (numeric expression)
        self.token = token


# --- I/O Statements ---
# prod 367–370: ASK(SCROLL-lit, @id<arr-str>)!!

class AskNode(ASTNode):
    """
    ASK("Enter x: ", @x, @arr{0})!!
    format_string: str literal (the prompt)
    targets: list[AddressNode]
    """
    def __init__(self, format_string, targets, token=None):
        self.format_string = format_string  # str
        self.targets = targets              # list[AddressNode]
        self.token = token


class AddressNode(ASTNode):
    """
    A single @id target inside ASK.
    prod 368: @id <arr-str>
    target_kind: 'var' | 'array1d' | 'array2d' | 'member'
    """
    def __init__(self, var_name, target_kind, index1, index2, member, token=None):
        self.var_name = var_name        # str
        self.target_kind = target_kind  # 'var' | 'array1d' | 'array2d' | 'member'
        self.index1 = index1            # ASTNode | None
        self.index2 = index2            # ASTNode | None
        self.member = member            # str | None
        self.token = token


# prod 371: ECHO(SCROLL-lit, arg1, arg2, ...)!!

class EchoNode(ASTNode):
    """
    ECHO("Value: ", x, y)!!
    format_string: str literal
    args: list[ASTNode] — additional expressions to print
    """
    def __init__(self, format_string, args, token=None):
        self.format_string = format_string  # str
        self.args = args                    # list[ASTNode]
        self.token = token


# --- Conditional: LOOK / DROPLOOK / DROP ---
# prods 372–381

class LookNode(ASTNode):
    """
    LOOK (cond) [ body ] DROPLOOK (cond2) [ body2 ] DROP [ body3 ]

    droplooks is a list to support multiple DROPLOOK branches (else-if chain).
    drop_body is None if there is no DROP branch.
    """
    def __init__(self, condition, body, droplooks, drop_body, token=None):
        self.condition = condition    # ASTNode (must be BOOL)
        self.body = body              # list[ASTNode]
        self.droplooks = droplooks   # list[ (condition: ASTNode, body: list[ASTNode]) ]
        self.drop_body = drop_body   # list[ASTNode] | None
        self.token = token


# --- Switch: CHART ---
# prods 382–399

class ChartNode(ASTNode):
    """
    CHART(expr) [ COURSE val: body SAIL!! ... ADRIFT: body LAND!! ]
    """
    def __init__(self, expr, courses, adrift_body, token=None):
        self.expr = expr              # ASTNode (id or literal)
        self.courses = courses        # list[CourseNode]
        self.adrift_body = adrift_body  # list[ASTNode] | None
        self.token = token


class CourseNode(ASTNode):
    """
    COURSE COIN-lit: <statements> SAIL!!
    COURSE PARCH-lit: ...
    COURSE SCROLL-lit{idx}: ...

    value: LiteralNode | ScrollCharAccessNode
    body: list[ASTNode]
    jump: 'SAIL' | 'LAND' | None
    """
    def __init__(self, value, body, jump, token=None):
        self.value = value   # ASTNode (the case constant)
        self.body = body     # list[ASTNode]
        self.jump = jump     # 'SAIL' | 'LAND' | None
        self.token = token


# --- Loops ---
# prod 400: HOIST

class HoistNode(ASTNode):
    """
    HOIST (COIN i = 0, j = 0 !! i < 10 !! i+#, j += 2) [ body ]
    inits: list[HoistInitNode]
    condition: ASTNode (numeric comparison, must resolve to BOOL)
    updates: list[HoistUpdateNode]
    body: list[ASTNode]
    jump: 'SAIL' | 'LAND' | None
    """
    def __init__(self, inits, condition, updates, body, jump, token=None):
        self.inits = inits          # list[HoistInitNode]
        self.condition = condition  # ASTNode
        self.updates = updates      # list[HoistUpdateNode]
        self.body = body            # list[ASTNode]
        self.jump = jump            # 'SAIL' | 'LAND' | None
        self.token = token


class HoistInitNode(ASTNode):
    """
    One initializer inside HOIST's init section.
    prod 401: COIN id = COIN-lit  (declares new variable)
    prod 402: id = COIN-lit        (assigns to existing variable)

    declares_new: True if the COIN keyword appeared (new loop variable)
    """
    def __init__(self, declares_new, var_name, value, token=None):
        self.declares_new = declares_new  # bool
        self.var_name = var_name          # str
        self.value = value                # LiteralNode (always COIN-lit)
        self.token = token


class HoistUpdateNode(ASTNode):
    """
    One update expression in HOIST's update section.
    prod 416: <hoist-unary>  →  +#id  or  -#id
    prod 417: <hoist-assign> →  id <arith-assign-op> <coin-ope>

    update_kind: 'unary' | 'compound'
    unary_op: '+#' | '-#' | None
    compound_op: '+=', '-=', etc. | None
    var_name: str
    target_kind: 'var' | 'array1d' | 'member'
    index1: ASTNode | None
    member: str | None
    value: ASTNode | None  (None for unary)
    """
    def __init__(self, update_kind, var_name, target_kind, index1, member,
                 unary_op, compound_op, value, token=None):
        self.update_kind = update_kind  # 'unary' | 'compound'
        self.var_name = var_name        # str
        self.target_kind = target_kind  # 'var' | 'array1d' | 'member'
        self.index1 = index1            # ASTNode | None
        self.member = member            # str | None
        self.unary_op = unary_op        # '+#' | '-#' | None
        self.compound_op = compound_op  # str | None
        self.value = value              # ASTNode | None
        self.token = token


# prod 420: HEAVE (while)

class HeaveNode(ASTNode):
    """
    HEAVE (cond) [ body ]
    """
    def __init__(self, condition, body, jump, token=None):
        self.condition = condition  # ASTNode (must be BOOL)
        self.body = body            # list[ASTNode]
        self.jump = jump            # 'SAIL' | 'LAND' | None
        self.token = token


# prod 421: HAUL [ body ] HEAVE (cond)!! (do-while)

class HaulHeaveNode(ASTNode):
    """
    HAUL [ body ] HEAVE (cond)!!
    """
    def __init__(self, body, condition, jump, token=None):
        self.body = body            # list[ASTNode]
        self.condition = condition  # ASTNode (must be BOOL)
        self.jump = jump            # 'SAIL' | 'LAND' | None
        self.token = token


# --- Jump Statements ---
# prods 376–378

class SailNode(ASTNode):
    """SAIL!! — break out of loop or switch."""
    def __init__(self, token=None):
        self.token = token


class LandNode(ASTNode):
    """LAND!! — continue to next iteration (or fall-through in CHART)."""
    def __init__(self, token=None):
        self.token = token


# --- Return Statements ---

class ReturnNode(ASTNode):
    """
    BACK <value>!! — return with a value (inside returning functions).
    value: ASTNode
    """
    def __init__(self, value, token=None):
        self.value = value   # ASTNode
        self.token = token


class BackNode(ASTNode):
    """
    BACK!! — bare return with no value (inside ABYSS functions).
    prod 323: <nonret-back> → BACK!!
    """
    def __init__(self, token=None):
        self.token = token


# --- Unary Increment/Decrement Statements ---
# prods 422–424: +#id  or  -#id  as a standalone statement

class UnaryStmtNode(ASTNode):
    """
    +#x!!   -#arr{0}!!
    operator: '+#' | '-#'
    var_name: str
    target_kind: 'var' | 'array1d' | 'array2d' | 'member'
    index1, index2, member: same as AssignNode
    """
    def __init__(self, operator, var_name, target_kind, index1, index2, member, token=None):
        self.operator = operator        # '+#' | '-#'
        self.var_name = var_name        # str
        self.target_kind = target_kind  # str
        self.index1 = index1            # ASTNode | None
        self.index2 = index2            # ASTNode | None
        self.member = member            # str | None
        self.token = token


# --- Function Call as Statement ---
# prod 355: assign-tail → (<args>)  when used as a statement (not expr)

class FuncCallStmtNode(ASTNode):
    """
    myFunc(arg1, arg2)!!  — a function call used as a standalone statement.
    Wraps FuncCallNode when the call result is discarded.
    """
    def __init__(self, call_expr, token=None):
        self.call_expr = call_expr  # FuncCallNode
        self.token = token


# =============================================================================
# EXPRESSIONS
# All expression nodes return a type string when visited by the analyzer.
# =============================================================================

# --- Literals ---

class LiteralNode(ASTNode):
    """
    A literal value: COIN-lit, DIME-lit, PARCH-lit, SCROLL-lit, AYE, NAY.
    dtype is inferred from which literal kind it is.
    """
    def __init__(self, dtype, value, token=None):
        self.dtype = dtype    # 'COIN' | 'DIME' | 'PARCH' | 'SCROLL' | 'BOOL'
        self.value = value    # Python value (int, float, str, bool)
        self.token = token


# --- Identifiers ---

class IdentNode(ASTNode):
    """
    A bare variable reference: just `id` with no tail.
    The semantic analyzer looks up the name in the symbol table.
    """
    def __init__(self, name, token=None):
        self.name = name     # str
        self.token = token


# --- Array Access ---
# prods 226–231: id{index}  or  id{index}{index}

class ArrayAccessNode(ASTNode):
    """
    arr{0}    →  1D access
    arr{i}{j} →  2D access
    indices: list of 1 or 2 expression nodes (must be COIN type)
    """
    def __init__(self, name, indices, token=None):
        self.name = name        # str
        self.indices = indices  # list[ASTNode] — length 1 or 2
        self.token = token


# --- Struct Member Access ---
# prod 227: id$id

class MemberAccessNode(ASTNode):
    """
    ship$speed   →  access member 'speed' of struct variable 'ship'
    """
    def __init__(self, var_name, member_name, token=None):
        self.var_name = var_name      # str
        self.member_name = member_name  # str (without $)
        self.token = token


# --- SCROLL Character Access ---
# prods 116–119: SCROLL-lit{index}  or  id{index} where id is a SCROLL variable
# This is NOT array access — it indexes into a string and returns PARCH.

class ScrollCharAccessNode(ASTNode):
    """
    "hello"{0}   →  returns 'h' (PARCH)
    msg{i}       →  returns character at i (PARCH), where msg is SCROLL
    Also used in LOCKE constants: SCROLL name = "abc"{0} (a char constant).

    scroll_expr: ASTNode — the string (IdentNode or LiteralNode of SCROLL type)
    index: ASTNode — must resolve to COIN type
    Returns: PARCH
    """
    def __init__(self, scroll_expr, index, token=None):
        self.scroll_expr = scroll_expr  # ASTNode
        self.index = index              # ASTNode (must be COIN)
        self.token = token


# --- String Concatenation ---
# prods 120–121, 256, 263: scroll-ope & scroll-ope & ...
# The & operator in SCROLL context means concatenation, NOT address-of.

class StringConcatNode(ASTNode):
    """
    "Hello" & " " & name   →  concatenates SCROLL values
    operands: list[ASTNode] — all must be SCROLL type
    Returns: SCROLL
    """
    def __init__(self, operands, token=None):
        self.operands = operands  # list[ASTNode] (2 or more)
        self.token = token


# --- Function Call Expression ---
# prod 228, 233: id(<args>)

class FuncCallNode(ASTNode):
    """
    add(x, y)   →  call function 'add' with args [x, y]
    Returns: the function's declared return type
    """
    def __init__(self, name, args, token=None):
        self.name = name   # str
        self.args = args   # list[ASTNode]
        self.token = token


# --- Binary Operations ---
# Arithmetic, relational, equality, logical

class BinaryOpNode(ASTNode):
    """
    left OP right

    operator: '+' | '-' | '*' | '/' | '%' | '^'  (arithmetic, COIN/DIME)
              '<' | '>' | '<=' | '>='             (relational, returns BOOL)
              '==' | '!='                         (equality, returns BOOL)
              '&&' | '||'                         (logical, BOOL operands, returns BOOL)

    Type rules:
      - Arithmetic on COIN×COIN → COIN
      - Arithmetic involving DIME → DIME
      - Relational/equality on numerics → BOOL
      - Equality on PARCH/SCROLL → BOOL
      - Logical on BOOL×BOOL → BOOL
    """
    def __init__(self, left, operator, right, token=None):
        self.left = left          # ASTNode
        self.operator = operator  # str
        self.right = right        # ASTNode
        self.token = token


# --- Unary Operations ---

class UnaryOpNode(ASTNode):
    """
    Prefix unary operators in expressions.
    operator: '-'   (numeric negation, COIN/DIME → same type)
              '!'   (logical NOT, BOOL → BOOL)
              '!#'  (bitwise/logical complement, BOOL → BOOL)
    """
    def __init__(self, operator, operand, token=None):
        self.operator = operator  # str
        self.operand = operand    # ASTNode
        self.token = token


# --- Parenthesized Expression ---
# Grouping: (<value>) — the parser strips parens; no separate node needed.
# The inner expression node is used directly.


# =============================================================================
# QUICK REFERENCE — Node → Grammar Rule mapping
# =============================================================================
#
#  ProgramNode          prod 1
#  AhoyNode             prod 1
#  ConstDeclNode        prods 265–291
#  VarDeclNode          prods 7–11, 328–332
#  ArrayDeclNode        prods 36–47, 66–77, 90–101, 122–133, 202–213
#  StructDefNode        prods 292–298
#  MemberDeclNode       prod 294
#  StructVarDeclNode    prods 333–343
#  PositionalInitNode   prod 340
#  NamedInitNode        prod 341
#  FuncDefNode          prods 48, 78, 102, 134, 214, 307
#  ParamNode            prods 215–218
#  AssignNode           prods 353–359
#  CompoundAssignNode   prods 360–366
#  AskNode              prods 367–370
#  AddressNode          prod 368
#  EchoNode             prods 313, 371
#  LookNode             prods 372–381, 436–444
#  ChartNode            prods 382–399
#  CourseNode           prods 388–395
#  HoistNode            prods 400–419
#  HoistInitNode        prods 401–407
#  HoistUpdateNode      prods 413–419
#  HeaveNode            prod 420
#  HaulHeaveNode        prod 421
#  SailNode             prods 376, 391
#  LandNode             prods 377, 392, 396
#  ReturnNode           prods 48, 78, 102, 134, 214  (BACK <value>!!)
#  BackNode             prods 323–324                 (bare BACK!!)
#  UnaryStmtNode        prods 319, 352, 422–424
#  FuncCallStmtNode     prod 355
#  LiteralNode          prods 22, 59–60, 88, 113, 153–154, 162–163
#  IdentNode            (bare id with no tail)
#  ArrayAccessNode      prods 226, 230–231
#  MemberAccessNode     prod 227
#  ScrollCharAccessNode prods 116–119
#  StringConcatNode     prods 120–121, 256, 263
#  FuncCallNode         prods 228, 233
#  BinaryOpNode         prods 28–35, 64–65, 167–177, 198–201
#  UnaryOpNode          prods 23–25, 152, 155–156
#
# =============================================================================
