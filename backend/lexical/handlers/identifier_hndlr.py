from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters

# =================================================================================================
# INDENTIFIER TD: Identifiers state machine (rw0 - rw119)
# =================================================================================================

class IdentifierHandler: 
    
    DELIM_LIST = [
        "whitespace", 
        "+", "-", "*", "/", "%", "^", 
        "<", ">", "=", "!", "&", "|", 
        "(", ")", "{", "}", "]", "$", ","
    ]

    def _is_alphanumeric_or_underscore(self):
        # Checks if the current character is valid for an identifier body
        char = self.current_char
        return char is not None and (char.islower() or char.isdigit() or char == "_")

    # =========================================================================
    # IDENTIFIER TD: ASCII Character up to 20 Char
    # =========================================================================
    def _make_identifier(self):                                 
        if self.current_char is None:                           
            return self.i194()                                  
        return self.i193()

    # State i193 (Character 1 / New Start) 
    def i193(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i195()
        return self.i194()

    def i194(self): return self.finalize_id("id")

    # State i195 (Character 2) 
    def i195(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i197()
        return self.i196()

    def i196(self): return self.finalize_id("id")

    # State i197 (Character 3) 
    def i197(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i199()
        return self.i198()

    def i198(self): return self.finalize_id("id")
    
    # State i199 (Character 4)
    def i199(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i201()
        return self.i200()

    def i200(self): return self.finalize_id("id")

    # State i201 (Character 5) 
    def i201(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i203()
        return self.i202()

    def i202(self): return self.finalize_id("id")

    # State i203 (Character 6)
    def i203(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i205()
        return self.i204()

    def i204(self): return self.finalize_id("id")

    # State i205 (Character 7) 
    def i205(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i207()
        return self.i206()

    def i206(self): return self.finalize_id("id")

    # State i207 (Character 8) 
    def i207(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i209()
        return self.i208()

    def i208(self): return self.finalize_id("id")

    # State i209 (Character 9)
    def i209(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i211()
        return self.i210()

    def i210(self): return self.finalize_id("id")

    # State i211 (Character 10)
    def i211(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i213()
        return self.i212()

    def i212(self): return self.finalize_id("id")

    # State i213 (Character 11) 
    def i213(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i215()
        return self.i214()

    def i214(self): return self.finalize_id("id")

    # State i215 (Character 12)
    def i215(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i217()
        return self.i216()

    def i216(self): return self.finalize_id("id")

    # State i217 (Character 13)
    def i217(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i219()
        return self.i218()

    def i218(self): return self.finalize_id("id")
    
    # State i219 (Character 14)
    def i219(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i221()
        return self.i220()

    def i220(self): return self.finalize_id("id")

    # State i221 (Character 15)
    def i221(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i223()
        return self.i222()

    def i222(self): return self.finalize_id("id")

    # State i223 (Character 16)
    def i223(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i225()
        return self.i224()

    def i224(self): return self.finalize_id("id")

    # State i225 (Character 17)
    def i225(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i227()
        return self.i226()

    def i226(self): return self.finalize_id("id")

    # State i227 (Character 18)
    def i227(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i229()
        return self.i228()

    def i228(self): return self.finalize_id("id")
        
    # State i229 (Character 19) 
    def i229(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i231()
        return self.i230()

    def i230(self): return self.finalize_id("id")

    # State i231 (Character 20 - Max Length) 
    def i231(self):
        # Check for the 21st character (Overflow Check)
        if self._is_alphanumeric_or_underscore():
            # --- OVERFLOW ERROR ---
            error_token = Token(
                    "ERROR",
                    self.current_token_text(), 
                    self.line,
                    self.col - 1,
                    "Invalid Identifier. Limit (20) exceeded. Expected delimiter.",
                )
            # ATTACH EXPECTED LIST
            error_token.expected = self.DELIM_LIST
            
            self.errors.append(error_token)
            return None 
        
        # Valid identifier of exact length 20
        return self.i232()

    def i232(self):
        return self.finalize_id("id")

    # =========================================================================================
    # ACCEPTANCE LOGIC & DELIMITER CHECK
    # =========================================================================================
    def finalize_id(self, lexeme_type):
        result = self.current_token_text()
        line, col = self.line, self.col

        # DELIMITER CHECK FIRST
        if self._is_valid_delimiter("ID_DELIM"):
            
            # Lookup/assign an ID number
            if result not in self.identifier_table:
                self.identifier_table[result] = f"id{len(self.identifier_table) + 1}"

            token_type = self.identifier_table[result]
            return Token(token_type, result, line, col - 1) 
            
        else:
            # --- INVALID DELIMITER ERROR ---
            error_msg = "Invalid Identifier. Expected delimiter."
            
            err_token = Token(
                "ERROR",
                result,
                line,
                col - 1,
                error_msg
            )
            
            # ATTACH EXPECTED LIST
            err_token.expected = self.DELIM_LIST
            
            self.errors.append(err_token)
            
            return None