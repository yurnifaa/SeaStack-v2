import string
from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters
from backend.error_msg import ErrorHandler 

# =================================================================================================
# INDENTIFIER TD: Identifiers state machine (rw0 - rw119)
# This class recognizes and tokenizes sequences of lowercase letters/digits/underscores.
# It determines whether these are Reserved Words or User-Defined Identifiers.
# =================================================================================================

class IdentifierHandler: 

    # --- HELPER: DYNAMIC & CLEAN ERROR GENERATION ---
    def _report_id_error(self, delim_key="ID_DELIM", manual_extras=None, error_type=None, custom_msg=None, diff_char=None):
        """
        Generates a standardized error dictionary for identifiers.
        """
        if manual_extras is None:
            manual_extras = []
            
        # 1. Fetch the Set from Delimiters
        allowed_set = set(Delimiters._get_delimiters().get(delim_key, []))
        allowed_set.update(manual_extras)
        
        # 2. CLEANING LOGIC (Condenses 0-9, a-z, whitespace)
        cleaned_list = []

        # Condense Ranges
        if set(string.ascii_lowercase).issubset(allowed_set):
            cleaned_list.append("a-z")
            allowed_set -= set(string.ascii_lowercase)
        
        if set(string.ascii_uppercase).issubset(allowed_set):
            cleaned_list.append("A-Z")
            allowed_set -= set(string.ascii_uppercase)
            
        if set(string.digits).issubset(allowed_set):
            cleaned_list.append("0-9")
            allowed_set -= set(string.digits)

        # Condense Whitespace
        whitespace_subset = allowed_set.intersection(set(string.whitespace))
        if whitespace_subset:
            cleaned_list.append("whitespace")
            allowed_set -= whitespace_subset

        # Format Remaining
        for char in sorted(list(allowed_set)):
            if char == "\n": cleaned_list.append("\\n")
            elif char == "\t": cleaned_list.append("\\t")
            elif char == " ": cleaned_list.append("' '")
            else: cleaned_list.append(char)
        
        # 3. Determine Error Type
        if error_type is None:
            error_type = ErrorHandler.ERR_LEX_INVALID_DELIM

        # 4. Determine text to show (default to current lexeme)
        text_to_show = diff_char if diff_char else self.current_token_text()

        # 5. Generate Error
        return ErrorHandler.get_lexical_error(
            line=self.line,
            col=self.col - 1,
            invalid_char=text_to_show,
            expected_list=sorted(cleaned_list),
            header_type=error_type,
            custom_msg=custom_msg
        )

    def _is_alphanumeric_or_underscore(self):
        # Checks if the current character is valid for an identifier body
        char = self.current_char
        return char is not None and (char.islower() or char.isdigit() or char == "_")

    # =========================================================================
    # IDENTIFIER TD: ASCII Character up to 20 Char
    # =========================================================================
    def _make_identifier(self):                                 # Lexer.py has already consumed the first letter.
        if self.current_char is None:                           # We start checking the *next* character immediately.
            return self.i194()                                  # End of file, finalize immediately
        
        return self.i193()

    # State i193 (Character 1 / New Start) 
    def i193(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i195()
        return self.i194()

    def i194(self):
        return self.finalize_id("id")

    # State i195 (Character 2) 
    def i195(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i197()
        return self.i196()

    def i196(self):
        return self.finalize_id("id")

    # State i197 (Character 3) 
    def i197(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i199()
        return self.i198()

    def i198(self):
        return self.finalize_id("id")
    
    # State i199 (Character 4)
    def i199(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i201()
        return self.i200()

    def i200(self):
        return self.finalize_id("id")

    # State i201 (Character 5) 
    def i201(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i203()
        return self.i202()

    def i202(self):
        return self.finalize_id("id")

    # State i203 (Character 6)
    def i203(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i205()
        return self.i204()

    def i204(self):
        return self.finalize_id("id")

    # State i205 (Character 7) 
    def i205(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i207()
        return self.i206()

    def i206(self):
        return self.finalize_id("id")

    # State i207 (Character 8) 
    def i207(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i209()
        return self.i208()

    def i208(self):
        return self.finalize_id("id")

    # State i209 (Character 9)
    def i209(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i211()
        return self.i210()

    def i210(self):
        return self.finalize_id("id")

    # State i211 (Character 10)
    def i211(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i213()
        return self.i212()

    def i212(self):
        return self.finalize_id("id")

    # State i213 (Character 11) 
    def i213(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i215()
        return self.i214()

    def i214(self):
        return self.finalize_id("id")

    # State i215 (Character 12)
    def i215(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i217()
        return self.i216()

    def i216(self):
        return self.finalize_id("id")

    # State i217 (Character 13)
    def i217(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i219()
        return self.i218()

    def i218(self):
        return self.finalize_id("id")
    
    # State i219 (Character 14)
    def i219(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i221()
        return self.i220()

    def i220(self):
        return self.finalize_id("id")

    # State i221 (Character 15)
    def i221(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i223()
        return self.i222()

    def i222(self):
        return self.finalize_id("id")

    # State i223 (Character 16)
    def i223(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i225()
        return self.i224()

    def i224(self):
        return self.finalize_id("id")

    # State i225 (Character 17)
    def i225(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i227()
        return self.i226()

    def i226(self):
        return self.finalize_id("id")

    # State i227 (Character 18)
    def i227(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i229()
        return self.i228()

    def i228(self):
        return self.finalize_id("id")
        
    # State i229 (Character 19) 
    def i229(self):
        if self._is_alphanumeric_or_underscore():
            self.advance()
            return self.i231()
        return self.i230()

    def i230(self):
        return self.finalize_id("id")

    # State i231 (Character 20 - Max Length) 
    def i231(self):
        # Check for the 21st character (Overflow Check)
        if self._is_alphanumeric_or_underscore():
            # --- STOP IMMEDIATELY ---
            # We report the error for the current 20 characters + ... to show overflow
            full_text = self.text[self.token_start_pos:self.pos] + "..."
            
            # Use the new ErrorHandler with Limit Exceeded type
            limit_error = self._report_id_error(
                delim_key="ID_DELIM",
                error_type=ErrorHandler.ERR_LEX_LIMIT_EXCEEDED,
                custom_msg="Identifier exceeds 20 characters",
                diff_char=full_text
            )
            self.errors.append(limit_error)
            
            # Note: We return None so the Lexer loop continues from the current position,
            # treating the overflow characters as potentially new tokens or further errors.
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

        # DELIMITER CHECK FIRST -> only cares about assigning an ID if the token is actually valid.
        if self._is_valid_delimiter("ID_DELIM"):
            
            # Check for Reserved Word logic (if handled here or via table)
            if result not in self.identifier_table:
                self.identifier_table[result] = f"id{len(self.identifier_table) + 1}"

            token_type = self.identifier_table[result]
            
            return Token(token_type, result, line, col - 1) 
            
        else:
            # ERROR CASE: Invalid Delimiter
            # We use the new helper to show exactly what delimiters were allowed (whitespace, operators, etc.)
            
            error_dict = self._report_id_error(
                delim_key="ID_DELIM",
                error_type=ErrorHandler.ERR_LEX_INVALID_DELIM,
                diff_char=self.current_char if self.current_char else "EOF"
            )
            self.errors.append(error_dict)
            
            return None