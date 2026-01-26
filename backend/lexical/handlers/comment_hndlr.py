# lexer_handlers/comment_handler.py
from backend.lexical.lexer_token import Token

class CommentHandler:

    # =========================================================================
    # HELPER: Sanitize Delimiters for Display
    # =========================================================================
    def _sanitize_delims(self, delim_set):
        delims = list(delim_set) if isinstance(delim_set, set) else delim_set
        cleaned_list = []
        has_whitespace = False
        
        for d in delims:
            if d in [' ', '\t', '\n', '\r', '\v', '\f']:
                has_whitespace = True
            elif d == "whitespace":
                has_whitespace = True
            else:
                cleaned_list.append(d)
        
        if has_whitespace:
            cleaned_list.append("whitespace")
            
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
        err_token.expected = self._sanitize_delims(expected_list)
        self.errors.append(err_token)
        return None

    # =========================================================================
    # ENTRY POINT (State 294)
    # =========================================================================
    def cm294(self):
        # State 294: Expects '~'
        if self.current_char == '~':
            self.advance()
            return self.cm295()
        return None 

    # =========================================================================
    # STATE 295: Decision Point (Single vs Multi)
    # =========================================================================
    def cm295(self):
        char = self.current_char
        
        # Path 1: '(' -> State 298 (Start Multi-line)
        if char == '(':
            return self.cm298()

        # Path 2: newline -> State 297 (Empty Single Line Accept)
        if char == '\n':
            return self.cm297()
            
        # Path 3: ASCII except newline and ~ -> State 296 (Single Line Body)
        # Note: If we see '~' here, it's technically allowed in single line text 
        # unless rules forbid it, but usually single line consumes everything until \n.
        if char is not None:
            return self.cm296()
            
        return self._report_comment_error(
            "Invalid Comment Start. Expected '(', newline, or text.", 
            ["(", "newline", "text"]
        )

    # =========================================================================
    # STATE 296: Single-Line Body Loop
    # =========================================================================
    def cm296(self):
        self.advance() # Consume previous char
        
        # Self-Loop: Consume everything until newline
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
            
        # Transition: newline -> 297 (Accept)
        if self.current_char == '\n':
            return self.cm297()
            
        return self._report_comment_error(
            "Unterminated Single-line Comment. Expected newline.", 
            ["newline"]
        )

    # =========================================================================
    # STATE 297: Single-Line Final (Accepting)
    # =========================================================================
    def cm297(self):
        self.advance() # Consume the newline
        return Token(
            "single-comment", 
            self.current_token_text(), 
            self.token_start_line, 
            self.token_start_col
        )

    # =========================================================================
    # STATE 298: Multi-Line Start (After '~)(')
    # =========================================================================
    def cm298(self):
        self.advance() # Consume '('
        
        char = self.current_char
        
        # Check empty multi-line cases or straight to body
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
        # Loop until we see ')'
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
        
        # Transition: ~ -> 301 (Accept)
        if char == '~':
            return self.cm301()
            
        # False alarm (e.g., "( text ) more text" )
        # Go back to body loop
        if char is not None:
            return self.cm299()
            
        return self._report_comment_error(
            "Unterminated Multi-line Comment. Expected '~' or text.", 
            ["~", "text"]
        )

    # =========================================================================
    # STATE 301: Multi-Line Final (Accepting)
    # =========================================================================
    def cm301(self):
        self.advance() # Consume '~'
        
        # CORRECTED: Do NOT require a newline here. 
        # The comment is closed. We accept immediately.
        
        return Token(
            "multi-comment", 
            self.current_token_text(), 
            self.token_start_line, 
            self.token_start_col
        )