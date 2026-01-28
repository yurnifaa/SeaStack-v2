# lexer_handlers/digit_handler.py
from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters

class DigitHandler:
    
    # =========================================================================
    # HELPER: Sanitize Delimiters for Display
    # Replaces invisible chars ('\n', '\t', etc.) with the word "whitespace"
    # =========================================================================
    def _sanitize_delims(self, delim_set):
        # Ensure we are working with a list
        delims = list(delim_set) if isinstance(delim_set, set) else delim_set
        cleaned_list = []
        has_whitespace = False
        
        for d in delims:
            # Check for invisible whitespace characters
            if d in [' ', '\t', '\n', '\r', '\v', '\f']:
                has_whitespace = True
            # Check if the string "whitespace" was passed manually
            elif d == "whitespace":
                has_whitespace = True
            else:
                cleaned_list.append(d)
        
        if has_whitespace:
            cleaned_list.append("whitespace")
            
        # Remove duplicates and sort
        cleaned_list = list(set(cleaned_list))
        cleaned_list.sort(key=str)
        return cleaned_list

    # =========================================================================
    # HELPER: Create Error with Expected List
    # =========================================================================
    def _create_digit_error(self, message):
        # Retrieve the valid delimiters for Digits
        raw_delims = Delimiters._get_delimiters()["DIGIT_DELIM"]
        
        err_token = Token(
            "ERROR",
            self.current_token_text(),
            self.line,
            self.col - 1,
            message,
        )
        
        # --- SANITIZE BEFORE ATTACHING ---
        err_token.expected = self._sanitize_delims(raw_delims)
        
        return err_token

    # =========================================================================
    # ENTRY POINT
    # =========================================================================
    def _make_digit(self):
        # If we see a '-', consume it and treat it as part of the number
        if self.current_char == '-':
            self.advance()
        
        # Transition to State 235 (1st Digit of COIN)
        return self.c235()

    # =========================================================================
    # COIN-lit (Integers) - States 235 to 266
    # =========================================================================
    
    # --- Digit 1 (State 235) ---
    def c235(self):
        # Leading Zero Logic
        if self.current_char == '0':
            peek_char = self.text[self.pos + 1] if self.pos + 1 < len(self.text) else None
            
            if peek_char and peek_char.isdigit():
                self.advance()              # Consume the '0'
                return self.c235()          # Recurse           
        self.advance()

        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c236()
        if self.current_char == ".": return self.d267() # Transition to DIME (State 267)
        if self.current_char is not None and self.current_char.isdigit(): return self.c237() # To Digit 2
        
        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # State 236 (Accept 1 Digit)
    def c236(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 2 (State 237) ---
    def c237(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c238()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c239()
        
        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c238(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 3 (State 239) ---
    def c239(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c240()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c241()

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c240(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 4 (State 241) ---
    def c241(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c242()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c243()

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c242(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 5 (State 243) ---
    def c243(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c244()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c245()

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c244(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 6 (State 245) ---
    def c245(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c246()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c247()

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c246(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 7 (State 247) ---
    def c247(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c248()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c249()

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c248(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 8 (State 249) ---
    def c249(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c250()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c251()

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c250(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 9 (State 251) ---
    def c251(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c252()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c253()

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c252(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 10 (State 253) ---
    def c253(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c254()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c255()

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c254(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 11 (State 255) ---
    def c255(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c256()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c257()

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c256(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 12 (State 257) ---
    def c257(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c258()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c259()

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c258(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 13 (State 259) ---
    def c259(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c260()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c261()

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c260(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 14 (State 261) ---
    def c261(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c262()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c263()

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c262(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 15 (State 263) ---
    def c263(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c264()
        if self.current_char == ".": return self.d267()
        if self.current_char is not None and self.current_char.isdigit(): return self.c265()

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected digit, '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c264(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 16 (State 265) - MAX LENGTH COIN ---
    def c265(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c266()
        if self.current_char == ".": return self.d267()
        
        # If another digit appears, Limit Exceeded
        if self.current_char is not None and self.current_char.isdigit(): 
            self.errors.append(self._create_digit_error("Invalid COIN-lit. Limit (16) exceeded. Expected delimiter or '.'"))
            return None 

        self.errors.append(self._create_digit_error("Invalid COIN-lit. Expected '.', or delimiter."))
        return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    def c266(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # =========================================================================
    # DIME-lit (Decimals) - States 267 to 283
    # =========================================================================

    # State 267 (The Dot) -> Expects 1st Digit
    def d267(self):
        self.advance()
        if self.current_char is not None and self.current_char.isdigit(): return self.d268()
        
        # If no digit follows dot, it's an error (e.g., "123.")
        self.errors.append(self._create_digit_error("Invalid DIME-lit. Expected digit after '.'"))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 1 (State 268) ---
    def d268(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d269()
        if self.current_char is not None and self.current_char.isdigit(): return self.d270()

        self.errors.append(self._create_digit_error("Invalid DIME-lit. Expected digit or delimiter."))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d269(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 2 (State 270) ---
    def d270(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d271()
        if self.current_char is not None and self.current_char.isdigit(): return self.d272()

        self.errors.append(self._create_digit_error("Invalid DIME-lit. Expected digit or delimiter."))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d271(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 3 (State 272) ---
    def d272(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d273()
        if self.current_char is not None and self.current_char.isdigit(): return self.d274()

        self.errors.append(self._create_digit_error("Invalid DIME-lit. Expected digit or delimiter."))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d273(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 4 (State 274) ---
    def d274(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d275()
        if self.current_char is not None and self.current_char.isdigit(): return self.d276()
        
        self.errors.append(self._create_digit_error("Invalid DIME-lit. Expected digit or delimiter."))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d275(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 5 (State 276) ---
    def d276(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d277()
        if self.current_char is not None and self.current_char.isdigit(): return self.d278()

        self.errors.append(self._create_digit_error("Invalid DIME-lit. Expected digit or delimiter."))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
    
    def d277(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 6 (State 278) ---
    def d278(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d279()
        if self.current_char is not None and self.current_char.isdigit(): return self.d280()

        self.errors.append(self._create_digit_error("Invalid DIME-lit. Expected digit or delimiter."))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d279(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 7 (State 280) ---
    def d280(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d281()
        if self.current_char is not None and self.current_char.isdigit(): return self.d282()

        self.errors.append(self._create_digit_error("Invalid DIME-lit. Expected digit or delimiter."))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d281(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 8 (State 282) - MAX LENGTH DIME ---
    def d282(self):
        self.advance()
        
        significant_end = self.pos

        # Handle Trailing Zeros directly in a loop
        while self.current_char == '0':
            self.advance()

        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d283(significant_end)

        # If another digit appears, Limit Exceeded
        if self.current_char is not None and self.current_char.isdigit(): 
             self.errors.append(self._create_digit_error("Invalid DIME-lit. Limit (8) exceeded. Expected delimiter."))
             return None

        self.errors.append(self._create_digit_error("Invalid DIME-lit. Expected delimiter."))
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    def d283(self, lexeme_end=None): 
        if lexeme_end:
            result_lexeme = self.text[self.token_start_pos : lexeme_end]
            return Token("DIME-lit", result_lexeme, self.line, self.col - 1)
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)