from backend.lexical.token import Token
from backend.lexical.handlers.delimiters import Delimiters

# =================================================================================================
# IDENTIFIERS: must start with lowercase, followed by lowercase/digit/underscore, max of 20 chars.
# =================================================================================================

class Identifiers:

    # ==================================================
    # HELPERS: validate characters and finalize tokens
    # ==================================================

    # check character if valid for identifier
    def check_id(self):
        char = self.current_char
        return char is not None and (char.islower() or char.isdigit() or char == "_")
    
    # finalize identifier token
    def finalize_id(self):
        result = self.current_token_text()
        line, col = self.line, self.col

        # validate delimeter and check if id is new
        if self._comp_delims(Delimiters._get_delimiters()["ID_DELIM"]):

            if result not in self.identifier_table:
                self.identifier_table[result] = f"id{len(self.identifier_table) + 1}"

            token_type = self.identifier_table[result]
            return Token(token_type, result, line, col - 1)

        return self.error()
    
    # ==================================================
    # STATES: char sequences and transitions
    # ==================================================

    # char 1
    def id196(self):
        self.advance() 
        if self.check_id(): return self.i198()
        return self.i197()

    def i197(self): return self.finalize_id()

    # char 2
    def i198(self):
        self.advance()
        if self.check_id(): return self.i200()
        return self.i199()

    def i199(self): return self.finalize_id()

    # char 3
    def i200(self):
        self.advance()
        if self.check_id(): return self.i202()
        return self.i201()

    def i201(self): return self.finalize_id()

    # char 4
    def i202(self):
        self.advance()
        if self.check_id(): return self.i204()
        return self.i203()

    def i203(self): return self.finalize_id()

    # char 5
    def i204(self):
        self.advance()
        if self.check_id(): return self.i206()
        return self.i205()

    def i205(self): return self.finalize_id()

    # char 6
    def i206(self):
        self.advance()
        if self.check_id(): return self.i208()
        return self.i207()

    def i207(self): return self.finalize_id()

    # char 7
    def i208(self):
        self.advance()
        if self.check_id(): return self.i210()
        return self.i209()

    def i209(self): return self.finalize_id()

    # char 8
    def i210(self):
        self.advance()
        if self.check_id(): return self.i212()
        return self.i211()

    def i211(self): return self.finalize_id()

    # char 9
    def i212(self):
        self.advance()
        if self.check_id(): return self.i214()
        return self.i213()

    def i213(self): return self.finalize_id()

    # char 10
    def i214(self):
        self.advance()
        if self.check_id(): return self.i216()
        return self.i215()

    def i215(self): return self.finalize_id()

    # char 11
    def i216(self):
        self.advance()
        if self.check_id(): return self.i218()
        return self.i217()

    def i217(self): return self.finalize_id()

    # char 12
    def i218(self):
        self.advance()
        if self.check_id(): return self.i220()
        return self.i219()

    def i219(self): return self.finalize_id()

    # char 13
    def i220(self):
        self.advance()
        if self.check_id(): return self.i222()
        return self.i221()

    def i221(self): return self.finalize_id()

    # char 14
    def i222(self):
        self.advance()
        if self.check_id(): return self.i224()
        return self.i223()

    def i223(self): return self.finalize_id()

    # char 15
    def i224(self):
        self.advance()
        if self.check_id(): return self.i226()
        return self.i225()

    def i225(self): return self.finalize_id()

    # char 16
    def i226(self):
        self.advance()
        if self.check_id(): return self.i228()
        return self.i227()

    def i227(self): return self.finalize_id()

    # char 17
    def i228(self):
        self.advance()
        if self.check_id(): return self.i230()
        return self.i229()

    def i229(self): return self.finalize_id()

    # char 18
    def i230(self):
        self.advance()
        if self.check_id(): return self.i232()
        return self.i231()

    def i231(self): return self.finalize_id()

    # char 19
    def i232(self):
        self.advance()
        if self.check_id(): return self.i234()
        return self.i233()

    def i233(self): return self.finalize_id()

    # char 20
    def i234(self):
        self.advance()
        if self.check_id(): return self.error()
        return self.i235()

    # tokenize identifier
    def i235(self): return self.finalize_id()