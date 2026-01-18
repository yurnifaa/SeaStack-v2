# backend/error_msg.py

class ErrorHandler:
    # --- ERROR TYPES ---
    TYPE_SYNTAX = "Syntax Error"
    TYPE_LEXICAL = "Lexical Error"
    
    # --- SYNTAX SUB-TYPES ---
    ERR_UNEXPECTED_TOKEN = "Unexpected Token"
    ERR_UNEXPECTED_EOF = "Unexpected End of File"
    ERR_MISSING_MAIN = "Missing Main Function"

    # --- LEXICAL SUB-TYPES (NEW) ---
    ERR_LEX_INVALID_CHAR = "Invalid Character"
    ERR_LEX_INVALID_DELIM = "Invalid Delimiter"
    ERR_LEX_LIMIT_EXCEEDED = "Limit Exceeded"
    ERR_LEX_MALFORMED_LIT = "Malformed Literal"
    ERR_LEX_UNCLOSED_LIT = "Unclosed Literal"

    @staticmethod
    def get_lexical_error(line, col, invalid_char, expected_list=None, header_type=None, custom_msg=None):
        """
        Generates the standard dictionary for Lexical Errors with flexible headers.
        
        :param line: Line number
        :param col: Column number
        :param invalid_char: The text/char that caused the error
        :param expected_list: List of valid tokens/delimiters expected
        :param header_type: One of ErrorHandler.ERR_LEX_* constants
        :param custom_msg: Optional override for the main message
        """
        
        # 1. Default Defaults
        if expected_list is None:
            expected_list = ["Valid Token"]
        
        if header_type is None:
            header_type = ErrorHandler.ERR_LEX_INVALID_CHAR

        # 2. Construct the "Found" Header based on Type
        # This determines what shows up in BOLD RED in the UI
        found_msg = f"{header_type} '{invalid_char}'"
        
        # Special Case: For limits, we might not want the word 'Limit Exceeded' twice if custom_msg handles it
        if header_type == ErrorHandler.ERR_LEX_LIMIT_EXCEEDED:
             # For limits, the "found" message is essentially the header for the UI.
             # If a custom message is provided (e.g. "COIN-Lit exceeds 16 digits"), use that as the header.
             if custom_msg:
                 found_msg = custom_msg
             else:
                 found_msg = f"Limit Exceeded '{invalid_char}'"

        # 3. Construct the Detailed Message
        final_msg = custom_msg if custom_msg else found_msg

        return {
            "type": ErrorHandler.TYPE_LEXICAL,
            "line": line,
            "col": col,
            "found": found_msg,      # UI Header (Red Text)
            "expected": expected_list, # Expected list
            "message": final_msg     # Full description
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