# lexer_handlers/identifier_handler.py
from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters

# =================================================================================================
# IDENTIFIER TD: Identifiers state machine (i197 - i236)
# =================================================================================================

class IdentifierHandler: 
    
    # --- HELPER: Check for Alphanumeric or Underscore ---
    def _is_alphanumeric_or_underscore(self):
        char = self.current_char
        return char is not None and (char.isalnum() or char == "_")

    # --- HELPER: Create Error with Expected List ---
    def _create_id_error(self, message):
        # Retrieve the valid delimiters for ID to show in the expected list
        # Converting set to list for display purposes
        valid_delims = list(Delimiters._get_delimiters()["ID_DELIM"])
        # Optional: Sort them for cleaner UI output
        valid_delims.sort() 
        
        err_token = Token(
            "ERROR",
            self.current_token_text(),
            self.line,
            self.col - 1,
            message
        )
        err_token.expected = valid_delims
        return err_token

    # =========================================================================
    # START: ENTRY POINT (Matches diagram start)
    # =========================================================================
    def _make_identifier(self):                                 
        # The lexer likely detected a lowercase letter to get here.
        # We start verifying the *next* character or delimiter (State 197).
        return self.i197()

    # State 197 (Char 1 processed) -> Expects Char 2 or Delimiter
    def i197(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i199()
        return self.i198()

    def i198(self): return self.finalize_id()

    # State 199 (Char 2 processed) -> Expects Char 3 or Delimiter
    def i199(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i201()
        return self.i200()

    def i200(self): return self.finalize_id()

    # State 201 (Char 3 processed) -> Expects Char 4 or Delimiter
    def i201(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i203()
        return self.i202()

    def i202(self): return self.finalize_id()
    
    # State 203 (Char 4 processed) -> Expects Char 5 or Delimiter
    def i203(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i205()
        return self.i204()

    def i204(self): return self.finalize_id()

    # State 205 (Char 5 processed) -> Expects Char 6 or Delimiter
    def i205(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i207()
        return self.i206()

    def i206(self): return self.finalize_id()

    # State 207 (Char 6 processed) -> Expects Char 7 or Delimiter
    def i207(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i209()
        return self.i208()

    def i208(self): return self.finalize_id()

    # State 209 (Char 7 processed) -> Expects Char 8 or Delimiter
    def i209(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i211()
        return self.i210()

    def i210(self): return self.finalize_id()

    # State 211 (Char 8 processed) -> Expects Char 9 or Delimiter
    def i211(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i213()
        return self.i212()

    def i212(self): return self.finalize_id()

    # State 213 (Char 9 processed) -> Expects Char 10 or Delimiter
    def i213(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i215()
        return self.i214()

    def i214(self): return self.finalize_id()

    # State 215 (Char 10 processed) -> Expects Char 11 or Delimiter
    def i215(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i217()
        return self.i216()

    def i216(self): return self.finalize_id()

    # State 217 (Char 11 processed) -> Expects Char 12 or Delimiter
    def i217(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i219()
        return self.i218()

    def i218(self): return self.finalize_id()
    
    # State 219 (Char 12 processed) -> Expects Char 13 or Delimiter
    def i219(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i221()
        return self.i220()

    def i220(self): return self.finalize_id()

    # State 221 (Char 13 processed) -> Expects Char 14 or Delimiter
    def i221(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i223()
        return self.i222()

    def i222(self): return self.finalize_id()

    # State 223 (Char 14 processed) -> Expects Char 15 or Delimiter
    def i223(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i225()
        return self.i224()

    def i224(self): return self.finalize_id()

    # State 225 (Char 15 processed) -> Expects Char 16 or Delimiter
    def i225(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i227()
        return self.i226()

    def i226(self): return self.finalize_id()

    # State 227 (Char 16 processed) -> Expects Char 17 or Delimiter
    def i227(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i229()
        return self.i228()

    def i228(self): return self.finalize_id()
        
    # State 229 (Char 17 processed) -> Expects Char 18 or Delimiter
    def i229(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i231()
        return self.i230()

    def i230(self): return self.finalize_id()

    # State 231 (Char 18 processed) -> Expects Char 19 or Delimiter
    def i231(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i233()
        return self.i232()

    def i232(self): return self.finalize_id()

    # State 233 (Char 19 processed) -> Expects Char 20 or Delimiter
    def i233(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i235()
        return self.i234()
    
    def i234(self): return self.finalize_id()

    # State 235 (Char 20 processed - MAX LENGTH) -> Expects Delimiter ONLY
    def i235(self):
        # If there is ANOTHER alphanumeric character/underscore, we have exceeded the limit (20)
        if self._is_alphanumeric_or_underscore():
            msg = "Invalid Identifier. Limit (20) exceeded. Expected delimiter."
            self.errors.append(self._create_id_error(msg))
            return None 
        
        # Otherwise, check for delimiter at State 236
        return self.i236()

    def i236(self): return self.finalize_id()

    # =========================================================================================
    # ACCEPTANCE LOGIC & DELIMITER CHECK
    # =========================================================================================
    def finalize_id(self):
        result = self.current_token_text()
        line, col = self.line, self.col

        # CHECK 1: Is it a valid delimiter based on ID_DELIM in delimiters.py?
        if self._comp_delims(Delimiters._get_delimiters()["ID_DELIM"]):
            
            # Lookup/assign an ID number if it's new
            if result not in self.identifier_table:
                self.identifier_table[result] = f"id{len(self.identifier_table) + 1}"

            token_type = self.identifier_table[result]
            return Token(token_type, result, line, col - 1) 
            
        else:
            # CHECK 2: Invalid Delimiter Error
            self.errors.append(self._create_id_error("Invalid Identifier. Expected delimiter."))
            return None