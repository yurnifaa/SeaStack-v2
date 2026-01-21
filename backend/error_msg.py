class ErrorHandler:
    
    def __init__(self, source_code):
        self.source_code = source_code
        self.lines = source_code.split('\n') if source_code else []

    # --- HELPER: Format List ---
    @staticmethod
    def _format_list_static(expected_list):
        if not expected_list: return ""
        # Filter None, convert to string, remove duplicates, and sort
        clean = sorted(list(set([str(t) for t in expected_list if t is not None])))
        
        if not clean: return ""
        if len(clean) == 1: return clean[0]
        if len(clean) == 2: return f"{clean[0]} or {clean[1]}"
        return f"{', '.join(clean[:-1])}, or {clean[-1]}"

    # =========================================================================
    # SYNTAX METHODS 
    # =========================================================================
    def _get_line_content(self, line_num):
        if isinstance(line_num, int) and 1 <= line_num <= len(self.lines):
            return self.lines[line_num - 1].strip()
        return ""

    def _format_expected_list(self, expected_list):
        return ErrorHandler._format_list_static(expected_list)

    def _create_error(self, header, message_body, line, col, found_str=None, expected_list=None):
        return {
            "type": "Syntax Error",
            "error_header": header,
            "line": line,
            "col": col,
            "found": found_str if found_str else "Error",
            "expected": expected_list if expected_list else [],
            "message": message_body 
        }

    def get_missing_start_error(self):
        line, col = 1, 1
        header = "Missing Start"
        msg = f"Line {line}, Col {col} | Missing start"
        return self._create_error(header, msg, line, col)

    def get_program_start_error(self, token, expected_tokens):
        line, col = token.line, token.col
        found = token.type
        actual_line = self._get_line_content(line)
        expected_str = self._format_expected_list(expected_tokens)
        
        header = "Program Error"
        msg = (
            f"Line {line}, Col {col} | Program cannot begin with: '{found}'.\n"
            f"'{actual_line}'\n"
            f"Expected any: '{expected_str}'"
        )
        return self._create_error(header, msg, line, col, found, expected_tokens)

    def get_expected_eof_error(self, token):
        line, col = token.line, token.col
        found = token.type
        actual_line = self._get_line_content(line)
        
        header = "Unexpected Token"
        msg = (
            f"Line {line}, Col {col} | Unexpected token: '{found}' after AHOY.\n"
            f"'{actual_line}'\n"
            f"Expected any: 'End Of File/EOF'"
        )
        return self._create_error(header, msg, line, col, found, ["End Of File/EOF"])

    def get_invalid_token_error(self, token, expected_tokens):
        line, col = token.line, token.col
        found = token.type
        actual_line = self._get_line_content(line)
        expected_str = self._format_expected_list(expected_tokens)

        header = "Invalid Token"
        msg = (
            f"Line {line}, Col {col} | Invalid token: {found}.\n"
            f"'{actual_line}'\n"
            f"Expected any: '{expected_str}'"
        )
        return self._create_error(header, msg, line, col, found, expected_tokens)

    def get_missing_token_error(self, current_token, expected_token_type):
        if current_token:
            line, col = current_token.line, current_token.col
            found = current_token.type
            actual_line = self._get_line_content(line)
        else:
            line, col = "?", "?"
            found = "EOF"
            actual_line = ""

        header = "Missing Token"
        msg = (
            f"Line {line}, Col {col} | Missing token after Line {line}, Col {col}: {expected_token_type}.\n"
            f"'{actual_line}'"
        )
        return self._create_error(header, msg, line, col, found, [expected_token_type])

    def get_unexpected_token_error(self, token, expected_tokens):
        line, col = token.line, token.col
        found = token.type
        actual_line = self._get_line_content(line)
        expected_str = self._format_expected_list(expected_tokens)

        header = "Unexpected Token"
        msg = (
            f"Line {line}, Col {col} | Unexpected token at Line {line}, Col {col}: {found}.\n"
            f"'{actual_line}'\n"
            f"Expected any: '{expected_str}'"
        )
        return self._create_error(header, msg, line, col, found, expected_tokens)

    def get_custom_error(self, token, message):
        if token:
            line, col = token.line, token.col
            found = token.type
        else:
            line, col = "?", "?"
            found = "Unknown"

        header = "Syntax Error"
        msg = f"Line {line}, Col {col} | {message}"
        
        return self._create_error(header, msg, line, col, found)