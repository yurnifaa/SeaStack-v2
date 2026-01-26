class ErrorHandler:
    
    # =========================================================================
    # CENTRALIZED ERROR MESSAGE
    # =========================================================================
    ERROR_TEMPLATES = {
        "UNEXPECTED_TOKEN": (
            "Line {line}, Col {col} | Unexpected token: '{found}'.\n"
            "'{source_line}'\n"
            "Expected: {expected}"
        ),
        "MISPLACED_TOKEN": (
            "Line {line}, Col {col} | Misplaced token: '{found}'.\n"
            "'{source_line}'\n"
            "Expected: '{expected}'"
        ),
        "MISSING_MAIN_AHOY": (
            "Line {line}, Col {col} | Missing Main Function 'AHOY'.\n"
            "'{source_line}'\n"
            "Expected: 'AHOY' to define the entry point."
        ),
        "PROGRAM_START_ERROR": (
            "Line {line}, Col {col} | Program cannot begin with: '{found}'.\n"
            "'{source_line}'\n"
            "Expected: {expected}" # Usually Global Decs or AHOY
        ),
        "UNEXPECTED_EOF": (
            "Line {line}, Col {col} | Unexpected End Of File.\n"
            "Expected: {expected}" # e.g., ']' or more statements
        ),
        "MISSING_START": "Line {line}, Col {col} | Missing Start. Source code is empty.",
        "EXPECTED_EOF": (
            "Line {line}, Col {col} | Unexpected token: '{found}' after AHOY.\n"
            "'{source_line}'\n"
            "Expected: 'End Of File'"
        )
    }

    def __init__(self, source_code):
        self.source_code = source_code
        self.lines = source_code.split('\n') if source_code else []

    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    @staticmethod
    def _format_list_static(expected_list):
        # Formats a list of tokens into a readable string (e.g., 'A, B, or C').
        if not expected_list: 
            return "Nothing"
        
        # Filter None and convert to string
        clean = sorted(list(set([str(t) for t in expected_list if t is not None])))
        
        if not clean: return "Nothing"
        if len(clean) == 1: return f"'{clean[0]}'"
        if len(clean) == 2: return f"'{clean[0]}' or '{clean[1]}'"
        return f"'{', '.join(clean[:-1])}', or '{clean[-1]}'"

    def _get_line_content(self, line_num):
        # Safely retrieves the line content for context display.
        if isinstance(line_num, int) and 1 <= line_num <= len(self.lines):
            return self.lines[line_num - 1].strip()
        return ""

    def _create_error(self, header, message_body, line, col, found_str=None, expected_list=None):
        # Standardizes the error dictionary return format.
        return {
            "type": "Syntax Error",
            "error_header": header,
            "line": line,
            "col": col,
            "found": found_str if found_str else "Error",
            "expected": expected_list if expected_list else [],
            "message": message_body 
        }

    # =========================================================================
    # ERROR GENERATION METHODS
    # =========================================================================

    # ==========================================
    # Case 2: Missing Main/Start (Empty File)
    # ==========================================
    def get_missing_start_error(self):
        msg = self.ERROR_TEMPLATES["MISSING_START"].format(line=1, col=1)
        return self._create_error("Missing Start. Source code is empty.", msg, 1, 1)

    # ==========================================
    # Case 4: Program cannot begin with <token>
    # ==========================================
    def get_program_start_error(self, token, expected_tokens):
        if token:
            line, col = token.line, token.col
            found = token.type
            actual_line = self._get_line_content(line)
        else:
            line, col = "?", "?"
            found = "EOF"
            actual_line = ""
        
        expected_str = self._format_list_static(expected_tokens)
        msg = self.ERROR_TEMPLATES["PROGRAM_START_ERROR"].format(
            line=line, col=col, found=found, source_line=actual_line, expected=expected_str
        )
        
        return self._create_error("Unexpected Beginning Token:", msg, line, col, found, expected_tokens)

    def get_expected_eof_error(self, token):
        # Handled at the end of parse() if tokens remain.
        if token:
            line, col = token.line, token.col
            found = token.type
            actual_line = self._get_line_content(line)
        else:
            line, col = "?", "?"
            found = "Unknown"
            actual_line = ""
        
        msg = self.ERROR_TEMPLATES["EXPECTED_EOF"].format(
            line=line, col=col, found=found, source_line=actual_line
        )
        return self._create_error("Unexpected Token", msg, line, col, found, ["End Of File"])

    def get_invalid_token_error(self, token, expected_tokens):
        # Case 1 & 3: Unexpected Tokens & Unexpected End Of File.
        # Triggered when PREDICT table lookup fails.
        expected_str = self._format_list_static(expected_tokens)

        if token:
            # Case 1: Unexpected Token
            line, col = token.line, token.col
            found = token.type
            actual_line = self._get_line_content(line)
            
            msg = self.ERROR_TEMPLATES["UNEXPECTED_TOKEN"].format(
                line=line, col=col, found=found, source_line=actual_line, expected=expected_str
            )
            return self._create_error("Unexpected token:", msg, line, col, found, expected_tokens)
        
        else:
        # ==================================================================
        # Case 3: Unexpected End Of File
        # We hit EOF but expected something else (like ']' or statements)
        # ==================================================================
            line = len(self.lines) if self.lines else 1
            col = "End"
            found = "End Of File"
            
            msg = self.ERROR_TEMPLATES["UNEXPECTED_EOF"].format(
                line=line, col=col, expected=expected_str
            )
            return self._create_error("Unexpected EOF or", msg, line, col, found, expected_tokens)

    def get_missing_token_error(self, current_token, expected_token_type):
        # Case 5: Misplaced Token / Missing specific token.
        # Triggered by eat() failures.
        if current_token:
            line, col = current_token.line, current_token.col
            found = current_token.type
            actual_line = self._get_line_content(line)
        else:
            line = len(self.lines) if self.lines else 1
            col = "End"
            found = "End Of File"
            actual_line = ""

        # Special Case: Missing Main AHOY
        # If the parser specifically tried to eat "AHOY" and failed.
        if expected_token_type == "AHOY":
            msg = self.ERROR_TEMPLATES["MISSING_MAIN_AHOY"].format(
                line=line, col=col, source_line=actual_line
            )
            return self._create_error("Missing Main Function 'AHOY'", msg, line, col, found, [expected_token_type])

        # Standard Misplaced Token
        msg = self.ERROR_TEMPLATES["MISPLACED_TOKEN"].format(
            line=line, col=col, found=found, source_line=actual_line, expected=expected_token_type
        )
        return self._create_error("Misplaced Token:", msg, line, col, found, [expected_token_type])

    def get_unexpected_token_error(self, token, expected_tokens):
        # Wrapper for get_invalid_token_error to maintain backward compatibility if needed.
        return self.get_invalid_token_error(token, expected_tokens)

    def get_custom_error(self, token, message):
        # Generic fallback error.
        if token:
            line, col = token.line, token.col
            found = token.type
        else:
            line, col = "?", "?"
            found = "Unknown"

        header = "Syntax Error"
        msg = f"Line {line}, Col {col} | {message}"
        
        return self._create_error(header, msg, line, col, found)