# lexer_handlers/symbol_handler.py
import string
from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters
# IMPORT THE ERROR HANDLER
from backend.error_msg import ErrorHandler 

class SymbolHandler:
    
    # --- HELPER: DYNAMIC & CLEAN ERROR GENERATION ---
    def _report_sym_error(self, delim_key, manual_extras=None):
        if manual_extras is None:
            manual_extras = []
            
        # 1. Fetch the Set
        allowed_set = set(Delimiters._get_delimiters().get(delim_key, []))
        allowed_set.update(manual_extras)
        
        # 2. USE THE SAME CLEANING LOGIC AS LEXER
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
        
        # 3. Generate Error
        return ErrorHandler.get_lexical_error(
            line=self.line,
            col=self.col - 1,
            invalid_char=self.current_token_text(),
            expected_list=sorted(cleaned_list)
        )

    # =============================================
    # [ARITHMETIC] PLUS '+': +, +#, +=
    # =============================================
    def rs120(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs121()
        if self.current_char == "#": return self.rs122()
        if self.current_char == "=": return self.rs124()

        self.errors.append(self._report_sym_error("GEN_OP_DELIM", ["#", "="]))

    def rs121(self):  
        return Token("+", self.current_token_text(), self.line, self.col - 1)

    def rs122(self):  # INC '+#'
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]):
            return self.rs123()
        self.errors.append(self._report_sym_error("LOWLET"))
        
    def rs123(self): return Token("+#", self.current_token_text(), self.line, self.col - 1)
    
    def rs124(self):  # ADD-ASSIGN '+='
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs125()
        self.errors.append(self._report_sym_error("GEN_OP_DELIM"))

    def rs125(self): return Token("+=", self.current_token_text(), self.line, self.col - 1)
    
    # =============================================
    # [ARITHMETIC] SUB '-': -, -#, -=
    # =============================================
    def rs126(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs127()
        if self.current_char == "#": return self.rs128()
        if self.current_char == "=": return self.rs130()

        self.errors.append(self._report_sym_error("GEN_OP_DELIM", ["#", "="]))

    def rs127(self):  
        return Token("-", self.current_token_text(), self.line, self.col - 1)

    def rs128(self): # DEC '-#'
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]):
            return self.rs129()
        self.errors.append(self._report_sym_error("LOWLET"))
        
    def rs129(self): return Token("-#", self.current_token_text(), self.line, self.col - 1)
    
    def rs130(self):  # SUB-ASSIGN '-='
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs131()
        self.errors.append(self._report_sym_error("GEN_OP_DELIM"))
        
    def rs131(self): return Token("-=", self.current_token_text(), self.line, self.col - 1)
    
    # =============================================
    # [ARITHMETIC] MULTI '*': *, *=
    # =============================================
    def rs132(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs133()
        if self.current_char == "=": return self.rs134()

        self.errors.append(self._report_sym_error("GEN_OP_DELIM", ["="]))

    def rs133(self):  
        return Token("*", self.current_token_text(), self.line, self.col - 1)

    def rs134(self):  # MULTI-ASSIGN '*='
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs135()
        self.errors.append(self._report_sym_error("GEN_OP_DELIM"))

    def rs135(self): return Token("*=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] DIVIDE '/': /, /=
    # =============================================
    def rs136(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs137()
        if self.current_char == "=": return self.rs138()

        self.errors.append(self._report_sym_error("GEN_OP_DELIM", ["="]))
        
    def rs137(self):  
        return Token("/", self.current_token_text(), self.line, self.col - 1)

    def rs138(self):  # DIV-ASSIGN '/='
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs139()
        self.errors.append(self._report_sym_error("GEN_OP_DELIM"))
        
    def rs139(self): return Token("/=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] MOD '%': %, %=
    # =============================================
    def rs140(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["MOD_DELIM"]):
            return self.rs141()
        if self.current_char == "=": return self.rs142()

        self.errors.append(self._report_sym_error("MOD_DELIM", ["="]))
        
    def rs141(self):  
        return Token("%", self.current_token_text(), self.line, self.col - 1)

    def rs142(self):  # MOD-ASSIGN '%='
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs143()
        self.errors.append(self._report_sym_error("GEN_OP_DELIM"))

    def rs143(self): return Token("%=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] EXPONENT '^': ^, ^=
    # =============================================
    def rs144(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): 
            return self.rs145()
        if self.current_char == "=": return self.rs146()

        self.errors.append(self._report_sym_error("GEN_OP_DELIM", ["="]))
        
    def rs145(self):  
        return Token("^", self.current_token_text(), self.line, self.col - 1)

    def rs146(self):  # EXP-ASSIGN '^='
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs147()
        self.errors.append(self._report_sym_error("GEN_OP_DELIM"))

    def rs147(self): return Token("^=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] ASSIGN '=': =, ==
    # =============================================
    def rs148(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["ASSIGN_DELIM"]):
            return self.rs149()
        if self.current_char == "=": return self.rs150()

        self.errors.append(self._report_sym_error("ASSIGN_DELIM", ["="]))

    def rs149(self):  
        return Token("=", self.current_token_text(), self.line, self.col - 1)

    def rs150(self):  # EQUAL '=='
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]):
            return self.rs151()
        self.errors.append(self._report_sym_error("LOG_OP_DELIM"))

    def rs151(self): return Token("==", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] NOT '!': !, !!, !#, !=
    # =============================================
    def rs152(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["NOT_DELIM"]):
            return self.rs153()
        if self.current_char == "!": return self.rs154()
        if self.current_char == "#": return self.rs156()
        if self.current_char == "=": return self.rs158()

        self.errors.append(self._report_sym_error("NOT_DELIM", ["!", "#", "="]))

    def rs153(self):  
        return Token("!", self.current_token_text(), self.line, self.col - 1)

    def rs154(self):  # STMT TERM '!!'
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["TERM_DELIM"]):
            return self.rs155()
        self.errors.append(self._report_sym_error("TERM_DELIM"))
        
    def rs155(self): return Token("!!", self.current_token_text(), self.line, self.col - 1)
    
    def rs156(self):  # DOUBLE-NOT '!#'
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["NOT_DELIM"]):
            return self.rs157()
        self.errors.append(self._report_sym_error("NOT_DELIM"))
        
    def rs157(self): return Token("!#", self.current_token_text(), self.line, self.col - 1)
    
    def rs158(self):  # NOT-EQUAL '!='
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]):
            return self.rs159()
        self.errors.append(self._report_sym_error("LOG_OP_DELIM"))
        
    def rs159(self): return Token("!=", self.current_token_text(), self.line, self.col - 1)
    
    # =============================================
    # [REL-LOG] LESS '<': <, <=
    # =============================================
    def rs160(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs161()
        if self.current_char == "=": return self.rs162()

        self.errors.append(self._report_sym_error("GEN_OP_DELIM", ["="]))
        
    def rs161(self):  
        return Token("<", self.current_token_text(), self.line, self.col - 1)

    def rs162(self):  # LESS-EQ '<='
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs163()
        self.errors.append(self._report_sym_error("GEN_OP_DELIM"))
        
    def rs163(self): return Token("<=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] GREAT '>': >, >=
    # =============================================
    def rs164(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs165()
        if self.current_char == "=": return self.rs166()

        self.errors.append(self._report_sym_error("GEN_OP_DELIM", ["="]))
        
    def rs165(self): 
        return Token(">", self.current_token_text(), self.line, self.col - 1)

    def rs166(self):  # GREAT-E '>='
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]):
            return self.rs167()
        self.errors.append(self._report_sym_error("GEN_OP_DELIM"))
    
    def rs167(self): return Token(">=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] CONCAT '&': &, &&
    # =============================================
    def rs168(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CONCAT_DELIM"]):
            return self.rs169()
        if self.current_char == "&": return self.rs170()

        self.errors.append(self._report_sym_error("CONCAT_DELIM", ["&"]))

    def rs169(self):  
        return Token("&", self.current_token_text(), self.line, self.col - 1)

    def rs170(self):  # AND '&&'
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]):
            return self.rs171()
        self.errors.append(self._report_sym_error("LOG_OP_DELIM"))
    
    def rs171(self): return Token("&&", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] OR '||': ||
    # =============================================
    def rs172(self): 
        self.advance()
        if self.current_char == "|": return self.rs173()
        self.errors.append(self._report_sym_error("", ["|"])) # No delimiter set, just '|' expected
    
    def rs173(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]):
            return self.rs174()
        self.errors.append(self._report_sym_error("LOG_OP_DELIM"))
    
    def rs174(self):  
        return Token("||", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] COLON ':'
    # =============================================
    def rs175(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["COLON_DELIM"]):
            return self.rs176()
        self.errors.append(self._report_sym_error("COLON_DELIM"))
    
    def rs176(self): return Token(":", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] ADDR '@'
    # =============================================
    def rs177(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]):
            return self.rs178()
        self.errors.append(self._report_sym_error("LOWLET"))
        
    def rs178(self): return Token("@", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] MEM '$'
    # =============================================
    def rs179(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]):
            return self.rs180()
        self.errors.append(self._report_sym_error("LOWLET"))
        
    def rs180(self): return Token("$", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] COMMA ','
    # =============================================
    def rs181(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["COMMA_DELIM"]):
            return self.rs182()
        self.errors.append(self._report_sym_error("COMMA_DELIM"))
        
    def rs182(self): return Token(",", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] NEWLINE '\n'
    # =============================================
    def rs183(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["ASCII"]):
            return self.rs184()
        self.errors.append(self._report_sym_error("ASCII"))

    def rs184(self): return Token("newline", "\\n", self.line, self.col - 1)

    # =============================================
    # [OTHERS] OPEN-CB '{'
    # =============================================
    def rs185(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["ALPHANUMERIC"]):
            return self.rs186()
        self.errors.append(self._report_sym_error("ALPHANUMERIC"))
        
    def rs186(self): return Token("{", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] CLOSED-CB '}'
    # =============================================
    def rs187(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CLOSECB_DELIM"]):
            return self.rs188()
        self.errors.append(self._report_sym_error("CLOSECB_DELIM"))
        
    def rs188(self): return Token("}", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] OPEN-P '('
    # =============================================
    def rs189(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["OPENP_DELIM"]):
            return self.rs190()
        self.errors.append(self._report_sym_error("OPENP_DELIM"))
        
    def rs190(self): return Token("(", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] CLOSED-P ')'
    # =============================================
    def rs191(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CLOSEP_DELIM"]):
            return self.rs192()
        self.errors.append(self._report_sym_error("CLOSEP_DELIM"))
    
    def rs192(self): return Token(")", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] OPEN-SB '['
    # =============================================
    def rs193(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["OPENSB_DELIM"]):
            return self.rs194()
        self.errors.append(self._report_sym_error("OPENSB_DELIM"))
        
    def rs194(self): return Token("[", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] CLOSED-SB ']'
    # =============================================
    def rs195(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CLOSESB_DELIM"]):
            return self.rs196()
        self.errors.append(self._report_sym_error("CLOSESB_DELIM"))
        
    def rs196(self): return Token("]", self.current_token_text(), self.line, self.col - 1)