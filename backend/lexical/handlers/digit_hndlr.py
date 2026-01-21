from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters

class DigitHandler:
    
    # String for the message
    DELIM_ERR_MSG = "whitespace, +, -, *, /, %, <, >, =, !, &, |, ), }, ], :, ,"
    
    # List for the UI "Expected" column
    DELIM_LIST = [
        "whitespace", "+", "-", "*", "/", "%", 
        "<", ">", "=", "!", "&", "|", 
        ")", "}", "]", ":", ","
    ]
    
    # Instance variable to store DIME token value before trailing zeros
    final_dime_value = None

    # =========================================================================
    # HELPER: Create Error with Expected List
    # =========================================================================
    def _create_digit_error(self, message, expected_list):
        err_token = Token(
            "ERROR",
            self.current_token_text(),
            self.line,
            self.col - 1,
            message,
        )
        # Attach list for UI
        err_token.expected = expected_list
        return err_token

    # =========================================================================
    # ENTRY POINT: COIN and DIME Transition Diagram
    # =========================================================================
    def c233(self):         
        return self.c234()
    
    # =========================================================================
    # COIN-lit TD: Digit up to 16 digits
    # =========================================================================
    def c234(self):             # Digit 1
        # Leading Zero Logic
        if self.current_char == '0':
            self.advance() 
            if self.current_char is not None and self.current_char.isdigit():
                self.token_start_pos += 1   
                return self.c234()
            # Handle leading zero followed by decimal point (e.g., 0.1234567800)
            elif self.current_char == ".":
                return self.s266()
        else:
            self.advance()

        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c235()
        if self.current_char and self.current_char.isdigit(): return self.c236()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c235(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c236(self):             # Digit 2
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c237()
        if self.current_char and self.current_char.isdigit(): return self.c238()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c237(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)
    
    def c238(self):             # Digit 3
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c239()
        if self.current_char and self.current_char.isdigit(): return self.c240()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))

    def c239(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c240(self):             # Digit 4
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c241()
        if self.current_char and self.current_char.isdigit(): return self.c242()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
    
    def c241(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c242(self):             # Digit 5
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c243()
        if self.current_char and self.current_char.isdigit(): return self.c244()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
    
    def c243(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c244(self):             # Digit 6
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c245()
        if self.current_char and self.current_char.isdigit(): return self.c246()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
    
    def c245(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c246(self):             # Digit 7
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c247()
        if self.current_char and self.current_char.isdigit(): return self.c248()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
    
    def c247(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c248(self):             # Digit 8
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c249()
        if self.current_char and self.current_char.isdigit(): return self.c250()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
    
    def c249(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c250(self):             # Digit 9
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c251()
        if self.current_char and self.current_char.isdigit(): return self.c252()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
    
    def c251(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c252(self):             # Digit 10
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c253()
        if self.current_char and self.current_char.isdigit(): return self.c254()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
    
    def c253(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c254(self):             # Digit 11
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c255()
        if self.current_char and self.current_char.isdigit(): return self.c256()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
    
    def c255(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c256(self):             # Digit 12
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c257()
        if self.current_char and self.current_char.isdigit(): return self.c258()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
    
    def c257(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c258(self):             # Digit 13
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c259()
        if self.current_char and self.current_char.isdigit(): return self.c260()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
    
    def c259(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c260(self):             # Digit 14
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c261()
        if self.current_char and self.current_char.isdigit(): return self.c262()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
    
    def c261(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c262(self):             # Digit 15
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c263()
        if self.current_char and self.current_char.isdigit(): return self.c264()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR_MSG}",
            ["digit", "."] + self.DELIM_LIST
        ))
    
    def c263(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # =========================================================================
    # COIN-lit TD: 16th Digit
    # =========================================================================    
    def c264(self):             # 16th digit
        self.advance()

        # If the next char is a digit → EXCEEDS 16 
        if self.current_char == ".": return self.s266()
        if self.current_char and self.current_char.isdigit():
            # Record error for the first 16 digits
            err = Token(
                "ERROR",
                self.text[self.token_start_pos:self.pos],  # the first 16 digits
                self.line,
                self.col - 1, 
                "COIN-Lit exceeds 16 digits. Expected delimiter.",
            )
            err.expected = self.DELIM_LIST
            self.errors.append(err)

            self.token_start_pos = self.pos  # start new token
            return self.state0()  
        
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c265()
        
        self.errors.append(self._create_digit_error(
            f"Invalid COIN-lit. Expected '.', {self.DELIM_ERR_MSG}",
            ["."] + self.DELIM_LIST
        ))
        
    def c265(self):
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # =========================================================================
    # DIME-lit TD: Digit up to 8 digits
    # =========================================================================
    def s266(self):  # Checking the Delimiter after the decimal point
        self.advance()
        
        # Check for valid digit following the dot
        if self.current_char and self.current_char.isdigit(): 
            return self.d267()
            
        self.errors.append(self._create_digit_error(
            "Invalid DIME-lit. Expected digit after decimal point.",
            ["digit"]
        ))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
        
    def d267(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d268()
        if self.current_char and self.current_char.isdigit(): return self.d269()
            
        self.errors.append(self._create_digit_error(
            f"Invalid DIME-lit. Expected digit {self.DELIM_ERR_MSG}",
            ["digit"] + self.DELIM_LIST
        ))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
    
    def d268(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # DIME-lit TD: Digits 2-8 (AFTER decimal)
    # =============================================
    def d269(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d270()
        if self.current_char and self.current_char.isdigit(): return self.d271()
        
        self.errors.append(self._create_digit_error(
            f"Invalid DIME-lit. Expected digit {self.DELIM_ERR_MSG}",
            ["digit"] + self.DELIM_LIST
        ))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
    
    def d270(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d271(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d272()
        if self.current_char and self.current_char.isdigit(): return self.d273()
        
        self.errors.append(self._create_digit_error(
            f"Invalid DIME-lit. Expected digit {self.DELIM_ERR_MSG}",
            ["digit"] + self.DELIM_LIST
        ))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
    
    def d272(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d273(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d274()
        if self.current_char and self.current_char.isdigit(): return self.d275()
        
        self.errors.append(self._create_digit_error(
            f"Invalid DIME-lit. Expected digit {self.DELIM_ERR_MSG}",
            ["digit"] + self.DELIM_LIST
        ))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
    
    def d274(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d275(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d276()
        if self.current_char and self.current_char.isdigit(): return self.d277()
        
        self.errors.append(self._create_digit_error(
            f"Invalid DIME-lit. Expected digit {self.DELIM_ERR_MSG}",
            ["digit"] + self.DELIM_LIST
        ))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
    
    def d276(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d277(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d278()
        if self.current_char and self.current_char.isdigit(): return self.d279()
        
        self.errors.append(self._create_digit_error(
            f"Invalid DIME-lit. Expected digit {self.DELIM_ERR_MSG}",
            ["digit"] + self.DELIM_LIST
        ))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
    
    def d278(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d279(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d280()
        if self.current_char and self.current_char.isdigit(): return self.d281()
        
        self.errors.append(self._create_digit_error(
            f"Invalid DIME-lit. Expected digit {self.DELIM_ERR_MSG}",
            ["digit"] + self.DELIM_LIST
        ))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
    
    def d280(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d281(self):
        self.advance()
        
        # Check for Delimiter (Valid DIME)
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): 
            return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
        
        # Check for Excess Digits
        if self.current_char and self.current_char.isdigit():
            # Save token value BEFORE processing trailing zeros
            if self.current_char == '0':
                self.final_dime_value = self.current_token_text()
                return self.d_ignore_trailing_zeros()
            
            # REJECT non-zeros immediately
            self.errors.append(self._create_digit_error(
                f"Invalid DIME-Lit. 8-digit limit reached. Expected delimiter, {self.DELIM_ERR_MSG}",
                self.DELIM_LIST
            ))
            return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

        # Invalid Delimiter Error
        self.errors.append(self._create_digit_error(
            f"Invalid DIME-lit. Expected delimiter, {self.DELIM_ERR_MSG}",
            self.DELIM_LIST
        ))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
    
    def d282(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # DIME-lit TD: IGNORE TRAILING Zeroes (NOT TOKENIZED)
    # =============================================
    def d_ignore_trailing_zeros(self):
        # Loop through all trailing zeros, advancing without including them in token
        while self.current_char == '0':
            self.advance()
            
        # After zeros, it should be followed by a valid delimiter
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): 
            # Return token using saved value (without trailing zeros)
            return Token("DIME-lit", self.final_dime_value, self.line, self.col - 1)
            
        # Error: Non-zero digit after 8-digit limit
        if self.current_char and self.current_char.isdigit():
            self.errors.append(self._create_digit_error(
                f"Invalid DIME-Lit. 8-digit limit reached. Expected delimiter, {self.DELIM_ERR_MSG}",
                self.DELIM_LIST
            ))
            return Token("DIME-lit", self.final_dime_value, self.line, self.col - 1)
             
        # Fallback error for invalid delimiters
        self.errors.append(self._create_digit_error(
            f"Invalid DIME-lit. Expected delimiter, {self.DELIM_ERR_MSG}",
            self.DELIM_LIST
        ))
        return Token("DIME-lit", self.final_dime_value, self.line, self.col - 1)