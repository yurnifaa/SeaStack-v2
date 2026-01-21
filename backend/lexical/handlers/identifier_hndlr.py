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
        # Retrieve ID_DELIM
        raw_delims = Delimiters._get_delimiters()["ID_DELIM"]
        
        # CLEAN THE DELIMITERS: Replace invisible chars with "whitespace"
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
    # START: ENTRY POINT (Matches diagram start)
    # =========================================================================
    def _make_identifier(self):                                 
        return self.i197()

    # State 197 -> 198 (Accept) or 199
    def i197(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i199()
        return self.i198()

    def i198(self): return self.finalize_id()

    # State 199 -> 200 (Accept) or 201
    def i199(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i201()
        return self.i200()

    def i200(self): return self.finalize_id()

    # State 201 -> 202 (Accept) or 203
    def i201(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i203()
        return self.i202()

    def i202(self): return self.finalize_id()
    
    # State 203 -> 204 (Accept) or 205
    def i203(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i205()
        return self.i204()

    def i204(self): return self.finalize_id()

    # State 205 -> 206 (Accept) or 207
    def i205(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i207()
        return self.i206()

    def i206(self): return self.finalize_id()

    # State 207 -> 208 (Accept) or 209
    def i207(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i209()
        return self.i208()

    def i208(self): return self.finalize_id()

    # State 209 -> 210 (Accept) or 211
    def i209(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i211()
        return self.i210()

    def i210(self): return self.finalize_id()

    # State 211 -> 212 (Accept) or 213
    def i211(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i213()
        return self.i212()

    def i212(self): return self.finalize_id()

    # State 213 -> 214 (Accept) or 215
    def i213(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i215()
        return self.i214()

    def i214(self): return self.finalize_id()

    # State 215 -> 216 (Accept) or 217
    def i215(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i217()
        return self.i216()

    def i216(self): return self.finalize_id()

    # State 217 -> 218 (Accept) or 219
    def i217(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i219()
        return self.i218()

    def i218(self): return self.finalize_id()
    
    # State 219 -> 220 (Accept) or 221
    def i219(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i221()
        return self.i220()

    def i220(self): return self.finalize_id()

    # State 221 -> 222 (Accept) or 223
    def i221(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i223()
        return self.i222()

    def i222(self): return self.finalize_id()

    # State 223 -> 224 (Accept) or 225
    def i223(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i225()
        return self.i224()

    def i224(self): return self.finalize_id()

    # State 225 -> 226 (Accept) or 227
    def i225(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i227()
        return self.i226()

    def i226(self): return self.finalize_id()

    # State 227 -> 228 (Accept) or 229
    def i227(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i229()
        return self.i228()

    def i228(self): return self.finalize_id()
        
    # State 229 -> 230 (Accept) or 231
    def i229(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i231()
        return self.i230()

    def i230(self): return self.finalize_id()

    # State 231 -> 232 (Accept) or 233
    def i231(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i233()
        return self.i232()

    def i232(self): return self.finalize_id()

    # State 233 -> 234 (Accept) or 235
    def i233(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i235()
        return self.i234()
    
    def i234(self): return self.finalize_id()

    # State 235 (Char 20 - Max Length) -> 236 (Accept) or Error
    def i235(self):
        # If there is ANOTHER alphanumeric character/underscore, we have exceeded the limit (20)
        if self._is_alphanumeric_or_underscore():
            msg = "Invalid Identifier. Limit (20) exceeded. Expected delimiter."
            self.errors.append(self._create_id_error(msg))
            return None 
        
        return self.i236()

    def i236(self): return self.finalize_id()

    # =========================================================================================
    # ACCEPTANCE LOGIC & DELIMITER CHECK
    # =========================================================================================
    def finalize_id(self):
        result = self.current_token_text()
        line, col = self.line, self.col

        # CHECK 1: Is it a valid delimiter?
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