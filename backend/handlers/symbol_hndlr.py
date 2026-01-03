# lexer_handlers/symbol_handler.py
from lexer_token import Token
from handlers.delimiters import Delimiters

# =========================================================================================
# RESERVED SYMBOLS TD: Reserved SYMBOLS state machine (rs120 - rs196)
# This class recognizes and tokenizes single-character and multi-character operators/symbols 
# using the Transition diagram.
# ========================================================================================= 

class SymbolHandler:
    
    # =============================================
    # [ARITHMETIC] PLUS '+': +, +#, +=
    # States: 120 -> 121, 122->123, 124->125
    # =============================================
    def rs120(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs121()
        if self.current_char == "#": return self.rs122()
        if self.current_char == "=": return self.rs124()

        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))

    def rs121(self):  
        return Token("+", self.current_token_text(), self.line, self.col - 1)

    # --- INC '+#' ---
    def rs122(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]):
            return self.rs123()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected: lowercase letter (a-z)"))
        
    def rs123(self): return Token("+#", self.current_token_text(), self.line, self.col - 1)
    
    # --- ADD-ASSIGN '+=' ---
    def rs124(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs125()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))

    def rs125(self): return Token("+=", self.current_token_text(), self.line, self.col - 1)
    
    # =============================================
    # [ARITHMETIC] SUB '-': -, -#, -=
    # States: 126 -> 127, 128->129, 130->131
    # =============================================
    def rs126(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs127()
        if self.current_char == "#": return self.rs128()
        if self.current_char == "=": return self.rs130()

        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))

    def rs127(self):  
        return Token("-", self.current_token_text(), self.line, self.col - 1)

    # --- DEC '-#' ---
    def rs128(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]):
            return self.rs129()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected: lowercase letter (a-z)"))
        
    def rs129(self): return Token("-#", self.current_token_text(), self.line, self.col - 1)
    
    # --- SUB-ASSIGN '-=' ---
    def rs130(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs131()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))
        
    def rs131(self): return Token("-=", self.current_token_text(), self.line, self.col - 1)
    
    # =============================================
    # [ARITHMETIC] MULTI '*': *, *=
    # States: 132 -> 133, 134->135
    # =============================================
    def rs132(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs133()
        if self.current_char == "=": return self.rs134()

        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))

    def rs133(self):  
        return Token("*", self.current_token_text(), self.line, self.col - 1)

    # --- MULTI-ASSIGN '*=' ---
    def rs134(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs135()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))

    def rs135(self): return Token("*=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] DIVIDE '/': /, /=
    # States: 136 -> 137, 138->139
    # =============================================
    def rs136(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs137()
        if self.current_char == "=": return self.rs138()

        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))
        
    def rs137(self):  
        return Token("/", self.current_token_text(), self.line, self.col - 1)

    # --- DIV-ASSIGN '/=' ---
    def rs138(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs139()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))
        
    def rs139(self): return Token("/=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] MOD '%': %, %=
    # States: 140 -> 141, 142->143
    # =============================================
    def rs140(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["MOD_DELIM"]):
            return self.rs141()
        if self.current_char == "=": return self.rs142()

        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace or B C D P S"))
        
    def rs141(self):  
        return Token("%", self.current_token_text(), self.line, self.col - 1)

    # --- MOD-ASSIGN '%=' ---
    def rs142(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs143()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))

    def rs143(self): return Token("%=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] EXPONENT '^': ^, ^=
    # States: 144 -> 145, 146->147
    # =============================================
    def rs144(self): 
        self.advance()
        # Based on TD: ^ uses gen_op_delim
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): 
            return self.rs145()
        if self.current_char == "=": return self.rs146()

        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))
        
    def rs145(self):  
        return Token("^", self.current_token_text(), self.line, self.col - 1)

    # --- EXP-ASSIGN '^=' ---
    def rs146(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs147()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))

    def rs147(self): return Token("^=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] ASSIGN '=': =, ==
    # States: 148 -> 149, 150->151
    # =============================================
    def rs148(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["ASSIGN_DELIM"]):
            return self.rs149()
        if self.current_char == "=": return self.rs150()

        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected = or delimiter: [ ' \" ( - A N or alphanumeric/whitespace"))

    def rs149(self):  
        return Token("=", self.current_token_text(), self.line, self.col - 1)

    # --- EQUAL '==' ---
    def rs150(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]):
            return self.rs151()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected = or delimiter: [ ' \" ( - A N or alphanumeric/whitespace"))

    def rs151(self): return Token("==", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] NOT '!': !, !!, !#, !=
    # States: 152 -> 153, 154->155, 156->157, 158->159
    # =============================================
    def rs152(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["NOT_DELIM"]):
            return self.rs153()
        if self.current_char == "!": return self.rs154()
        if self.current_char == "#": return self.rs156()
        if self.current_char == "=": return self.rs158()

        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected: ! # = ( a-z or A N"))

    def rs153(self):  
        return Token("!", self.current_token_text(), self.line, self.col - 1)

    # --- STMT TERM '!!' ---
    def rs154(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["TERM_DELIM"]):
            return self.rs155()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected delimiter: \\n or whitespace"))
        
    def rs155(self): return Token("!!", self.current_token_text(), self.line, self.col - 1)
    
    # --- DOUBLE-NOT '!#' ---
    def rs156(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["NOT_DELIM"]):
            return self.rs157()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected: ! # = ( a-z or A N"))
        
    def rs157(self): return Token("!#", self.current_token_text(), self.line, self.col - 1)
    
    # --- NOT-EQUAL '!=' ---
    def rs158(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]):
            return self.rs159()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected = or delimiter: [ ' \" ( - A N or alphanumeric/whitespace"))
        
    def rs159(self): return Token("!=", self.current_token_text(), self.line, self.col - 1)
    
    # =============================================
    # [REL-LOG] LESS '<': <, <=
    # States: 160 -> 161, 162->163
    # =============================================
    def rs160(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs161()
        if self.current_char == "=": return self.rs162()

        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))
        
    def rs161(self):  
        return Token("<", self.current_token_text(), self.line, self.col - 1)

    # --- LESS-EQ '<=' ---
    def rs162(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs163()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))
        
    def rs163(self): return Token("<=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] GREAT '>': >, >=
    # States: 164 -> 165, 166->167
    # =============================================
    def rs164(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs165()
        if self.current_char == "=": return self.rs166()

        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))
        
    def rs165(self): 
        return Token(">", self.current_token_text(), self.line, self.col - 1)

    # --- GREAT-E '>=' ---
    def rs166(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs167()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"))
    
    def rs167(self): return Token(">=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] CONCAT '&': &, &&
    # States: 168 -> 169, 170->171
    # =============================================
    def rs168(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CONCAT_DELIM"]):
            return self.rs169()
        if self.current_char == "&": return self.rs170()

        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected & or delimiter: ' ( a-z or whitespace"))

    def rs169(self):  
        return Token("&", self.current_token_text(), self.line, self.col - 1)

    # --- AND '&&' ---
    def rs170(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]):
            return self.rs171()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected = or delimiter: [ ' \" ( - A N or alphanumeric/whitespace"))
    
    def rs171(self): return Token("&&", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] OR '||': ||
    # States: 172 -> 173 -> 174
    # =============================================
    def rs172(self): 
        # State 172: Expects the second '|'
        self.advance()
        if self.current_char == "|": return self.rs173()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected second pipe: |"))
    
    def rs173(self): 
        # State 173: Delimiter Check
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]):
            return self.rs174()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected = or delimiter: [ ' \" ( - A N or alphanumeric/whitespace"))
    
    def rs174(self):  
        return Token("||", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] COLON ':'
    # States: 175 -> 176
    # =============================================
    def rs175(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["COLON_DELIM"]):
            return self.rs176()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected delimiter: \\n, whitespace, or Reserved Word (A B C D E H L M N P S)") )
    
    def rs176(self): return Token(":", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] ADDR '@'
    # States: 177 -> 178
    # =============================================
    def rs177(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]):
            return self.rs178()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected: lowercase letter (a-z)"))
        
    def rs178(self): return Token("@", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] MEM '$'
    # States: 179 -> 180
    # =============================================
    def rs179(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]):
            return self.rs180()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected: lowercase letter (a-z)"))
        
    def rs180(self): return Token("$", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] COMMA ','
    # States: 181 -> 182
    # =============================================
    def rs181(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["COMMA_DELIM"]):
            return self.rs182()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected: [ ( ' \" alphanumeric or whitespace"))
        
    def rs182(self): return Token(",", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] NEWLINE '\n'
    # States: 183 -> 184
    # =============================================
    def rs183(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["ASCII"]):
            return self.rs184()
        
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected: any printable ASCII character"))

    def rs184(self): return Token("newline", "\\n", self.line, self.col - 1)

    # =============================================
    # [OTHERS] OPEN-CB '{'
    # States: 185 -> 186
    # =============================================
    def rs185(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["ALPHANUMERIC"]):
            return self.rs186()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected: lowercase letter or digit"))
        
    def rs186(self): return Token("{", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] CLOSED-CB '}'
    # States: 187 -> 188
    # =============================================
    def rs187(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CLOSECB_DELIM"]):
            return self.rs188()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected delimiter: , ) ] } or operator/whitespace"))
        
    def rs188(self): return Token("}", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] OPEN-P '('
    # States: 189 -> 190
    # =============================================
    def rs189(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["OPENP_DELIM"]):
            return self.rs190()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected: ( ) \" - or Reserved Word start (A B C D N P S)"))
        
    def rs190(self): return Token("(", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] CLOSED-P ')'
    # States: 191 -> 192
    # =============================================
    def rs191(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CLOSEP_DELIM"]):
            return self.rs192()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected delimiter: ) [ ] , or operator/whitespace"))
    
    def rs192(self): return Token(")", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] OPEN-SB '['
    # States: 193 -> 194
    # =============================================
    def rs193(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["OPENSB_DELIM"]):
            return self.rs194()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected: [ ' \" - or A N alphanumeric/whitespace"))
        
    def rs194(self): return Token("[", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] CLOSED-SB ']'
    # States: 195 -> 196
    # =============================================
    def rs195(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CLOSESB_DELIM"]):
            return self.rs196()
        self.errors.append(Token("ERROR", self.current_token_text(), self.line, self.col - 1, 
            "Invalid Character. Expected delimiter: , ) ] } or operator/whitespace"))
        
    def rs196(self): return Token("]", self.current_token_text(), self.line, self.col - 1)