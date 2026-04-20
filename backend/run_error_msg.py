# =============================================================================
# run_error_msg.py — SeaStack Runtime Error Handler
# =============================================================================

import re
import traceback


# =============================================================================
#  Messages
# =============================================================================

class RuntimeErrorMessages:

    @staticmethod
    def division_by_zero():
        return "Division by Zero", "Cannot divide by zero."

    @staticmethod
    def index_out_of_bounds():
        return "Index Out of Bounds", "Array index is out of bounds."

    @staticmethod
    def key_error(exc_msg: str):
        return "Undefined Member", f"Struct field {exc_msg} does not exist."

    @staticmethod
    def name_error(var_name: str):
        return "Undefined Variable", f"Variable '{var_name}' is not defined."

    @staticmethod
    def value_error(exc_msg: str):
        m = exc_msg.lower()
        if 'aye' in m or 'nay' in m:
            return "Value Error", "Expected a BOOL (AYE or NAY)."
        if 'coin input exceeds' in m:
            return "Value Error", "COIN input exceeds 16 digits."
        if 'dime input exceeds' in m:
            return "Value Error", "DIME input exceeds 8 digits."
        if 'int' in m or 'base 10' in m:
            return "Value Error", "Expected a COIN but got an incompatible value."
        if 'float' in m:
            return "Value Error", "Expected a DIME but got an incompatible value."
        return "Value Error", "Invalid value encountered during execution."

    @staticmethod
    def overflow_error():
        return "Overflow Error", "Number is too large to process."

    @staticmethod
    def recursion_error():
        return "Stack Overflow", "Too many nested function calls (infinite recursion?)."

    @staticmethod
    def memory_error():
        return "Memory Error", "Program ran out of memory."

    @staticmethod
    def attribute_error_none():
        return "Null Dereference", "Accessed a value that has not been set (null)."

    @staticmethod
    def attribute_error():
        return "Attribute Error", "Accessed an attribute that does not exist."

    @staticmethod
    def type_error():
        return "Type Error", "A value of the wrong type was used in an operation."

    @staticmethod
    def syntax_error(exc_msg: str, sanitize_fn):
        if 'break' in exc_msg:
            return "Syntax Error", "LAND!! can only be used inside a loop or CHART block."
        if 'continue' in exc_msg:
            return "Syntax Error", "SAIL!! can only be used inside a loop."
        if 'return' in exc_msg:
            return "Syntax Error", "BACK can only be used inside a function."
        return "Syntax Error", sanitize_fn(exc_msg)

    @staticmethod
    def timeout():
        return "Timeout Error", "Program ran for over 20 minutes and was stopped. Check for infinite loops."

    @staticmethod
    def unknown(exc_msg: str, sanitize_fn):
        return "Runtime Error", sanitize_fn(exc_msg)


# =============================================================================
#  Helpers
# =============================================================================

def _sanitize_py_message(msg):
    replacements = [
        ("'break'",    "LAND!!"),  ("'continue'", "SAIL!!"),  ("'return'", "BACK"),
        ("'int'",      "'COIN'"),  ("'float'",    "'DIME'"),   ("'str'",    "'SCROLL'"),
        ("'bool'",     "'BOOL'"),  ("'list'",     "'array'"),  ("'dict'",   "'struct'"),
        (" int ",      " COIN "),  (" float ",    " DIME "),   (" str ",    " SCROLL "),
        (" bool ",     " BOOL "),  (" list ",     " array "),
        ("<string>",   "the program"),
        ("<module>",   "the program"),
    ]
    for old, new in replacements:
        msg = msg.replace(old, new)
    return msg


def _extract_tokens(code_line):
    # Capture ALL alphanumeric identifiers (including Uppercase and CamelCase)
    tokens = [m for m in re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\b', code_line)
            if m.lower() not in {'print', 'input', 'int', 'float', 'str', 'bool',
                         'true', 'false', 'none', 'not', 'and', 'or',
                         'if', 'else', 'while', 'for', 'return', 'def',
                         'pass', 'break', 'continue', 'math', 'sys',
                         'end', 'format', 'self', 'flush', 'len', 'type',
                         'list', 'dict', 'set', 'tuple', 'Exception'}]
    
    # Capture string literals
    for match in re.finditer(r'["\'](.*?)["\']', code_line):
        val = match.group(1).strip()
        if val:
            tokens.append(val)
            
    # Capture numbers
    tokens.extend(re.findall(r'\b(\d+(?:\.\d+)?)\b', code_line))
    
    return tokens


