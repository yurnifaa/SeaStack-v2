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

    def _get_line_content(self, line_num) -> str:
        try:
            ln = int(line_num) - 1
            if 0 <= ln < len(self._lines):
                return self._lines[ln]
        except (TypeError, ValueError):
            pass
        return ""

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
        return self._build(token, 'Undeclared Variable',
            f"Variable '{name}' has not been declared.")

    def undeclared_variable_in_context(self, token, name: str, context: str) -> dict:
        return self._build(token, 'Undeclared Variable',
            f"Undeclared variable '{name}' in {context}.")

    def undeclared_function(self, token, name: str) -> dict:
        return self._build(token, 'Undeclared Function',
            f"'{name}' has not been declared as a function.")

    def undefined_struct_type(self, token, type_name: str) -> dict:
        return self._build(token, 'Undefined Struct Type',
            f"Struct type '{type_name}' has not been defined.")

    def not_a_function(self, token, name: str) -> dict:
        return self._build(token, 'Undeclared Function',
            f"'{name}' is not a function.")

    def not_an_array(self, token, name: str) -> dict:
        return self._build(token, 'Invalid Array Access',
            f"'{name}' is not an array.")

    def not_a_struct_variable(self, token, name: str) -> dict:
        return self._build(token, 'Invalid Member Access',
            f"'{name}' is not a struct.")

    def unresolvable_struct_type(self, token, type_name: str) -> dict:
        return self._build(token, 'Undefined Struct Type',
            f"Struct type '{type_name}' is undeclared or used before definition.")

    # =========================================================================
    # CATEGORY 2 — DUPLICATE DECLARATION
    # =========================================================================

    def duplicate_variable(self, token, name: str) -> dict:
        return self._build(token, 'Duplicate Declaration',
            f"Variable '{name}' is already declared in this scope.")

    def duplicate_array(self, token, name: str) -> dict:
        return self._build(token, 'Duplicate Declaration',
            f"Array '{name}' is already declared in this scope.")

    def duplicate_function(self, token, name: str) -> dict:
        return self._build(token, 'Duplicate Declaration',
            f"Function '{name}' is already declared in this scope.")

    def duplicate_const(self, token, name: str) -> dict:
        return self._build(token, 'Duplicate Declaration',
            f"LOCKE constant '{name}' is already declared in this scope.")

    def duplicate_identifier(self, token, name: str) -> dict:
        return self._build(token, 'Duplicate Declaration',
            f"Identifier '{name}' is already declared in this scope.")

    def duplicate_parameter(self, token, param_name: str, func_name: str) -> dict:
        return self._build(token, 'Duplicate Declaration',
            f"Parameter '{param_name}' is duplicated in function '{func_name}'.")

    def duplicate_struct_member(self, token, member_name: str, struct_name: str) -> dict:
        return self._build(token, 'Duplicate Declaration',
            f"Struct '{struct_name}' already has a member '{member_name}'.")

    def function_name_conflict(self, token, name: str, existing_kind: str) -> dict:
        return self._build(token, 'Duplicate Declaration',
            f"'{name}' is already declared as a '{existing_kind}'.")

    def loop_variable_conflict(self, token, name: str) -> dict:
        return self._build(token, 'Duplicate Declaration',
            f"HOIST variable '{name}' is already declared in this scope.")

    # =========================================================================
    # CATEGORY 3 — UNINITIALIZED VARIABLE
    # =========================================================================

    def uninitialized_variable(self, token, name: str) -> dict:
        return self._build(token, 'Uninitialized Variable',
            f"Variable '{name}' is used before being initialized.")

    # =========================================================================
    # CATEGORY 4 — LOCKE (CONST) MODIFICATION
    # =========================================================================

    def locke_assignment(self, token, name: str) -> dict:
        return self._build(token, 'LOCKE Modification',
            f"'{name}' is a LOCKE constant and cannot be reassigned.")

    def locke_operator(self, token, operator: str, name: str) -> dict:
        return self._build(token, 'LOCKE Modification',
            f"'{name}' is a LOCKE constant. Operator '{operator}' cannot modify it.")

    def locke_ask_target(self, token, name: str) -> dict:
        return self._build(token, 'LOCKE Modification',
            f"'{name}' is a LOCKE constant and cannot be an ASK target.")

    def locke_hoist_init(self, token, name: str) -> dict:
        return self._build(token, 'LOCKE Modification',
            f"Cannot assign to LOCKE constant '{name}' in a HOIST initializer.")

    def locke_hoist_update(self, token, name: str) -> dict:
        return self._build(token, 'LOCKE Modification',
            f"Cannot modify LOCKE constant '{name}' in a HOIST update.")

    # =========================================================================
    # CATEGORY 5 — INVALID LOCKE SCOPE
    # =========================================================================

    def locke_not_global(self, token, name: str) -> dict:
        return self._build(token, 'Invalid LOCKE Scope',
            f"LOCKE constant '{name}' must be declared at global scope.")

    # =========================================================================
    # CATEGORY 6 — TYPE MISMATCH
    # =========================================================================

    def type_mismatch_init(self, token, var_name: str, declared_type: str, actual_type: str) -> dict:
        return self._build(token, 'Type Mismatch',
            f"Cannot initialize '{declared_type}' '{var_name}' with '{actual_type}'.")

    def type_mismatch_assign(self, token, target_label: str, target_type: str, value_type: str) -> dict:
        return self._build(token, 'Type Mismatch',
            f"Cannot assign '{value_type}' to '{target_label}' (declared as '{target_type}').")

    def type_mismatch_array_element(self, token, arr_name: str, index_str: str, expected_type: str, actual_type: str) -> dict:
        return self._build(token, 'Type Mismatch',
            f"'{arr_name}' expects '{expected_type}' but element {index_str} is '{actual_type}'.")

    def type_mismatch_struct_member(self, token, member_name: str, struct_name: str, expected_type: str, actual_type: str) -> dict:
        return self._build(token, 'Type Mismatch',
            f"Member '{member_name}' of '{struct_name}' expects '{expected_type}', got '{actual_type}'.")

    def type_mismatch_return(self, token, func_name: str, declared_type: str, actual_type: str) -> dict:
        return self._build(token, 'Type Mismatch',
            f"'{func_name}' returns '{declared_type}', but BACK has '{actual_type}'.")

    def type_mismatch_hoist_init(self, token, var_name: str, actual_type: str) -> dict:
        return self._build(token, 'Type Mismatch',
            f"HOIST initializer for '{var_name}' must be COIN, got '{actual_type}'.")

    def type_mismatch_hoist_var(self, token, var_name: str, actual_type: str) -> dict:
        return self._build(token, 'Type Mismatch',
            f"HOIST variable '{var_name}' must be COIN, not '{actual_type}'.")

    # =========================================================================
    # CATEGORY 7 — INVALID OPERAND TYPE
    # =========================================================================

    def invalid_operand_binary(self, token, operator: str, side: str, actual_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"'{operator}' requires numeric operands, but {side} is '{actual_type}'.")

    def invalid_operand_relational(self, token, operator: str, side: str, actual_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"'{operator}' requires numeric operands, but {side} is '{actual_type}'.")

    def invalid_operand_logical(self, token, operator: str, side: str, actual_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"'{operator}' requires BOOL operands, but {side} is '{actual_type}'.")

    def invalid_operand_unary_neg(self, token, actual_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"Unary '-' requires a numeric operand, but got '{actual_type}'.")

    def invalid_operand_not(self, token, operator: str, actual_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"'{operator}' requires a BOOL operand, but got '{actual_type}'.")

    def invalid_operand_unary_stmt(self, token, operator: str, var_name: str, actual_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"'{operator}' requires a COIN variable, but '{var_name}' is '{actual_type}'.")

    def incompatible_comparison(self, token, operator: str, left_type: str, right_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"Cannot compare '{left_type}' with '{right_type}' using '{operator}'.")

    def compound_assign_not_numeric(self, token, operator: str, label: str, actual_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"'{operator}' requires a numeric type, but '{label}' is '{actual_type}'.")

    def compound_assign_rhs_not_numeric(self, token, operator: str, actual_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"Right-hand side of '{operator}' must be numeric, got '{actual_type}'.")

    def hoist_update_unary_not_coin(self, token, operator: str, var_name: str, actual_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"HOIST update '{operator}' requires COIN, but '{var_name}' is '{actual_type}'.")

    def hoist_update_compound_not_numeric(self, token, var_name: str, actual_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"HOIST update target '{var_name}' must be numeric, not '{actual_type}'.")

    def hoist_update_value_not_numeric(self, token, actual_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"HOIST update value must be numeric, but got '{actual_type}'.")

    # =========================================================================
    # CATEGORY 8 — ARRAY INDEX
    # =========================================================================

    def array_index_not_coin(self, token, arr_name: str, idx_pos: int, actual_type: str) -> dict:
        pos_label = {0: 'first', 1: 'second'}.get(idx_pos, f'index {idx_pos}')
        return self._build(token, 'Invalid Index Type',
            f"Index for '{arr_name}' must be COIN, but {pos_label} index is '{actual_type}'.")

    def array_index_out_of_bounds(self, token, arr_name: str, _dim_label: str, index: int, size: int) -> dict:
        return self._build(token, 'Array Index Out of Bounds',
            f"'{arr_name}' index {index} is out of bounds (valid: 0–{size - 1}).")

    def array_init_too_many_rows(self, token, arr_name: str, given: int, declared: int) -> dict:
        return self._build(token, 'Array Bounds Exceeded',
            f"'{arr_name}' has {declared} row(s) but {given} were given.")

    def array_init_row_too_long(self, token, arr_name: str, row: int, given: int, declared: int) -> dict:
        return self._build(token, 'Array Bounds Exceeded',
            f"'{arr_name}' row [{row}] has {given} element(s), expected {declared}.")

    def array_init_too_many_elements(self, token, arr_name: str, given: int, declared: int) -> dict:
        return self._build(token, 'Array Bounds Exceeded',
            f"'{arr_name}' has {declared} element(s) but {given} were given.")

    def ask_array_index_not_coin(self, token, var_name: str, idx_pos: int, actual_type: str) -> dict:
        pos_label = {0: 'first', 1: 'second'}.get(idx_pos, f'index {idx_pos}')
        return self._build(token, 'Invalid Index Type',
            f"ASK index for '{var_name}' must be COIN, but {pos_label} index is '{actual_type}'.")

    def scroll_char_index_not_coin(self, token, actual_type: str) -> dict:
        return self._build(token, 'Invalid Index Type',
            f"SCROLL character index must be COIN, but got '{actual_type}'.")

    def scroll_char_index_out_of_bounds(self, token, index: int, length: int) -> dict:
        return self._build(token, 'Array Index Out of Bounds',
            f"SCROLL index {index} is out of bounds (valid: 0–{length - 1}).")

    def scroll_char_requires_scroll(self, token, actual_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"Character indexing requires a SCROLL value, but got '{actual_type}'.")

    def scroll_concat_requires_scroll(self, token, actual_type: str) -> dict:
        return self._build(token, 'Invalid Operand Type',
            f"'&' requires SCROLL operands, but got '{actual_type}'.")

    # =========================================================================
    # CATEGORY 9 — STRUCT MEMBERS
    # =========================================================================

    def no_such_member(self, token, struct_type: str, member_name: str) -> dict:
        return self._build(token, 'Undefined Struct Member',
            f"Struct '{struct_type}' has no member '{member_name}'.")

    def struct_too_many_inits(self, token, struct_type: str, n_members: int, n_given: int) -> dict:
        return self._build(token, 'Struct Init Error',
            f"'{struct_type}' has {n_members} member(s), but {n_given} were given.")

    def struct_positional_overflow(self, token, struct_type: str) -> dict:
        return self._build(token, 'Struct Init Error',
            f"Too many initializers for struct '{struct_type}'.")

    # =========================================================================
    # CATEGORY 10 — FUNCTION CALLS
    # =========================================================================

    def arg_count_mismatch(self, token, func_name: str, expected: int, actual: int) -> dict:
        return self._build(token, 'Argument Count Mismatch',
            f"'{func_name}' expects {expected} argument(s), but {actual} were given.")

    def arg_type_mismatch(self, token, func_name: str, arg_pos: int, expected_type: str, actual_type: str) -> dict:
        return self._build(token, 'Argument Type Mismatch',
            f"Argument {arg_pos} of '{func_name}': expected '{expected_type}', got '{actual_type}'.")

    def abyss_in_expression(self, token, func_name: str) -> dict:
        return self._build(token, 'Invalid Expression Context',
            f"'{func_name}' is ABYSS and has no return value.")

    # =========================================================================
    # CATEGORY 11 — RETURN STATEMENTS
    # =========================================================================

    def back_outside_function(self, token) -> dict:
        return self._build(token, 'Invalid Return Context',
            "BACK used outside of a function body.")

    def back_value_in_abyss(self, token) -> dict:
        return self._build(token, 'Invalid Return Context',
            "ABYSS functions cannot return a value. Use BACK!! with no value.")

    def back_missing_value(self, token, func_return_type: str) -> dict:
        return self._build(token, 'Invalid Return Context',
            f"BACK!! must return a '{func_return_type}' value here.")

    # =========================================================================
    # CATEGORY 12 — JUMP STATEMENTS (SAIL / LAND)
    # =========================================================================

    def sail_outside_loop(self, token) -> dict:
        return self._build(token, 'Invalid Jump Context',
            "SAIL!! can only be used inside a loop.")

    def sail_inside_adrift(self, token) -> dict:
        return self._build(token, 'Invalid Jump Context',
            "SAIL!! is not allowed inside an ADRIFT block.")

    def land_outside_loop(self, token) -> dict:
        return self._build(token, 'Invalid Jump Context',
            "LAND!! can only be used inside a loop or CHART block.")

    # =========================================================================
    # CATEGORY 13 — CONDITION TYPE
    # =========================================================================

    def condition_not_bool(self, token, construct: str, actual_type: str) -> dict:
        return self._build(token, 'Invalid Condition Type',
            f"{construct} condition must be BOOL, but got '{actual_type}'.")

    # =========================================================================
    # CATEGORY 14 — CHART / COURSE
    # =========================================================================

    def chart_invalid_expr_type(self, token, actual_type: str) -> dict:
        return self._build(token, 'Invalid CHART Expression',
            f"CHART expression must be COIN, PARCH, or SCROLL, but got '{actual_type}'.")

    def course_type_mismatch(self, token, case_type: str, chart_type: str) -> dict:
        return self._build(token, 'Invalid CHART Expression',
            f"COURSE type '{case_type}' doesn't match CHART type '{chart_type}'.")

    def course_duplicate_label(self, token) -> dict:
        return self._build(token, 'Duplicate COURSE Label',
            "Duplicate COURSE label. Each COURSE value must be unique.")

    # =========================================================================
    # CATEGORY 15 — FORMAT SPECIFIERS (ASK / ECHO)
    # =========================================================================

    def ask_specifier_count_mismatch(self, token, n_specs: int, n_targets: int) -> dict:
        return self._build(token, 'Format Specifier Mismatch',
            f"ASK has {n_specs} specifier(s) but {n_targets} target variable(s) were given.")

    def ask_specifier_type_mismatch(self, token, specifier: str, expected_type: str, var_name: str, actual_type: str) -> dict:
        return self._build(token, 'Format Specifier Mismatch',
            f"ASK %{specifier} expects '{expected_type}', but '{var_name}' is '{actual_type}'.")

    def echo_specifier_count_mismatch(self, token, n_specs: int, n_args: int) -> dict:
        return self._build(token, 'Format Specifier Mismatch',
            f"ECHO has {n_specs} specifier(s) but {n_args} argument(s) were given.")

    def echo_specifier_type_mismatch(self, token, specifier: str, expected_type: str, actual_type: str) -> dict:
        return self._build(token, 'Format Specifier Mismatch',
            f"ECHO %{specifier} expects '{expected_type}', but got '{actual_type}'.")

    # =========================================================================
    # CATEGORY 16 — INTERNAL / FALLBACK
    # =========================================================================

    def internal_no_visitor(self, node_class_name: str) -> dict:
        return {
            'line':        '?',
            'col':         '?',
            'error_type':  'Internal Error',
            'message':     f"No visitor for '{node_class_name}'. This is a compiler bug.",
            'actual_line': '',
        }