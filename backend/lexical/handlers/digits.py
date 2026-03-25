from backend.lexical.token import Token
from backend.lexical.handlers.delimiters import Delimiters
from backend.lexical.lexer_errors import LexerErrors

# =================================================================================================
# DIGITS: must start with lowercase. followed by lowercase, digit, or underscore. max 20 chars.
# =================================================================================================

class Digits(LexerErrors):

    # =========================================================================
    # ENTRY POINT
    # =========================================================================
    def _make_digit(self):
        if self.current_char == '-':
            self.advance()
        return self.c236()

    # =========================================================================
    # COIN-lit (Integers) - States 236 to 267
    # =========================================================================

    # --- Digit 1 (State 236) ---
    def c236(self):
        # PATH A: Leading Zero
        if self.current_char == '0':
            self.advance()

            if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]):
                return self.c237()

            if self.current_char == ".":
                return self.d268()

            if self.current_char is not None and self.current_char.isdigit():
                return self.error()

            return self.error()

        # PATH B: Non-Zero Digit
        elif self.current_char in Delimiters._get_delimiters()["NONZERO"]:
            self.advance()

            if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]):
                return self.c239()
            if self.current_char == ".":
                return self.d268()
            if self.current_char is not None and self.current_char.isdigit():
                return self.c238()

            return self.error()

        self.advance()
        return self.error()

    def c237(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 2 (State 238) ---
    def c238(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c239()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c240()

        return self.error()

    def c239(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 3 (State 240) ---
    def c240(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c241()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c242()

        return self.error()

    def c241(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 4 (State 242) ---
    def c242(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c243()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c244()

        return self.error()

    def c243(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 5 (State 244) ---
    def c244(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c245()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c246()

        return self.error()

    def c245(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 6 (State 246) ---
    def c246(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c247()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c248()

        return self.error()

    def c247(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 7 (State 248) ---
    def c248(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c249()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c250()

        return self.error()

    def c249(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 8 (State 250) ---
    def c250(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c251()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c252()

        return self.error()

    def c251(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 9 (State 252) ---
    def c252(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c253()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c254()

        return self.error()

    def c253(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 10 (State 254) ---
    def c254(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c255()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c256()

        return self.error()

    def c255(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 11 (State 256) ---
    def c256(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c257()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c258()

        return self.error()

    def c257(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 12 (State 258) ---
    def c258(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c259()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c260()

        return self.error()

    def c259(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 13 (State 260) ---
    def c260(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c261()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c262()

        return self.error()

    def c261(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 14 (State 262) ---
    def c262(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c263()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c264()

        return self.error()

    def c263(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 15 (State 264) ---
    def c264(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c265()
        if self.current_char == ".": return self.d268()
        if self.current_char is not None and self.current_char.isdigit(): return self.c266()

        return self.error()

    def c265(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # --- Digit 16 (State 266) - MAX LENGTH COIN ---
    def c266(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.c267()
        if self.current_char == ".": return self.d268()

        # Limit Exceeded
        if self.current_char is not None and self.current_char.isdigit():
            return self.error()

        return self.error()

    def c267(self): return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)

    # =========================================================================
    # DIME-lit (Decimals) - States 268 to 284
    # =========================================================================

    # State 268 (The Dot)
    def d268(self):
        self.advance()
        if self.current_char is not None and self.current_char.isdigit(): return self.d269()

        return self.error()

    # --- DIME Digit 1 (State 269) ---
    def d269(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d270()
        if self.current_char is not None and self.current_char.isdigit(): return self.d271()

        return self.error()

    def d270(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 2 (State 271) ---
    def d271(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d272()
        if self.current_char is not None and self.current_char.isdigit(): return self.d273()

        return self.error()

    def d272(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 3 (State 273) ---
    def d273(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d274()
        if self.current_char is not None and self.current_char.isdigit(): return self.d275()

        return self.error()

    def d274(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 4 (State 275) ---
    def d275(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d276()
        if self.current_char is not None and self.current_char.isdigit(): return self.d277()

        return self.error()

    def d276(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 5 (State 277) ---
    def d277(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d278()
        if self.current_char is not None and self.current_char.isdigit(): return self.d279()

        return self.error()
    
    def d278(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 6 (State 279) ---
    def d279(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d280()
        if self.current_char is not None and self.current_char.isdigit(): return self.d281()

        return self.error()

    def d280(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 7 (State 281) ---
    def d281(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]): return self.d282()
        if self.current_char is not None and self.current_char.isdigit(): return self.d283()

        return self.error()

    def d282(self): return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)

    # --- DIME Digit 8 (State 283) - MAX LENGTH DIME ---
    def d283(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]):
            return self.d284()
        if self.current_char is not None and self.current_char.isdigit():
            return self.error()

        return self.error()

    def d284(self):
        return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
