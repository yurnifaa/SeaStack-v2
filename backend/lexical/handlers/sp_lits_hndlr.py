import string
from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters
from backend.error_msg import ErrorHandler 

# =========================================================================================
# SCROLL and PARCH TD: Scroll and Parch state machine (rs120 - rs192)
# This class recognizes and tokenizes literal values, specifically PARCH-lit & SCROLL-lit
# ========================================================================================= 

class LiteralHandler:

    # --- HELPER: DYNAMIC & CLEAN ERROR GENERATION ---
    def _report_lit_error(self, allowed_set=None, error_type=None, custom_msg=None, diff_char=None):
        """
        Generates a standardized error dictionary for literals.
        """
        if allowed_set is None:
            allowed_set = set()
        else:
            # Ensure it's a set copy to avoid modifying the original
            allowed_set = set(allowed_set)

        # 1. CLEANING LOGIC (Condenses 0-9, a-z, whitespace)
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
        
        # 2. Determine Error Type
        if error_type is None:
            error_type = ErrorHandler.ERR_LEX_INVALID_CHAR

        # 3. Determine text to show
        text_to_show = diff_char if diff_char else self.current_token_text()

        # 4. Generate Error
        return ErrorHandler.get_lexical_error(
            line=self.line,
            col=self.col - 1,
            invalid_char=text_to_show,
            expected_list=sorted(cleaned_list),
            header_type=error_type,
            custom_msg=custom_msg
        )

    # --- Utility Functions ---
    def _get_parch_end_delims(self):
        return Delimiters._get_delimiters()["PARCH_DELIM"]

    def _get_scroll_body_allowed(self):
        return Delimiters._get_delimiters()["ASCII"] - set("\"\\\n\r")

    def _get_scroll_delims(self):
        return Delimiters._get_delimiters()["SCR_DELIM"]

    # =========================================================================
    # PARCH LITERAL (Single Character)
    # =========================================================================
    def p283(self):
        if self.current_char == "'":
            self.advance()
            return self.p284()

    def p284(self):
        # 1. Check Empty ('')
        if self.current_char == "'":
            # Error: Malformed (Empty)
            self.errors.append(self._report_lit_error(
                allowed_set=set(), # No specific chars expected, just 'anything'
                error_type=ErrorHandler.ERR_LEX_MALFORMED_LIT,
                custom_msg="Invalid PARCH Literal. Expected: character inside quotes"
            ))
            return []
        
        # 2. Check Invalid Newline
        if self.current_char == '\n':
            self.errors.append(self._report_lit_error(
                allowed_set=set(),
                error_type=ErrorHandler.ERR_LEX_MALFORMED_LIT,
                custom_msg="Invalid PARCH Literal. Newline not allowed."
            ))
            return []

        # 3. Consume the valid character
        if self.current_char is not None:
            self.advance() 
            return self.p285()

        # 4. Unexpected EOF
        self.errors.append(self._report_lit_error(
            allowed_set=["'"],
            error_type=ErrorHandler.ERR_LEX_UNCLOSED_LIT,
            custom_msg="Unclosed PARCH Literal. Expected closing quote."
        ))
        return []

    def p285(self):
        # 1. Check Closing Quote
        if self.current_char == "'":
            
            # --- PEEK LOGIC (Delimiter Check) ---
            next_pos = self.pos + 1
            if next_pos < len(self.text):
                peek_char = self.text[next_pos]
            else:
                peek_char = None 
            
            valid_delims = self._get_parch_end_delims()

            # 2. Check Neighbor
            if peek_char is None or peek_char in valid_delims:
                self.advance() 
                return self.p286()
            
            else:
                # ERROR: Invalid Delimiter
                # We consume the quote to finish the literal, then report the error on the NEXT char
                self.advance() 
                
                # Report error on the PEEK char (which is now current char after advance)
                # But wait, logic says "invalid character 'Hello!'" in your example. 
                # If we want to flag the whole literal + char as invalid:
                full_text = self.current_token_text() + (peek_char if peek_char else "")
                
                self.errors.append(self._report_lit_error(
                    allowed_set=valid_delims,
                    error_type=ErrorHandler.ERR_LEX_INVALID_DELIM,
                    diff_char=peek_char # Show the invalid delimiter
                ))
                return []

        # 3. Malformed Literal Case (e.g. 'ab')
        else:    
            self.errors.append(self._report_lit_error(
                allowed_set=["'"],
                error_type=ErrorHandler.ERR_LEX_MALFORMED_LIT,
                custom_msg="Invalid PARCH Literal. Expected closing quote."
            ))
            return []
    
    def p286(self):
        return [Token("PARCH-lit", self.current_token_text(), self.line, self.col - 1)]

    # =========================================================================
    # SCROLL LITERAL (Double Quoted String)
    # =========================================================================

    # ENTRY POINT: Consumes opening quote
    def s287(self):
        if self.current_char == '"':
            self.advance() 
            
            # Check IF Empty SCROLL ("")
            if self.current_char == '"':              
                # In some languages "" is valid, but here it seems strict "non-empty" based on your prev code
                self.errors.append(self._report_lit_error(
                    allowed_set=set(),
                    error_type=ErrorHandler.ERR_LEX_MALFORMED_LIT,
                    custom_msg="Invalid SCROLL Literal. Expected string content."
                ))       
                return []
            
            elif self.current_char is None:
                 self.errors.append(self._report_lit_error(
                    allowed_set=['"'],
                    error_type=ErrorHandler.ERR_LEX_UNCLOSED_LIT
                ))
                 return []

            return self.s288(current_text='"', start_line=self.line, start_col=self.col-1)
    
    # SCROLL BODY
    def s288(self, current_text, start_line, start_col):
        while self.current_char is not None:
            # 1. Closing Quote
            if self.current_char == '"':
                self.advance()
                return self.s289(current_text + '"', start_line, start_col)
            
            # 2. Invalid Newline
            if self.current_char == '\n':
                self.errors.append(self._report_lit_error(
                    allowed_set=['"'],
                    error_type=ErrorHandler.ERR_LEX_UNCLOSED_LIT,
                    custom_msg="Unclosed SCROLL Literal. Newline reached before closing quote."
                ))
                return []

            # 3. Valid Body Character
            if self._comp_delims(self._get_scroll_body_allowed()):
                current_text += self.current_char
                self.advance()
                continue
            
            # 4. Backslash (Escape Start)
            if self.current_char == '\\':
                # Move to escape handler
                return self.s291(current_text, start_line, start_col)
            
            # 5. Invalid Character (Non-ASCII etc)
            self.errors.append(self._report_lit_error(
                allowed_set=self._get_scroll_body_allowed(),
                error_type=ErrorHandler.ERR_LEX_INVALID_CHAR
            ))
            self.advance()
            return []

        # EOF
        self.errors.append(self._report_lit_error(
            allowed_set=['"'],
            error_type=ErrorHandler.ERR_LEX_UNCLOSED_LIT
        ))
        return []

    def s291(self, current_text, start_line, start_col):
        """State 291: Check Escape Char."""
        # We are on the backslash. Consume it.
        self.advance()
        
        if self.current_char is None:
             self.errors.append(self._report_lit_error(
                allowed_set=['n', 't', 'd', '"', '\\'],
                error_type=ErrorHandler.ERR_LEX_UNCLOSED_LIT
            ))
             return []

        char = self.current_char

        # Valid Escapes: \n, \t, \d, \", \\
        if char in ['n', 't', 'd', '"', '\\']:
            self.advance()
            # Append backslash + char and return to body
            return self.s288(current_text + '\\' + char, start_line, start_col)
            
        # Invalid Escape
        self.errors.append(self._report_lit_error(
            allowed_set=['n', 't', 'd', '"', '\\'],
            error_type=ErrorHandler.ERR_LEX_MALFORMED_LIT,
            custom_msg=f"Invalid Escape Sequence \\{char}"
        ))
        return []

    def s289(self, current_text, start_line, start_col):
        """State 289: Delimiter Check."""
        
        # Check current char (which is the one AFTER the closing quote)
        if self._comp_delims(self._get_scroll_delims()):
            return [Token("SCROLL-lit", current_text, start_line, start_col)]
        
        # Invalid Delimiter
        self.errors.append(self._report_lit_error(
            allowed_set=self._get_scroll_delims(),
            error_type=ErrorHandler.ERR_LEX_INVALID_DELIM,
            # Diff char is usually just the current invalid char
            diff_char=self.current_char if self.current_char else "EOF"
        ))
        
        return []