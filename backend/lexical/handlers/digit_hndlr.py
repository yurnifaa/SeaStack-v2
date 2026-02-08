# lexer_handlers/digit_handler.py
from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters

class DigitHandler:
    
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
    # HELPER: Report Error (Matches resword_hndlr pattern)
    # Creates token, appends to errors, and returns None
    # =========================================================================
    def _report_digit_error(self, message):
        # Default expectation for digits is DIGIT_DELIM
        raw_delims = Delimiters._get_delimiters()["DIGIT_DELIM"]
        
        err_token = Token(
            "ERROR",
            self.current_token_text(),
            self.line,
            self.col - 1,
            message,
        )
        
        err_token.expected = self._sanitize_delims(raw_delims)
        
        self.errors.append(err_token)
        return None

    # =========================================================================
    # ENTRY POINT
    # =========================================================================
    def _make_digit(self):
        if self.current_char == '-':
            self.advance()
        return self.c235()

    # =========================================================================
    # COIN-lit (Integers) - States 235 to 266
    # =========================================================================
    
    # --- Digit 1 (State 235) ---
    def c235(self):
        # PATH A: Leading Zero
        if self.current_char == '0':
            self.advance() 
            
            if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]):
                return self.c236()
            
            if self.current_char == ".":
                return self.d267()
                
            if self.current_char is not None and self.current_char.isdigit():
                return self._report_digit_error("Invalid COIN-lit. Leading zeros are not allowed.")
            
            return self._report_digit_error("Invalid COIN-lit. Expected '.', or delimiter.")

        # PATH B: Non-Zero Digit
        elif self.current_char in Delimiters._get_delimiters()["NONZERO"]:
            self.advance()
            
            if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]):
                return self.c238()
            if self.current_char == ".":
                return self.d267()
            if self.current_char is not None and self.current_char.isdigit():
                return self.c237() 
                
            return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

        self.advance()
        return self._report_digit_error("Invalid Digit Start.")

    def c236(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 2 (State 237) ---
    def c237(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c238()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c239()
        
        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c238(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 3 (State 239) ---
    def c239(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c240()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c241()

        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c240(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 4 (State 241) ---
    def c241(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c242()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c243()

        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c242(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 5 (State 243) ---
    def c243(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c244()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c245()

        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c244(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 6 (State 245) ---
    def c245(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c246()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c247()

        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c246(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 7 (State 247) ---
    def c247(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c248()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c249()

        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c248(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 8 (State 249) ---
    def c249(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c250()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c251()

        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c250(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 9 (State 251) ---
    def c251(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c252()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c253()

        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c252(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 10 (State 253) ---
    def c253(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c254()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c255()

        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c254(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 11 (State 255) ---
    def c255(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c256()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c257()

        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c256(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 12 (State 257) ---
    def c257(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c258()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c259()

        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c258(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 13 (State 259) ---
    def c259(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c260()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c261()

        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c260(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 14 (State 261) ---
    def c261(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c262()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c263()

        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c262(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 15 (State 263) ---
    def c263(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c264()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c265()

        return self._report_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter.")

    def c264(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 16 (State 265) - MAX LENGTH COIN ---
    def c265(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c266()
        if self.current_char == ".": return self.d267()
        
        # Limit Exceeded
        if self.current_char is not None and self.current_char.isdigit(): 
            return self._report_digit_error("Invalid COIN-lit. Limit (16) exceeded. Expected delimiter or '.'")

        return self._report_digit_error("Invalid COIN-lit. Expected '.', or delimiter.")

    def c266(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # =========================================================================
    # DIME-lit (Decimals) - States 267 to 283
    # =========================================================================

    # State 267 (The Dot)
    def d267(self):
        self.advance()
        if self.current_char is not None and self.current_char.isdigit(): return self.d268()
        
        return self._report_digit_error("Invalid DIME-lit. Expected digit after '.'")

    # --- DIME Digit 1 (State 268) ---
    def d268(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d269()
        if self.current_char is not None and self.current_char.isdigit(): return self.d270()

        return self._report_digit_error("Invalid DIME-lit. Expected digit or delimiter.")

    def d269(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 2 (State 270) ---
    def d270(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d271()
        if self.current_char is not None and self.current_char.isdigit(): return self.d272()

        return self._report_digit_error("Invalid DIME-lit. Expected digit or delimiter.")

    def d271(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 3 (State 272) ---
    def d272(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d273()
        if self.current_char is not None and self.current_char.isdigit(): return self.d274()

        return self._report_digit_error("Invalid DIME-lit. Expected digit or delimiter.")

    def d273(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 4 (State 274) ---
    def d274(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d275()
        if self.current_char is not None and self.current_char.isdigit(): return self.d276()
        
        return self._report_digit_error("Invalid DIME-lit. Expected digit or delimiter.")

    def d275(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 5 (State 276) ---
    def d276(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d277()
        if self.current_char is not None and self.current_char.isdigit(): return self.d278()

        return self._report_digit_error("Invalid DIME-lit. Expected digit or delimiter.")
    
    def d277(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 6 (State 278) ---
    def d278(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d279()
        if self.current_char is not None and self.current_char.isdigit(): return self.d280()

        return self._report_digit_error("Invalid DIME-lit. Expected digit or delimiter.")

    def d279(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 7 (State 280) ---
    def d280(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d281()
        if self.current_char is not None and self.current_char.isdigit(): return self.d282()

        return self._report_digit_error("Invalid DIME-lit. Expected digit or delimiter.")

    def d281(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 8 (State 282) - MAX LENGTH DIME ---
    def d282(self):
        self.advance()
        significant_end = self.pos
        while self.current_char == '0':
            self.advance()

        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d283(significant_end)

        if self.current_char is not None and self.current_char.isdigit(): 
             return self._report_digit_error("Invalid DIME-lit. Limit (8) exceeded. Expected delimiter.")

        return self._report_digit_error("Invalid DIME-lit. Expected delimiter.")

    def d283(self, lexeme_end=None): 
        if lexeme_end:
            result_lexeme = self.text[self.token_start_pos : lexeme_end]
            return Token("DIME-lit", result_lexeme, self.line, self.col - 1)
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)