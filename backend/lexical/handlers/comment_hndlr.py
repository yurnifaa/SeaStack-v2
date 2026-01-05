from backend.lexical.lexer_token import Token

class CommentHandler:

    # =========================================================================
    # HELPER FUNC: HARD syntax errors (like '~)a' or '~( ~(').
    # =========================================================================
    def _report_comment_error(self, message):
        err_token = Token(
            "ERROR",
            self.current_token_text(), # Show the partial comment
            self.token_start_line,
            self.token_start_col,
            message
        )
        self.errors.append(err_token)
        return None

    # =========================================================================
    # START STATE (cm293)
    # =========================================================================
    def cm293(self):
        self.advance()              # Consume the initial '~'
        return self.cm294()

    # =========================================================================
    # State cm294: Controller state. Decides single-line or multi-line.
    # =========================================================================
    def cm294(self):
        char = self.current_char

        if char is None:            # Case: "~"
            return self.cm295()
        
        if char == "\n":            # Case: "~" followed immediately by a newline
            self.advance()          # Consume the newline
            return self.cm295()
        
        if char == "(":             # Case: "~(" Uses a Try-and-Rollback Logic
            # 1. Save state before trying multi-line
            saved_state = self.save()
            self.advance() # Consume '('
            
            # 2. Attempt to parse the multi-line comment
            multi_comment_result = self.cm297()
            
            # 3. Check the result
            if multi_comment_result == "ROLLBACK":
                # 4. Rollback to state before '(' was consumed
                self.restore(saved_state)
                
                # Now, re-parse as a single-line comment.
                # The current_char is '(', which cm296 will simply treat as text.
                return self.cm296()
            else:
                # It was either a valid token or a hard syntax error (None)
                return multi_comment_result
        
        if char == "~":             # Case: "~~" Hard error
            self._report_comment_error("Invalid Comment for multi-line or any text for single-line")
            self.advance()
            return None
            
        # Default: It's a single-line comment
        return self.cm296()

    def cm295(self):
    # =========================================================================
    # State cm295: Final state for a single-line comment.
    # =========================================================================
        return Token(
            "single-comment", 
            self.current_token_text(), 
            self.token_start_line, 
            self.token_start_col
        )

    def cm296(self):
    # =========================================================================
    # State cm296: Consumes all characters in a single-line comment
    # =========================================================================
        # CHANGED: Removed the check for '~'. 
        # Single-line comments should consume ANY character until newline.
        while self.current_char is not None and self.current_char != "\n":
            self.advance()
        
        if self.current_char == "\n":
            self.advance() # Consume the newline
            
        return self.cm295() # Go to the final state

    def cm297(self):
    # =========================================================================
    # State cm297: Inside a multi-line comment, after "~(".
    # =========================================================================

        if self.current_char is None:
            return "ROLLBACK"                # Soft failure
        
        if self.current_char == ")":
            self.advance()                   # Consume ')'
            return self.cm299()              # Check for '~'
        
        if self.current_char == "~":
            # CHANGED: Return ROLLBACK instead of None.
            # This allows cm294 to catch it and say "Oh, this isn't multi-line, treat as single line."
            return "ROLLBACK"

        # Any other character, loop in cm298
        self.advance()
        return self.cm298()

    def cm298(self):
    # =========================================================================
    # State cm298: Looping inside a multi-line comment.
    # =========================================================================
        while self.current_char is not None:
            if self.current_char == ")":
                self.advance()              # Consume ')'
                return self.cm299()         # Go to check for '~'
            
            if self.current_char == "~":    
                # CHANGED: Return ROLLBACK instead of None.
                # If we see a nested '~', we assume the user meant a single-line comment containing '~'.
                return "ROLLBACK"
            
            else:
                self.advance()
        
        # EOF reached
        return "ROLLBACK" # Soft failure

    def cm299(self):
    # =========================================================================
    # State cm299: After a ")", checking for the final "~".
    # =========================================================================
        if self.current_char is None:
            return "ROLLBACK"               # Soft failure
            
        if self.current_char == "~":        # Success!
            self.advance()                  # Consume the '~'
            return self.cm300()             # Go to final multi-line state
        
        # If we see something else (e.g. ")a"), it's not a valid closing sequence.
        # CHANGED: Return ROLLBACK so we fall back to single-line logic.
        return "ROLLBACK"
        

    def cm300(self):
    # =========================================================================
    # State cm300: Final State for multi-line comment.
    # =========================================================================
        return Token(
            "multi-comment", 
            self.current_token_text(), 
            self.token_start_line, 
            self.token_start_col
        )