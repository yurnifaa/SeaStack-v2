from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters
from backend.error_msg import ErrorHandler 

class CommentHandler:

    # =========================================================================
    # HELPER FUNC: Report Errors using ErrorHandler
    # =========================================================================
    def _report_comment_error(self, message, error_type=None):
        if error_type is None:
            error_type = ErrorHandler.ERR_LEX_INVALID_CHAR

        error_dict = ErrorHandler.get_lexical_error(
            line=self.token_start_line,
            col=self.token_start_col,
            invalid_char=self.current_token_text(),
            header_type=error_type,
            custom_msg=message
        )
        self.errors.append(error_dict)
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

        if char is None:            # Case: "~" (EOF immediately)
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
                return self.cm296()
            else:
                return multi_comment_result
        
        if char == "~":             # Case: "~~" Hard error
            self.advance()
            return self._report_comment_error(
                "Invalid Comment. '~~' is not allowed. Did you mean '~('?", 
                ErrorHandler.ERR_LEX_INVALID_CHAR
            )
            
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
        ascii_set = Delimiters._get_delimiters()["ASCII"]

        while self.current_char is not None and self.current_char != "\n":
            
            # Optional: Strict Character Check (Consistency with Literals)
            if self.current_char not in ascii_set:
                 return self._report_comment_error(
                     f"Invalid character inside comment: '{self.current_char}'", 
                     ErrorHandler.ERR_LEX_INVALID_CHAR
                 )

            self.advance()
        
        if self.current_char == "\n":
            self.advance() # Consume the newline
            
        return self.cm295() # Go to the final state

    def cm297(self):
    # =========================================================================
    # State cm297: Inside a multi-line comment, after "~(".
    # =========================================================================

        if self.current_char is None:
            return "ROLLBACK"                # Soft failure -> Becomes single line
        
        if self.current_char == ")":
            self.advance()                   # Consume ')'
            return self.cm299()              # Check for '~'
        
        if self.current_char == "~":
            return "ROLLBACK"

        # Any other character, loop in cm298
        self.advance()
        return self.cm298()

    def cm298(self):
    # =========================================================================
    # State cm298: Looping inside a multi-line comment.
    # =========================================================================
        ascii_set = Delimiters._get_delimiters()["ASCII"]

        while self.current_char is not None:
            # 1. Check for Exit Sequence Start
            if self.current_char == ")":
                self.advance()              # Consume ')'
                return self.cm299()         # Go to check for '~'
            
            # 2. Check for Nested/Invalid Tilde
            if self.current_char == "~":    
                return "ROLLBACK"
            
            # 3. Check Validity (using Delimiters)
            if self.current_char not in ascii_set and self.current_char != '\n':
                 # Note: If we error here, we technically can't "ROLLBACK" cleanly 
                 # because it's a hard invalid char. But for safety in comments, 
                 # we might just flag it or let it slide. 
                 # Strict Lexer = Flag it.
                 return self._report_comment_error(
                     f"Invalid character inside comment: '{self.current_char}'", 
                     ErrorHandler.ERR_LEX_INVALID_CHAR
                 )

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