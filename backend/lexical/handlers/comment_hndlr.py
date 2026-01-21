# lexer_handlers/comment_handler.py
from backend.lexical.lexer_token import Token

class CommentHandler:

    # =========================================================================
    # HELPER: Sanitize Delimiters for Display
    # Replaces invisible chars ('\n', '\t', etc.) with the word "whitespace"
    # =========================================================================
    def _sanitize_delims(self, delim_set):
        # Ensure we are working with a list
        delims = list(delim_set) if isinstance(delim_set, set) else delim_set
        cleaned_list = []
        has_whitespace = False
        
        for d in delims:
            # Check for invisible whitespace characters
            if d in [' ', '\t', '\n', '\r', '\v', '\f']:
                has_whitespace = True
            # Check if the string "whitespace" was passed manually
            elif d == "whitespace":
                has_whitespace = True
            else:
                cleaned_list.append(d)
        
        if has_whitespace:
            cleaned_list.append("whitespace")
            
        # Remove duplicates and sort
        cleaned_list = list(set(cleaned_list))
        cleaned_list.sort(key=str)
        return cleaned_list

    # =========================================================================
    # HELPER: Syntax Errors
    # =========================================================================
    def _report_comment_error(self, message, expected_list):
        err_token = Token(
            "ERROR",
            self.current_token_text(),
            self.token_start_line,
            self.token_start_col,
            message
        )
        
        # --- SANITIZE BEFORE ATTACHING ---
        err_token.expected = self._sanitize_delims(expected_list)
        
        self.errors.append(err_token)
        return None

    # =========================================================================
    # ENTRY POINT (State 0 -> 295)
    # =========================================================================
    def cm293(self):
        # State 0: Expects '~'
        if self.current_char == '~':
            self.advance()
            return self.cm295()
        return None # Should be handled by lexer dispatch

    # =========================================================================
    # STATE 295: Decision Point
    # =========================================================================
    def cm295(self):
        char = self.current_char
        
        # Path 1: newline -> State 296 (Empty Single Line)
        if char == '\n':
            return self.cm296()
            
        # Path 2: '(' -> State 298 (Start Multi-line)
        if char == '(':
            return self.cm298()
            
        # Path 3: ASCII except newline and ~ -> State 297 (Single Line Text)
        if char is not None and char != '~':
            return self.cm297()
            
        # Error: Likely found '~' (forbidden) or EOF
        return self._report_comment_error(
            "Invalid Comment Start. Expected '(', newline, or text (except '~').", 
            ["(", "newline", "text"]
        )

    # =========================================================================
    # STATE 296: Single-Line Final (Accepting)
    # =========================================================================
    def cm296(self):
        self.advance() # Consume the newline (transition logic)
        return Token(
            "single-comment", 
            self.current_token_text(), 
            self.token_start_line, 
            self.token_start_col
        )

    # =========================================================================
    # STATE 297: Single-Line Body Loop
    # =========================================================================
    def cm297(self):
        self.advance() # Consume the char that brought us here
        
        # Self-Loop: ASCII except newline
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
            
        # Transition: newline -> 296
        if self.current_char == '\n':
            return self.cm296()
            
        return self._report_comment_error(
            "Unterminated Single-line Comment. Expected newline.", 
            ["newline"]
        )

    # =========================================================================
    # STATE 298: Multi-Line Start (After '~(')
    # =========================================================================
    def cm298(self):
        self.advance() # Consume '('
        
        char = self.current_char
        
        # Transition: ) -> 300 (Empty body case '~()~')
        if char == ')':
            return self.cm300()
            
        # Transition: ASCII except ) -> 299
        if char is not None:
            return self.cm299()
            
        return self._report_comment_error(
            "Invalid Multi-line Comment. Unexpected end of file.", 
            ["text", ")"]
        )

    # =========================================================================
    # STATE 299: Multi-Line Body Loop
    # =========================================================================
    def cm299(self):
        self.advance() # Consume previous char
        
        # Self-Loop: ASCII except )
        while self.current_char is not None and self.current_char != ')':
            self.advance()
            
        # Transition: ) -> 300
        if self.current_char == ')':
            return self.cm300()
            
        return self._report_comment_error(
            "Unterminated Multi-line Comment. Expected ')'.", 
            [")"]
        )

    # =========================================================================
    # STATE 300: Check Closing Tilde (After ')')
    # =========================================================================
    def cm300(self):
        self.advance() # Consume ')'
        
        char = self.current_char
        
        # Transition: ~ -> 301
        if char == '~':
            return self.cm301()
            
        # Transition: ASCII except ~ -> 299 (False alarm, go back to body)
        # We found a ')', but it wasn't followed by '~', so it's just text.
        if char is not None:
            return self.cm299()
            
        return self._report_comment_error(
            "Unterminated Multi-line Comment. Expected '~' or text.", 
            ["~", "text"]
        )

    # =========================================================================
    # STATE 301: Check Final Newline (After '...)~')
    # =========================================================================
    def cm301(self):
        self.advance() # Consume '~'
        
        # Transition: newline -> 302
        if self.current_char == '\n':
            return self.cm302()
            
        return self._report_comment_error(
            "Invalid Comment Termination. Expected newline after '~'.", 
            ["newline"]
        )

    # =========================================================================
    # STATE 302: Multi-Line Final (Accepting)
    # =========================================================================
    def cm302(self):
        self.advance() # Consume newline
        return Token(
            "multi-comment", 
            self.current_token_text(), 
            self.token_start_line, 
            self.token_start_col
        )