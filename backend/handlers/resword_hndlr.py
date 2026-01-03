from lexer_token import Token
from handlers.delimiters import Delimiters
import string

# =================================================================================================
# RESERVED WORDS TD: Reserved words state machine (i193 - i231)
# Identifiers (like variable names) in the source code.
# - must start with a lowercase letter (handled in Lexer.state0).
# - limited to a maximum length of 20 characters.
# =================================================================================================

# --- Inherited Methods ---
# Entry Point: The main method is _make_identifier(), which is called by the main Lexer.state0() 
#              when it sees the first lowercase letter.

# --- Program Flow & its helper method ---
# 1. one state checks for a valid next character and advances (states i193, i195, etc.), 
#    and the next state finalizes the token if no valid character was found (states i194, i196, etc.). 
#    This pattern repeats for 20 characters.
# 2. (_is_alphanumeric_or_underscore checks for char.islower()). 
# 3. If the identifier is 21 characters or more:
#    - state i231 sees a valid character (the 21st). It calls self.advance().
#    - It enters a while loop to consume all remaining invalid identifier characters.
#    - It creates an ERROR token, reporting the entire oversized lexeme and the "exceeds 20 character limit" message.
#    - It returns None to ensure this error is logged but not added to the valid token list.

class ReservedWordHandler:

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
        
        # 1. Capture the invalid char
        err_char = self.current_char
        # 2. Advance FIRST so self.col updates
        self.advance() 
        # 3. Report with the captured char
        self._report_char_error("Invalid Character. Expected start of Reserved Word.", err_char)
        return None
    
    # =========================================================================================
    # Error Reporting Helper
    # =========================================================================================

    def _report_char_error(self, message, lex_txt=None):
        # 1. Use the passed text if available, otherwise check current token
        error_text = lex_txt if lex_txt else self.current_token_text()
        
        # 2. Fallback to current_char if still empty
        if not error_text and self.current_char:
            error_text = self.current_char

        err_token = Token(
            "ERROR",
            error_text, 
            self.line,
            self.col - 1,
            message 
        )
        self.errors.append(err_token)        
        return None

    # =========================================================================================
    # RESERVED WORDS "A"": ABYSS, ADRIFT, AHOY, ASK, AYE
    # =========================================================================================
    def rw1(self): # On 'A'
        self.advance() # Consume 'A'
        char = self.current_char
        if char == 'B': return self.rw2()
        if char == 'D': return self.rw7()
        if char == 'H': return self.rw13()
        if char == 'S': return self.rw17()
        if char == 'Y': return self.rw20()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'B', 'D', 'H', 'S', or 'Y'")
        return None

    def rw2(self): # On 'B' (AB)
        self.advance() # Consume 'B'
        if self.current_char == 'Y': return self.rw3()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'Y'")
        
        return None

    def rw3(self): # On 'Y' (ABY)
        self.advance() # Consume 'Y'
        if self.current_char == 'S': return self.rw4()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'S'")
        
        return None

    def rw4(self): # On 'S' (ABYS)
        self.advance() # Consume 'S'
        if self.current_char == 'S': return self.rw5()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'S'")
        
        return None
        
    def rw5(self): # On 'S' (ABYSS)
        self.advance() # Consume 'S'
        char = self.current_char
        if char is None or char.isspace(): # Whitespace
            return self.rw6()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)")

    def rw6(self): # End state for ABYSS
        return Token("ABYSS", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw7(self): # On 'D' (AD)
        self.advance() # Consume 'D'
        if self.current_char == 'R': return self.rw8()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'R'")
        
        return None

    def rw8(self): # On 'R' (ADR)
        self.advance() # Consume 'R'
        if self.current_char == 'I': return self.rw9()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'I'")
        
        return None

    def rw9(self): # On 'I' (ADRI)
        self.advance() # Consume 'I'
        if self.current_char == 'F': return self.rw10()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'F'")
        
        return None

    def rw10(self): # On 'F' (ADRIF)
        self.advance() # Consume 'F'
        if self.current_char == 'T': return self.rw11()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'T'")
        
        return None

    def rw11(self): # On 'T' (ADRIFT)
        self.advance() # Consume 'T'
        char = self.current_char
        if char is None or char.isspace() or char == ':':
            return self.rw12()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or ':')")

    def rw12(self): # End state for ADRIFT
        return Token("ADRIFT", self.current_token_text(), self.token_start_line, self.token_start_col)
        
    def rw13(self): # On 'H' (AH)
        self.advance() # Consume 'H'
        if self.current_char == 'O': return self.rw14()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'O'")
        
        return None
    
    def rw14(self): # On 'O' (AHO)
        self.advance() # Consume 'O'
        if self.current_char == 'Y': return self.rw15()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'Y'")
        
        return None

    def rw15(self): # On 'Y' (AHOY)
        self.advance() # Consume 'Y'
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw16()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')")
        
    def rw16(self): # End state for AHOY
        return Token("AHOY", self.current_token_text(), self.token_start_line, self.token_start_col)
        
    def rw17(self): # On 'S' (AS)
        self.advance() # Consume 'S'
        if self.current_char == 'K': return self.rw18()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'K'")
        
        return None
        
    def rw18(self): # On 'K' (ASK)
        self.advance() # Consume 'K'
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw19()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')")
        
    def rw19(self): # End state for ASK
        return Token("ASK", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw20(self): # On 'Y' (AY)
        self.advance() # Consume 'Y'
        if self.current_char == 'E': return self.rw21()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'E'")
        
        return None

    def rw21(self): # On 'E' (AYE)
        self.advance() # Consume 'E'
        if self._comp_delims(Delimiters._get_delimiters()["BOOL_DELIM"]):
            return self.rw22()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter")

    def rw22(self): # End state for AYE
        return Token("AYE", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "B": BACK, BOOL
    # =========================================================================================
    def rw23(self): # On 'B'
        self.advance() # Consume 'B'
        char = self.current_char
        if char == 'A': return self.rw24()
        if char == 'O': return self.rw28()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'A' or 'O'")
        return None

    def rw24(self): # On 'A' (BA)
        self.advance() # Consume 'A'
        if self.current_char == 'C': return self.rw25()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'C'")
        
        return None

    def rw25(self): # On 'C' (BAC)
        self.advance() # Consume 'C'
        if self.current_char == 'K': return self.rw26()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'K'")
        
        return None

    def rw26(self): # On 'K' (BACK)
        self.advance() # Consume 'K'
        char = self.current_char
        if char is None or char.isspace() or char == '(' or char == '!':
            return self.rw27()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace, '(', or '!')")

    def rw27(self): # End state for BACK
        return Token("BACK", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw28(self): # On 'O' (BO)
        self.advance() # Consume 'O'
        if self.current_char == 'O': return self.rw29()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'O'")
        
        return None

    def rw29(self): # On 'O' (BOO)
        self.advance() # Consume 'O'
        if self.current_char == 'L': return self.rw30()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'L'")
        
        return None

    def rw30(self): # On 'L' (BOOL)
        self.advance() # Consume 'L'
        char = self.current_char
        if char is None or char.isspace():
            return self.rw31()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)")

    def rw31(self): # End state for BOOL
        return Token("BOOL", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "C": CHART, COIN, COURSE
    # =========================================================================================
    def rw32(self): # On 'C'
        self.advance() # Consume 'C'
        char = self.current_char
        if char == 'H': return self.rw33()
        if char == 'O': return self.rw38()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'H' or 'O'")
        return None

    def rw33(self): # On 'H' (CH)
        self.advance() # Consume 'H'
        if self.current_char == 'A': return self.rw34()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'A'")
        
        return None

    def rw34(self): # On 'A' (CHA)
        self.advance() # Consume 'A'
        if self.current_char == 'R': return self.rw35()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'R'")
        
        return None

    def rw35(self): # On 'R' (CHAR)
        self.advance() # Consume 'R'
        if self.current_char == 'T': return self.rw36()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'T'")
        
        return None

    def rw36(self): # On 'T' (CHART)
        self.advance() # Consume 'T'
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw37()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')")

    def rw37(self): # End state for CHART
        return Token("CHART", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw38(self): # On 'O' (CO)
        self.advance() # Consume 'O'
        char = self.current_char
        if char == 'I': return self.rw39()
        if char == 'U': return self.rw42()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'I' or 'U'")
        
        return None

    def rw39(self): # On 'I' (COI)
        self.advance() # Consume 'I'
        if self.current_char == 'N': return self.rw40()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'N'")
        
        return None

    def rw40(self): # On 'N' (COIN)
        self.advance() # Consume 'N'
        char = self.current_char
        if char is None or char.isspace():
            return self.rw41()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)")

    def rw41(self): # End state for COIN
        return Token("COIN", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw42(self): # On 'U' (COU)
        self.advance() # Consume 'U'
        if self.current_char == 'R': return self.rw43()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'R'")
        
        return None

    def rw43(self): # On 'R' (COUR)
        self.advance() # Consume 'R'
        if self.current_char == 'S': return self.rw44()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'S'")
        
        return None

    def rw44(self): # On 'S' (COURS)
        self.advance() # Consume 'S'
        if self.current_char == 'E': return self.rw45()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'E'")
        
        return None

    def rw45(self): # On 'E' (COURSE)
        self.advance() # Consume 'E'
        char = self.current_char
        if char is None or char.isspace() or char == ':':
            return self.rw46()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or ':')")

    def rw46(self): # End state for COURSE
        return Token("COURSE", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "D": DIME, DROP, DROPLOOK
    # =========================================================================================
    def rw47(self): # On 'D'
        self.advance() # Consume 'D'
        char = self.current_char
        if char == 'I': return self.rw48()
        if char == 'R': return self.rw52()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'I' or 'R'")
        return None

    def rw48(self): # On 'I' (DI)
        self.advance() # Consume 'I'
        if self.current_char == 'M': return self.rw49()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'M'")
        
        return None

    def rw49(self): # On 'M' (DIM)
        self.advance() # Consume 'M'
        if self.current_char == 'E': return self.rw50()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'E'")
        
        return None

    def rw50(self): # On 'E' (DIME)
        self.advance() # Consume 'E'
        char = self.current_char
        if char is None or char.isspace():
            return self.rw51()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)")

    def rw51(self): # End state for DIME
        return Token("DIME", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw52(self): # On 'R' (DR)
        self.advance() # Consume 'R'
        if self.current_char == 'O': return self.rw53()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'O'")
        
        return None

    def rw53(self): # On 'O' (DRO)
        self.advance() # Consume 'O'
        if self.current_char == 'P': return self.rw54()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'P'")
        
        return None

    def rw54(self): # On 'P' (DROP)
        self.advance() # Consume 'P'
        # Must check for longer keyword 'DROPLOOK' first
        if self.current_char == 'L': return self.rw56()
        # If not, check for 'DROP' delimiter
        char = self.current_char
        if char is None or char.isspace() or char == '[':
            return self.rw55()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected 'L' or delimiter (whitespace or '[')")

    def rw55(self): # End state for DROP
        return Token("DROP", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw56(self): # On 'L' (DROPL)
        self.advance() # Consume 'L'
        if self.current_char == 'O': return self.rw57()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'O'")
        
        return None

    def rw57(self): # On 'O' (DROPLO)
        self.advance() # Consume 'O'
        if self.current_char == 'O': return self.rw58()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'O'")
        
        return None

    def rw58(self): # On 'O' (DROPLOO)
        self.advance() # Consume 'O'
        if self.current_char == 'K': return self.rw59()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'K'")
        
        return None

    def rw59(self): # On 'K' (DROPLOOK)
        self.advance() # Consume 'K'
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw60()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')")

    def rw60(self): # End state for DROPLOOK
        return Token("DROPLOOK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "E": ECHO
    # =========================================================================================
    def rw61(self): # On 'E'
        self.advance() # Consume 'E'
        if self.current_char == 'C': return self.rw62()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'C'")
        return None

    def rw62(self): # On 'C' (EC)
        self.advance() # Consume 'C'
        if self.current_char == 'H': return self.rw63()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'H'")
        
        return None

    def rw63(self): # On 'H' (ECH)
        self.advance() # Consume 'H'
        if self.current_char == 'O': return self.rw64()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'O'")
        
        return None

    def rw64(self): # On 'O' (ECHO)
        self.advance() # Consume 'O'
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw65()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')")

    def rw65(self): # End state for ECHO
        return Token("ECHO", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "H": HAUL, HEAVE, HOIST
    # =========================================================================================
    def rw66(self): # On 'H'
        self.advance() # Consume 'H'
        char = self.current_char
        if char == 'A': return self.rw67()
        if char == 'E': return self.rw71()
        if char == 'O': return self.rw76()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'A', 'E', or 'O'")
        return None

    def rw67(self): # On 'A' (HA)
        self.advance() # Consume 'A'
        if self.current_char == 'U': return self.rw68()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'U'")
        
        return None

    def rw68(self): # On 'U' (HAU)
        self.advance() # Consume 'U'
        if self.current_char == 'L': return self.rw69()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'L'")
        
        return None

    def rw69(self): # On 'L' (HAUL)
        self.advance() # Consume 'L'
        char = self.current_char
        if char is None or char.isspace() or char == '[':
            return self.rw70()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '[')")

    def rw70(self): # End state for HAUL
        return Token("HAUL", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw71(self): # On 'E' (HE)
        self.advance() # Consume 'E'
        if self.current_char == 'A': return self.rw72()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'A'")
        
        return None

    def rw72(self): # On 'A' (HEA)
        self.advance() # Consume 'A'
        if self.current_char == 'V': return self.rw73()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'V'")
        
        return None

    def rw73(self): # On 'V' (HEAV)
        self.advance() # Consume 'V'
        if self.current_char == 'E': return self.rw74()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'E'")
        
        return None

    def rw74(self): # On 'E' (HEAVE)
        self.advance() # Consume 'E'
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw75()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')")

    def rw75(self): # End state for HEAVE
        return Token("HEAVE", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw76(self): # On 'O' (HO)
        self.advance() # Consume 'O'
        if self.current_char == 'I': return self.rw77()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'I'")
        
        return None

    def rw77(self): # On 'I' (HOI)
        self.advance() # Consume 'I'
        if self.current_char == 'S': return self.rw78()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'S'")
        
        return None

    def rw78(self): # On 'S' (HOIS)
        self.advance() # Consume 'S'
        if self.current_char == 'T': return self.rw79()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'T'")
        
        return None

    def rw79(self): # On 'T' (HOIST)
        self.advance() # Consume 'T'
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw80()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')")

    def rw80(self): # End state for HOIST
        return Token("HOIST", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "L": LAND, LOCKE, LOOK
    # =========================================================================================
    def rw81(self): # On 'L'
        self.advance() # Consume 'L'
        char = self.current_char
        if char == 'A': return self.rw82()
        if char == 'O': return self.rw86()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'A' or 'O'")
        return None

    def rw82(self): # On 'A' (LA)
        self.advance() # Consume 'A'
        if self.current_char == 'N': return self.rw83()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'N'")
        
        return None

    def rw83(self): # On 'N' (LAN)
        self.advance() # Consume 'N'
        if self.current_char == 'D': return self.rw84()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'D'")
        
        return None

    def rw84(self): # On 'D' (LAND)
        self.advance() # Consume 'D'
        char = self.current_char
        if char is None or char == '!':
            return self.rw85()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '!')")

    def rw85(self): # End state for LAND
        return Token("LAND", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw86(self): # On 'O' (LO)
        self.advance() # Consume 'O'
        char = self.current_char
        if char == 'C': return self.rw87()
        if char == 'O': return self.rw91()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'C' or 'O'")
        
        return None

    def rw87(self): # On 'C' (LOC)
        self.advance() # Consume 'C'
        if self.current_char == 'K': return self.rw88()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'K'")
        
        return None

    def rw88(self): # On 'K' (LOCK)
        self.advance() # Consume 'K'
        if self.current_char == 'E': return self.rw89()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'E'")
        
        return None

    def rw89(self): # On 'E' (LOCKE)
        self.advance() # Consume 'E'
        char = self.current_char
        if char is None or char.isspace():
            return self.rw90()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)")

    def rw90(self): # End state for LOCKE
        return Token("LOCKE", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw91(self): # On 'O' (LOO)
        self.advance() # Consume 'O'
        if self.current_char == 'K': return self.rw92()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'K'")
        
        return None

    def rw92(self): # On 'K' (LOOK)
        self.advance() # Consume 'K'
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw93()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')")

    def rw93(self): # End state for LOOK
        return Token("LOOK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "M": MAST
    # =========================================================================================
    def rw94(self): # On 'M'
        self.advance() # Consume 'M'
        if self.current_char == 'A': return self.rw95()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'A'")
        return None

    def rw95(self): # On 'A' (MA)
        self.advance() # Consume 'A'
        if self.current_char == 'S': return self.rw96()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'S'")
        
        return None

    def rw96(self): # On 'S' (MAS)
        self.advance() # Consume 'S'
        if self.current_char == 'T': return self.rw97()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'T'")
        
        return None

    def rw97(self): # On 'T' (MAST)
        self.advance() # Consume 'T'
        char = self.current_char
        if char is None or char.isspace():
            return self.rw98()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)")

    def rw98(self): # End state for MAST
        return Token("MAST", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "N": NAY
    # =========================================================================================
    def rw99(self): # On 'N'
        self.advance() # Consume 'N'
        if self.current_char == 'A': return self.rw100()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'A'")
        return None

    def rw100(self): # On 'A' (NA)
        self.advance() # Consume 'A'
        if self.current_char == 'Y': return self.rw101()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'Y'")
        
        return None

    def rw101(self): # On 'Y' (NAY)
        self.advance() # Consume 'Y'
        if self._comp_delims(Delimiters._get_delimiters()["BOOL_DELIM"]):
            return self.rw102()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter")

    def rw102(self): # End state for NAY
        return Token("NAY", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "P": PARCH
    # =========================================================================================
    def rw103(self): # On 'P'
        self.advance() # Consume 'P'
        if self.current_char == 'A': return self.rw104()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'A'")
        return None

    def rw104(self): # On 'A' (PA)
        self.advance() # Consume 'A'
        if self.current_char == 'R': return self.rw105()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'R'")
        
        return None

    def rw105(self): # On 'R' (PAR)
        self.advance() # Consume 'R'
        if self.current_char == 'C': return self.rw106()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'C'")
        
        return None

    def rw106(self): # On 'C' (PARC)
        self.advance() # Consume 'C'
        if self.current_char == 'H': return self.rw107()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'H'")
        
        return None

    def rw107(self): # On 'H' (PARCH)
        self.advance() # Consume 'H'
        char = self.current_char
        if char is None or char.isspace():
            return self.rw108()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)")

    def rw108(self): # End state for PARCH
        return Token("PARCH", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "S": SAIL, SCROLL
    # =========================================================================================
    def rw109(self): # On 'S'
        self.advance() # Consume 'S'
        char = self.current_char
        if char == 'A': return self.rw110()
        if char == 'C': return self.rw114()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'A' or 'C'")

        return None

    def rw110(self): # On 'A' (SA)
        self.advance() # Consume 'A'
        if self.current_char == 'I': return self.rw111()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'I'")
        
        return None

    def rw111(self): # On 'I' (SAI)
        self.advance() # Consume 'I'
        if self.current_char == 'L': return self.rw112()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'L'")
        
        return None

    def rw112(self): # On 'L' (SAIL)
        self.advance() # Consume 'L'
        char = self.current_char
        if char is None or char == '!':
            return self.rw113()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '!')")

    def rw113(self): # End state for SAIL
        return Token("SAIL", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw114(self): # On 'C' (SC)
        self.advance() # Consume 'C'
        if self.current_char == 'R': return self.rw115()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'R'")
        
        return None

    def rw115(self): # On 'R' (SCR)
        self.advance() # Consume 'R'
        if self.current_char == 'O': return self.rw116()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'O'")
        
        return None

    def rw116(self): # On 'O' (SCRO)
        self.advance() # Consume 'O'
        if self.current_char == 'L': return self.rw117()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'L'")
        
        return None

    def rw117(self): # On 'L' (SCROL)
        self.advance() # Consume 'L'
        if self.current_char == 'L': return self.rw118()
        
        # --- "Path" Error ---
        self._report_char_error("Invalid Reserved Word. Expected 'L'")
        
        return None

    def rw118(self): # On 'L' (SCROLL)
        self.advance() # Consume 'L'
        char = self.current_char
        if char is None or char.isspace():
            return self.rw119()
            
        # --- "Delimiter" Error ---
        return self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)")

    def rw119(self): # End state for SCROLL
        return Token("SCROLL", self.current_token_text(), self.token_start_line, self.token_start_col)