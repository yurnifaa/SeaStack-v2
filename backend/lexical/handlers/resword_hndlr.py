from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters
import string

# =================================================================================================
# RESERVED WORDS TD: Reserved words state machine (i193 - i231)
# =================================================================================================

class ReservedWordHandler:

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
        err_token.expected = expected_list
        
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
        
        self._report_char_error("Invalid Reserved Word. Expected 'B', 'D', 'H', 'S', or 'Y'", ["B", "D", "H", "S", "Y"])
        return None

    def rw2(self): # On 'B' (AB)
        self.advance() 
        if self.current_char == 'Y': return self.rw3()
        self._report_char_error("Invalid Reserved Word. Expected 'Y'", ["Y"])
        return None

    def rw3(self): # On 'Y' (ABY)
        self.advance() 
        if self.current_char == 'S': return self.rw4()
        self._report_char_error("Invalid Reserved Word. Expected 'S'", ["S"])
        return None

    def rw4(self): # On 'S' (ABYS)
        self.advance() 
        if self.current_char == 'S': return self.rw5()
        self._report_char_error("Invalid Reserved Word. Expected 'S'", ["S"])
        return None
        
    def rw5(self): # On 'S' (ABYSS)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace():
            return self.rw6()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)", ["whitespace"])

    def rw6(self): 
        return Token("ABYSS", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw7(self): # On 'D' (AD)
        self.advance() 
        if self.current_char == 'R': return self.rw8()
        self._report_char_error("Invalid Reserved Word. Expected 'R'", ["R"])
        return None

    def rw8(self): # On 'R' (ADR)
        self.advance() 
        if self.current_char == 'I': return self.rw9()
        self._report_char_error("Invalid Reserved Word. Expected 'I'", ["I"])
        return None

    def rw9(self): # On 'I' (ADRI)
        self.advance() 
        if self.current_char == 'F': return self.rw10()
        self._report_char_error("Invalid Reserved Word. Expected 'F'", ["F"])
        return None

    def rw10(self): # On 'F' (ADRIF)
        self.advance() 
        if self.current_char == 'T': return self.rw11()
        self._report_char_error("Invalid Reserved Word. Expected 'T'", ["T"])
        return None

    def rw11(self): # On 'T' (ADRIFT)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace() or char == ':':
            return self.rw12()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or ':')", ["whitespace", ":"])

    def rw12(self): 
        return Token("ADRIFT", self.current_token_text(), self.token_start_line, self.token_start_col)
        
    def rw13(self): # On 'H' (AH)
        self.advance() 
        if self.current_char == 'O': return self.rw14()
        self._report_char_error("Invalid Reserved Word. Expected 'O'", ["O"])
        return None
    
    def rw14(self): # On 'O' (AHO)
        self.advance() 
        if self.current_char == 'Y': return self.rw15()
        self._report_char_error("Invalid Reserved Word. Expected 'Y'", ["Y"])
        return None

    def rw15(self): # On 'Y' (AHOY)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw16()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')", ["whitespace", "("])
        
    def rw16(self): 
        return Token("AHOY", self.current_token_text(), self.token_start_line, self.token_start_col)
        
    def rw17(self): # On 'S' (AS)
        self.advance() 
        if self.current_char == 'K': return self.rw18()
        self._report_char_error("Invalid Reserved Word. Expected 'K'", ["K"])
        return None
        
    def rw18(self): # On 'K' (ASK)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw19()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')", ["whitespace", "("])
        
    def rw19(self): 
        return Token("ASK", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw20(self): # On 'Y' (AY)
        self.advance() 
        if self.current_char == 'E': return self.rw21()
        self._report_char_error("Invalid Reserved Word. Expected 'E'", ["E"])
        return None

    def rw21(self): # On 'E' (AYE)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["BOOL_DELIM"]):
            return self.rw22()
        self._report_char_error("Invalid Reserved Word. Expected delimiter", ["whitespace", ")", "]", "&", "!", "=", ",", "|"])

    def rw22(self): 
        return Token("AYE", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "B": BACK, BOOL
    # =========================================================================================
    def rw23(self): # On 'B'
        self.advance() 
        char = self.current_char
        if char == 'A': return self.rw24()
        if char == 'O': return self.rw28()
        self._report_char_error("Invalid Reserved Word. Expected 'A' or 'O'", ["A", "O"])
        return None

    def rw24(self): # On 'A' (BA)
        self.advance() 
        if self.current_char == 'C': return self.rw25()
        self._report_char_error("Invalid Reserved Word. Expected 'C'", ["C"])
        return None

    def rw25(self): # On 'C' (BAC)
        self.advance() 
        if self.current_char == 'K': return self.rw26()
        self._report_char_error("Invalid Reserved Word. Expected 'K'", ["K"])
        return None

    def rw26(self): # On 'K' (BACK)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace() or char == '(' or char == '!':
            return self.rw27()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace, '(', or '!')", ["whitespace", "(", "!"])

    def rw27(self): 
        return Token("BACK", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw28(self): # On 'O' (BO)
        self.advance() 
        if self.current_char == 'O': return self.rw29()
        self._report_char_error("Invalid Reserved Word. Expected 'O'", ["O"])
        return None

    def rw29(self): # On 'O' (BOO)
        self.advance() 
        if self.current_char == 'L': return self.rw30()
        self._report_char_error("Invalid Reserved Word. Expected 'L'", ["L"])
        return None

    def rw30(self): # On 'L' (BOOL)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace():
            return self.rw31()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)", ["whitespace"])

    def rw31(self): 
        return Token("BOOL", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "C": CHART, COIN, COURSE
    # =========================================================================================
    def rw32(self): # On 'C'
        self.advance() 
        char = self.current_char
        if char == 'H': return self.rw33()
        if char == 'O': return self.rw38()
        self._report_char_error("Invalid Reserved Word. Expected 'H' or 'O'", ["H", "O"])
        return None

    def rw33(self): # On 'H' (CH)
        self.advance() 
        if self.current_char == 'A': return self.rw34()
        self._report_char_error("Invalid Reserved Word. Expected 'A'", ["A"])
        return None

    def rw34(self): # On 'A' (CHA)
        self.advance() 
        if self.current_char == 'R': return self.rw35()
        self._report_char_error("Invalid Reserved Word. Expected 'R'", ["R"])
        return None

    def rw35(self): # On 'R' (CHAR)
        self.advance() 
        if self.current_char == 'T': return self.rw36()
        self._report_char_error("Invalid Reserved Word. Expected 'T'", ["T"])
        return None

    def rw36(self): # On 'T' (CHART)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw37()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')", ["whitespace", "("])

    def rw37(self): 
        return Token("CHART", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw38(self): # On 'O' (CO)
        self.advance() 
        char = self.current_char
        if char == 'I': return self.rw39()
        if char == 'U': return self.rw42()
        self._report_char_error("Invalid Reserved Word. Expected 'I' or 'U'", ["I", "U"])
        return None

    def rw39(self): # On 'I' (COI)
        self.advance() 
        if self.current_char == 'N': return self.rw40()
        self._report_char_error("Invalid Reserved Word. Expected 'N'", ["N"])
        return None

    def rw40(self): # On 'N' (COIN)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace():
            return self.rw41()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)", ["whitespace"])

    def rw41(self): 
        return Token("COIN", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw42(self): # On 'U' (COU)
        self.advance() 
        if self.current_char == 'R': return self.rw43()
        self._report_char_error("Invalid Reserved Word. Expected 'R'", ["R"])
        return None

    def rw43(self): # On 'R' (COUR)
        self.advance() 
        if self.current_char == 'S': return self.rw44()
        self._report_char_error("Invalid Reserved Word. Expected 'S'", ["S"])
        return None

    def rw44(self): # On 'S' (COURS)
        self.advance() 
        if self.current_char == 'E': return self.rw45()
        self._report_char_error("Invalid Reserved Word. Expected 'E'", ["E"])
        return None

    def rw45(self): # On 'E' (COURSE)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace() or char == ':':
            return self.rw46()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or ':')", ["whitespace", ":"])

    def rw46(self): 
        return Token("COURSE", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "D": DIME, DROP, DROPLOOK
    # =========================================================================================
    def rw47(self): # On 'D'
        self.advance() 
        char = self.current_char
        if char == 'I': return self.rw48()
        if char == 'R': return self.rw52()
        self._report_char_error("Invalid Reserved Word. Expected 'I' or 'R'", ["I", "R"])
        return None

    def rw48(self): # On 'I' (DI)
        self.advance() 
        if self.current_char == 'M': return self.rw49()
        self._report_char_error("Invalid Reserved Word. Expected 'M'", ["M"])
        return None

    def rw49(self): # On 'M' (DIM)
        self.advance() 
        if self.current_char == 'E': return self.rw50()
        self._report_char_error("Invalid Reserved Word. Expected 'E'", ["E"])
        return None

    def rw50(self): # On 'E' (DIME)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace():
            return self.rw51()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)", ["whitespace"])

    def rw51(self): 
        return Token("DIME", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw52(self): # On 'R' (DR)
        self.advance() 
        if self.current_char == 'O': return self.rw53()
        self._report_char_error("Invalid Reserved Word. Expected 'O'", ["O"])
        return None

    def rw53(self): # On 'O' (DRO)
        self.advance() 
        if self.current_char == 'P': return self.rw54()
        self._report_char_error("Invalid Reserved Word. Expected 'P'", ["P"])
        return None

    def rw54(self): # On 'P' (DROP)
        self.advance() 
        if self.current_char == 'L': return self.rw56()
        
        char = self.current_char
        if char is None or char.isspace() or char == '[':
            return self.rw55()
        self._report_char_error("Invalid Reserved Word. Expected 'L' or delimiter (whitespace or '[')", ["L", "whitespace", "["])

    def rw55(self): 
        return Token("DROP", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw56(self): # On 'L' (DROPL)
        self.advance() 
        if self.current_char == 'O': return self.rw57()
        self._report_char_error("Invalid Reserved Word. Expected 'O'", ["O"])
        return None

    def rw57(self): # On 'O' (DROPLO)
        self.advance() 
        if self.current_char == 'O': return self.rw58()
        self._report_char_error("Invalid Reserved Word. Expected 'O'", ["O"])
        return None

    def rw58(self): # On 'O' (DROPLOO)
        self.advance() 
        if self.current_char == 'K': return self.rw59()
        self._report_char_error("Invalid Reserved Word. Expected 'K'", ["K"])
        return None

    def rw59(self): # On 'K' (DROPLOOK)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw60()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')", ["whitespace", "("])

    def rw60(self): 
        return Token("DROPLOOK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "E": ECHO
    # =========================================================================================
    def rw61(self): # On 'E'
        self.advance() 
        if self.current_char == 'C': return self.rw62()
        self._report_char_error("Invalid Reserved Word. Expected 'C'", ["C"])
        return None

    def rw62(self): # On 'C' (EC)
        self.advance() 
        if self.current_char == 'H': return self.rw63()
        self._report_char_error("Invalid Reserved Word. Expected 'H'", ["H"])
        return None

    def rw63(self): # On 'H' (ECH)
        self.advance() 
        if self.current_char == 'O': return self.rw64()
        self._report_char_error("Invalid Reserved Word. Expected 'O'", ["O"])
        return None

    def rw64(self): # On 'O' (ECHO)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw65()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')", ["whitespace", "("])

    def rw65(self): 
        return Token("ECHO", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "H": HAUL, HEAVE, HOIST
    # =========================================================================================
    def rw66(self): # On 'H'
        self.advance() 
        char = self.current_char
        if char == 'A': return self.rw67()
        if char == 'E': return self.rw71()
        if char == 'O': return self.rw76()
        self._report_char_error("Invalid Reserved Word. Expected 'A', 'E', or 'O'", ["A", "E", "O"])
        return None

    def rw67(self): # On 'A' (HA)
        self.advance() 
        if self.current_char == 'U': return self.rw68()
        self._report_char_error("Invalid Reserved Word. Expected 'U'", ["U"])
        return None

    def rw68(self): # On 'U' (HAU)
        self.advance() 
        if self.current_char == 'L': return self.rw69()
        self._report_char_error("Invalid Reserved Word. Expected 'L'", ["L"])
        return None

    def rw69(self): # On 'L' (HAUL)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace() or char == '[':
            return self.rw70()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '[')", ["whitespace", "["])

    def rw70(self): 
        return Token("HAUL", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw71(self): # On 'E' (HE)
        self.advance() 
        if self.current_char == 'A': return self.rw72()
        self._report_char_error("Invalid Reserved Word. Expected 'A'", ["A"])
        return None

    def rw72(self): # On 'A' (HEA)
        self.advance() 
        if self.current_char == 'V': return self.rw73()
        self._report_char_error("Invalid Reserved Word. Expected 'V'", ["V"])
        return None

    def rw73(self): # On 'V' (HEAV)
        self.advance() 
        if self.current_char == 'E': return self.rw74()
        self._report_char_error("Invalid Reserved Word. Expected 'E'", ["E"])
        return None

    def rw74(self): # On 'E' (HEAVE)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw75()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')", ["whitespace", "("])

    def rw75(self): 
        return Token("HEAVE", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw76(self): # On 'O' (HO)
        self.advance() 
        if self.current_char == 'I': return self.rw77()
        self._report_char_error("Invalid Reserved Word. Expected 'I'", ["I"])
        return None

    def rw77(self): # On 'I' (HOI)
        self.advance() 
        if self.current_char == 'S': return self.rw78()
        self._report_char_error("Invalid Reserved Word. Expected 'S'", ["S"])
        return None

    def rw78(self): # On 'S' (HOIS)
        self.advance() 
        if self.current_char == 'T': return self.rw79()
        self._report_char_error("Invalid Reserved Word. Expected 'T'", ["T"])
        return None

    def rw79(self): # On 'T' (HOIST)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw80()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')", ["whitespace", "("])

    def rw80(self): 
        return Token("HOIST", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "L": LAND, LOCKE, LOOK
    # =========================================================================================
    def rw81(self): # On 'L'
        self.advance() 
        char = self.current_char
        if char == 'A': return self.rw82()
        if char == 'O': return self.rw86()
        self._report_char_error("Invalid Reserved Word. Expected 'A' or 'O'", ["A", "O"])
        return None

    def rw82(self): # On 'A' (LA)
        self.advance() 
        if self.current_char == 'N': return self.rw83()
        self._report_char_error("Invalid Reserved Word. Expected 'N'", ["N"])
        return None

    def rw83(self): # On 'N' (LAN)
        self.advance() 
        if self.current_char == 'D': return self.rw84()
        self._report_char_error("Invalid Reserved Word. Expected 'D'", ["D"])
        return None

    def rw84(self): # On 'D' (LAND)
        self.advance() 
        char = self.current_char
        if char is None or char == '!':
            return self.rw85()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '!')", ["whitespace", "!"])

    def rw85(self): 
        return Token("LAND", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw86(self): # On 'O' (LO)
        self.advance() 
        char = self.current_char
        if char == 'C': return self.rw87()
        if char == 'O': return self.rw91()
        self._report_char_error("Invalid Reserved Word. Expected 'C' or 'O'", ["C", "O"])
        return None

    def rw87(self): # On 'C' (LOC)
        self.advance() 
        if self.current_char == 'K': return self.rw88()
        self._report_char_error("Invalid Reserved Word. Expected 'K'", ["K"])
        return None

    def rw88(self): # On 'K' (LOCK)
        self.advance() 
        if self.current_char == 'E': return self.rw89()
        self._report_char_error("Invalid Reserved Word. Expected 'E'", ["E"])
        return None

    def rw89(self): # On 'E' (LOCKE)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace():
            return self.rw90()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)", ["whitespace"])

    def rw90(self): 
        return Token("LOCKE", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw91(self): # On 'O' (LOO)
        self.advance() 
        if self.current_char == 'K': return self.rw92()
        self._report_char_error("Invalid Reserved Word. Expected 'K'", ["K"])
        return None

    def rw92(self): # On 'K' (LOOK)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace() or char == '(':
            return self.rw93()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '(')", ["whitespace", "("])

    def rw93(self): 
        return Token("LOOK", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "M": MAST
    # =========================================================================================
    def rw94(self): # On 'M'
        self.advance() 
        if self.current_char == 'A': return self.rw95()
        self._report_char_error("Invalid Reserved Word. Expected 'A'", ["A"])
        return None

    def rw95(self): # On 'A' (MA)
        self.advance() 
        if self.current_char == 'S': return self.rw96()
        self._report_char_error("Invalid Reserved Word. Expected 'S'", ["S"])
        return None

    def rw96(self): # On 'S' (MAS)
        self.advance() 
        if self.current_char == 'T': return self.rw97()
        self._report_char_error("Invalid Reserved Word. Expected 'T'", ["T"])
        return None

    def rw97(self): # On 'T' (MAST)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace():
            return self.rw98()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)", ["whitespace"])

    def rw98(self): 
        return Token("MAST", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "N": NAY
    # =========================================================================================
    def rw99(self): # On 'N'
        self.advance() 
        if self.current_char == 'A': return self.rw100()
        self._report_char_error("Invalid Reserved Word. Expected 'A'", ["A"])
        return None

    def rw100(self): # On 'A' (NA)
        self.advance() 
        if self.current_char == 'Y': return self.rw101()
        self._report_char_error("Invalid Reserved Word. Expected 'Y'", ["Y"])
        return None

    def rw101(self): # On 'Y' (NAY)
        self.advance() 
        if self._comp_delims(Delimiters._get_delimiters()["BOOL_DELIM"]):
            return self.rw102()
        self._report_char_error("Invalid Reserved Word. Expected delimiter", ["whitespace", ")", "]", "&", "!", "=", ",", "|"])

    def rw102(self): 
        return Token("NAY", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "P": PARCH
    # =========================================================================================
    def rw103(self): # On 'P'
        self.advance() 
        if self.current_char == 'A': return self.rw104()
        self._report_char_error("Invalid Reserved Word. Expected 'A'", ["A"])
        return None

    def rw104(self): # On 'A' (PA)
        self.advance() 
        if self.current_char == 'R': return self.rw105()
        self._report_char_error("Invalid Reserved Word. Expected 'R'", ["R"])
        return None

    def rw105(self): # On 'R' (PAR)
        self.advance() 
        if self.current_char == 'C': return self.rw106()
        self._report_char_error("Invalid Reserved Word. Expected 'C'", ["C"])
        return None

    def rw106(self): # On 'C' (PARC)
        self.advance() 
        if self.current_char == 'H': return self.rw107()
        self._report_char_error("Invalid Reserved Word. Expected 'H'", ["H"])
        return None

    def rw107(self): # On 'H' (PARCH)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace():
            return self.rw108()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)", ["whitespace"])

    def rw108(self): 
        return Token("PARCH", self.current_token_text(), self.token_start_line, self.token_start_col)

    # =========================================================================================
    # RESERVED WORDS "S": SAIL, SCROLL
    # =========================================================================================
    def rw109(self): # On 'S'
        self.advance() 
        char = self.current_char
        if char == 'A': return self.rw110()
        if char == 'C': return self.rw114()
        self._report_char_error("Invalid Reserved Word. Expected 'A' or 'C'", ["A", "C"])
        return None

    def rw110(self): # On 'A' (SA)
        self.advance() 
        if self.current_char == 'I': return self.rw111()
        self._report_char_error("Invalid Reserved Word. Expected 'I'", ["I"])
        return None

    def rw111(self): # On 'I' (SAI)
        self.advance() 
        if self.current_char == 'L': return self.rw112()
        self._report_char_error("Invalid Reserved Word. Expected 'L'", ["L"])
        return None

    def rw112(self): # On 'L' (SAIL)
        self.advance() 
        char = self.current_char
        if char is None or char == '!':
            return self.rw113()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace or '!')", ["whitespace", "!"])

    def rw113(self): 
        return Token("SAIL", self.current_token_text(), self.token_start_line, self.token_start_col)

    def rw114(self): # On 'C' (SC)
        self.advance() 
        if self.current_char == 'R': return self.rw115()
        self._report_char_error("Invalid Reserved Word. Expected 'R'", ["R"])
        return None

    def rw115(self): # On 'R' (SCR)
        self.advance() 
        if self.current_char == 'O': return self.rw116()
        self._report_char_error("Invalid Reserved Word. Expected 'O'", ["O"])
        return None

    def rw116(self): # On 'O' (SCRO)
        self.advance() 
        if self.current_char == 'L': return self.rw117()
        self._report_char_error("Invalid Reserved Word. Expected 'L'", ["L"])
        return None

    def rw117(self): # On 'L' (SCROL)
        self.advance() 
        if self.current_char == 'L': return self.rw118()
        self._report_char_error("Invalid Reserved Word. Expected 'L'", ["L"])
        return None

    def rw118(self): # On 'L' (SCROLL)
        self.advance() 
        char = self.current_char
        if char is None or char.isspace():
            return self.rw119()
        self._report_char_error("Invalid Reserved Word. Expected delimiter (whitespace)", ["whitespace"])

    def rw119(self): 
        return Token("SCROLL", self.current_token_text(), self.token_start_line, self.token_start_col)