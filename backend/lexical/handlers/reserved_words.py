# lexer_handlers/resword_handler.py
from backend.lexical.token import Token
from backend.lexical.handlers.delimiters import Delimiters

# =================================================================================================
# RESERVED WORDS TD: Reserved words state machine (rw0 - rw119)
# =================================================================================================

class ReservedWords:  

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
    
    # =========================================================================================
    # RESERVED WORDS "A"
    # =========================================================================================
    def rw1(self): # On 'A'
        self.advance() # Consume 'A'
        char = self.current_char
        if char == 'B': return self.rw2()
        if char == 'D': return self.rw7()
        if char == 'H': return self.rw13()
        if char == 'S': return self.rw17()
        if char == 'Y': return self.rw20()
        
        return self.error()

    # --- ABYSS ---
    def rw2(self): # On 'B' (AB)
        self.advance() 
        if self.current_char == 'Y': return self.rw3()
        # DELIMITERS
        return self.error()

    def rw3(self): # On 'Y' (ABY)
        self.advance() 
        if self.current_char == 'S': return self.rw4()
        return self.error()

    def rw4(self): # On 'S' (ABYS)
        self.advance() 
        if self.current_char == 'S': return self.rw5()
        # DELIMITERS
        return self.error()
        
    def rw5(self): # On 'S' (ABYSS)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw6()
        # DELIMITERS
        return self.error()

    def rw6(self): 
        return Token("ABYSS", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- ADRIFT ---
    def rw7(self): # On 'D' (AD)
        self.advance() 
        if self.current_char == 'R': return self.rw8()
        # DELIMITERS
        return self.error()

    def rw8(self): # On 'R' (ADR)
        self.advance() 
        if self.current_char == 'I': return self.rw9()
        # DELIMITERS
        return self.error()

    def rw9(self): # On 'I' (ADRI)
        self.advance() 
        if self.current_char == 'F': return self.rw10()
        # DELIMITERS
        return self.error()

    def rw10(self): # On 'F' (ADRIF)
        self.advance() 
        if self.current_char == 'T': return self.rw11()
        # DELIMITERS
        return self.error()

    def rw11(self): # On 'T' (ADRIFT)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set(':')
        if self._comp_delims(valid):
            return self.rw12()
        # DELIMITERS
        return self.error()

    def rw12(self): 
        return Token("ADRIFT", self.current_token_text(), self.token_start_line, self.token_start_col)
        
    # --- AHOY ---
    def rw13(self): # On 'H' (AH)
        self.advance() 
        if self.current_char == 'O': return self.rw14()
        # DELIMITERS
        return self.error()
    
    def rw14(self): # On 'O' (AHO)
        self.advance() 
        if self.current_char == 'Y': return self.rw15()
        # DELIMITERS
        return self.error()

    def rw15(self): # On 'Y' (AHOY)
        self.advance() 
        if self.current_char == '(': return self.rw16()
        # DELIMITERS
        return self.error()
        
    def rw16(self): 
        return Token("AHOY", self.current_token_text(), self.token_start_line, self.token_start_col)
        
    # --- ASK ---
    def rw17(self): # On 'S' (AS)
        self.advance() # DELIMITERS
        if self.current_char == 'K': return self.rw18()
        # DELIMITERS
        return self.error()

    def rw18(self): # On 'K' (ASK)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw19()
        # DELIMITERS
        return self.error()

    def rw19(self): 
        return Token("ASK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- AYE ---
    def rw20(self): # On 'Y' (AY)
        self.advance() 
        if self.current_char == 'E': return self.rw21()
        # DELIMITERS
        return self.error()

    def rw21(self): # On 'E' (AYE)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["BOOL_DELIM"]):
            return self.rw22()
        
        # DELIMITERS
        return self.error()

    def rw22(self): 
        return Token("AYE", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "B"
    # =========================================================================================
    def rw23(self): # On 'B'
        self.advance() 
        char = self.current_char
        if char == 'A': return self.rw24()
        if char == 'O': return self.rw28()
        # DELIMITERS
        return self.error()

    # --- BACK ---
    def rw24(self): # On 'A' (BA)
        self.advance() 
        if self.current_char == 'C': return self.rw25()
        # DELIMITERS
        return self.error()

    def rw25(self): # On 'C' (BAC)
        self.advance() 
        if self.current_char == 'K': return self.rw26()
        # DELIMITERS
        return self.error()

    def rw26(self): # On 'K' (BACK)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set(['(', '!'])
        if self._comp_delims(valid):
            return self.rw27()
        # DELIMITERS
        return self.error()

    def rw27(self): 
        return Token("BACK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- BOOL ---
    def rw28(self): # On 'O' (BO)
        self.advance() 
        if self.current_char == 'O': return self.rw29()
        # DELIMITERS
        return self.error()

    def rw29(self): # On 'O' (BOO)
        self.advance() 
        if self.current_char == 'L': return self.rw30()
        # DELIMITERS
        return self.error()

    def rw30(self): # On 'L' (BOOL)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw31()
        # DELIMITERS
        return self.error()

    def rw31(self): 
        return Token("BOOL", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "C"
    # =========================================================================================
    def rw32(self): # On 'C'
        self.advance() 
        char = self.current_char
        if char == 'H': return self.rw33()
        if char == 'O': return self.rw38()
        # DELIMITERS
        return self.error()

    # --- CHART ---
    def rw33(self): # On 'H' (CH)
        self.advance() 
        if self.current_char == 'A': return self.rw34()
        # DELIMITERS
        return self.error()

    def rw34(self): # On 'A' (CHA)
        self.advance() 
        if self.current_char == 'R': return self.rw35()
        # DELIMITERS
        return self.error()

    def rw35(self): # On 'R' (CHAR)
        self.advance() 
        if self.current_char == 'T': return self.rw36()
        # DELIMITERS
        return self.error()

    def rw36(self): # On 'T' (CHART)
        self.advance() 
        # DIAGRAM: whitespace, (
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw37()
        # DELIMITERS
        return self.error()

    def rw37(self): 
        return Token("CHART", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- COIN ---
    def rw38(self): # On 'O' (CO)
        self.advance() 
        char = self.current_char
        if char == 'I': return self.rw39()
        if char == 'U': return self.rw42()
        # DELIMITERS
        return self.error()

    def rw39(self): # On 'I' (COI)
        self.advance() 
        if self.current_char == 'N': return self.rw40()
        # DELIMITERS
        return self.error()

    def rw40(self): # On 'N' (COIN)
        self.advance() 
        # DIAGRAM: whitespace
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw41()
        # DELIMITERS
        return self.error()

    def rw41(self): 
        return Token("COIN", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- COURSE ---
    def rw42(self): # On 'U' (COU)
        self.advance() 
        if self.current_char == 'R': return self.rw43()
        # DELIMITERS
        return self.error()

    def rw43(self): # On 'R' (COUR)
        self.advance() 
        if self.current_char == 'S': return self.rw44()
        # DELIMITERS
        return self.error()

    def rw44(self): # On 'S' (COURS)
        self.advance() 
        if self.current_char == 'E': return self.rw45()
        # DELIMITERS
        return self.error()

    def rw45(self): # On 'E' (COURSE)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw46()
        # DELIMITERS
        return self.error()

    def rw46(self): 
        return Token("COURSE", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "D"
    # =========================================================================================
    def rw47(self): # On 'D'
        self.advance() 
        char = self.current_char
        if char == 'I': return self.rw48()
        if char == 'R': return self.rw52()
        # DELIMITERS
        return self.error()

    # --- DIME ---
    def rw48(self): # On 'I' (DI)
        self.advance() 
        if self.current_char == 'M': return self.rw49()
        # DELIMITERS
        return self.error()

    def rw49(self): # On 'M' (DIM)
        self.advance() 
        if self.current_char == 'E': return self.rw50()
        # DELIMITERS
        return self.error()

    def rw50(self): # On 'E' (DIME)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw51()
        # DELIMITERS
        return self.error()

    def rw51(self): 
        return Token("DIME", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- DROP / DROPLOOK ---
    def rw52(self): # On 'R' (DR)
        self.advance() 
        if self.current_char == 'O': return self.rw53()
        # DELIMITERS
        return self.error()

    def rw53(self): # On 'O' (DRO)
        self.advance() 
        if self.current_char == 'P': return self.rw54()
        # DELIMITERS
        return self.error()

    def rw54(self): # On 'P' (DROP)
        self.advance() 
        
        # Check for L (Branch to DROPLOOK)
        if self.current_char == 'L': return self.rw56()
        
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('[')
        if self._comp_delims(valid):
            return self.rw55()
        # DELIMITERS           
        return self.error()

    def rw55(self): 
        return Token("DROP", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw56(self): # On 'L' (DROPL)
        self.advance() 
        if self.current_char == 'O': return self.rw57()
        # DELIMITERS
        return self.error()

    def rw57(self): # On 'O' (DROPLO)
        self.advance() 
        if self.current_char == 'O': return self.rw58()
        # DELIMITERS
        return self.error()

    def rw58(self): # On 'O' (DROPLOO)
        self.advance() 
        if self.current_char == 'K': return self.rw59()
        # DELIMITERS
        return self.error()

    def rw59(self): # On 'K' (DROPLOOK)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw60()
        # DELIMITERS
        return self.error()

    def rw60(self): 
        return Token("DROPLOOK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "E"
    # =========================================================================================
    def rw61(self): # On 'E'
        self.advance() 
        if self.current_char == 'C': return self.rw62()
        # DELIMITERS
        return self.error()

    # --- ECHO ---
    def rw62(self): # On 'C' (EC)
        self.advance() 
        if self.current_char == 'H': return self.rw63()
        # DELIMITERS
        return self.error()

    def rw63(self): # On 'H' (ECH)
        self.advance() 
        if self.current_char == 'O': return self.rw64()
        # DELIMITERS
        return self.error()

    def rw64(self): # On 'O' (ECHO)
        self.advance()
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw65()
        # DELIMITERS
        return self.error()

    def rw65(self): 
        return Token("ECHO", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "H"
    # =========================================================================================
    def rw66(self): # On 'H'
        self.advance() 
        char = self.current_char
        if char == 'A': return self.rw67()
        if char == 'E': return self.rw71()
        if char == 'O': return self.rw76()
        # DELIMITERS
        self._report_char_error("", ["A", "E", "O"])
        return None

    # --- HAUL ---
    def rw67(self): # On 'A' (HA)
        self.advance() 
        if self.current_char == 'U': return self.rw68()
        # DELIMITERS
        return self.error()

    def rw68(self): # On 'U' (HAU)
        self.advance() 
        if self.current_char == 'L': return self.rw69()
        # DELIMITERS
        return self.error()

    def rw69(self): # On 'L' (HAUL)
        self.advance() 
        # DIAGRAM: whitespace, [
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('[')
        if self._comp_delims(valid):
            return self.rw70()
        # DELIMITERS
        return self.error()

    def rw70(self): 
        return Token("HAUL", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- HEAVE ---
    def rw71(self): # On 'E' (HE)
        self.advance() 
        if self.current_char == 'A': return self.rw72()
        # DELIMITERS
        return self.error()

    def rw72(self): # On 'A' (HEA)
        self.advance() 
        if self.current_char == 'V': return self.rw73()
        # DELIMITERS
        return self.error()

    def rw73(self): # On 'V' (HEAV)
        self.advance() 
        if self.current_char == 'E': return self.rw74()
        # DELIMITERS
        return self.error()

    def rw74(self): # On 'E' (HEAVE)
        self.advance() 
        # DIAGRAM: whitespace, (
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw75()
        # DELIMITERS
        return self.error()

    def rw75(self): 
        return Token("HEAVE", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- HOIST ---
    def rw76(self): # On 'O' (HO)
        self.advance() 
        if self.current_char == 'I': return self.rw77()
        # DELIMITERS
        return self.error()

    def rw77(self): # On 'I' (HOI)
        self.advance() 
        if self.current_char == 'S': return self.rw78()
        # DELIMITERS
        return self.error()

    def rw78(self): # On 'S' (HOIS)
        self.advance() 
        if self.current_char == 'T': return self.rw79()
        # DELIMITERS
        return self.error()

    def rw79(self): # On 'T' (HOIST)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw80()
        # DELIMITERS
        return self.error()

    def rw80(self): 
        return Token("HOIST", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "L"
    # =========================================================================================
    def rw81(self): # On 'L'
        self.advance() 
        char = self.current_char
        if char == 'A': return self.rw82()
        if char == 'O': return self.rw86()
        # DELIMITERS
        return self.error()

    # --- LAND ---
    def rw82(self): # On 'A' (LA)
        self.advance() 
        if self.current_char == 'N': return self.rw83()
        # DELIMITERS
        return self.error()

    def rw83(self): # On 'N' (LAN)
        self.advance() 
        if self.current_char == 'D': return self.rw84()
        # DELIMITERS
        return self.error()

    def rw84(self): # On 'D' (LAND)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('!')
        if self._comp_delims(valid):
            return self.rw85()
        # DELIMITERS
        return self.error()

    def rw85(self): 
        return Token("LAND", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- LOCKE / LOOK ---
    def rw86(self): # On 'O' (LO)
        self.advance() 
        char = self.current_char
        if char == 'C': return self.rw87()
        if char == 'O': return self.rw91()
        # DELIMITERS
        return self.error()

    def rw87(self): # On 'C' (LOC)
        self.advance() 
        if self.current_char == 'K': return self.rw88()
        # DELIMITERS
        return self.error()

    def rw88(self): # On 'K' (LOCK)
        self.advance() 
        if self.current_char == 'E': return self.rw89()
        # DELIMITERS
        return self.error()

    def rw89(self): # On 'E' (LOCKE)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw90()
        # DELIMITERS
        return self.error()

    def rw90(self): 
        return Token("LOCKE", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw91(self): # On 'O' (LOO)
        self.advance() 
        if self.current_char == 'K': return self.rw92()
        # DELIMITERS
        return self.error()

    def rw92(self): # On 'K' (LOOK)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw93()
        # DELIMITERS
        return self.error()

    def rw93(self): 
        return Token("LOOK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "M"
    # =========================================================================================
    def rw94(self): # On 'M'
        self.advance() 
        if self.current_char == 'A': return self.rw95()
        # DELIMITERS
        return self.error()

    # --- MAST ---
    def rw95(self): # On 'A' (MA)
        self.advance() 
        if self.current_char == 'S': return self.rw96()
        # DELIMITERS
        return self.error()

    def rw96(self): # On 'S' (MAS)
        self.advance() 
        if self.current_char == 'T': return self.rw97()
        # DELIMITERS
        return self.error()

    def rw97(self): # On 'T' (MAST)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw98()
        # DELIMITERS
        return self.error()

    def rw98(self): 
        return Token("MAST", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "N"
    # =========================================================================================
    def rw99(self): # On 'N'
        self.advance() 
        if self.current_char == 'A': return self.rw100()
        # DELIMITERS
        return self.error()

    # --- NAY ---
    def rw100(self): # On 'A' (NA)
        self.advance() 
        if self.current_char == 'Y': return self.rw101()
        # DELIMITERS
        return self.error()

    def rw101(self): # On 'Y' (NAY)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["BOOL_DELIM"]):
            return self.rw102()
        
        # DELIMITERS
        return self.error()

    def rw102(self): 
        return Token("NAY", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "P"
    # =========================================================================================
    def rw103(self): # On 'P'
        self.advance() 
        if self.current_char == 'A': return self.rw104()
        # DELIMITERS
        return self.error()

    # --- PARCH ---
    def rw104(self): # On 'A' (PA)
        self.advance() 
        if self.current_char == 'R': return self.rw105()
        # DELIMITERS
        return self.error()

    def rw105(self): # On 'R' (PAR)
        self.advance() 
        if self.current_char == 'C': return self.rw106()
        # DELIMITERS
        return self.error()

    def rw106(self): # On 'C' (PARC)
        self.advance() 
        if self.current_char == 'H': return self.rw107()
        # DELIMITERS
        return self.error()

    def rw107(self): # On 'H' (PARCH)
        self.advance() 
        # DIAGRAM: whitespace
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw108()
        # DELIMITERS
        return self.error()

    def rw108(self): 
        return Token("PARCH", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "S"
    # =========================================================================================
    def rw109(self): # On 'S'
        self.advance() 
        char = self.current_char
        if char == 'A': return self.rw110()
        if char == 'C': return self.rw114()
        # DELIMITERS
        return self.error()

    # --- SAIL ---
    def rw110(self): # On 'A' (SA)
        self.advance() 
        if self.current_char == 'I': return self.rw111()
        # DELIMITERS
        return self.error()

    def rw111(self): # On 'I' (SAI)
        self.advance() 
        if self.current_char == 'L': return self.rw112()
        # DELIMITERS
        return self.error()

    def rw112(self): # On 'L' (SAIL)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('!')
        if self._comp_delims(valid):
            return self.rw113()
        # DELIMITERS
        return self.error()

    def rw113(self): 
        return Token("SAIL", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- SCROLL ---
    def rw114(self): # On 'C' (SC)
        self.advance() 
        if self.current_char == 'R': return self.rw115()
        # DELIMITERS
        return self.error()

    def rw115(self): # On 'R' (SCR)
        self.advance() 
        if self.current_char == 'O': return self.rw116()
        # DELIMITERS
        return self.error()

    def rw116(self): # On 'O' (SCRO)
        self.advance() 
        if self.current_char == 'L': return self.rw117()
        # DELIMITERS
        return self.error()

    def rw117(self): # On 'L' (SCROL)
        self.advance() 
        if self.current_char == 'L': return self.rw118()
        # DELIMITERS
        return self.error()

    def rw118(self): # On 'L' (SCROLL)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw119()
        # DELIMITERS
        return self.error()

    def rw119(self): 
        return Token("SCROLL", self.current_token_text(), self.token_start_line, self.token_start_col)