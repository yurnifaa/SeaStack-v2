from backend.lexical.token import Token
from backend.lexical.handlers.delimiters import Delimiters

# =================================================================================================
# RESERVED WORDS: must be uppercase letter only
# =================================================================================================

class ReservedWords:  

    # =======================
    # RESERVED WORDS HELPERS
    # =======================

    # check char if valid as rw
    def check_rw(self, char, next_state):
        self.advance()
        if self.current_char == char: return next_state()
        return self.error()

    # check delimeter if valid
    def check_rwdelim(self, valid_delims, next_state):
        self.advance()
        char = self.current_char
        if char in valid_delims or char is None: 
            return next_state()
        return self.error()

    # finalize reserved word token
    def finalize_rw(self, token_type):
        return Token(token_type, self.current_token_text(), self.token_start_line, self.token_start_col)
    

    # =======================
    # RESERVED WORDS "A"
    # =======================

    def rw1(self): 
        self.advance()
        char = self.current_char

        if char == 'B': return self.rw2()
        if char == 'D': return self.rw7()
        if char == 'H': return self.rw13()
        if char == 'S': return self.rw17()
        if char == 'Y': return self.rw20()

        return self.error()

    # ABYSS
    def rw2(self): return self.check_rw('Y', self.rw3)
    def rw3(self): return self.check_rw('S', self.rw4)
    def rw4(self): return self.check_rw('S', self.rw5)
    def rw5(self): return self.check_rwdelim(Delimiters.delims()["WHITESPACE"], self.rw6)
    def rw6(self): return self.finalize_rw("ABYSS")

    # ADRIFT
    def rw7(self): return self.check_rw('R', self.rw8)
    def rw8(self): return self.check_rw('I', self.rw9)
    def rw9(self): return self.check_rw('F', self.rw10)
    def rw10(self): return self.check_rw('T', self.rw11)
    def rw11(self):
        valid = Delimiters.delims()["WHITESPACE"] | set(':')
        return self.check_rwdelim(valid, self.rw12)
    def rw12(self): return self.finalize_rw("ADRIFT")

    # AHOY 
    def rw13(self): return self.check_rw('O', self.rw14)
    def rw14(self): return self.check_rw('Y', self.rw15)
    def rw15(self): return self.check_rw('(', self.rw16)
    def rw16(self): return self.finalize_rw("AHOY")
 
    # ASK
    def rw17(self): return self.check_rw('K', self.rw18)
    def rw18(self): return self.check_rw('(', self.rw19)
    def rw19(self): return self.finalize_rw("ASK")

    # AYE
    def rw20(self): return self.check_rw('E', self.rw21)
    def rw21(self): return self.check_rwdelim(Delimiters.delims()["BOOL_DELIM"], self.rw22)
    def rw22(self): return self.finalize_rw("AYE")


    # =======================
    # RESERVED WORDS "B"
    # =======================

    def rw23(self): 
        self.advance() 
        char = self.current_char

        if char == 'A': return self.rw24()
        if char == 'O': return self.rw28()
        
        return self.error()

    # BACK
    def rw24(self): return self.check_rw('C', self.rw25)
    def rw25(self): return self.check_rw('K', self.rw26)
    def rw26(self):
        valid = Delimiters.delims()["WHITESPACE"] | set("(!")
        return self.check_rwdelim(valid, self.rw27)
    def rw27(self): return self.finalize_rw("BACK")

    # BOOL
    def rw28(self): return self.check_rw('O', self.rw29)
    def rw29(self): return self.check_rw('L', self.rw30)
    def rw30(self): return self.check_rwdelim(Delimiters.delims()["WHITESPACE"], self.rw31)
    def rw31(self): return self.finalize_rw("BOOL")


    # =======================
    # RESERVED WORDS "C"
    # =======================

    def rw32(self): 
        self.advance() 
        char = self.current_char

        if char == 'H': return self.rw33()
        if char == 'O': return self.rw38()
        
        return self.error()

    # CHART
    def rw33(self): return self.check_rw('A', self.rw34)
    def rw34(self): return self.check_rw('R', self.rw35)
    def rw35(self): return self.check_rw('T', self.rw36)
    def rw36(self):
        valid = Delimiters.delims()["WHITESPACE"] | set('(')
        return self.check_rwdelim(valid, self.rw37)
    def rw37(self): return self.finalize_rw("CHART")

    # COIN/COURSE
    def rw38(self): 
        self.advance() 
        char = self.current_char

        if char == 'I': return self.rw39()
        if char == 'U': return self.rw42()
        
        return self.error()
    
    # COIN
    def rw39(self): return self.check_rw('N', self.rw40)
    def rw40(self): return self.check_rwdelim(Delimiters.delims()["WHITESPACE"], self.rw41)
    def rw41(self): return self.finalize_rw("COIN")

    # COURSE 
    def rw42(self): return self.check_rw('R', self.rw43)
    def rw43(self): return self.check_rw('S', self.rw44)
    def rw44(self): return self.check_rw('E', self.rw45)
    def rw45(self): return self.check_rwdelim(Delimiters.delims()["WHITESPACE"], self.rw46)
    def rw46(self): return self.finalize_rw("COURSE")


    # =======================
    # RESERVED WORDS "D"
    # =======================

    def rw47(self): 
        self.advance() 
        char = self.current_char

        if char == 'I': return self.rw48()
        if char == 'R': return self.rw52()
        
        return self.error()

    # DIME
    def rw48(self): return self.check_rw('M', self.rw49)
    def rw49(self): return self.check_rw('E', self.rw50)
    def rw50(self): return self.check_rwdelim(Delimiters.delims()["WHITESPACE"], self.rw51)
    def rw51(self): return self.finalize_rw("DIME")

    # DROP
    def rw52(self): return self.check_rw('O', self.rw53)
    def rw53(self): return self.check_rw('P', self.rw54)
    def rw54(self): 
        self.advance() 
        char = self.current_char

        if char == 'L': return self.rw56()

        valid = Delimiters.delims()["WHITESPACE"] | set('[')
        if self._comp_delims(valid):
            return self.rw55()    
        return self.error()
    def rw55(self): return self.finalize_rw("DROP")

    # DROPLOOK
    def rw56(self): return self.check_rw('O', self.rw57)
    def rw57(self): return self.check_rw('O', self.rw58)
    def rw58(self): return self.check_rw('K', self.rw59)
    def rw59(self):
        valid = Delimiters.delims()["WHITESPACE"] | set('(')
        return self.check_rwdelim(valid, self.rw60)
    def rw60(self): return self.finalize_rw("DROPLOOK")


    # =======================
    # RESERVED WORD "ECHO"
    # =======================

    def rw61(self): return self.check_rw('C', self.rw62)
    def rw62(self): return self.check_rw('H', self.rw63)
    def rw63(self): return self.check_rw('O', self.rw64)
    def rw64(self): return self.check_rw('(', self.rw65)
    def rw65(self): return self.finalize_rw("ECHO")


    # =======================
    # RESERVED WORDS "H"
    # =======================

    def rw66(self): 
        self.advance() 
        char = self.current_char

        if char == 'A': return self.rw67()
        if char == 'E': return self.rw71()
        if char == 'O': return self.rw76()
        
        return self.error()

    # HAUL
    def rw67(self): return self.check_rw('U', self.rw68)
    def rw68(self): return self.check_rw('L', self.rw69)
    def rw69(self):
        valid = Delimiters.delims()["WHITESPACE"] | set('[')
        return self.check_rwdelim(valid, self.rw70)
    def rw70(self): return self.finalize_rw("HAUL")

    # HEAVE
    def rw71(self): return self.check_rw('A', self.rw72)
    def rw72(self): return self.check_rw('V', self.rw73)
    def rw73(self): return self.check_rw('E', self.rw74)
    def rw74(self):
        valid = Delimiters.delims()["WHITESPACE"] | set('(')
        return self.check_rwdelim(valid, self.rw75)
    def rw75(self): return self.finalize_rw("HEAVE")

    # HOIST
    def rw76(self): return self.check_rw('I', self.rw77)
    def rw77(self): return self.check_rw('S', self.rw78)
    def rw78(self): return self.check_rw('T', self.rw79)
    def rw79(self):
        valid = Delimiters.delims()["WHITESPACE"] | set('(')
        return self.check_rwdelim(valid, self.rw80)
    def rw80(self): return self.finalize_rw("HOIST")


    # =======================
    # RESERVED WORDS "L"
    # =======================

    def rw81(self): 
        self.advance() 
        char = self.current_char

        if char == 'A': return self.rw82()
        if char == 'O': return self.rw86()
        
        return self.error()

    # LAND 
    def rw82(self): return self.check_rw('N', self.rw83)
    def rw83(self): return self.check_rw('D', self.rw84)
    def rw84(self):
        valid = Delimiters.delims()["WHITESPACE"] | set('!')
        return self.check_rwdelim(valid, self.rw85)
    def rw85(self): return self.finalize_rw("LAND")

    # LOCKE/LOOK
    def rw86(self): 
        self.advance() 
        char = self.current_char

        if char == 'C': return self.rw87()
        if char == 'O': return self.rw91()
        
        return self.error()

    # LOCKE
    def rw87(self): return self.check_rw('K', self.rw88)
    def rw88(self): return self.check_rw('E', self.rw89)
    def rw89(self): return self.check_rwdelim(Delimiters.delims()["WHITESPACE"], self.rw90)
    def rw90(self): return self.finalize_rw("LOCKE")

    # LOOK
    def rw91(self): return self.check_rw('K', self.rw92)
    def rw92(self):
        valid = Delimiters.delims()["WHITESPACE"] | set('(')
        return self.check_rwdelim(valid, self.rw93)
    def rw93(self): return self.finalize_rw("LOOK")

    # =======================
    # RESERVED WORD "MAST"
    # =======================
    def rw94(self): return self.check_rw('A', self.rw95)
    def rw95(self): return self.check_rw('S', self.rw96)
    def rw96(self): return self.check_rw('T', self.rw97)
    def rw97(self): return self.check_rwdelim(Delimiters.delims()["WHITESPACE"], self.rw98)
    def rw98(self): return self.finalize_rw("MAST")

    # =======================
    # RESERVED WORD "NAY"
    # =======================
    def rw99(self): return self.check_rw('A', self.rw100)
    def rw100(self): return self.check_rw('Y', self.rw101)
    def rw101(self): return self.check_rwdelim(Delimiters.delims()["BOOL_DELIM"], self.rw102)
    def rw102(self): return self.finalize_rw("NAY")

    # =======================
    # RESERVED WORD "PARCH"
    # =======================
    def rw103(self): return self.check_rw('A', self.rw104)
    def rw104(self): return self.check_rw('R', self.rw105)
    def rw105(self): return self.check_rw('C', self.rw106)
    def rw106(self): return self.check_rw('H', self.rw107)
    def rw107(self): return self.check_rwdelim(Delimiters.delims()["WHITESPACE"], self.rw108)
    def rw108(self): return self.finalize_rw("PARCH")

    # =======================
    # RESERVED WORDS "S"
    # =======================
    def rw109(self): 
        self.advance() 
        char = self.current_char

        if char == 'A': return self.rw110()
        if char == 'C': return self.rw114()
        
        return self.error()

    # SAIL
    def rw110(self): return self.check_rw('I', self.rw111)
    def rw111(self): return self.check_rw('L', self.rw112)
    def rw112(self):
        valid = Delimiters.delims()["WHITESPACE"] | set('!')
        return self.check_rwdelim(valid, self.rw113)
    def rw113(self): return self.finalize_rw("SAIL")

    # SCROLL
    def rw114(self): return self.check_rw('R', self.rw115)
    def rw115(self): return self.check_rw('O', self.rw116)
    def rw116(self): return self.check_rw('L', self.rw117)
    def rw117(self): return self.check_rw('L', self.rw118)
    def rw118(self): return self.check_rwdelim(Delimiters.delims()["WHITESPACE"], self.rw119)
    def rw119(self): return self.finalize_rw("SCROLL")