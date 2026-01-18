# backend/error_msg.py

from pyparsing import col, line


class ErrorHandler:
    # --- ERROR TYPES ---
    TYPE_SYNTAX = "Syntax Error"
    TYPE_LEXICAL = "Lexical Error"
    
    # --- SYNTAX SUB-TYPES ---
    ERR_UNEXPECTED_TOKEN = "Unexpected Token"
    ERR_UNEXPECTED_EOF = "Unexpected End of File"
    ERR_MISSING_MAIN = "Missing Main Function"

    @staticmethod
    def get_lexical_error(line, col, invalid_char, expected_list=None):
        # Generates the standard dictionary for Lexical Errors.
        # Now supports a list of expected delimiters.
        # Default fallback if nothing is passed
        if expected_list is None:
            expected_list = ["Valid Token"]
            
        return {
            "type": ErrorHandler.TYPE_LEXICAL,
            "line": line,
            "col": col,
            "found": f"Invalid character '{invalid_char}'",
            "expected": expected_list, # This sends the list to the frontend
            "message": f"Invalid character '{invalid_char}'"
        }

    @staticmethod
    def get_syntax_error(token=None, expected_tokens=None, custom_msg_type=None):
        if expected_tokens is None:
            expected_tokens = []
        
        if token:
            line = token.line
            col = token.col
            found_str = token.type
        else:
            line = "?"
            col = "?"
            found_str = "EOF"

        error_header = ErrorHandler.ERR_UNEXPECTED_TOKEN

        if found_str == "EOF":
            if "AHOY" in expected_tokens or custom_msg_type == "MISSING_MAIN":
                error_header = ErrorHandler.ERR_MISSING_MAIN
            else:
                error_header = ErrorHandler.ERR_UNEXPECTED_EOF

        clean_expected = sorted(list(set([str(t) for t in expected_tokens if t])))

        return {
            "type": ErrorHandler.TYPE_SYNTAX,
            "error_header": error_header,
            "line": line,
            "col": col,
            "found": found_str,
            "expected": clean_expected,
            "message": f"{error_header}: '{found_str}'"
        }