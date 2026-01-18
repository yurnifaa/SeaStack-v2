import string
from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters
from backend.error_msg import ErrorHandler 

class DigitHandler:
    
    # --- HELPER: DYNAMIC & CLEAN ERROR GENERATION ---
    def _report_digit_error(self, delim_key="DIGIT_DELIM", manual_extras=None, error_type=None, custom_msg=None, diff_char=None):
        """
        :param delim_key: The key in Delimiters to fetch allowed chars from
        :param manual_extras: List of extra chars allowed (e.g. ['.'])
        :param error_type: ErrorHandler.ERR_LEX_* constant
        :param custom_msg: Specific message override (e.g. for limits)
        :param diff_char: If we want to report a specific string (like the whole number) instead of current_token_text
        """
        if manual_extras is None:
            manual_extras = []
            
        # 1. Fetch the Set
        allowed_set = set(Delimiters._get_delimiters().get(delim_key, []))
        allowed_set.update(manual_extras)
        
        # 2. CLEANING LOGIC (Condenses 0-9, a-z, whitespace)
        cleaned_list = []

        # Condense Ranges
        if set(string.ascii_lowercase).issubset(allowed_set):
            cleaned_list.append("a-z")
            allowed_set -= set(string.ascii_lowercase)
        
        if set(string.ascii_uppercase).issubset(allowed_set):
            cleaned_list.append("A-Z")
            allowed_set -= set(string.ascii_uppercase)
            
        if set(string.digits).issubset(allowed_set):
            cleaned_list.append("0-9")
            allowed_set -= set(string.digits)

        # Condense Whitespace
        whitespace_subset = allowed_set.intersection(set(string.whitespace))
        if whitespace_subset:
            cleaned_list.append("whitespace")
            allowed_set -= whitespace_subset

        # Format Remaining
        for char in sorted(list(allowed_set)):
            if char == "\n": cleaned_list.append("\\n")
            elif char == "\t": cleaned_list.append("\\t")
            elif char == " ": cleaned_list.append("' '")
            else: cleaned_list.append(char)
        
        # 3. Determine Error Type
        # If not specified, assume it's a Delimiter error (since digits usually fail on delimiters)
        if error_type is None:
            error_type = ErrorHandler.ERR_LEX_INVALID_DELIM

        # 4. Determine Invalid Char/Text to show
        text_to_show = diff_char if diff_char else self.current_token_text()

        # 5. Generate Error
        return ErrorHandler.get_lexical_error(
            line=self.line,
            col=self.col - 1,
            invalid_char=text_to_show,
            expected_list=sorted(cleaned_list),
            header_type=error_type,
            custom_msg=custom_msg
        )

    # =========================================================================
    # ENTRY POINT: COIN and DIME Transition Diagram
    # =========================================================================
    def c233(self):         # NULL ENTRY
        return self.c234()
    
    # =========================================================================
    # COIN-lit TD: Digit up to 16 digits
    # =========================================================================
    def c234(self):             # Digit 1
        # Leading Zero Logic
        if self.current_char == '0':
            self.advance()
            if self.current_char is not None and self.current_char.isdigit():
                self.token_start_pos += 1   # Discard leading zero
                return self.c234()          # Recurse
        else:
            self.advance()

        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]):
            return self.c235()
        if self.current_char and self.current_char.isdigit(): 
            return self.c236()
        if self.current_char == ".": return self.s266()
        
        # ERROR: Expected Digit, Dot, or Delimiter
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))

    def c235(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c236(self):             # Digit 2
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c237()
        if self.current_char and self.current_char.isdigit(): return self.c238()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))

    def c237(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)
    
    def c238(self):             # Digit 3
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c239()
        if self.current_char and self.current_char.isdigit(): return self.c240()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))

    def c239(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c240(self):             # Digit 4
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c241()
        if self.current_char and self.current_char.isdigit(): return self.c242()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))
    
    def c241(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c242(self):             # Digit 5
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c243()
        if self.current_char and self.current_char.isdigit(): return self.c244()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))
    
    def c243(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c244(self):             # Digit 6
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c245()
        if self.current_char and self.current_char.isdigit(): return self.c246()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))
    
    def c245(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c246(self):             # Digit 7
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c247()
        if self.current_char and self.current_char.isdigit(): return self.c248()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))
    
    def c247(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c248(self):             # Digit 8
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c249()
        if self.current_char and self.current_char.isdigit(): return self.c250()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))
    
    def c249(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c250(self):             # Digit 9
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c251()
        if self.current_char and self.current_char.isdigit(): return self.c252()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))
    
    def c251(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c252(self):             # Digit 10
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c253()
        if self.current_char and self.current_char.isdigit(): return self.c254()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))
    
    def c253(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c254(self):             # Digit 11
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c255()
        if self.current_char and self.current_char.isdigit(): return self.c256()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))
    
    def c255(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c256(self):             # Digit 12
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c257()
        if self.current_char and self.current_char.isdigit(): return self.c258()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))
    
    def c257(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c258(self):             # Digit 13
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c259()
        if self.current_char and self.current_char.isdigit(): return self.c260()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))
    
    def c259(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c260(self):             # Digit 14
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c261()
        if self.current_char and self.current_char.isdigit(): return self.c262()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))
    
    def c261(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c262(self):             # Digit 15
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c263()
        if self.current_char and self.current_char.isdigit(): return self.c264()
        if self.current_char == ".": return self.s266()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9", "."]))
    
    def c263(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # =========================================================================
    # COIN-lit TD: 16th Digit (LIMIT CHECK)
    # =========================================================================    
    def c264(self):             # 16th digit
        self.advance()

        # If the next char is a digit → EXCEEDS 16 
        if self.current_char == ".": return self.s266()
        if self.current_char and self.current_char.isdigit():
            
            # --- CUSTOM ERROR: LIMIT REACHED ---
            # We want the UI to show "COIN-Lit exceeds 16 digits" as the header.
            full_number = self.text[self.token_start_pos:self.pos] + "..."
            
            limit_error = self._report_digit_error(
                delim_key="DIGIT_DELIM", 
                manual_extras=[],
                error_type=ErrorHandler.ERR_LEX_LIMIT_EXCEEDED,
                custom_msg="COIN-Lit exceeds 16 digits",
                diff_char=full_number # Send the full number, but the header will use custom_msg
            )
            self.errors.append(limit_error)

            self.token_start_pos = self.pos  # start new token
            return self.state0()  # treat current digit as first digit of new COIN-lit
        
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c265()
        
        # Fallthrough Error for 16th digit transition
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["."]))
        
    def c265(self):
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # =========================================================================
    # DIME-lit TD: Digit up to 8 digits
    # =========================================================================
    def s266(self):  # Checking the Delimiter after the decimal point
        self.advance()
        
        if self.current_char and self.current_char.isdigit(): 
            return self.d267()
            
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9"]))
        return None
        
    def d267(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d268()
        if self.current_char and self.current_char.isdigit(): return self.d269()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9"]))
        return None
    
    def d268(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d269(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d270()
        if self.current_char and self.current_char.isdigit(): return self.d271()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9"]))
        return None
    
    def d270(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d271(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d272()
        if self.current_char and self.current_char.isdigit(): return self.d273()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9"]))
        return None
    
    def d272(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d273(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d274()
        if self.current_char and self.current_char.isdigit(): return self.d275()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9"]))
        return None
    
    def d274(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d275(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d276()
        if self.current_char and self.current_char.isdigit(): return self.d277()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9"]))
        return None
    
    def d276(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d277(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d278()
        if self.current_char and self.current_char.isdigit(): return self.d279()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9"]))
        return None
    
    def d278(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d279(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d280()
        if self.current_char and self.current_char.isdigit(): return self.d281()
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0-9"]))
        return None
    
    def d280(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d281(self): # Digit 8
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
            limit_error = self._report_digit_error(
                delim_key="DIGIT_DELIM", 
                manual_extras=["0"],
                error_type=ErrorHandler.ERR_LEX_LIMIT_EXCEEDED,
                custom_msg="DIME-Lit exceeds 8 decimal digits"
            )
            self.errors.append(limit_error)
            return None

        # 3. Invalid Delimiter Error
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0"]))
        return None
    
    def d282(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # DIME-lit TD: EXTRA/TRAILING Zeroes
    # =============================================
    def d_extra_zeros(self):
        self.advance() # Consume the zero
        
        # IF Delimiter kasunod? edi Done
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): 
            return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
        
        # IF More Zeros kasunod? edi Keep going
        if self.current_char == '0':
            return self.d_extra_zeros()
            
        # IF Non-Zero Digit kasunod? edi Error
        if self.current_char and self.current_char.isdigit():
             limit_error = self._report_digit_error(
                delim_key="DIGIT_DELIM", 
                manual_extras=["0"],
                error_type=ErrorHandler.ERR_LEX_LIMIT_EXCEEDED,
                custom_msg="DIME-Lit exceeds 8 decimal digits"
            )
             self.errors.append(limit_error)
             return None
             
        # Invalid Char/Delimiter
        self.errors.append(self._report_digit_error("DIGIT_DELIM", ["0"]))
        return None