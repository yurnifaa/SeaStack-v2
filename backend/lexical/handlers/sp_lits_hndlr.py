import string
from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters

# =========================================================================================
# SCROLL and PARCH TD: Scroll and Parch state machine (rs120 - rs192)
# This class recognizes and tokenizes literal values, specifically PARCH-lit & SCROLL-lit
# ========================================================================================= 

class LiteralHandler:

    # --- Utility Functions ---
    def _get_parch_end_delims(self):
        delims = Delimiters._get_delimiters()
        return Delimiters._get_delimiters()["PARCH_DELIM"]

    def _get_scroll_body_allowed(self):
        delims = Delimiters._get_delimiters()
        return delims["ASCII"] - set("\"\\\n\r")

    def _get_scroll_delims(self):
        return Delimiters._get_delimiters()["SCR_DELIM"]

    # --- Error Utility : Logs error and returns empty list (hides from table) ---
    def _error_token(self, message, expected_list, current_text=""):
        error_char = self.current_char if self.current_char is not None else ""        
        err_col = max(1, self.col - 1)
        
        error_token = Token("ERROR", current_text, self.line, err_col, message)
        
        # ATTACH EXPECTED LIST
        error_token.expected = expected_list
        
        self.errors.append(error_token)
        return []

    # =========================================================================
    # PARCH LITERAL (Single Character)
    # =========================================================================
    def p283(self):
        if self.current_char == "'":
            self.advance()
            return self.p284()

    def p284(self):
        # 1. Check Empty ('')
        if self.current_char == "'":
            return self._error_token(
                "Invalid PARCH Literal. Expected: any character inside quotes", 
                ["Unclosed PARCH Literal"], 
                "'"
            ) 
        
        # Prevent consuming Newlines
        if self.current_char == '\n':
            err_token = Token(
                "ERROR", 
                "'",
                self.line, 
                self.col - 1, 
                "Invalid Character. Expected: any character except newline"
            )
            err_token.expected = ["any character"]
            self.errors.append(err_token)
            return []

        # 2. Consume the character inside
        if self.current_char is not None:
            self.advance() 
            return self.p285()

        # EOF Case
        err_token = Token(
            "ERROR", 
            "'",            
            self.line, 
            self.col - 1,   
            "Invalid PARCH Literal. Expected: any character or closing quote."
        )
        err_token.expected = ["ASCII", "'"]
        self.errors.append(err_token)
        return []

    def p285(self):
        # 3. Check if we are at the closing quote
        if self.current_char == "'":
            
            # --- PEEK LOGIC ---
            next_pos = self.pos + 1
            if next_pos < len(self.text):
                peek_char = self.text[next_pos]
            else:
                peek_char = None 
            
            valid_delims = self._get_parch_end_delims() 

            # 2. Check Neighbor
            if peek_char is None or peek_char in valid_delims:
                self.advance() 
                return self.p286()
            
            else:
                full_text = self.current_token_text() + "'"
                
                # ERROR: Invalid Delimiter
                err_token = Token(
                    "ERROR", 
                    full_text, 
                    self.line, 
                    self.col - 1, 
                    f"Invalid PARCH Literal. Expected delimiter: ] ! , or whitespace"
                )
                # Manually defining expected delimiters for PARCH
                err_token.expected = ["whitespace", "]", ":", "&", "|", "!", "=", ","]
                self.errors.append(err_token)
                
                # Consume the closing quote so we move forward
                self.advance() 
                return []

        # 3. Malformed Literal Case (e.g., 'da or 'adas...)
        else:    
            # ERROR 2: Invalid char inside literal
            err_token = Token(
                "ERROR", 
                self.current_token_text(),
                self.line, 
                self.col - 1,
                f"Invalid PARCH Literal. Expected: closing quote '"
            )
            err_token.expected = ["'"]
            self.errors.append(err_token)
            
            return []
    
    def p286(self):
        return [Token("PARCH-lit", self.current_token_text(), self.line, self.col - 1)]

    # =========================================================================
    # SCROLL LITERAL (Double Quoted String)
    # =========================================================================

    # ENTRY POINT: Consumes opening quote
    def s287(self):
        if self.current_char == '"':
            self.advance() 
            
            # Check IF Empty SCROLL ("")
            if self.current_char == '"':              
                error_token = Token(
                    "ERROR", '"', self.line, self.col - 1, 
                    "Invalid Character. Expected: non-empty string content"
                )
                error_token.expected = ["string content"]
                self.errors.append(error_token)          
                return []
            
            elif self.current_char is None:
                return self._error_token(
                    "Invalid Character. Expected: string content or closing quote", 
                    ["string content", '"'], 
                    '"'
                )

            return self.s288(current_text='"', start_line=self.line, start_col=self.col-1)
    
    
    def _get_scroll_body_allowed(self):
        delims = Delimiters._get_delimiters()
        return delims["ASCII"] - set("\"\n\r")

    # SCROLL BODY
    def s288(self, current_text, start_line, start_col):
        while self.current_char is not None:
            # 1. Closing Quote
            if self.current_char == '"':
                self.advance()
                return self.s289(current_text + '"', start_line, start_col)
            
            # 2. Invalid Newline
            if self.current_char == '\n':
                return self._error_token(
                    "Invalid SCROLL literal. Expected: closing quote \" before newline", 
                    ['"'], 
                    current_text
                )

            # 3. Valid Body Character (includes '\')
            if self._comp_delims(self._get_scroll_body_allowed()):
                current_text += self.current_char
                self.advance()
                continue
            
            # 4. Invalid Character
            self.advance()
            return self._error_token(
                f"Invalid Character. Expected: printable ASCII character", 
                ["printable ASCII"], 
                current_text
            )

        # EOF Reached
        return self._error_token(
            "Invalid SCROLL literal. Expected: closing quote \"", 
            ['"'], 
            current_text
        )

    def s291(self, current_text, start_line, start_col):
        """State 291: Check Escape Char."""
        if self.current_char is None:
            return self._error_token(
                "Invalid SCROLL literal. Expected: escape character", 
                ["n", "t", "d", '"', "\\"], 
                current_text
            )

        char = self.current_char

        if char in ['n', 't', 'd']:
            self.advance()
            return self.s288(current_text + '\\' + char, start_line, start_col)

        if char == '"': 
            self.advance()
            return self.s288(current_text + '"', start_line, start_col)

        if char == '\\':
            self.advance()
            return self.s288(current_text + '\\', start_line, start_col)
            
        return self._error_token(
            f"Invalid SCROLL Literal \\{char}. Expected: n, t, d, \", or \\", 
            ["n", "t", "d", '"', "\\"], 
            current_text
        )

    def s292(self, current_text, start_line, start_col, escape_char):
        tokens = []
        if len(current_text) > 0:
             tokens.append(Token("SCROLL-lit", current_text, start_line, start_col))
        
        tokens.extend(self.s288("", self.line, self.col))
        return tokens

    def s289(self, current_text, start_line, start_col):
        """State 289: Delimiter Check."""
        
        final_tokens = self.s290(current_text, start_line, start_col)
        
        if self._comp_delims(self._get_scroll_delims()):
            return final_tokens
        
        # 1. Error for Literal (Point to Closing Quote: Col 11)
        lit_error_col = self.col - 1
        token_error = Token(
            "ERROR", 
            current_text, 
            start_line, 
            lit_error_col, 
            "Invalid SCROLL literal. Expected delimiter: ) ] & ! , or whitespace"
        )
        # Explicit SCROLL Delimiters
        token_error.expected = ["whitespace", ")", "]", "&", "!", "=", ",", "|", "{"]
        self.errors.append(token_error)
        
        return []

    def s290(self, current_text, start_line, start_col):
        return [Token("SCROLL-lit", current_text, start_line, start_col)]