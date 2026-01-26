# lexer_handlers/identifier_handler.py
from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters

# =================================================================================================
# IDENTIFIER TD: Identifiers state machine (States 195 - 234)
# Rule: Must start with lowercase. Followed by lowercase, digit, or underscore. Max 20 chars.
# =================================================================================================

class IdentifierHandler: 
    
    # --- HELPER: STRICT Validation (Lowercase, Digit, Underscore) ---
    def _is_valid_id_char(self):
        char = self.current_char
        # RULE: Lowercase, Digit, or Underscore ONLY. No Uppercase.
        return char is not None and (char.islower() or char.isdigit() or char == "_")

    # --- HELPER: Sanitize Delimiters for Display ---
    def _sanitize_delims(self, delim_set):
        # Convert set to list
        delims = list(delim_set) if isinstance(delim_set, set) else delim_set
        cleaned_list = []
        has_whitespace = False
        
        # Filter loop
        for d in delims:
            if d in [' ', '\t', '\n', '\r', '\v', '\f']:
                has_whitespace = True
            else:
                cleaned_list.append(d)
        
        # Add the label if any whitespace was found
        if has_whitespace:
            cleaned_list.append("whitespace")
            
        # Sort for consistency
        cleaned_list.sort(key=str)
        return cleaned_list

    # --- HELPER: Create Error with Expected List ---
    def _create_id_error(self, message):
        raw_delims = Delimiters._get_delimiters()["ID_DELIM"]    
        valid_delims = self._sanitize_delims(raw_delims)
        
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
    # START: ENTRY POINT (State 195)
    # The Lexer has already consumed the 1st char (lowercase).
    # We now check the 2nd character.
    # =========================================================================
    def id195(self):                                 
        return self.i197()

    # State 197 (Check 2nd char) -> 199 (Next) or 198 (Accept 1 char)
    def i197(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i199()
        return self.i198()

    def i198(self): return self.finalize_id()

    # State 199 (Check 3rd char) -> 201 (Next) or 200 (Accept 2 chars)
    def i199(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i201()
        return self.i200()

    def i200(self): return self.finalize_id()

    # State 201 (Check 4th char) -> 203 (Next) or 202 (Accept 3 chars)
    def i201(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i203()
        return self.i202()

    def i202(self): return self.finalize_id()
    
    # State 203 (Check 5th char) -> 205 (Next) or 204 (Accept 4 chars)
    def i203(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i205()
        return self.i204()

    def i204(self): return self.finalize_id()

    # State 205 (Check 6th char) -> 207 (Next) or 206 (Accept 5 chars)
    def i205(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i207()
        return self.i206()

    def i206(self): return self.finalize_id()

    # State 207 (Check 7th char) -> 209 (Next) or 208 (Accept 6 chars)
    def i207(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i209()
        return self.i208()

    def i208(self): return self.finalize_id()

    # State 209 (Check 8th char) -> 211 (Next) or 210 (Accept 7 chars)
    def i209(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i211()
        return self.i210()

    def i210(self): return self.finalize_id()

    # State 211 (Check 9th char) -> 213 (Next) or 212 (Accept 8 chars)
    def i211(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i213()
        return self.i212()

    def i212(self): return self.finalize_id()

    # State 213 (Check 10th char) -> 215 (Next) or 214 (Accept 9 chars)
    def i213(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i215()
        return self.i214()

    def i214(self): return self.finalize_id()

    # State 215 (Check 11th char) -> 217 (Next) or 216 (Accept 10 chars)
    def i215(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i217()
        return self.i216()

    def i216(self): return self.finalize_id()

    # State 217 (Check 12th char) -> 219 (Next) or 218 (Accept 11 chars)
    def i217(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i219()
        return self.i218()

    def i218(self): return self.finalize_id()
    
    # State 219 (Check 13th char) -> 221 (Next) or 220 (Accept 12 chars)
    def i219(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i221()
        return self.i220()

    def i220(self): return self.finalize_id()

    # State 221 (Check 14th char) -> 223 (Next) or 222 (Accept 13 chars)
    def i221(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i223()
        return self.i222()

    def i222(self): return self.finalize_id()

    # State 223 (Check 15th char) -> 225 (Next) or 224 (Accept 14 chars)
    def i223(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i225()
        return self.i224()

    def i224(self): return self.finalize_id()

    # State 225 (Check 16th char) -> 227 (Next) or 226 (Accept 15 chars)
    def i225(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i227()
        return self.i226()

    def i226(self): return self.finalize_id()

    # State 227 (Check 17th char) -> 229 (Next) or 228 (Accept 16 chars)
    def i227(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i229()
        return self.i228()

    def i228(self): return self.finalize_id()
        
    # State 229 (Check 18th char) -> 231 (Next) or 230 (Accept 17 chars)
    def i229(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i231()
        return self.i230()

    def i230(self): return self.finalize_id()

    # State 231 (Check 19th char) -> 233 (Next) or 232 (Accept 18 chars)
    def i231(self):
        if self._is_valid_id_char():
            self.advance()
            return self.i233()
        return self.i232()

    def i232(self): return self.finalize_id()

    # =========================================================================
    # STATE 233: The Boundary Check (19th -> 20th Character)
    # =========================================================================
    def i233(self):
        if self._is_valid_id_char():
            self.advance()
            if self._is_valid_id_char():
                
                # OPTIONAL: You might want to consume the rest of the invalid word 
                # so the lexer doesn't try to tokenize the tail as a new ID.
                # while self._is_valid_id_char():
                #     self.advance()
                msg = "Invalid Identifier. Exceeds 20 characters."
                self.errors.append(self._create_id_error(msg))
                return None 
            return self.i234()
            
        return self.i234() 
    
    # State 234 (Final Accept State)
    def i234(self): 
        return self.finalize_id()

    # =========================================================================
    # ACCEPTANCE LOGIC & DELIMITER CHECK
    # =========================================================================
    def finalize_id(self):
        result = self.current_token_text()
        line, col = self.line, self.col

        # CHECK 1: Delimiter Validation
        # Per Regular Definition, id_delim includes:
        # whitespace, gen_op, (, ), }, {, }, $, ,
        if self._comp_delims(Delimiters._get_delimiters()["ID_DELIM"]):
            
            # Lookup/assign an ID number if it's new
            # Note: SeaStack reserved words must not be used as identifiers [cite: 2390]
            # Ensure your Lexer checks reserved words BEFORE entering this handler
            # or checks against a reserved word list here.
            
            if result not in self.identifier_table:
                self.identifier_table[result] = f"id{len(self.identifier_table) + 1}"

            token_type = self.identifier_table[result]
            return Token(token_type, result, line, col - 1) 
            
        else:
            # CHECK 2: Invalid Delimiter Error
            # This handles cases where the identifier ends with an illegal character 
            # (e.g., '@' or '#') that is not a valid delimiter.
            self.errors.append(self._create_id_error(f"Invalid Identifier. Unexpected character '{self.current_char}'."))
            return None