from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters

class DigitHandler:
    
    # Error message constant for consistency
    # lists all chars in DIGIT_DELIM: Whitespace | +-*/% | <>=!&| | ) } ] : ,
    DELIM_ERR = "whitespace, +, -, *, /, %, <, >, =, !, &, |, ), }, ], :, ,"

    # =========================================================================
    # ENTRY POINT: COIN and DIME Transition Diagram
    # =========================================================================
    def c233(self):         # NULL ENTRY → do not consume → go directly to 230.
        return self.c234()
    
    # =========================================================================
    # COIN-lit TD: Digit up to 16 digits
    # =========================================================================
    def c234(self):             # Digit 1
        
        # ======================================
        # LEADING ZEROS LOGIC
        # ======================================
        if self.current_char == '0':
            self.advance() # Consume the '0'
            
            # If the NEXT character is NON-ZERO, the previous '0' was a leading zero.
            if self.current_char is not None and self.current_char.isdigit():
                self.token_start_pos += 1   # Discard the '0' from the token text
                return self.c234()          # Recurse: The next digit becomes the new "Digit 1"
            
            # If the next character is NOT a digit (a '.', delimiter,  End of File),
            # then the '0' we just consumed is significant.
            
        else:
            self.advance()

        # --- NON ZERO DIGIT 1 LOGIC ---
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]):
            return self.c235()
        if self.current_char and self.current_char.isdigit(): 
            return self.c236()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )

    def c235(self):             # End after 1 digit
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c236(self):             # Digit 2
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]):
            return self.c237()
        if self.current_char and self.current_char.isdigit():
            return self.c238()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )

    def c237(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)
    
    def c238(self):             # Digit 3
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c239()
        if self.current_char and self.current_char.isdigit(): return self.c240()
        if self.current_char == ".": return self.s266()
        
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )

    def c239(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c240(self):             # Digit 4
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c241()
        if self.current_char and self.current_char.isdigit(): return self.c242()
        if self.current_char == ".": return self.s266()
        self.errors.append(
            Token(
            "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )
    
    def c241(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c242(self):             # Digit 5
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c243()
        if self.current_char and self.current_char.isdigit(): return self.c244()
        if self.current_char == ".": return self.s266()
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )
    
    def c243(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c244(self):             # Digit 6
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c245()
        if self.current_char and self.current_char.isdigit(): return self.c246()
        if self.current_char == ".": return self.s266()
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )

    
    def c245(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c246(self):             # Digit 7
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c247()
        if self.current_char and self.current_char.isdigit(): return self.c248()
        if self.current_char == ".": return self.s266()
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )
    
    def c247(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c248(self):             # Digit 8
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c249()
        if self.current_char and self.current_char.isdigit(): return self.c250()
        if self.current_char == ".": return self.s266()
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )
    
    def c249(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c250(self):             # Digit 9
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c251()
        if self.current_char and self.current_char.isdigit(): return self.c252()
        if self.current_char == ".": return self.s266()
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )
    
    def c251(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c252(self):             # Digit 10
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c253()
        if self.current_char and self.current_char.isdigit(): return self.c254()
        if self.current_char == ".": return self.s266()
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )
    
    def c253(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c254(self):             # Digit 11
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c255()
        if self.current_char and self.current_char.isdigit(): return self.c256()
        if self.current_char == ".": return self.s266()
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )
    
    def c255(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c256(self):             # Digit 12
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c257()
        if self.current_char and self.current_char.isdigit(): return self.c258()
        if self.current_char == ".": return self.s266()
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )
    
    def c257(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c258(self):             # Digit 13
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c259()
        if self.current_char and self.current_char.isdigit(): return self.c260()
        if self.current_char == ".": return self.s266()
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )

    
    def c259(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c260(self):             # Digit 14
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c261()
        if self.current_char and self.current_char.isdigit(): return self.c262()
        if self.current_char == ".": return self.s266()
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )
    
    def c261(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c262(self):             # Digit 15
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c263()
        if self.current_char and self.current_char.isdigit(): return self.c264()
        if self.current_char == ".": return self.s266()
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected digit, '.', {self.DELIM_ERR}",
            )
        )
    
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
            self.errors.append(
                Token(
                    "ERROR",
                    self.text[self.token_start_pos:self.pos],  # the first 16 digits
                    self.line,
                    self.col - 1, 
                    "COIN-Lit exceeds 16 digits. Expected delimiter: .)}]:, ",
                )
            )

            self.token_start_pos = self.pos  # start new token
            return self.state0()  # treat current digit as first digit of new COIN-lit
        
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c265()
        
        # Fallthrough Error for 16th digit transition
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid COIN-lit. Expected '.', {self.DELIM_ERR}",
            )
        )
        
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
            
        # ERROR: No digit after dot  invalid char after dot (e.g., "123.")
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                "Invalid DIME-lit. Expected digit after decimal point.",
            )
        )
        return None
        
    def d267(self):
        self.advance()
        
        # IF Valid Delimiter
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): 
            return self.d268()
            
        # IF Valid Next Digit
        if self.current_char and self.current_char.isdigit(): 
            return self.d269()
            
        # ERROR: Invalid Character OR Delimiter
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid DIME-lit. Expected digit {self.DELIM_ERR}",
            )
        )
        return None
    
    def d268(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # DIME-lit TD: Digit 2 (AFTER decimal)
    # =============================================
    def d269(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d270()
        if self.current_char and self.current_char.isdigit(): return self.d271()
        
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid DIME-lit. Expected digit {self.DELIM_ERR}",
            )
        )
        return None
    
    def d270(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # DIME-lit TD: Digit 3 (AFTER decimal)
    # =============================================
    def d271(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d272()
        if self.current_char and self.current_char.isdigit(): return self.d273()
        
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid DIME-lit. Expected digit {self.DELIM_ERR}",
            )
        )
        return None
    
    def d272(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # DIME-lit TD: Digit 4 (AFTER decimal)
    # =============================================
    def d273(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d274()
        if self.current_char and self.current_char.isdigit(): return self.d275()
        
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid DIME-lit. Expected digit {self.DELIM_ERR}",
            )
        )
        return None
    
    def d274(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # DIME-lit TD: Digit 5 (AFTER decimal)
    # =============================================
    def d275(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d276()
        if self.current_char and self.current_char.isdigit(): return self.d277()
        
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid DIME-lit. Expected digit {self.DELIM_ERR}",
            )
        )
        return None
    
    def d276(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # DIME-lit TD: Digit 6 (AFTER decimal)
    # =============================================
    def d277(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d278()
        if self.current_char and self.current_char.isdigit(): return self.d279()
        
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid DIME-lit. Expected digit {self.DELIM_ERR}",
            )
        )
        return None
    
    def d278(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # DIME-lit TD: Digit 7 (AFTER decimal)
    # =============================================
    def d279(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d280()
        if self.current_char and self.current_char.isdigit(): return self.d281()
        
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid DIME-lit. Expected digit {self.DELIM_ERR}",
            )
        )
        return None
    
    def d280(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # DIME-lit TD: Digit 8 (AFTER decimal)
    # =============================================
    def d281(self):
        self.advance()
        
        # 1. Check for Delimiter (Valid DIME)
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): 
            return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
        
        # 2. Check for Excess Digits
        if self.current_char and self.current_char.isdigit():
            # ALLOW trailing zeros
            if self.current_char == '0':
                return self.d_extra_zeros()
            
            # REJECT non-zeros immediately
            self.errors.append(
                Token(
                    "ERROR",
                    self.current_token_text(), 
                    self.line,
                    self.col - 1, 
                    f"Invalid DIME-Lit. 8-digit limit reached. Expected '0', {self.DELIM_ERR}",
                )
            )
            return None

        # 3. Invalid Delimiter Error
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid DIME-lit. Expected '0', {self.DELIM_ERR}",
            )
        )
        return None
    
    def d282(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # DIME-lit TD: EXTRA/TRAILING Zeroes
    # =============================================
    def d_extra_zeros(self):
        # Saw a '0' after the 8th digit.
        self.advance() # Consume the zero
        
        # IF Delimiter kasunod? edi Done
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): 
            return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
        
        # IF More Zeros kasunod? edi Keep going
        if self.current_char == '0':
            return self.d_extra_zeros()
            
        # IF Non-Zero Digit kasunod? edi Error
        if self.current_char and self.current_char.isdigit():
             self.errors.append(
                Token(
                    "ERROR",
                    self.current_token_text(), 
                    self.line,
                    self.col - 1, 
                    f"Invalid DIME-Lit. 8-digit limit reached. Expected '0', {self.DELIM_ERR}",
                )
            )
             return None
             
        # Invalid Char/Delimiter
        self.errors.append(
            Token(
                "ERROR",
                self.current_token_text(),
                self.line,
                self.col - 1,
                f"Invalid DIME-lit. Expected '0', {self.DELIM_ERR}",
            )
        )
        return None