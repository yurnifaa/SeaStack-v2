import string
from lexer_token import Token
from handlers.delimiters import Delimiters

# =========================================================================================
# SCROLL and PARCH TD: Scroll and Parch state machine (rs120 - rs192)
# This class recognizes and tokenizes literal values, specifically PARCH-lit & SCROLL-lit
# ========================================================================================= 

# --- Inherited Methods ---
# _get_parch_end_delims() and _get_scroll_body_allowed(): precisely define what characters are allowed inside the literal and 
#                                                         what characters are valid immediately following the closing quote.

# --- Program Flow ---
# 1. s287() (Entry Point): Consumes the opening double quote ("). 
#                          IF the next character is immediately " (an empty string ""), it's logged as an ERROR 
#                          IF not empty, it proceeds to the body loop (s288).
# 2. s288() (Body Loop): acts as a loop that runs until the closing quote is found OR an error occurs.
#                        Closing Quote: IF qoute is found, it advance()'s and moves to s289 for the final delimiter check.
#                        Escape Sequence: If \ is found, it advance()'s and moves to s291 to process the escape sequence.
#                        Newline: If a \n is found, it logs an error.
#                        Valid Character: (via _get_scroll_body_allowed), it appends the character to current_text and advance()'s, continuing the loop (continue).
#                        Invalid Character: Any other character results in an error and termination.
# 3. s291() (Escape Sequence): Handles characters following the backslash (\).
#   a. Checks for valid escape sequences (e.g., \n, \t, \d, \", \\).
#   b. IF valid sequence, it appends the two characters (\ + char) to current_text 
#      and returns to the body loop s288() to continue scanning the rest of the string.
# 4. s289() (Delimiter Check): After the closing quote is consumed, this state checks 
#      the character following the entire string literal (via _comp_delims) against the required SCR_DELIM set.
#   a. IF the delimiter is valid, it proceeds to s290.
#   b. IF the delimiter is invalid (e.g., "test"123), it logs an ERROR pointing to the invalid literal and returns [].
# 5. s290() (Final Tokenize): Creates and returns the final SCROLL-lit token.

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
    def _error_token(self, message, current_text=""):
        error_char = self.current_char if self.current_char is not None else ""        
        err_col = max(1, self.col - 1)
        error_token = Token("ERROR", current_text, self.line, err_col, message)
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
            err = self._error_token("Invalid PARCH Literal. Expected: any character inside quotes", "'") 
            return err
        
        # Prevent consuming Newlines
        if self.current_char == '\n':
            err_token = Token(
                "ERROR", 
                "'",
                self.line, 
                self.col - 1, 
                "Invalid Character. Expected: any character except newline"
            )
            self.errors.append(err_token)
            return []
        # 2. Consume the character inside
        if self.current_char is not None:
            self.advance() 
            return self.p285()

        err_token = Token(
            "ERROR", 
            "'",            # The lexeme causing the issue
            self.line, 
            self.col - 1,   # Point back to the opening quote we just consumed
            "Invalid PARCH Literal. Expected: any character or closing quote."
        )
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
                
                err_token = Token(
                    "ERROR", 
                    full_text, 
                    self.line, 
                    self.col - 1, 
                    f"Invalid PARCH Literal. Expected delimiter: ] ! , or whitespace"
                )
                self.errors.append(err_token)
                
                # Consume the closing quote so we move forward
                self.advance() 
                return []

        # 3. Malformed Literal Case (e.g., 'da or 'adas...)
        else:    
            char = self.current_char if self.current_char is not None else "EOF"
            
            # ERROR 2: Invalid char inside literal
            # CHANGED: Use self.current_token_text() instead of 'char'.
            # This captures the partial literal (e.g., "'a") instead of the invalid next char ("d").
            err_token = Token(
                "ERROR", 
                self.current_token_text(),
                self.line, 
                self.col - 1,
                f"Invalid PARCH Literal. Expected: closing quote '"
            )
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
                self.errors.append(error_token)          
                return []
            
            elif self.current_char is None:
                return self._error_token("Invalid Character. Expected: string content or closing quote", '"')

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
                return self._error_token("Invalid SCROLL literal. Expected: closing quote \" before newline", current_text)

            # 3. Valid Body Character (includes '\')
            if self._comp_delims(self._get_scroll_body_allowed()):
                current_text += self.current_char
                self.advance()
                continue
            
            # 4. Invalid Character
            err_char = self.current_char
            self.advance()
            return self._error_token(f"Invalid Character. Expected: printable ASCII character", current_text)

        return self._error_token("Invalid SCROLL literal. Expected: closing quote \"", current_text)

    def s291(self, current_text, start_line, start_col):
        """State 291: Check Escape Char."""
        if self.current_char is None:
            return self._error_token("Invalid SCROLL literal. Expected: escape character", current_text)

        char = self.current_char

        # --- CHANGED SECTION ---
        # Instead of calling s292 (which splits the token), 
        # we append the backslash + char and go back to s288 (the body loop).
        
        if char in ['n', 't', 'd']:
            self.advance()
            # We append "\\" (the backslash we consumed previously) + char ('n', 't', or 'd')
            return self.s288(current_text + '\\' + char, start_line, start_col)
        # -----------------------

        if char == '"': 
            self.advance()
            return self.s288(current_text + '"', start_line, start_col)

        if char == '\\':
            self.advance()
            return self.s288(current_text + '\\', start_line, start_col)
            
        return self._error_token(f"Invalid SCROLL Literal \\{char}. Expected: n, t, d, \", or \\", current_text)

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
        
        # --- FIX FOR STANDARD STRING ERRORS ---

        # 1. Error for Literal (Point to Closing Quote: Col 11)
        lit_error_col = self.col - 1
        token_error = Token(
            "ERROR", 
            current_text, 
            start_line, 
            lit_error_col, 
            "Invalid SCROLL literal. Expected delimiter: ) ] & ! , or whitespace"
        )
        self.errors.append(token_error)
        
        return []

    def s290(self, current_text, start_line, start_col):
        return [Token("SCROLL-lit", current_text, start_line, start_col)]