# lexer_handlers/resword_handler.py
from backend.lexical.token import Token
from backend.lexical.handlers.delimiters import Delimiters

# =================================================================================================
# RESERVED WORDS TD: Reserved words state machine (rw0 - rw119)
# =================================================================================================

class ReservedWords:

    # =========================================================================================
    # HELPER: Sanitize Delimiters for Display
    # Replaces invisible chars ('\n', '\t', etc.) with the word "whitespace"
    # =========================================================================================
    def _sanitize_delims(self, delim_set):
        # Ensure we are working with a list
        delims = list(delim_set) if isinstance(delim_set, set) else delim_set
        cleaned_list = []
        has_whitespace = False
        
        for d in delims:
            # Check for invisible whitespace characters
            if d in [' ', '\t', '\n', '\r', '\v', '\f']:
                has_whitespace = True
            # Check if the string "whitespace" was passed manually
            elif d == "whitespace":
                has_whitespace = True
            else:
                cleaned_list.append(d)
        
        if has_whitespace:
            cleaned_list.append("whitespace")
            
        # Remove duplicates (in case both ' ' and "whitespace" were present)
        cleaned_list = list(set(cleaned_list))
        
        # Sort for clean UI output
        cleaned_list.sort(key=str)
        return cleaned_list

    # =========================================================================================
    # Error Reporting Helper
    # =========================================================================================
    def _report_char_error(self, message, expected_list, lex_txt=None):
        error_text = lex_txt if lex_txt else self.current_token_text()
        
        if not error_text and self.current_char:
            error_text = self.current_char

        err_token = Token(
            "ERROR",
            error_text, 
            self.line,
            self.col - 1,
            message 
        )
        
        # --- SANITIZE BEFORE ATTACHING ---
        err_token.expected = self._sanitize_delims(expected_list)
        
        self.errors.append(err_token)        
        return None

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
        self._report_char_error(
            "Invalid Character. Expected start of Reserved Word.", 
            ["A", "B", "C", "D", "E", "H", "L", "M", "N", "P", "S"], 
            err_char
        )
        return None
    
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
        
        # DELIMITERS
        self._report_char_error("", ["B", "D", "H", "S", "Y"])
        return None

    # --- ABYSS ---
    def rw2(self): # On 'B' (AB)
        self.advance() 
        if self.current_char == 'Y': return self.rw3()
        # DELIMITERS
        self._report_char_error("", ["Y"])
        return None

    def rw3(self): # On 'Y' (ABY)
        self.advance() 
        if self.current_char == 'S': return self.rw4()
        # DELIMITERS
        self._report_char_error("", ["S"])
        return None

    def rw4(self): # On 'S' (ABYS)
        self.advance() 
        if self.current_char == 'S': return self.rw5()
        # DELIMITERS
        self._report_char_error("", ["S"])
        return None
        
    def rw5(self): # On 'S' (ABYSS)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw6()
        # DELIMITERS
        self._report_char_error("", ["whitespace"])

    def rw6(self): 
        return Token("ABYSS", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- ADRIFT ---
    def rw7(self): # On 'D' (AD)
        self.advance() 
        if self.current_char == 'R': return self.rw8()
        # DELIMITERS
        self._report_char_error("", ["R"])
        return None

    def rw8(self): # On 'R' (ADR)
        self.advance() 
        if self.current_char == 'I': return self.rw9()
        # DELIMITERS
        self._report_char_error("", ["I"])
        return None

    def rw9(self): # On 'I' (ADRI)
        self.advance() 
        if self.current_char == 'F': return self.rw10()
        # DELIMITERS
        self._report_char_error("", ["F"])
        return None

    def rw10(self): # On 'F' (ADRIF)
        self.advance() 
        if self.current_char == 'T': return self.rw11()
        # DELIMITERS
        self._report_char_error("", ["T"])
        return None

    def rw11(self): # On 'T' (ADRIFT)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set(':')
        if self._comp_delims(valid):
            return self.rw12()
        # DELIMITERS
        self._report_char_error("", ["whitespace", ":"])

    def rw12(self): 
        return Token("ADRIFT", self.current_token_text(), self.token_start_line, self.token_start_col)
        
    # --- AHOY ---
    def rw13(self): # On 'H' (AH)
        self.advance() 
        if self.current_char == 'O': return self.rw14()
        # DELIMITERS
        self._report_char_error("", ["O"])
        return None
    
    def rw14(self): # On 'O' (AHO)
        self.advance() 
        if self.current_char == 'Y': return self.rw15()
        # DELIMITERS
        self._report_char_error("", ["Y"])
        return None

    def rw15(self): # On 'Y' (AHOY)
        self.advance() 
        if self.current_char == '(': return self.rw16()
        # DELIMITERS
        self._report_char_error("", ["("])
        
    def rw16(self): 
        return Token("AHOY", self.current_token_text(), self.token_start_line, self.token_start_col)
        
    # --- ASK ---
    def rw17(self): # On 'S' (AS)
        self.advance() # DELIMITERS
        if self.current_char == 'K': return self.rw18()
        # DELIMITERS
        self._report_char_error("", ["K"])
        return None
        
    def rw18(self): # On 'K' (ASK)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw19()
        # DELIMITERS
        self._report_char_error("", ["whitespace", "("])
        
    def rw19(self): 
        return Token("ASK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- AYE ---
    def rw20(self): # On 'Y' (AY)
        self.advance() 
        if self.current_char == 'E': return self.rw21()
        # DELIMITERS
        self._report_char_error("", ["E"])
        return None

    def rw21(self): # On 'E' (AYE)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["BOOL_DELIM"]):
            return self.rw22()
        
        # DELIMITERS
        bool_delims = list(Delimiters._get_delimiters()["BOOL_DELIM"])
        self._report_char_error("", bool_delims)

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
        self._report_char_error("", ["A", "O"])
        return None

    # --- BACK ---
    def rw24(self): # On 'A' (BA)
        self.advance() 
        if self.current_char == 'C': return self.rw25()
        # DELIMITERS
        self._report_char_error("", ["C"])
        return None

    def rw25(self): # On 'C' (BAC)
        self.advance() 
        if self.current_char == 'K': return self.rw26()
        # DELIMITERS
        self._report_char_error("", ["K"])
        return None

    def rw26(self): # On 'K' (BACK)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set(['(', '!'])
        if self._comp_delims(valid):
            return self.rw27()
        # DELIMITERS
        self._report_char_error("", ["whitespace", "(", "!"])

    def rw27(self): 
        return Token("BACK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- BOOL ---
    def rw28(self): # On 'O' (BO)
        self.advance() 
        if self.current_char == 'O': return self.rw29()
        # DELIMITERS
        self._report_char_error("", ["O"])
        return None

    def rw29(self): # On 'O' (BOO)
        self.advance() 
        if self.current_char == 'L': return self.rw30()
        # DELIMITERS
        self._report_char_error("", ["L"])
        return None

    def rw30(self): # On 'L' (BOOL)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw31()
        # DELIMITERS
        self._report_char_error("", ["whitespace"])

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
        self._report_char_error("", ["H", "O"])
        return None

    # --- CHART ---
    def rw33(self): # On 'H' (CH)
        self.advance() 
        if self.current_char == 'A': return self.rw34()
        # DELIMITERS
        self._report_char_error("", ["A"])
        return None

    def rw34(self): # On 'A' (CHA)
        self.advance() 
        if self.current_char == 'R': return self.rw35()
        # DELIMITERS
        self._report_char_error("", ["R"])
        return None

    def rw35(self): # On 'R' (CHAR)
        self.advance() 
        if self.current_char == 'T': return self.rw36()
        # DELIMITERS
        self._report_char_error("", ["T"])
        return None

    def rw36(self): # On 'T' (CHART)
        self.advance() 
        # DIAGRAM: whitespace, (
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw37()
        # DELIMITERS
        self._report_char_error("", ["whitespace", "("])

    def rw37(self): 
        return Token("CHART", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- COIN ---
    def rw38(self): # On 'O' (CO)
        self.advance() 
        char = self.current_char
        if char == 'I': return self.rw39()
        if char == 'U': return self.rw42()
        # DELIMITERS
        self._report_char_error("", ["I", "U"])
        return None

    def rw39(self): # On 'I' (COI)
        self.advance() 
        if self.current_char == 'N': return self.rw40()
        # DELIMITERS
        self._report_char_error("", ["N"])
        return None

    def rw40(self): # On 'N' (COIN)
        self.advance() 
        # DIAGRAM: whitespace
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw41()
        # DELIMITERS
        self._report_char_error("", ["whitespace"])

    def rw41(self): 
        return Token("COIN", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- COURSE ---
    def rw42(self): # On 'U' (COU)
        self.advance() 
        if self.current_char == 'R': return self.rw43()
        # DELIMITERS
        self._report_char_error("", ["R"])
        return None

    def rw43(self): # On 'R' (COUR)
        self.advance() 
        if self.current_char == 'S': return self.rw44()
        # DELIMITERS
        self._report_char_error("", ["S"])
        return None

    def rw44(self): # On 'S' (COURS)
        self.advance() 
        if self.current_char == 'E': return self.rw45()
        # DELIMITERS
        self._report_char_error("", ["E"])
        return None

    def rw45(self): # On 'E' (COURSE)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw46()
        # DELIMITERS
        self._report_char_error("", ["whitespace"])

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
        self._report_char_error("", ["I", "R"])
        return None

    # --- DIME ---
    def rw48(self): # On 'I' (DI)
        self.advance() 
        if self.current_char == 'M': return self.rw49()
        # DELIMITERS
        self._report_char_error("", ["M"])
        return None

    def rw49(self): # On 'M' (DIM)
        self.advance() 
        if self.current_char == 'E': return self.rw50()
        # DELIMITERS
        self._report_char_error("", ["E"])
        return None

    def rw50(self): # On 'E' (DIME)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw51()
        # DELIMITERS
        self._report_char_error("", ["whitespace"])

    def rw51(self): 
        return Token("DIME", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- DROP / DROPLOOK ---
    def rw52(self): # On 'R' (DR)
        self.advance() 
        if self.current_char == 'O': return self.rw53()
        # DELIMITERS
        self._report_char_error("", ["O"])
        return None

    def rw53(self): # On 'O' (DRO)
        self.advance() 
        if self.current_char == 'P': return self.rw54()
        # DELIMITERS
        self._report_char_error("", ["P"])
        return None

    def rw54(self): # On 'P' (DROP)
        self.advance() 
        
        # Check for L (Branch to DROPLOOK)
        if self.current_char == 'L': return self.rw56()
        
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('[')
        if self._comp_delims(valid):
            return self.rw55()
        # DELIMITERS           
        self._report_char_error("", ["L", "whitespace", "["])

    def rw55(self): 
        return Token("DROP", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw56(self): # On 'L' (DROPL)
        self.advance() 
        if self.current_char == 'O': return self.rw57()
        # DELIMITERS
        self._report_char_error("", ["O"])
        return None

    def rw57(self): # On 'O' (DROPLO)
        self.advance() 
        if self.current_char == 'O': return self.rw58()
        # DELIMITERS
        self._report_char_error("", ["O"])
        return None

    def rw58(self): # On 'O' (DROPLOO)
        self.advance() 
        if self.current_char == 'K': return self.rw59()
        # DELIMITERS
        self._report_char_error("", ["K"])
        return None

    def rw59(self): # On 'K' (DROPLOOK)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw60()
        # DELIMITERS
        self._report_char_error("", ["whitespace", "("])

    def rw60(self): 
        return Token("DROPLOOK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "E"
    # =========================================================================================
    def rw61(self): # On 'E'
        self.advance() 
        if self.current_char == 'C': return self.rw62()
        # DELIMITERS
        self._report_char_error("", ["C"])
        return None

    # --- ECHO ---
    def rw62(self): # On 'C' (EC)
        self.advance() 
        if self.current_char == 'H': return self.rw63()
        # DELIMITERS
        self._report_char_error("", ["H"])
        return None

    def rw63(self): # On 'H' (ECH)
        self.advance() 
        if self.current_char == 'O': return self.rw64()
        # DELIMITERS
        self._report_char_error("", ["O"])
        return None

    def rw64(self): # On 'O' (ECHO)
        self.advance()
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw65()
        # DELIMITERS
        self._report_char_error("", ["whitespace", "("])

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
        self._report_char_error("", ["U"])
        return None

    def rw68(self): # On 'U' (HAU)
        self.advance() 
        if self.current_char == 'L': return self.rw69()
        # DELIMITERS
        self._report_char_error("", ["L"])
        return None

    def rw69(self): # On 'L' (HAUL)
        self.advance() 
        # DIAGRAM: whitespace, [
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('[')
        if self._comp_delims(valid):
            return self.rw70()
        # DELIMITERS
        self._report_char_error("", ["whitespace", "["])

    def rw70(self): 
        return Token("HAUL", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- HEAVE ---
    def rw71(self): # On 'E' (HE)
        self.advance() 
        if self.current_char == 'A': return self.rw72()
        # DELIMITERS
        self._report_char_error("", ["A"])
        return None

    def rw72(self): # On 'A' (HEA)
        self.advance() 
        if self.current_char == 'V': return self.rw73()
        # DELIMITERS
        self._report_char_error("", ["V"])
        return None

    def rw73(self): # On 'V' (HEAV)
        self.advance() 
        if self.current_char == 'E': return self.rw74()
        # DELIMITERS
        self._report_char_error("", ["E"])
        return None

    def rw74(self): # On 'E' (HEAVE)
        self.advance() 
        # DIAGRAM: whitespace, (
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw75()
        # DELIMITERS
        self._report_char_error("", ["whitespace", "("])

    def rw75(self): 
        return Token("HEAVE", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- HOIST ---
    def rw76(self): # On 'O' (HO)
        self.advance() 
        if self.current_char == 'I': return self.rw77()
        # DELIMITERS
        self._report_char_error("", ["I"])
        return None

    def rw77(self): # On 'I' (HOI)
        self.advance() 
        if self.current_char == 'S': return self.rw78()
        # DELIMITERS
        self._report_char_error("", ["S"])
        return None

    def rw78(self): # On 'S' (HOIS)
        self.advance() 
        if self.current_char == 'T': return self.rw79()
        # DELIMITERS
        self._report_char_error("", ["T"])
        return None

    def rw79(self): # On 'T' (HOIST)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw80()
        # DELIMITERS
        self._report_char_error("", ["whitespace", "("])

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
        self._report_char_error("", ["A", "O"])
        return None

    # --- LAND ---
    def rw82(self): # On 'A' (LA)
        self.advance() 
        if self.current_char == 'N': return self.rw83()
        # DELIMITERS
        self._report_char_error("", ["N"])
        return None

    def rw83(self): # On 'N' (LAN)
        self.advance() 
        if self.current_char == 'D': return self.rw84()
        # DELIMITERS
        self._report_char_error("", ["D"])
        return None

    def rw84(self): # On 'D' (LAND)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('!')
        if self._comp_delims(valid):
            return self.rw85()
        # DELIMITERS
        self._report_char_error("", ["whitespace", "!"])

    def rw85(self): 
        return Token("LAND", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- LOCKE / LOOK ---
    def rw86(self): # On 'O' (LO)
        self.advance() 
        char = self.current_char
        if char == 'C': return self.rw87()
        if char == 'O': return self.rw91()
        # DELIMITERS
        self._report_char_error("", ["C", "O"])
        return None

    def rw87(self): # On 'C' (LOC)
        self.advance() 
        if self.current_char == 'K': return self.rw88()
        # DELIMITERS
        self._report_char_error("", ["K"])
        return None

    def rw88(self): # On 'K' (LOCK)
        self.advance() 
        if self.current_char == 'E': return self.rw89()
        # DELIMITERS
        self._report_char_error("", ["E"])
        return None

    def rw89(self): # On 'E' (LOCKE)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw90()
        # DELIMITERS
        self._report_char_error("", ["whitespace"])

    def rw90(self): 
        return Token("LOCKE", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw91(self): # On 'O' (LOO)
        self.advance() 
        if self.current_char == 'K': return self.rw92()
        # DELIMITERS
        self._report_char_error("", ["K"])
        return None

    def rw92(self): # On 'K' (LOOK)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('(')
        if self._comp_delims(valid):
            return self.rw93()
        # DELIMITERS
        self._report_char_error("", ["whitespace", "("])

    def rw93(self): 
        return Token("LOOK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "M"
    # =========================================================================================
    def rw94(self): # On 'M'
        self.advance() 
        if self.current_char == 'A': return self.rw95()
        # DELIMITERS
        self._report_char_error("", ["A"])
        return None

    # --- MAST ---
    def rw95(self): # On 'A' (MA)
        self.advance() 
        if self.current_char == 'S': return self.rw96()
        # DELIMITERS
        self._report_char_error("", ["S"])
        return None

    def rw96(self): # On 'S' (MAS)
        self.advance() 
        if self.current_char == 'T': return self.rw97()
        # DELIMITERS
        self._report_char_error("", ["T"])
        return None

    def rw97(self): # On 'T' (MAST)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw98()
        # DELIMITERS
        self._report_char_error("", ["whitespace"])

    def rw98(self): 
        return Token("MAST", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "N"
    # =========================================================================================
    def rw99(self): # On 'N'
        self.advance() 
        if self.current_char == 'A': return self.rw100()
        # DELIMITERS
        self._report_char_error("", ["A"])
        return None

    # --- NAY ---
    def rw100(self): # On 'A' (NA)
        self.advance() 
        if self.current_char == 'Y': return self.rw101()
        # DELIMITERS
        self._report_char_error("", ["Y"])
        return None

    def rw101(self): # On 'Y' (NAY)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["BOOL_DELIM"]):
            return self.rw102()
        
        bool_delims = list(Delimiters._get_delimiters()["BOOL_DELIM"])
        # DELIMITERS
        self._report_char_error("", bool_delims)

    def rw102(self): 
        return Token("NAY", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "P"
    # =========================================================================================
    def rw103(self): # On 'P'
        self.advance() 
        if self.current_char == 'A': return self.rw104()
        # DELIMITERS
        self._report_char_error("", ["A"])
        return None

    # --- PARCH ---
    def rw104(self): # On 'A' (PA)
        self.advance() 
        if self.current_char == 'R': return self.rw105()
        # DELIMITERS
        self._report_char_error("", ["R"])
        return None

    def rw105(self): # On 'R' (PAR)
        self.advance() 
        if self.current_char == 'C': return self.rw106()
        # DELIMITERS
        self._report_char_error("", ["C"])
        return None

    def rw106(self): # On 'C' (PARC)
        self.advance() 
        if self.current_char == 'H': return self.rw107()
        # DELIMITERS
        self._report_char_error("", ["H"])
        return None

    def rw107(self): # On 'H' (PARCH)
        self.advance() 
        # DIAGRAM: whitespace
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw108()
        # DELIMITERS
        self._report_char_error("", ["whitespace"])

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
        self._report_char_error("", ["A", "C"])
        return None

    # --- SAIL ---
    def rw110(self): # On 'A' (SA)
        self.advance() 
        if self.current_char == 'I': return self.rw111()
        # DELIMITERS
        self._report_char_error("", ["I"])
        return None

    def rw111(self): # On 'I' (SAI)
        self.advance() 
        if self.current_char == 'L': return self.rw112()
        # DELIMITERS
        self._report_char_error("", ["L"])
        return None

    def rw112(self): # On 'L' (SAIL)
        self.advance() 
        valid = Delimiters._get_delimiters()["WHITESPACE"] | set('!')
        if self._comp_delims(valid):
            return self.rw113()
        # DELIMITERS
        self._report_char_error("", ["whitespace", "!"])

    def rw113(self): 
        return Token("SAIL", self.current_token_text(), self.token_start_line, self.token_start_col)

    # --- SCROLL ---
    def rw114(self): # On 'C' (SC)
        self.advance() 
        if self.current_char == 'R': return self.rw115()
        # DELIMITERS
        self._report_char_error("", ["R"])
        return None

    def rw115(self): # On 'R' (SCR)
        self.advance() 
        if self.current_char == 'O': return self.rw116()
        # DELIMITERS
        self._report_char_error("", ["O"])
        return None

    def rw116(self): # On 'O' (SCRO)
        self.advance() 
        if self.current_char == 'L': return self.rw117()
        # DELIMITERS
        self._report_char_error("", ["L"])
        return None

    def rw117(self): # On 'L' (SCROL)
        self.advance() 
        if self.current_char == 'L': return self.rw118()
        # DELIMITERS
        self._report_char_error("", ["L"])
        return None

    def rw118(self): # On 'L' (SCROLL)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["WHITESPACE"]):
            return self.rw119()
        # DELIMITERS
        self._report_char_error("", ["whitespace"])

    def rw119(self): 
        return Token("SCROLL", self.current_token_text(), self.token_start_line, self.token_start_col)