from backend.lexical.token import Token
from backend.lexical.handlers.delimiters import Delimiters
from backend.lexical.lexer_errors import LexerErrors

# =================================================================================================
# DIGITS: max of 16 digits for integer part, 8 digits for decimal part.
#         no leading or trailing zeros allowed except 0 or .0
# =================================================================================================

class Digits(LexerErrors):

    # ==================================================
    # HELPERS
    # ==================================================

    # check digit if valid
    def check_digit(self):
        return self.current_char is not None and self.current_char.isdigit()
    
    # finalize COIN or DIME literal token
    def finalize_coin(self):
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]):
            return Token("COIN-lit", self.current_token_text(), self.line, self.col - 1)
        return self.error()

    def finalize_dime(self):
        if self._comp_delims(Delimiters._get_delimiters()["DIGIT_DELIM"]):
            return Token("DIME-lit", self.current_token_text(), self.line, self.col - 1)
        return self.error()

    # ==================================================
    # COIN Literals
    # ==================================================

    # lone 0
    def c236(self):
        self.advance()
        if self.current_char == ".": return self.d270()
        return self.c237()

    def c237(self): return self.finalize_coin()

    # digit 1
    def c238(self):
        self.advance()
        if self.check_digit(): return self.c240()
        if self.current_char == ".": return self.d270()
        return self.c239()

    def c239(self): return self.finalize_coin()

    # digit 2
    def c240(self):
        self.advance()
        if self.check_digit(): return self.c242()
        if self.current_char == ".": return self.d270()
        return self.c241()

    def c241(self): return self.finalize_coin()

    # digit 3
    def c242(self):
        self.advance()
        if self.check_digit(): return self.c244()
        if self.current_char == ".": return self.d270()
        return self.c243()

    def c243(self): return self.finalize_coin()

    # digit 4
    def c244(self):
        self.advance()
        if self.check_digit(): return self.c246()
        if self.current_char == ".": return self.d270()
        return self.c245()

    def c245(self): return self.finalize_coin()

    # digit 5
    def c246(self):
        self.advance()
        if self.check_digit(): return self.c248()
        if self.current_char == ".": return self.d270()
        return self.c247()

    def c247(self): return self.finalize_coin()

    # digit 6
    def c248(self):
        self.advance()
        if self.check_digit(): return self.c250()
        if self.current_char == ".": return self.d270()
        return self.c249()

    def c249(self): return self.finalize_coin()

    # digit 7
    def c250(self):
        self.advance()
        if self.check_digit(): return self.c252()
        if self.current_char == ".": return self.d270()
        return self.c251()

    def c251(self): return self.finalize_coin()

    # digit 8
    def c252(self):
        self.advance()
        if self.check_digit(): return self.c254()
        if self.current_char == ".": return self.d270()
        return self.c253()

    def c253(self): return self.finalize_coin()

    # digit 9
    def c254(self):
        self.advance()
        if self.check_digit(): return self.c256()
        if self.current_char == ".": return self.d270()
        return self.c255()

    def c255(self): return self.finalize_coin()

    # digit 10
    def c256(self):
        self.advance()
        if self.check_digit(): return self.c258()
        if self.current_char == ".": return self.d270()
        return self.c257()

    def c257(self): return self.finalize_coin()

    # digit 11
    def c258(self):
        self.advance()
        if self.check_digit(): return self.c260()
        if self.current_char == ".": return self.d270()
        return self.c259()

    def c259(self): return self.finalize_coin()

    # digit 12
    def c260(self):
        self.advance()
        if self.check_digit(): return self.c262()
        if self.current_char == ".": return self.d270()
        return self.c261()

    def c261(self): return self.finalize_coin()

    # digit 13
    def c262(self):
        self.advance()
        if self.check_digit(): return self.c264()
        if self.current_char == ".": return self.d270()
        return self.c263()

    def c263(self): return self.finalize_coin()

    # digit 14
    def c264(self):
        self.advance()
        if self.check_digit(): return self.c266()
        if self.current_char == ".": return self.d270()
        return self.c265()

    def c265(self): return self.finalize_coin()

    # digit 15
    def c266(self):
        self.advance()
        if self.check_digit(): return self.c268()
        if self.current_char == ".": return self.d270()
        return self.c267()

    def c267(self): return self.finalize_coin()

    # digit 16
    def c268(self):
        self.advance()
        if self.check_digit(): return self.error()
        if self.current_char == ".": return self.d270()
        return self.c269()

    def c269(self): return self.finalize_coin()

    # =========================================================================
    # DIME Literals
    # =========================================================================

    # decimal point
    def d270(self):
        self.advance()
        if self.check_digit(): return self.d271()
        return self.error()

    # decimal 1
    def d271(self):
        self.advance()
        if self.check_digit(): return self.d273()
        return self.d272()

    def d272(self): return self.finalize_dime

    # decimal 2
    def d273(self):
        self.advance()
        if self.check_digit(): return self.d275()
        return self.d274()

    def d274(self): return self.finalize_dime

    # decimal 3
    def d275(self):
        self.advance()
        if self.check_digit(): return self.d277()
        return self.d276()

    def d276(self): return self.finalize_dime
    
    # decimal 4
    def d277(self):
        self.advance()
        if self.check_digit(): return self.d279()
        return self.d278()

    def d278(self): return self.finalize_dime

    # decimal 5
    def d279(self):
        self.advance()
        if self.check_digit(): return self.d281()
        return self.d280()

    def d280(self): return self.finalize_dime
    
    # decimal 6
    def d281(self):
        self.advance()
        if self.check_digit(): return self.d283()
        return self.d282()

    def d282(self): return self.finalize_dime

    # decimal 7
    def d283(self):
        self.advance()
        if self.check_digit(): return self.d285()
        return self.d284()

    def d284(self): return self.finalize_dime

    # decimal 8
    def d285(self):
        self.advance()
        if self.check_digit(): return self.error()
        return self.d286()

    def d286(self): return self.finalize_dime