# =============================================================================
#  Main entry point — called by server.py
# =============================================================================

def map_runtime_error(exc, source_code, generated_code, exec_globals=None):
    tb      = traceback.extract_tb(exc.__traceback__)
    py_line = None
    for frame in reversed(tb):
        if frame.filename == '<string>':
            py_line = frame.lineno
            break

    exc_msg   = str(exc)
    sanitized = lambda m: _sanitize_py_message(re.sub(r'\s*\(<[^)]*>,\s*line\s*\d+\)', '', m).strip())

    if isinstance(exc, ZeroDivisionError):
        error_type, message = RuntimeErrorMessages.division_by_zero()
    elif isinstance(exc, IndexError):
        error_type, message = RuntimeErrorMessages.index_out_of_bounds()
    elif isinstance(exc, KeyError):
        error_type, message = RuntimeErrorMessages.key_error(exc_msg)
    elif isinstance(exc, NameError):
        match    = re.search(r"name '(\w+)' is not defined", exc_msg)
        var_name = match.group(1) if match else "unknown"
        error_type, message = RuntimeErrorMessages.name_error(var_name)
    elif isinstance(exc, ValueError):
        error_type, message = RuntimeErrorMessages.value_error(exc_msg)
    elif isinstance(exc, OverflowError):
        error_type, message = RuntimeErrorMessages.overflow_error()
    elif isinstance(exc, RecursionError):
        error_type, message = RuntimeErrorMessages.recursion_error()
    elif isinstance(exc, MemoryError):
        error_type, message = RuntimeErrorMessages.memory_error()
    elif isinstance(exc, AttributeError):
        if 'nonetype' in exc_msg.lower():
            error_type, message = RuntimeErrorMessages.attribute_error_none()
        else:
            error_type, message = RuntimeErrorMessages.attribute_error()
    elif isinstance(exc, TypeError):
        error_type, message = RuntimeErrorMessages.type_error()
    elif isinstance(exc, SyntaxError):
        error_type, message = RuntimeErrorMessages.syntax_error(exc_msg, sanitized)
    else:
        error_type, message = RuntimeErrorMessages.unknown(exc_msg, sanitized)

    # Map to SeaStack source line
    ss_line     = "-"
    ss_col      = "-"
    actual_line = ""

    if exec_globals:
        raw_line = exec_globals.get('_ss_line', 0)
        raw_col  = exec_globals.get('_ss_col',  0)
        if raw_line and int(raw_line) > 0:
            ss_line = str(raw_line)
            if raw_col:
                ss_col = str(raw_col)
            src_lines = source_code.split('\n') if source_code else []
            idx = int(raw_line) - 1
            if 0 <= idx < len(src_lines):
                actual_line = src_lines[idx]

    if ss_line == "-" and py_line and generated_code:
        gen_lines = generated_code.split('\n')
        if 0 < py_line <= len(gen_lines):
            py_code_line = gen_lines[py_line - 1].strip()
            src_lines    = source_code.split('\n') if source_code else []
            
            # Use our new robust token extractor
            search_tokens = _extract_tokens(py_code_line)
            
            for si, sl in enumerate(src_lines):
                stripped = sl.strip()
                # Ignore empty lines and SeaStack comments
                if stripped and not stripped.startswith('~'):
                    # Check if ANY significant token from the python line is in the SeaStack line
                    if search_tokens and any(w in stripped for w in search_tokens):
                        ss_line     = str(si + 1)
                        actual_line = sl
                        break

    return {
        "line":        ss_line,
        "col":         ss_col,
        "found":       error_type,
        "expected":    [],
        "message":     message,
        "actual_line": actual_line,
        "phase":       "Runtime",
        "error_type":  error_type,
    }


def map_timeout_error():
    error_type, message = RuntimeErrorMessages.timeout()
    return {
        "line":        "-",
        "col":         "-",
        "error_type":  error_type,
        "message":     message,
        "actual_line": "",
        "phase":       "Runtime",
    }
