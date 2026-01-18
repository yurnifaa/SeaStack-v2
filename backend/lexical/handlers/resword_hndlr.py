import string
from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters
from backend.error_msg import ErrorHandler 

# =================================================================================================
# RESERVED WORDS TD: Reserved words state machine (i193 - i231)
# Identifiers (like variable names) in the source code.
# - must start with a lowercase letter (handled in Lexer.state0).
# - limited to a maximum length of 20 characters.
# =================================================================================================

class ReservedWordHandler:

    # --- HELPER: DYNAMIC & CLEAN ERROR GENERATION ---
    def _report_rw_error(self, allowed_set=None, error_type=None, custom_msg=None, diff_char=None):
        """
        Generates a standardized error dictionary for Reserved Words.
        """
        if allowed_set is None:
            allowed_set = set()
        else:
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
        # Check against the full Delimiters.WHITESPACE set or string.whitespace
        if allowed_set.intersection(set(string.whitespace)):
            cleaned_list.append("whitespace")
            allowed_set -= set(string.whitespace)

        # Format Remaining
        for char in sorted(list(allowed_set)):
            if char == "\n": cleaned_list.append("\\n")
            elif char == "\t": cleaned_list.append("\\t")
            elif char == " ": cleaned_list.append("' '")
            else: cleaned_list.append(char)
        
        # 2. Determine Error Type
        if error_type is None:
            # Default to Invalid Character for path errors (e.g. A -> B failed)
            error_type = ErrorHandler.ERR_LEX_INVALID_CHAR

        # 3. Determine text to show
        text_to_show = diff_char if diff_char else self.current_token_text()
        if not text_to_show and self.current_char:
            text_to_show = self.current_char

        # 4. Generate Error
        return ErrorHandler.get_lexical_error(
            line=self.line,
            col=self.col - 1,
            invalid_char=text_to_show,
            expected_list=sorted(cleaned_list),
            header_type=error_type,
            custom_msg=custom_msg
        )

    # =========================================================================================
    # RESERVED WORDS TD: Reserved Word state machine (rw0)
    # ========================================================================================= 
    def _make_keyword(self):
        char = self.current_char
        
        # --- Reserved Words Transitions ---
        if char == 'A': return self.rw1()
        if char == 'B': return self.rw23()
        if char == 'C': return self.rw32()
        if char == 'D': return self.rw47()
        if char == 'E': return self.rw61()
        if char == 'H': return self.rw66()
        if char == 'L': return self.rw81()
        if char == 'M': return self.rw94()
        if char == 'N': return self.rw99()
        if char == 'P': return self.rw103()
        if char == 'S': return self.rw109()
        
        # --- "Path" Error ---
        err_char = self.current_char
        self.advance() 
        self.errors.append(self._report_rw_error(
            allowed_set=['A', 'B', 'C', 'D', 'E', 'H', 'L', 'M', 'N', 'P', 'S'],
            custom_msg="Invalid Character. Expected start of Reserved Word.",
            diff_char=err_char
        ))
        return None

    # =========================================================================================
    # RESERVED WORDS "A"": ABYSS, ADRIFT, AHOY, ASK, AYE
    # =========================================================================================
    def rw1(self): # On 'A'
        self.advance() 
        char = self.current_char
        if char == 'B': return self.rw2()
        if char == 'D': return self.rw7()
        if char == 'H': return self.rw13()
        if char == 'S': return self.rw17()
        if char == 'Y': return self.rw20()
        
        self.errors.append(self._report_rw_error(['B', 'D', 'H', 'S', 'Y']))
        return None

    def rw2(self): # On 'B' (AB)
        self.advance() 
        if self.current_char == 'Y': return self.rw3()
        self.errors.append(self._report_rw_error(['Y']))
        return None

    def rw3(self): # On 'Y' (ABY)
        self.advance() 
        if self.current_char == 'S': return self.rw4()
        self.errors.append(self._report_rw_error(['S']))
        return None

    def rw4(self): # On 'S' (ABYS)
        self.advance() 
        if self.current_char == 'S': return self.rw5()
        self.errors.append(self._report_rw_error(['S']))
        return None
        
    def rw5(self): # On 'S' (ABYSS)
        self.advance() 
        # Delimiter Check: Whitespace
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"]
        if self._comp_delims(valid_delims):
            return self.rw6()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw6(self): return Token("ABYSS", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw7(self): # On 'D' (AD)
        self.advance() 
        if self.current_char == 'R': return self.rw8()
        self.errors.append(self._report_rw_error(['R']))
        return None

    def rw8(self): # On 'R' (ADR)
        self.advance() 
        if self.current_char == 'I': return self.rw9()
        self.errors.append(self._report_rw_error(['I']))
        return None

    def rw9(self): # On 'I' (ADRI)
        self.advance() 
        if self.current_char == 'F': return self.rw10()
        self.errors.append(self._report_rw_error(['F']))
        return None

    def rw10(self): # On 'F' (ADRIF)
        self.advance() 
        if self.current_char == 'T': return self.rw11()
        self.errors.append(self._report_rw_error(['T']))
        return None

    def rw11(self): # On 'T' (ADRIFT)
        self.advance() 
        # Delimiter Check: Whitespace OR Colon ':'
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {':'}
        if self._comp_delims(valid_delims):
            return self.rw12()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw12(self): return Token("ADRIFT", self.current_token_text(), self.token_start_line, self.token_start_col)
        
    def rw13(self): # On 'H' (AH)
        self.advance() 
        if self.current_char == 'O': return self.rw14()
        self.errors.append(self._report_rw_error(['O']))
        return None
    
    def rw14(self): # On 'O' (AHO)
        self.advance() 
        if self.current_char == 'Y': return self.rw15()
        self.errors.append(self._report_rw_error(['Y']))
        return None

    def rw15(self): # On 'Y' (AHOY)
        self.advance() 
        # Delimiter Check: Whitespace OR '('
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {'('}
        if self._comp_delims(valid_delims):
            return self.rw16()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None
        
    def rw16(self): return Token("AHOY", self.current_token_text(), self.token_start_line, self.token_start_col)
        
    def rw17(self): # On 'S' (AS)
        self.advance() 
        if self.current_char == 'K': return self.rw18()
        self.errors.append(self._report_rw_error(['K']))
        return None
        
    def rw18(self): # On 'K' (ASK)
        self.advance() 
        # Delimiter Check: Whitespace OR '('
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {'('}
        if self._comp_delims(valid_delims):
            return self.rw19()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None
        
    def rw19(self): return Token("ASK", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw20(self): # On 'Y' (AY)
        self.advance() 
        if self.current_char == 'E': return self.rw21()
        self.errors.append(self._report_rw_error(['E']))
        return None

    def rw21(self): # On 'E' (AYE)
        self.advance() 
        # Delimiter Check: BOOL_DELIM
        valid_delims = Delimiters._get_delimiters()["BOOL_DELIM"]
        if self._comp_delims(valid_delims):
            return self.rw22()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw22(self): return Token("AYE", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "B": BACK, BOOL
    # =========================================================================================
    def rw23(self): # On 'B'
        self.advance() 
        char = self.current_char
        if char == 'A': return self.rw24()
        if char == 'O': return self.rw28()
        self.errors.append(self._report_rw_error(['A', 'O']))
        return None

    def rw24(self): # On 'A' (BA)
        self.advance() 
        if self.current_char == 'C': return self.rw25()
        self.errors.append(self._report_rw_error(['C']))
        return None

    def rw25(self): # On 'C' (BAC)
        self.advance() 
        if self.current_char == 'K': return self.rw26()
        self.errors.append(self._report_rw_error(['K']))
        return None

    def rw26(self): # On 'K' (BACK)
        self.advance() 
        # Delimiter Check: BACK_DELIM (Whitespace | ( | !)
        valid_delims = Delimiters._get_delimiters()["BACK_DELIM"]
        if self._comp_delims(valid_delims):
            return self.rw27()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw27(self): return Token("BACK", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw28(self): # On 'O' (BO)
        self.advance() 
        if self.current_char == 'O': return self.rw29()
        self.errors.append(self._report_rw_error(['O']))
        return None

    def rw29(self): # On 'O' (BOO)
        self.advance() 
        if self.current_char == 'L': return self.rw30()
        self.errors.append(self._report_rw_error(['L']))
        return None

    def rw30(self): # On 'L' (BOOL)
        self.advance() 
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"]
        if self._comp_delims(valid_delims):
            return self.rw31()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw31(self): return Token("BOOL", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "C": CHART, COIN, COURSE
    # =========================================================================================
    def rw32(self): # On 'C'
        self.advance() 
        char = self.current_char
        if char == 'H': return self.rw33()
        if char == 'O': return self.rw38()
        self.errors.append(self._report_rw_error(['H', 'O']))
        return None

    def rw33(self): # On 'H' (CH)
        self.advance() 
        if self.current_char == 'A': return self.rw34()
        self.errors.append(self._report_rw_error(['A']))
        return None

    def rw34(self): # On 'A' (CHA)
        self.advance() 
        if self.current_char == 'R': return self.rw35()
        self.errors.append(self._report_rw_error(['R']))
        return None

    def rw35(self): # On 'R' (CHAR)
        self.advance() 
        if self.current_char == 'T': return self.rw36()
        self.errors.append(self._report_rw_error(['T']))
        return None

    def rw36(self): # On 'T' (CHART)
        self.advance() 
        # Delimiter Check: Whitespace | '('
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {'('}
        if self._comp_delims(valid_delims):
            return self.rw37()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw37(self): return Token("CHART", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw38(self): # On 'O' (CO)
        self.advance() 
        char = self.current_char
        if char == 'I': return self.rw39()
        if char == 'U': return self.rw42()
        self.errors.append(self._report_rw_error(['I', 'U']))
        return None

    def rw39(self): # On 'I' (COI)
        self.advance() 
        if self.current_char == 'N': return self.rw40()
        self.errors.append(self._report_rw_error(['N']))
        return None

    def rw40(self): # On 'N' (COIN)
        self.advance() 
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"]
        if self._comp_delims(valid_delims):
            return self.rw41()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw41(self): return Token("COIN", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw42(self): # On 'U' (COU)
        self.advance() 
        if self.current_char == 'R': return self.rw43()
        self.errors.append(self._report_rw_error(['R']))
        return None

    def rw43(self): # On 'R' (COUR)
        self.advance() 
        if self.current_char == 'S': return self.rw44()
        self.errors.append(self._report_rw_error(['S']))
        return None

    def rw44(self): # On 'S' (COURS)
        self.advance() 
        if self.current_char == 'E': return self.rw45()
        self.errors.append(self._report_rw_error(['E']))
        return None

    def rw45(self): # On 'E' (COURSE)
        self.advance() 
        # Delimiter Check: Whitespace | ':'
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {':'}
        if self._comp_delims(valid_delims):
            return self.rw46()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw46(self): return Token("COURSE", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "D": DIME, DROP, DROPLOOK
    # =========================================================================================
    def rw47(self): # On 'D'
        self.advance() 
        char = self.current_char
        if char == 'I': return self.rw48()
        if char == 'R': return self.rw52()
        self.errors.append(self._report_rw_error(['I', 'R']))
        return None

    def rw48(self): # On 'I' (DI)
        self.advance() 
        if self.current_char == 'M': return self.rw49()
        self.errors.append(self._report_rw_error(['M']))
        return None

    def rw49(self): # On 'M' (DIM)
        self.advance() 
        if self.current_char == 'E': return self.rw50()
        self.errors.append(self._report_rw_error(['E']))
        return None

    def rw50(self): # On 'E' (DIME)
        self.advance() 
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"]
        if self._comp_delims(valid_delims):
            return self.rw51()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw51(self): return Token("DIME", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw52(self): # On 'R' (DR)
        self.advance() 
        if self.current_char == 'O': return self.rw53()
        self.errors.append(self._report_rw_error(['O']))
        return None

    def rw53(self): # On 'O' (DRO)
        self.advance() 
        if self.current_char == 'P': return self.rw54()
        self.errors.append(self._report_rw_error(['P']))
        return None

    def rw54(self): # On 'P' (DROP)
        self.advance() 
        # Must check for longer keyword 'DROPLOOK' first
        if self.current_char == 'L': return self.rw56()
        
        # If not, check for 'DROP' delimiter: Whitespace | '['
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {'['}
        if self._comp_delims(valid_delims):
            return self.rw55()
            
        self.errors.append(self._report_rw_error(valid_delims | {'L'}, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw55(self): return Token("DROP", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw56(self): # On 'L' (DROPL)
        self.advance() 
        if self.current_char == 'O': return self.rw57()
        self.errors.append(self._report_rw_error(['O']))
        return None

    def rw57(self): # On 'O' (DROPLO)
        self.advance() 
        if self.current_char == 'O': return self.rw58()
        self.errors.append(self._report_rw_error(['O']))
        return None

    def rw58(self): # On 'O' (DROPLOO)
        self.advance() 
        if self.current_char == 'K': return self.rw59()
        self.errors.append(self._report_rw_error(['K']))
        return None

    def rw59(self): # On 'K' (DROPLOOK)
        self.advance() 
        # Delimiter Check: Whitespace | '('
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {'('}
        if self._comp_delims(valid_delims):
            return self.rw60()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw60(self): return Token("DROPLOOK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "E": ECHO
    # =========================================================================================
    def rw61(self): # On 'E'
        self.advance() 
        if self.current_char == 'C': return self.rw62()
        self.errors.append(self._report_rw_error(['C']))
        return None

    def rw62(self): # On 'C' (EC)
        self.advance() 
        if self.current_char == 'H': return self.rw63()
        self.errors.append(self._report_rw_error(['H']))
        return None

    def rw63(self): # On 'H' (ECH)
        self.advance() 
        if self.current_char == 'O': return self.rw64()
        self.errors.append(self._report_rw_error(['O']))
        return None

    def rw64(self): # On 'O' (ECHO)
        self.advance() 
        # Delimiter Check: Whitespace | '('
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {'('}
        if self._comp_delims(valid_delims):
            return self.rw65()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw65(self): return Token("ECHO", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "H": HAUL, HEAVE, HOIST
    # =========================================================================================
    def rw66(self): # On 'H'
        self.advance() 
        char = self.current_char
        if char == 'A': return self.rw67()
        if char == 'E': return self.rw71()
        if char == 'O': return self.rw76()
        self.errors.append(self._report_rw_error(['A', 'E', 'O']))
        return None

    def rw67(self): # On 'A' (HA)
        self.advance() 
        if self.current_char == 'U': return self.rw68()
        self.errors.append(self._report_rw_error(['U']))
        return None

    def rw68(self): # On 'U' (HAU)
        self.advance() 
        if self.current_char == 'L': return self.rw69()
        self.errors.append(self._report_rw_error(['L']))
        return None

    def rw69(self): # On 'L' (HAUL)
        self.advance() 
        # Delimiter Check: Whitespace | '['
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {'['}
        if self._comp_delims(valid_delims):
            return self.rw70()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw70(self): return Token("HAUL", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw71(self): # On 'E' (HE)
        self.advance() 
        if self.current_char == 'A': return self.rw72()
        self.errors.append(self._report_rw_error(['A']))
        return None

    def rw72(self): # On 'A' (HEA)
        self.advance() 
        if self.current_char == 'V': return self.rw73()
        self.errors.append(self._report_rw_error(['V']))
        return None

    def rw73(self): # On 'V' (HEAV)
        self.advance() 
        if self.current_char == 'E': return self.rw74()
        self.errors.append(self._report_rw_error(['E']))
        return None

    def rw74(self): # On 'E' (HEAVE)
        self.advance() 
        # Delimiter Check: Whitespace | '('
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {'('}
        if self._comp_delims(valid_delims):
            return self.rw75()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw75(self): return Token("HEAVE", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw76(self): # On 'O' (HO)
        self.advance() 
        if self.current_char == 'I': return self.rw77()
        self.errors.append(self._report_rw_error(['I']))
        return None

    def rw77(self): # On 'I' (HOI)
        self.advance() 
        if self.current_char == 'S': return self.rw78()
        self.errors.append(self._report_rw_error(['S']))
        return None

    def rw78(self): # On 'S' (HOIS)
        self.advance() 
        if self.current_char == 'T': return self.rw79()
        self.errors.append(self._report_rw_error(['T']))
        return None

    def rw79(self): # On 'T' (HOIST)
        self.advance() 
        # Delimiter Check: Whitespace | '('
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {'('}
        if self._comp_delims(valid_delims):
            return self.rw80()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw80(self): return Token("HOIST", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "L": LAND, LOCKE, LOOK
    # =========================================================================================
    def rw81(self): # On 'L'
        self.advance() 
        char = self.current_char
        if char == 'A': return self.rw82()
        if char == 'O': return self.rw86()
        self.errors.append(self._report_rw_error(['A', 'O']))
        return None

    def rw82(self): # On 'A' (LA)
        self.advance() 
        if self.current_char == 'N': return self.rw83()
        self.errors.append(self._report_rw_error(['N']))
        return None

    def rw83(self): # On 'N' (LAN)
        self.advance() 
        if self.current_char == 'D': return self.rw84()
        self.errors.append(self._report_rw_error(['D']))
        return None

    def rw84(self): # On 'D' (LAND)
        self.advance() 
        # Delimiter Check: Whitespace | '!'
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {'!'}
        if self._comp_delims(valid_delims):
            return self.rw85()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw85(self): return Token("LAND", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw86(self): # On 'O' (LO)
        self.advance() 
        char = self.current_char
        if char == 'C': return self.rw87()
        if char == 'O': return self.rw91()
        self.errors.append(self._report_rw_error(['C', 'O']))
        return None

    def rw87(self): # On 'C' (LOC)
        self.advance() 
        if self.current_char == 'K': return self.rw88()
        self.errors.append(self._report_rw_error(['K']))
        return None

    def rw88(self): # On 'K' (LOCK)
        self.advance() 
        if self.current_char == 'E': return self.rw89()
        self.errors.append(self._report_rw_error(['E']))
        return None

    def rw89(self): # On 'E' (LOCKE)
        self.advance() 
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"]
        if self._comp_delims(valid_delims):
            return self.rw90()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw90(self): return Token("LOCKE", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw91(self): # On 'O' (LOO)
        self.advance() 
        if self.current_char == 'K': return self.rw92()
        self.errors.append(self._report_rw_error(['K']))
        return None

    def rw92(self): # On 'K' (LOOK)
        self.advance() 
        # Delimiter Check: Whitespace | '('
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {'('}
        if self._comp_delims(valid_delims):
            return self.rw93()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw93(self): return Token("LOOK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "M": MAST
    # =========================================================================================
    def rw94(self): # On 'M'
        self.advance() 
        if self.current_char == 'A': return self.rw95()
        self.errors.append(self._report_rw_error(['A']))
        return None

    def rw95(self): # On 'A' (MA)
        self.advance() 
        if self.current_char == 'S': return self.rw96()
        self.errors.append(self._report_rw_error(['S']))
        return None

    def rw96(self): # On 'S' (MAS)
        self.advance() 
        if self.current_char == 'T': return self.rw97()
        self.errors.append(self._report_rw_error(['T']))
        return None

    def rw97(self): # On 'T' (MAST)
        self.advance() 
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"]
        if self._comp_delims(valid_delims):
            return self.rw98()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw98(self): return Token("MAST", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "N": NAY
    # =========================================================================================
    def rw99(self): # On 'N'
        self.advance() 
        if self.current_char == 'A': return self.rw100()
        self.errors.append(self._report_rw_error(['A']))
        return None

    def rw100(self): # On 'A' (NA)
        self.advance() 
        if self.current_char == 'Y': return self.rw101()
        self.errors.append(self._report_rw_error(['Y']))
        return None

    def rw101(self): # On 'Y' (NAY)
        self.advance() 
        # Delimiter Check: BOOL_DELIM
        valid_delims = Delimiters._get_delimiters()["BOOL_DELIM"]
        if self._comp_delims(valid_delims):
            return self.rw102()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw102(self): return Token("NAY", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "P": PARCH
    # =========================================================================================
    def rw103(self): # On 'P'
        self.advance() 
        if self.current_char == 'A': return self.rw104()
        self.errors.append(self._report_rw_error(['A']))
        return None

    def rw104(self): # On 'A' (PA)
        self.advance() 
        if self.current_char == 'R': return self.rw105()
        self.errors.append(self._report_rw_error(['R']))
        return None

    def rw105(self): # On 'R' (PAR)
        self.advance() 
        if self.current_char == 'C': return self.rw106()
        self.errors.append(self._report_rw_error(['C']))
        return None

    def rw106(self): # On 'C' (PARC)
        self.advance() 
        if self.current_char == 'H': return self.rw107()
        self.errors.append(self._report_rw_error(['H']))
        return None

    def rw107(self): # On 'H' (PARCH)
        self.advance() 
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"]
        if self._comp_delims(valid_delims):
            return self.rw108()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw108(self): return Token("PARCH", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "S": SAIL, SCROLL
    # =========================================================================================
    def rw109(self): # On 'S'
        self.advance() 
        char = self.current_char
        if char == 'A': return self.rw110()
        if char == 'C': return self.rw114()
        self.errors.append(self._report_rw_error(['A', 'C']))
        return None

    def rw110(self): # On 'A' (SA)
        self.advance() 
        if self.current_char == 'I': return self.rw111()
        self.errors.append(self._report_rw_error(['I']))
        return None

    def rw111(self): # On 'I' (SAI)
        self.advance() 
        if self.current_char == 'L': return self.rw112()
        self.errors.append(self._report_rw_error(['L']))
        return None

    def rw112(self): # On 'L' (SAIL)
        self.advance() 
        # Delimiter Check: Whitespace | '!'
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"] | {'!'}
        if self._comp_delims(valid_delims):
            return self.rw113()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw113(self): return Token("SAIL", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw114(self): # On 'C' (SC)
        self.advance() 
        if self.current_char == 'R': return self.rw115()
        self.errors.append(self._report_rw_error(['R']))
        return None

    def rw115(self): # On 'R' (SCR)
        self.advance() 
        if self.current_char == 'O': return self.rw116()
        self.errors.append(self._report_rw_error(['O']))
        return None

    def rw116(self): # On 'O' (SCRO)
        self.advance() 
        if self.current_char == 'L': return self.rw117()
        self.errors.append(self._report_rw_error(['L']))
        return None

    def rw117(self): # On 'L' (SCROL)
        self.advance() 
        if self.current_char == 'L': return self.rw118()
        self.errors.append(self._report_rw_error(['L']))
        return None

    def rw118(self): # On 'L' (SCROLL)
        self.advance() 
        valid_delims = Delimiters._get_delimiters()["WHITESPACE"]
        if self._comp_delims(valid_delims):
            return self.rw119()
            
        self.errors.append(self._report_rw_error(valid_delims, ErrorHandler.ERR_LEX_INVALID_DELIM))
        return None

    def rw119(self): return Token("SCROLL", self.current_token_text(), self.token_start_line, self.token_start_col)