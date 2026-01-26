# lexer_handlers/sp_lits_hndlr.py
import string
from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters

# =========================================================================================
# SCROLL and PARCH TD: States 284 - 293
# ========================================================================================= 

class LiteralHandler:

    # --- Utility Functions ---
    def _get_parch_delims(self):
        return Delimiters._get_delimiters()["PARCH_DELIM"]

    def _get_scroll_body_allowed(self):
        # Allow everything except ", \, and Newline
        delims = Delimiters._get_delimiters()
        return delims["ASCII"] - set("\"\\\n\r")

    def _get_scroll_delims(self):
        return Delimiters._get_delimiters()["SCR_DELIM"]

    # --- Error Utility ---
    def _error_token(self, message, expected_list, current_text=""):
        err_col = max(1, self.col - 1)
        error_token = Token("ERROR", current_text, self.line, err_col, message)
        error_token.expected = expected_list
        self.errors.append(error_token)
        return []

    # =========================================================================
    # PARCH LITERAL (Single Character) - States 284 to 288
    # =========================================================================
    
    # State 284: Opening Quote '
    def p284(self):
        if self.current_char == "'":
            self.advance()
            return self.p285()
        return None # Should not happen if called correctly from Lexer

    # State 285: The Content (Char or Backslash)
    def p285(self):
        # 1. Check Empty ('')
        if self.current_char == "'":
            return self._error_token(
                "Invalid PARCH Literal. Expected: character or escape sequence.", 
                ["ASCII"], 
                "''"
            ) 
        
        # 2. Check Newline (Illegal)
        if self.current_char == '\n':
            return self._error_token("Invalid PARCH Literal. Newline not allowed.", ["ASCII"], "'")

        # 3. Check Escape Sequence Start
        if self.current_char == '\\':
            self.advance()
            return self.p286() # Go to Escape Handler

        # 4. Standard Character
        if self.current_char is not None:
            self.advance() 
            return self.p287() # Go to Closing Quote Check

        # EOF
        return self._error_token("Invalid PARCH Literal. Unexpected EOF.", ["'"], "'")

    # State 286: PARCH Escape Sequence (n, t, d, \, ')
    def p286(self):
        if self.current_char in ['n', 't', 'd', '\\', "'"]:
            self.advance()
            return self.p287() # Go to Closing Quote Check
        
        return self._error_token(
            f"Invalid PARCH Escape Sequence \\{self.current_char}. Expected: n, t, d, \\, or '", 
            ["n", "t", "d", "\\", "'"], 
            self.current_token_text()
        )

    # State 287: Closing Quote '
    def p287(self):
        if self.current_char == "'":
            self.advance()
            return self.p288() # Go to Delimiter Check
        
        # If we have chars but no closing quote (e.g., 'ab')
        return self._error_token(
            "Invalid PARCH Literal. Expected closing quote '.", 
            ["'"], 
            self.current_token_text()
        )
    
    # State 288: Delimiter Check & Accept
    def p288(self):
        # Check valid delimiter using PARCH_DELIM
        if self._comp_delims(self._get_parch_delims()):
            return [Token("PARCH-lit", self.current_token_text(), self.line, self.col - 1)]
        
        # Error: Invalid Delimiter
        err_token = Token(
            "ERROR", 
            self.current_token_text(), 
            self.line, 
            self.col - 1, 
            "Invalid PARCH Literal. Expected delimiter."
        )
        err_token.expected = ["whitespace", "]", ":", "&", "|", "!", "=", ","]
        self.errors.append(err_token)
        return []

    # =========================================================================
    # SCROLL LITERAL (Double Quoted String) - States 289 to 293
    # =========================================================================

    # State 289: Opening Quote "
    def s289(self):
        if self.current_char == '"':
            self.advance() 
            return self.s290(current_text='"', start_line=self.line, start_col=self.col-1)
        return None

    # State 290: SCROLL Body Loop
    def s290(self, current_text, start_line, start_col):
        while self.current_char is not None:
            
            # 1. Closing Quote -> Transition to End
            if self.current_char == '"':
                self.advance()
                return self.s292(current_text + '"', start_line, start_col)
            
            # 2. Escape Sequence Start -> Transition to s291
            if self.current_char == '\\':
                self.advance()
                return self.s291(current_text + '\\', start_line, start_col)

            # 3. Newline -> Error
            if self.current_char == '\n':
                return self._error_token(
                    "Invalid SCROLL literal. Newline not allowed.", 
                    ['"'], 
                    current_text
                )

            # 4. Valid Body Character
            if self._comp_delims(self._get_scroll_body_allowed()):
                current_text += self.current_char
                self.advance()
                continue
            
            # 5. Invalid Character (Unprintable or disallowed)
            self.advance()
            return self._error_token(
                "Invalid Character inside SCROLL.", 
                ["printable ASCII"], 
                current_text
            )

        # EOF
        return self._error_token(
            "Invalid SCROLL literal. Expected closing quote \".", 
            ['"'], 
            current_text
        )

    # State 291: SCROLL Escape Sequence (n, t, d, ", \)
    def s291(self, current_text, start_line, start_col):
        if self.current_char in ['n', 't', 'd', '"', '\\']:
            char = self.current_char
            self.advance()
            # Return to Body Loop (s290)
            return self.s290(current_text + char, start_line, start_col)

        return self._error_token(
            f"Invalid SCROLL Escape Sequence \\{self.current_char}. Expected: n, t, d, \", or \\", 
            ["n", "t", "d", '"', "\\"], 
            current_text
        )

    # State 292: Delimiter Check
    def s292(self, current_text, start_line, start_col):
        if self._comp_delims(self._get_scroll_delims()):
            return self.s293(current_text, start_line, start_col)
        
        # Error: Invalid Delimiter
        err_token = Token(
            "ERROR", 
            current_text, 
            start_line, 
            start_col, 
            "Invalid SCROLL literal. Expected delimiter."
        )
        err_token.expected = ["whitespace", ")", "]", "&", "!", "=", ",", "|", "{"]
        self.errors.append(err_token)
        return []

    # State 293: Accept
    def s293(self, current_text, start_line, start_col):
        return [Token("SCROLL-lit", current_text, start_line, start_col)]