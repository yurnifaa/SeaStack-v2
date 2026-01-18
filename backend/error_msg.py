# backend/error_msg.py

class ErrorHandler:
    # --- ERROR TYPES ---
    TYPE_SYNTAX = "Syntax Error"
    TYPE_LEXICAL = "Lexical Error"
    
    # --- SYNTAX SUB-TYPES ---
    ERR_UNEXPECTED_TOKEN = "Unexpected Token"
    ERR_UNEXPECTED_EOF = "Unexpected End of File"
    ERR_MISSING_MAIN = "Missing Main Function"

    @staticmethod
    def get_lexical_error(line, col, invalid_char, expected_desc="Valid Token"):
        """
        Generates the standard dictionary for Lexical Errors.
        Format: Invalid character '<token>'
        """
        found_str = f"Invalid character '{invalid_char}'"
        
        return {
            "type": ErrorHandler.TYPE_LEXICAL,
            "line": line,
            "col": col,
            "found": found_str, # Used for display
            "expected": [expected_desc], # List of strings
            "message": f"{found_str}" # Fallback message
        }

    @staticmethod
    def get_syntax_error(token=None, expected_tokens=None, custom_msg_type=None):
        """
        Generates the standard dictionary for Syntax Errors.
        Logic handles: Unexpected Token, EOF, and Missing Main.
        """
        if expected_tokens is None:
            expected_tokens = []
        
        # 1. Determine Location and 'Found' string
        if token:
            line = token.line
            col = token.col
            found_str = token.type  # e.g., "id", "int_lit"
        else:
            line = "?"
            col = "?"
            found_str = "EOF"

        # 2. Determine Specific Error Message Type
        error_header = ErrorHandler.ERR_UNEXPECTED_TOKEN # Default

        if found_str == "EOF":
            if "AHOY" in expected_tokens or custom_msg_type == "MISSING_MAIN":
                error_header = ErrorHandler.ERR_MISSING_MAIN
            else:
                error_header = ErrorHandler.ERR_UNEXPECTED_EOF

        # 3. Format Expected List (Clean up duplicates and sort)
        clean_expected = sorted(list(set([str(t) for t in expected_tokens if t])))

        return {
            "type": ErrorHandler.TYPE_SYNTAX,
            "error_header": error_header, # Passed to frontend to bold specific error types
            "line": line,
            "col": col,
            "found": found_str,
            "expected": clean_expected,
            "message": f"{error_header}: '{found_str}'"
        }