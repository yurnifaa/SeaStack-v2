from lexer_token import Token
from handlers.delimiters import Delimiters

# =================================================================================================
# INDENTIFIER TD: Identifiers state machine (rw0 - rw119)
# This class recognizes and tokenizes lprocess sequences of uppercase letters that start in state0
# It determines whether these sequences are pre-defined Reserved Words (Keywords) in the language or 
# if they are Identifiers (variable names, function names, etc.) that the user has defined.
# =================================================================================================

# --- Inherited Methods ---
# _make_keyword: uses a single entry point and relies on helper methods and a lookup table to resolve the token type.
# Lookup Table: dictionary of all valid, uppercase keywords. The handler's job is to match the consumed text against this table.
# Token Classification: IF lexeme matches a reserved word in the list, it returns the corresponding Reserved Word Token. 
#                       ELSE, classifies the lexeme as an Identifier.

# --- Program Flow & its helper method ---
# 1. _make_keyword() (Scanning the Lexeme) Starts after the Lexer encounters the first uppercase letter (e.g., the 'I' in IF).
#   - Initialization: Captures the starting position of the token using self.mark_token_start().
#   - Loop: Enters while loop that runs as long as the current character (self.current_char) is an uppercase letter.
#           Inside the loop, self.advance() is called repeatedly to consume all subsequent uppercase letters, 
#           building up the potential keyword lexeme (e.g., consuming 'I' then 'F').
#   - Lexeme Extraction: Once the loop terminates (bcus next char not uplet), 
#           lexeme = self.current_token_text() is called to retrieve the full string (e.g., "IF").
#   - Classification: The handler then calls self._is_reserved_word(lexeme) to check the nature of the scanned text.
# 2. "LOOK UP TABLE" _is_reserved_word(lexeme)
#   - Performs the critical distinction between reserved words and identifiers.
#   - Check Table: It checks if the lexeme (e.g., "IF") is present in the internal set or dictionary of reserved words (self.reserved_words).
#       - Case A: Reserved Word Match: If found (e.g., "IF" is a reserved word):
#                 Returns the classification type for that word (e.g., "IF_KW" or just "IF").
#       - Case B: No Match: If not found (e.g., "MYVAR" is not in the reserved word list):
#                 Returns the generic classification type for user-defined names (e.g., "IDENTIFIER").

class IdentifierHandler: 

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
            # Do NOT advance. Do NOT consume the 21st character.
            # We report the error for the current 20 characters, 
            # allowing the lexer to pick up the 21st char as a new token next time.
            
            error_token = Token(
                    "ERROR",
                    self.current_token_text(), # This holds exactly 20 chars
                    self.line,
                    self.col - 1,
                    "Invalid Identifier. Expected delimiter (whitespace, gen_op, (, ), ], {, }, $, })",
                )
            self.errors.append(error_token)
            return None 
        
        # Valid identifier of exact length 20
        return self.i232()

    def i232(self):
        return self.finalize_id("id")

    # =========================================================================================
    # ACCEPTANCE LOGIC & DELIMITER CHECK: checks if Identifier ends correctly. 
    #                                     If valid, ONLY THEN check/create the ID number.
    # =========================================================================================
    def finalize_id(self, lexeme_type):
        result = self.current_token_text()
        line, col = self.line, self.col

        # DELIMITER CHECK FIRST -> only cares about assigning an ID if the token is actually valid.
        if self._is_valid_delimiter("ID_DELIM"):
            
            # NOW it will Look up/assign an ID number
            # Since we know it's valid, we can safely add it to our table or look it up.
            if result not in self.identifier_table:
                self.identifier_table[result] = f"id{len(self.identifier_table) + 1}"

            token_type = self.identifier_table[result]
            
            return Token(token_type, result, line, col - 1) # Added - 1
            
        else:
            # ERROR CASE -> does NOT touch self.identifier_table here. 
            # The counter will not increment for this invalid token.
            
            # --- FIX: Removed the trailing comma below ---
            error_msg = "Invalid Identifier. Expected delimiter (whitespace, gen_op, (, ), ], {, }, $, })"
            
            err_token = Token(
                "ERROR",
                result,
                line,
                col - 1,
                error_msg
            )
            self.errors.append(err_token)
            
            return None