# =============================================================================
# sem_error_msg.py — SeaStack Semantic Error Handler
# =============================================================================


class SemanticErrorHandler:

    def __init__(self, source_code: str):
        self.source_code = source_code
        self._lines = source_code.split('\n') if source_code else []

    # =========================================================================
    # HELPERS
    # =========================================================================

    # Return the raw source line at line_num
    def _get_line_content(self, line_num) -> str:
        try:
            ln = int(line_num) - 1
            if 0 <= ln < len(self._lines):
                return self._lines[ln]
        except (TypeError, ValueError):
            pass
        return ""

    # Construct the standard error dict from a token + category + message.
    def _build(self, token, error_type: str, message: str) -> dict:
        line = getattr(token, 'line', '?')
        col  = getattr(token, 'col',  '?')
        actual_line = ""
        if line not in ('?', '-', None):
            actual_line = self._get_line_content(line)
        return {
            'line':        line,
            'col':         col,
            'error_type':  error_type,
            'message':     message,
            'actual_line': actual_line,
        }

    # =========================================================================
    # CATEGORY 1 — UNDECLARED / UNDEFINED
    # =========================================================================

    def undeclared_variable(self, token, name: str) -> dict:
        return self._build(
            token,
            'Undeclared Variable',
            f"Variable '{name}' has not been declared."
        )

    # For undeclared variables found in a specific context (ASK target, HOIST init/update).
    def undeclared_variable_in_context(self, token, name: str, context: str) -> dict:
        return self._build(
            token,
            'Undeclared Variable',
            f"Undeclared variable '{name}' in {context}."
        )

    def undeclared_function(self, token, name: str) -> dict:
        return self._build(
            token,
            'Undeclared Function',
            f"Call to undeclared function '{name}'."
        )

    def undefined_struct_type(self, token, type_name: str) -> dict:
        return self._build(
            token,
            'Undefined Struct Type',
            f"Struct type '{type_name}' has not been defined."
        )

    def not_a_function(self, token, name: str) -> dict:
        return self._build(
            token,
            'Undeclared Function',
            f"'{name}' is not a function and cannot be called."
        )

    def not_an_array(self, token, name: str) -> dict:
        return self._build(
            token,
            'Invalid Array Access',
            f"'{name}' is not an array and cannot be indexed."
        )

    def not_a_struct_variable(self, token, name: str) -> dict:
        return self._build(
            token,
            'Invalid Member Access',
            f"'{name}' is not a struct variable and has no members."
        )

    def unresolvable_struct_type(self, token, type_name: str) -> dict:
        return self._build(
            token,
            'Undefined Struct Type',
            f"Cannot resolve struct type '{type_name}'. "
            f"It may have been declared after use or is missing."
        )

    # =========================================================================
    # CATEGORY 2 — DUPLICATE DECLARATION
    # =========================================================================

    def duplicate_variable(self, token, name: str) -> dict:
        return self._build(
            token,
            'Duplicate Declaration',
            f"Variable '{name}' is already declared in this scope."
        )

    def duplicate_array(self, token, name: str) -> dict:
        return self._build(
            token,
            'Duplicate Declaration',
            f"Array '{name}' is already declared in this scope."
        )

    def duplicate_function(self, token, name: str) -> dict:
        return self._build(
            token,
            'Duplicate Declaration',
            f"Function '{name}' is already declared in this scope."
        )

    def duplicate_const(self, token, name: str) -> dict:
        return self._build(
            token,
            'Duplicate Declaration',
            f"LOCKE constant '{name}' is already declared in this scope."
        )

    # Generic duplicate for identifiers that conflict across kinds (e.g. a struct name clashing with a variable)
    def duplicate_identifier(self, token, name: str) -> dict:
        return self._build(
            token,
            'Duplicate Declaration',
            f"Identifier '{name}' is already declared in this scope."
        )

    def duplicate_parameter(self, token, param_name: str, func_name: str) -> dict:
        return self._build(
            token,
            'Duplicate Declaration',
            f"Parameter name '{param_name}' is duplicated in function '{func_name}'."
        )

    def duplicate_struct_member(self, token, member_name: str, struct_name: str) -> dict:
        return self._build(
            token,
            'Duplicate Declaration',
            f"Struct '{struct_name}' has a duplicate member '{member_name}'."
        )

    def function_name_conflict(self, token, name: str, existing_kind: str) -> dict:
        return self._build(
            token,
            'Duplicate Declaration',
            f"'{name}' is already declared as a '{existing_kind}' and "
            f"cannot also be declared as a function."
        )

    def loop_variable_conflict(self, token, name: str) -> dict:
        return self._build(
            token,
            'Duplicate Declaration',
            f"HOIST loop variable '{name}' conflicts with an existing "
            f"declaration in this scope."
        )

    # =========================================================================
    # CATEGORY 3 — UNINITIALIZED VARIABLE
    # =========================================================================

    def uninitialized_variable(self, token, name: str) -> dict:
        return self._build(
            token,
            'Uninitialized Variable',
            f"Variable '{name}' may be used before it is initialized. "
            f"Assign a value to '{name}' before reading it."
        )

    # =========================================================================
    # CATEGORY 4 — LOCKE (CONST) MODIFICATION
    # =========================================================================

    def locke_assignment(self, token, name: str) -> dict:
        return self._build(
            token,
            'LOCKE Modification',
            f"Cannot assign to LOCKE constant '{name}'. "
            f"LOCKE values are read-only after declaration."
        )

    def locke_operator(self, token, operator: str, name: str) -> dict:
        return self._build(
            token,
            'LOCKE Modification',
            f"Cannot apply operator '{operator}' to LOCKE constant '{name}'. "
            f"LOCKE values are read-only."
        )

    def locke_ask_target(self, token, name: str) -> dict:
        return self._build(
            token,
            'LOCKE Modification',
            f"Cannot use LOCKE constant '{name}' as an ASK input target. "
            f"LOCKE values cannot be overwritten by user input."
        )

    def locke_hoist_init(self, token, name: str) -> dict:
        return self._build(
            token,
            'LOCKE Modification',
            f"Cannot assign to LOCKE constant '{name}' in a HOIST initializer."
        )

    def locke_hoist_update(self, token, name: str) -> dict:
        return self._build(
            token,
            'LOCKE Modification',
            f"Cannot modify LOCKE constant '{name}' in a HOIST update expression."
        )

    # =========================================================================
    # CATEGORY 5 — INVALID LOCKE SCOPE
    # =========================================================================

    def locke_not_global(self, token, name: str) -> dict:
        return self._build(
            token,
            'Invalid LOCKE Scope',
            f"LOCKE constant '{name}' can only be declared at the global scope. "
            f"Move this declaration outside of any function or block."
        )

    # =========================================================================
    # CATEGORY 6 — TYPE MISMATCH
    # =========================================================================

    def type_mismatch_init(self, token, var_name: str, declared_type: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Type Mismatch',
            f"Cannot initialize '{declared_type}' variable '{var_name}' "
            f"with a value of type '{actual_type}'. "
            f"Expected '{declared_type}', got '{actual_type}'."
        )

    def type_mismatch_assign(self, token, target_label: str, target_type: str, value_type: str) -> dict:
        return self._build(
            token,
            'Type Mismatch',
            f"Cannot assign '{value_type}' to '{target_label}' "
            f"(declared as '{target_type}')."
        )

    def type_mismatch_array_element(self, token, arr_name: str, index_str: str, expected_type: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Type Mismatch',
            f"Array '{arr_name}' element {index_str} has type '{actual_type}', "
            f"but the array is declared as '{expected_type}'."
        )

    def type_mismatch_struct_member(self, token, member_name: str, struct_name: str, expected_type: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Type Mismatch',
            f"Member '{member_name}' of struct '{struct_name}' expects "
            f"'{expected_type}', but got '{actual_type}'."
        )

    def type_mismatch_return(self, token, func_name: str, declared_type: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Type Mismatch',
            f"Function '{func_name}' is declared to return '{declared_type}', "
            f"but the BACK expression has type '{actual_type}'."
        )

    def type_mismatch_hoist_init(self, token, var_name: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Type Mismatch',
            f"HOIST initializer for '{var_name}' must be COIN, "
            f"but got '{actual_type}'."
        )

    def type_mismatch_hoist_var(self, token, var_name: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Type Mismatch',
            f"HOIST init variable '{var_name}' must be COIN, "
            f"but it is declared as '{actual_type}'."
        )

    # =========================================================================
    # CATEGORY 7 — INVALID OPERAND TYPE
    # =========================================================================

    def invalid_operand_binary(self, token, operator: str, side: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"Operator '{operator}' requires numeric operands, "
            f"but the {side} operand is '{actual_type}'."
        )

    def invalid_operand_relational(self, token, operator: str, side: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"Relational operator '{operator}' requires numeric operands, "
            f"but the {side} operand is '{actual_type}'."
        )

    def invalid_operand_logical(self, token, operator: str, side: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"Logical operator '{operator}' requires BOOL operands, "
            f"but the {side} operand is '{actual_type}'."
        )

    def invalid_operand_unary_neg(self, token, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"Unary '-' requires a numeric operand, but got '{actual_type}'."
        )

    def invalid_operand_not(self, token, operator: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"Operator '{operator}' requires a BOOL operand, but got '{actual_type}'."
        )

    def invalid_operand_unary_stmt(self, token, operator: str, var_name: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"Operator '{operator}' requires a COIN variable, "
            f"but '{var_name}' is '{actual_type}'."
        )

    def incompatible_comparison(self, token, operator: str, left_type: str, right_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"Cannot compare '{left_type}' and '{right_type}' "
            f"using '{operator}'. Both operands must be the same type."
        )

    def compound_assign_not_numeric(self, token, operator: str, label: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"Compound assignment operator '{operator}' can only be used on "
            f"numeric types, but '{label}' is '{actual_type}'."
        )

    def compound_assign_rhs_not_numeric(self, token, operator: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"The right-hand side of '{operator}' must be numeric, "
            f"but got '{actual_type}'."
        )

    def hoist_update_unary_not_coin(self, token, operator: str, var_name: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"Unary operator '{operator}' in HOIST update requires a COIN variable, "
            f"but '{var_name}' is '{actual_type}'."
        )

    def hoist_update_compound_not_numeric(self, token, var_name: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"HOIST compound update target '{var_name}' must be numeric, "
            f"but got '{actual_type}'."
        )

    def hoist_update_value_not_numeric(self, token, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"HOIST update value must be numeric, but got '{actual_type}'."
        )

    # =========================================================================
    # CATEGORY 8 — ARRAY INDEX
    # =========================================================================

    def array_index_not_coin(self, token, arr_name: str, idx_pos: int, actual_type: str) -> dict:
        pos_label = {0: 'first', 1: 'second'}.get(idx_pos, f'index {idx_pos}')
        return self._build(
            token,
            'Invalid Index Type',
            f"Array index for '{arr_name}' must be COIN, "
            f"but the {pos_label} index is '{actual_type}'."
        )

    def array_index_out_of_bounds(self, token, arr_name: str, dim_label: str, index: int, size: int) -> dict:
        return self._build(
            token,
            'Array Index Out of Bounds',
            f"Array '{arr_name}' {dim_label} {index} is out of bounds. "
            f"Declared size is {size} (valid range: 0–{size - 1})."
        )

    def array_init_too_many_rows(self, token, arr_name: str, given: int, declared: int) -> dict:
        return self._build(
            token,
            'Array Bounds Exceeded',
            f"Array '{arr_name}' initializer has {given} row(s), "
            f"but the array was declared with {declared} row(s)."
        )

    def array_init_row_too_long(self, token, arr_name: str, row: int, given: int, declared: int) -> dict:
        return self._build(
            token,
            'Array Bounds Exceeded',
            f"Array '{arr_name}' row [{row}] has {given} element(s), "
            f"but the declared column size is {declared}."
        )

    def array_init_too_many_elements(self, token, arr_name: str, given: int, declared: int) -> dict:
        return self._build(
            token,
            'Array Bounds Exceeded',
            f"Array '{arr_name}' initializer has {given} element(s), "
            f"but the array was declared with size {declared}."
        )

    def ask_array_index_not_coin(self, token, var_name: str, idx_pos: int, actual_type: str) -> dict:
        pos_label = {0: 'first', 1: 'second'}.get(idx_pos, f'index {idx_pos}')
        return self._build(
            token,
            'Invalid Index Type',
            f"Array index in ASK target for '{var_name}' must be COIN, "
            f"but the {pos_label} index is '{actual_type}'."
        )

    def scroll_char_index_not_coin(self, token, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Index Type',
            f"SCROLL character index must be COIN, but got '{actual_type}'."
        )

    def scroll_char_index_out_of_bounds(self, token, index: int, length: int) -> dict:
        return self._build(
            token,
            'Array Index Out of Bounds',
            f"SCROLL character index {index} is out of bounds "
            f"(string length {length}, valid range: 0–{length - 1})."
        )

    def scroll_char_requires_scroll(self, token, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"Character indexing requires a SCROLL value, but got '{actual_type}'."
        )

    def scroll_concat_requires_scroll(self, token, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Operand Type',
            f"String concatenation '&' requires SCROLL operands, "
            f"but got '{actual_type}'."
        )

    # =========================================================================
    # CATEGORY 9 — STRUCT MEMBERS
    # =========================================================================

    def no_such_member(self, token, struct_type: str, member_name: str) -> dict:
        return self._build(
            token,
            'Undefined Struct Member',
            f"Struct '{struct_type}' has no member '{member_name}'."
        )

    def struct_too_many_inits(self, token, struct_type: str, n_members: int, n_given: int) -> dict:
        return self._build(
            token,
            'Struct Init Error',
            f"Struct '{struct_type}' has {n_members} member(s), "
            f"but {n_given} initializer(s) were provided."
        )

    def struct_positional_overflow(self, token, struct_type: str) -> dict:
        return self._build(
            token,
            'Struct Init Error',
            f"Too many positional initializers for struct '{struct_type}'."
        )

    # =========================================================================
    # CATEGORY 10 — FUNCTION CALLS
    # =========================================================================

    def arg_count_mismatch(self, token, func_name: str, expected: int, actual: int) -> dict:
        return self._build(
            token,
            'Argument Count Mismatch',
            f"Function '{func_name}' expects {expected} argument(s), "
            f"but {actual} were given."
        )

    def arg_type_mismatch(self, token, func_name: str, arg_pos: int, expected_type: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Argument Type Mismatch',
            f"Argument {arg_pos} of '{func_name}': "
            f"expected '{expected_type}', but got '{actual_type}'."
        )

    def abyss_in_expression(self, token, func_name: str) -> dict:
        return self._build(
            token,
            'Invalid Expression Context',
            f"Function '{func_name}' is declared ABYSS (void) and cannot be "
            f"used as an expression. Call it as a standalone statement instead."
        )

    # =========================================================================
    # CATEGORY 11 — RETURN STATEMENTS
    # =========================================================================

    def back_outside_function(self, token) -> dict:
        return self._build(
            token,
            'Invalid Return Context',
            "BACK used outside of a function body."
        )

    def back_value_in_abyss(self, token) -> dict:
        return self._build(
            token,
            'Invalid Return Context',
            "ABYSS functions cannot return a value. "
            "Use bare 'BACK!!' or remove the return statement."
        )

    def back_missing_value(self, token, func_return_type: str) -> dict:
        return self._build(
            token,
            'Invalid Return Context',
            f"BACK!! used inside a '{func_return_type}'-returning function. "
            f"This function must return a '{func_return_type}' value."
        )

    # =========================================================================
    # CATEGORY 12 — JUMP STATEMENTS (SAIL / LAND)
    # =========================================================================

    def sail_outside_loop(self, token) -> dict:
        return self._build(
            token,
            'Invalid Jump Context',
            "SAIL!! can only be used inside a loop."
        )

    def sail_inside_adrift(self, token) -> dict:
        return self._build(
            token,
            'Invalid Jump Context',
            "SAIL!! is not allowed inside an ADRIFT (default) body."
        )

    def land_outside_loop(self, token) -> dict:
        return self._build(
            token,
            'Invalid Jump Context',
            "LAND!! can only be used inside a loop or CHART block."
        )

    # =========================================================================
    # CATEGORY 13 — CONDITION TYPE
    # =========================================================================

    def condition_not_bool(self, token, construct: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid Condition Type',
            f"{construct} condition must resolve to BOOL, "
            f"but got '{actual_type}'."
        )

    # =========================================================================
    # CATEGORY 14 — CHART / COURSE
    # =========================================================================

    def chart_invalid_expr_type(self, token, actual_type: str) -> dict:
        return self._build(
            token,
            'Invalid CHART Expression',
            f"CHART expression must be COIN, PARCH, or SCROLL, "
            f"but got '{actual_type}'."
        )

    def course_type_mismatch(self, token, case_type: str, chart_type: str) -> dict:
        return self._build(
            token,
            'Invalid CHART Expression',
            f"COURSE value type '{case_type}' does not match the "
            f"CHART expression type '{chart_type}'."
        )

    def course_duplicate_label(self, token) -> dict:
        return self._build(
            token,
            'Duplicate COURSE Label',
            "Duplicate COURSE label detected in CHART block. "
            "Each COURSE value must be unique."
        )

    # =========================================================================
    # CATEGORY 15 — FORMAT SPECIFIERS (ASK / ECHO)
    # =========================================================================

    def ask_specifier_count_mismatch(self, token, n_specs: int, n_targets: int) -> dict:
        return self._build(
            token,
            'Format Specifier Mismatch',
            f"ASK format string has {n_specs} specifier(s), "
            f"but {n_targets} target variable(s) were given."
        )

    def ask_specifier_type_mismatch(self, token, specifier: str, expected_type: str, var_name: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Format Specifier Mismatch',
            f"ASK format specifier %{specifier} expects '{expected_type}', "
            f"but target '{var_name}' is '{actual_type}'."
        )

    def echo_specifier_count_mismatch(self, token, n_specs: int, n_args: int) -> dict:
        return self._build(
            token,
            'Format Specifier Mismatch',
            f"ECHO format string has {n_specs} specifier(s), "
            f"but {n_args} argument(s) were given."
        )

    def echo_specifier_type_mismatch(self, token, specifier: str, expected_type: str, actual_type: str) -> dict:
        return self._build(
            token,
            'Format Specifier Mismatch',
            f"ECHO format specifier %{specifier} expects '{expected_type}', "
            f"but got '{actual_type}'."
        )

    # =========================================================================
    # CATEGORY 16 — INTERNAL / FALLBACK
    # =========================================================================

    # Used by _visit_unknown — should never appear in normal operation.
    def internal_no_visitor(self, node_class_name: str) -> dict:
        return {
            'line':        '?',
            'col':         '?',
            'error_type':  'Internal Error',
            'message':     f"No semantic visitor implemented for '{node_class_name}'. "
                           f"This is a compiler bug.",
            'actual_line': '',
        }