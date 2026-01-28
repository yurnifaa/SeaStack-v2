# lexer_handlers/symbol_handler.py
from backend.lexical.lexer_token import Token
from backend.lexical.handlers.delimiters import Delimiters

class SymbolHandler:
    
    # =========================================================================
    # HELPER: Sanitize Delimiters for Display
    # Replaces invisible chars ('\n', '\t', etc.) with the word "whitespace"
    # =========================================================================
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
            
        # Remove duplicates and sort
        cleaned_list = list(set(cleaned_list))
        cleaned_list.sort(key=str)
        return cleaned_list

    # =========================================================================
    # HELPER: Create Error with Expected List
    # =========================================================================
    def _create_sym_error(self, message, expected_list):
        err_token = Token(
            "ERROR",
            self.current_token_text(),
            self.line,
            self.col - 1,
            message
        )
        
        # --- SANITIZE BEFORE ATTACHING ---
        err_token.expected = self._sanitize_delims(expected_list)
        
        return err_token

    # =============================================
    # [ARITHMETIC] PLUS '+': +, +#, +=
    # =============================================
    def rs120(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs121()
        if self.current_char == "#": return self.rs122()
        if self.current_char == "=": return self.rs124()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))

    def rs121(self): return Token("+", self.current_token_text(), self.line, self.col - 1)

    # --- INC '+#' ---
    def rs122(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["ALPHANUMERIC"]): return self.rs123()
        
        msg = "Invalid Character. Expected: lowercase letter (a-z) or digit"
        self.errors.append(self._create_sym_error(msg, ["alphanumeric"]))
        
    def rs123(self): return Token("+#", self.current_token_text(), self.line, self.col - 1)
    
    # --- ADD-ASSIGN '+=' ---
    def rs124(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs125()
        
        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))

    def rs125(self): return Token("+=", self.current_token_text(), self.line, self.col - 1)
    
    # =============================================
    # [ARITHMETIC] SUB '-': -, -#, -=
    # =============================================
    def rs126(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs127()
        if self.current_char == "#": return self.rs128()
        if self.current_char == "=": return self.rs130()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))

    def rs127(self): return Token("-", self.current_token_text(), self.line, self.col - 1)

    # --- DEC '-#' ---
    def rs128(self): 
        self.advance()
        # DIAGRAM UPDATE: Diagram 128->129 requires 'alphanumeric', not just 'lowlet'
        if self._comp_delims(Delimiters._get_delimiters()["ALPHANUMERIC"]): return self.rs129()
        
        msg = "Invalid Character. Expected: alphanumeric"
        self.errors.append(self._create_sym_error(msg, ["alphanumeric"]))
        
    def rs129(self): return Token("-#", self.current_token_text(), self.line, self.col - 1)
    
    # --- SUB-ASSIGN '-=' ---
    def rs130(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs131()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs131(self): return Token("-=", self.current_token_text(), self.line, self.col - 1)
    
    # =============================================
    # [ARITHMETIC] MULTI '*': *, *=
    # =============================================
    def rs132(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs133()
        if self.current_char == "=": return self.rs134()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))

    def rs133(self): return Token("*", self.current_token_text(), self.line, self.col - 1)

    # --- MULTI-ASSIGN '*=' ---
    def rs134(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs135()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))

    def rs135(self): return Token("*=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] DIVIDE '/': /, /=
    # =============================================
    def rs136(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs137()
        if self.current_char == "=": return self.rs138()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs137(self): return Token("/", self.current_token_text(), self.line, self.col - 1)

    # --- DIV-ASSIGN '/=' ---
    def rs138(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs139()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs139(self): return Token("/=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] MOD '%': %, %=
    # =============================================
    def rs140(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["MOD_DELIM"]): return self.rs141()
        if self.current_char == "=": return self.rs142()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace or B C D P S"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace", "B", "C", "D", "P", "S"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs141(self): return Token("%", self.current_token_text(), self.line, self.col - 1)

    # --- MOD-ASSIGN '%=' ---
    def rs142(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs143()
        
        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))

    def rs143(self): return Token("%=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] EXPONENT '^': ^, ^=
    # =============================================
    def rs144(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs145()
        if self.current_char == "=": return self.rs146()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs145(self): return Token("^", self.current_token_text(), self.line, self.col - 1)

    # --- EXP-ASSIGN '^=' ---
    def rs146(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs147()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))

    def rs147(self): return Token("^=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] ASSIGN '=': =, ==
    # =============================================
    def rs148(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["ASSIGN_DELIM"]): return self.rs149()
        if self.current_char == "=": return self.rs150()

        msg = "Invalid Character. Expected = or delimiter: [ ' \" ( - A N or alphanumeric/whitespace"
        exp = ["=", "[", "'", '"', "(", "-", "A", "N", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))

    def rs149(self): return Token("=", self.current_token_text(), self.line, self.col - 1)

    # --- EQUAL '==' ---
    def rs150(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]): return self.rs151()
        
        msg = "Invalid Character. Expected delimiter: [ ' \" ( - A N or alphanumeric/whitespace"
        exp = ["[", "'", '"', "(", "-", "A", "N", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))

    def rs151(self): return Token("==", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] NOT '!': !, !!, !#, !=
    # =============================================
    def rs152(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["NOT_DELIM"]): return self.rs153()
        if self.current_char == "!": return self.rs154()
        if self.current_char == "#": return self.rs156()
        if self.current_char == "=": return self.rs158()

        msg = "Invalid Character. Expected: ! # = ( a-z or A N"
        exp = ["!", "#", "=", "(", "lowercase letter", "A", "N"]
        self.errors.append(self._create_sym_error(msg, exp))

    def rs153(self): return Token("!", self.current_token_text(), self.line, self.col - 1)

    # --- STMT TERM '!!' ---
    def rs154(self):  
        self.advance()
        # DIAGRAM UPDATE: 154->155 accepts "whitespace, newline, ]"
        # TERM_DELIM is whitespace + newline. We combine it with ']'
        valid_delims = Delimiters._get_delimiters()["TERM_DELIM"] | set("]")
        
        if self._comp_delims(valid_delims): return self.rs155()
        
        msg = "Invalid Character. Expected delimiter: \\n, whitespace, or ]"
        self.errors.append(self._create_sym_error(msg, ["newline", "whitespace", "]"]))
        
    def rs155(self): return Token("!!", self.current_token_text(), self.line, self.col - 1)
    
    # --- DOUBLE-NOT '!#' ---
    def rs156(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["NOT_DELIM"]): return self.rs157()
        
        msg = "Invalid Character. Expected: ! # = ( a-z or A N"
        exp = ["!", "#", "=", "(", "lowercase letter", "A", "N"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs157(self): return Token("!#", self.current_token_text(), self.line, self.col - 1)
    
    # --- NOT-EQUAL '!=' ---
    def rs158(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]): return self.rs159()
        
        msg = "Invalid Character. Expected delimiter: [ ' \" ( - A N or alphanumeric/whitespace"
        exp = ["[", "'", '"', "(", "-", "A", "N", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs159(self): return Token("!=", self.current_token_text(), self.line, self.col - 1)
    
    # =============================================
    # [REL-LOG] LESS '<': <, <=
    # =============================================
    def rs160(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs161()
        if self.current_char == "=": return self.rs162()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs161(self): return Token("<", self.current_token_text(), self.line, self.col - 1)

    # --- LESS-EQ '<=' ---
    def rs162(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs163()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs163(self): return Token("<=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] GREAT '>': >, >=
    # =============================================
    def rs164(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs165()
        if self.current_char == "=": return self.rs166()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs165(self): return Token(">", self.current_token_text(), self.line, self.col - 1)

    # --- GREAT-E '>=' ---
    def rs166(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs167()

        msg = "Invalid Character. Expected symbol or delimiter: # = ( - or alphanumeric/whitespace"
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
    
    def rs167(self): return Token(">=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] CONCAT '&': &, &&
    # =============================================
    def rs168(self): 
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CONCAT_DELIM"]): return self.rs169()
        if self.current_char == "&": return self.rs170()

        msg = "Invalid Character. Expected & or delimiter: ' ( a-z or whitespace"
        exp = ["&", "'", "(", "lowercase letter", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))

    def rs169(self): return Token("&", self.current_token_text(), self.line, self.col - 1)

    # --- AND '&&' ---
    def rs170(self):  
        self.advance()
        # DIAGRAM UPDATE: 170->171 uses "gen_op_delim"
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs171()

        msg = "Invalid Character. Expected delimiter: whitespace, alphanumeric, -, ("
        exp = ["whitespace", "alphanumeric", "-", "("]
        self.errors.append(self._create_sym_error(msg, exp))
    
    def rs171(self): return Token("&&", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] OR '||': ||
    # =============================================
    def rs172(self): 
        # State 172: Expects the second '|'
        self.advance()
        if self.current_char == "|": return self.rs173()

        msg = "Invalid Character. Expected second pipe: |"
        self.errors.append(self._create_sym_error(msg, ["|"]))
    
    def rs173(self): 
        # State 173: Delimiter Check
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]): return self.rs174()

        msg = "Invalid Character. Expected delimiter: [ ' \" ( - A N or alphanumeric/whitespace"
        exp = ["[", "'", '"', "(", "-", "A", "N", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
    
    def rs174(self): return Token("||", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] COLON ':'
    # =============================================
    def rs175(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["COLON_DELIM"]): return self.rs176()

        msg = "Invalid Character. Expected delimiter: \\n or whitespace"
        exp = ["newline", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
    
    def rs176(self): return Token(":", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] ADDR '@'
    # =============================================
    def rs177(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]): return self.rs178()

        msg = "Invalid Character. Expected: lowercase letter (a-z)"
        self.errors.append(self._create_sym_error(msg, ["lowercase letter"]))
        
    def rs178(self): return Token("@", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] MEM '$'
    # =============================================
    def rs179(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]): return self.rs180()

        msg = "Invalid Character. Expected: lowercase letter (a-z)"
        self.errors.append(self._create_sym_error(msg, ["lowercase letter"]))
        
    def rs180(self): return Token("$", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] COMMA ','
    # =============================================
    def rs181(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["COMMA_DELIM"]): return self.rs182()

        msg = "Invalid Character. Expected: [ ( ' \" alphanumeric or whitespace"
        exp = ["[", "(", "'", '"', "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs182(self): return Token(",", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] OPEN-CB '{'
    # =============================================
    def rs183(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["ALPHANUMERIC"]): return self.rs184()

        msg = "Invalid Character. Expected: lowercase letter or digit"
        self.errors.append(self._create_sym_error(msg, ["lowercase letter", "digit"]))
        
    def rs184(self): return Token("{", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] CLOSED-CB '}'
    # =============================================
    def rs185(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CLOSECB_DELIM"]): return self.rs186()

        msg = "Invalid Character. Expected delimiter: , ) ] } or operator/whitespace"
        exp = [",", ")", "]", "}", "operator", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs186(self): return Token("}", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] OPEN-P '('
    # =============================================
    def rs187(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["OPENP_DELIM"]): return self.rs188()

        msg = "Invalid Character. Expected: ( ) \" - or Reserved Word start (A B C D N P S)"
        exp = ["(", ")", '"', "-", "A", "B", "C", "D", "N", "P", "S"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs188(self): return Token("(", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] CLOSED-P ')'
    # =============================================
    def rs189(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CLOSEP_DELIM"]): return self.rs190()

        msg = "Invalid Character. Expected delimiter: ) [ ] , or operator/whitespace"
        exp = [")", "[", "]", ",", "operator", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
    
    def rs190(self): return Token(")", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] OPEN-SB '['
    # =============================================
    def rs191(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["OPENSB_DELIM"]): return self.rs192()

        msg = "Invalid Character. Expected: [ ' \" - or A N alphanumeric/whitespace"
        exp = ['(', '[', '!', "'", '"', '-', "A", "B", 'C', "D", "E", "H", "L", "M", 'N', "P", "S", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs192(self): return Token("[", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] CLOSED-SB ']'
    # =============================================
    def rs193(self):  
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CLOSESB_DELIM"]): return self.rs194()

        msg = "Invalid Character. Expected delimiter: , ) ] } or operator/whitespace"
        exp = [ "]", "}", "!", ",", "A", "B", "C", "D", "E", "H", "L", "S", "newline", "lowercase letter", "whitespace"]
        self.errors.append(self._create_sym_error(msg, exp))
        
    def rs194(self): return Token("]", self.current_token_text(), self.line, self.col - 1)