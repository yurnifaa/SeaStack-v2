from backend.lexical.token import Token
from backend.lexical.handlers.delimiters import Delimiters

# =================================================================================================
# IDENTIFIERS: must start with lowercase. followed by lowercase, digit, or underscore. max 20 chars.
# =================================================================================================

class Identifiers:

    # id char checker
    def check_id(self):
        char = self.current_char
        return char is not None and (char.islower() or char.isdigit() or char == "_")

    # char 1
    def id196(self):
        self.advance() 

        if self.check_id():
            self.advance()
            return self.i198()
        return self.i197()

    def i197(self): return self.finalize_id()

    # char 2
    def i198(self):
        if self.check_id():
            self.advance()
            return self.i200()
        return self.i199()

    def i199(self): return self.finalize_id()

    # char 3
    def i200(self):
        if self.check_id():
            self.advance()
            return self.i202()
        return self.i201()

    def i201(self): return self.finalize_id()

    # State 202 (Check 4th char) -> 204 (Next) or 203 (Accept 3 chars)
    def i202(self):
        if self.check_id():
            self.advance()
            return self.i204()
        return self.i203()

    def i203(self): return self.finalize_id()

    # State 204 (Check 5th char) -> 206 (Next) or 205 (Accept 4 chars)
    def i204(self):
        if self.check_id():
            self.advance()
            return self.i206()
        return self.i205()

    def i205(self): return self.finalize_id()

    # State 206 (Check 6th char) -> 208 (Next) or 207 (Accept 5 chars)
    def i206(self):
        if self.check_id():
            self.advance()
            return self.i208()
        return self.i207()

    def i207(self): return self.finalize_id()

    # State 208 (Check 7th char) -> 210 (Next) or 209 (Accept 6 chars)
    def i208(self):
        if self.check_id():
            self.advance()
            return self.i210()
        return self.i209()

    def i209(self): return self.finalize_id()

    # State 210 (Check 8th char) -> 212 (Next) or 211 (Accept 7 chars)
    def i210(self):
        if self.check_id():
            self.advance()
            return self.i212()
        return self.i211()

    def i211(self): return self.finalize_id()

    # State 211 (Check 9th char) -> 214 (Next) or 213 (Accept 8 chars)
    def i212(self):
        if self.check_id():
            self.advance()
            return self.i214()
        return self.i213()

    def i213(self): return self.finalize_id()

    # State 214 (Check 10th char) -> 216 (Next) or 215 (Accept 9 chars)
    def i214(self):
        if self.check_id():
            self.advance()
            return self.i216()
        return self.i215()

    def i215(self): return self.finalize_id()

    # State 216 (Check 11th char) -> 218 (Next) or 217 (Accept 10 chars)
    def i216(self):
        if self.check_id():
            self.advance()
            return self.i218()
        return self.i217()

    def i217(self): return self.finalize_id()

    # State 218 (Check 12th char) -> 220 (Next) or 219 (Accept 11 chars)
    def i218(self):
        if self.check_id():
            self.advance()
            return self.i220()
        return self.i219()

    def i219(self): return self.finalize_id()

    # State 220 (Check 13th char) -> 222 (Next) or 221 (Accept 12 chars)
    def i220(self):
        if self.check_id():
            self.advance()
            return self.i222()
        return self.i221()

    def i221(self): return self.finalize_id()

    # State 222 (Check 14th char) -> 224 (Next) or 223 (Accept 13 chars)
    def i222(self):
        if self.check_id():
            self.advance()
            return self.i224()
        return self.i223()

    def i223(self): return self.finalize_id()

    # State 224 (Check 15th char) -> 226 (Next) or 225 (Accept 14 chars)
    def i224(self):
        if self.check_id():
            self.advance()
            return self.i226()
        return self.i225()

    def i225(self): return self.finalize_id()

    # State 226 (Check 16th char) -> 228 (Next) or 227 (Accept 15 chars)
    def i226(self):
        if self.check_id():
            self.advance()
            return self.i228()
        return self.i227()

    def i227(self): return self.finalize_id()

    # State 228 (Check 17th char) -> 230 (Next) or 229 (Accept 16 chars)
    def i228(self):
        if self.check_id():
            self.advance()
            return self.i230()
        return self.i229()

    def i229(self): return self.finalize_id()

    # State 230 (Check 18th char) -> 232 (Next) or 231 (Accept 17 chars)
    def i230(self):
        if self.check_id():
            self.advance()
            return self.i232()
        return self.i231()

    def i231(self): return self.finalize_id()

    # State 232 (Check 19th char) -> 234 (Next) or 233 (Accept 18 chars)
    def i232(self):
        if self.check_id():
            self.advance()
            return self.i234()
        return self.i233()

    def i233(self): return self.finalize_id()

    # =========================================================================
    # STATE 234: The Boundary Check (19th -> 20th Character)
    # =========================================================================
    def i234(self):
        if self.check_id():
            self.advance()
            if self.check_id():

                # OPTIONAL: IF we wanna consume the rest of the invalid word
                # so the lexer doesn't try to tokenize the tail as a new ID.
                # while self._is_valid_id_char():
                #     self.advance()
                return self.error()
            return self.i235()

        return self.i235()

    # State 235 (Final Accept State)
    def i235(self):
        return self.finalize_id()

    # =========================================================================
    # ACCEPTANCE LOGIC & DELIMITER CHECK
    # =========================================================================
    def finalize_id(self):
        result = self.current_token_text()
        line, col = self.line, self.col

        # Delimiter Validation
        if self._comp_delims(Delimiters._get_delimiters()["ID_DELIM"]):

            if result not in self.identifier_table:
                self.identifier_table[result] = f"id{len(self.identifier_table) + 1}"

            token_type = self.identifier_table[result]
            return Token(token_type, result, line, col - 1)

        else:
            return self.error()
