from backend.lexical.token import Token
from backend.lexical.handlers.delimiters import Delimiters
from backend.lexical.lexer_errors import LexerErrors

# =========================================================================================
# PARCH: single char except newline, ', \; supports \s, \n, \t, \0, \\
# SCROLL: sequence of any ASCII char except newline, ", \; supports \d, \n, \t, \0,\\
# =========================================================================================

class Texts(LexerErrors):

    # =========================================================================
    # TEXT HELPERS
    # =========================================================================
    def check_pdelim(self):
        return self._comp_delims(Delimiters._get_delimiters()["PARCH_DELIM"])

    def check_sdelim(self):
        return self._comp_delims(Delimiters._get_delimiters()["SCR_DELIM"])
    
    def check_parch(self):
        delims = Delimiters._get_delimiters()
        allowed = delims["ASCII"] - set("'\\\n\r")
        return self.current_char is not None and self.current_char in allowed
    
    def check_scroll(self):
        delims = Delimiters._get_delimiters()
        allowed = delims["ASCII"] - set("\"\\\n\r")
        return self.current_char is not None and self.current_char in allowed

    # =========================================================================
    # PARCH literals 
    # =========================================================================

    # start of PARCH literal
    def p287(self):
        self.advance() 
        char = self.current_char
        
        if char == "'": return self.error()
        if char == '\n' or char is None: return self.error()
        if char == '\\': return self.p291()
        if self.check_parch(): return self.p288()
        
        return self.error() 
    
    # close PARCH literal
    def p288(self):
        self.advance()
        if self.current_char == "'": return self.p289()
        return self.error()
    
    # close PARCH literal
    def p289(self):
        self.advance()
        if self.check_pdelim(): return self.p290()
        return self.error()

    # tokenize PARCH literal
    def p290(self): return Token("PARCH-lit", self.current_token_text(), self.token_start_line, self.token_start_col)
    
    # escape sequences in PARCH literal
    def p291(self):
        self.advance()
        valid_escapes = ['s', 'n', 't', '0', '\\']

        if self.current_char in valid_escapes: return self.p288() 
        return self.error()

    # =========================================================================
    # SCROLL literals
    # =========================================================================

    # start of SCROLL literal
    def s292(self):
        self.advance() 
        char = self.current_char
        
        if char == '"': return self.error()
        if char == '\n' or char is None: return self.error()
        if char == '\\': return self.s296()
        if self.check_scroll(): return self.s293() 

        return self.error()

    # body of SCROLL literal
    def s293(self):
        self.advance()
        char = self.current_char

        if char == '"': return self.s294()
        if char == '\n' or char is None: return self.error()
        if char == '\\': return self.s296()
        if self.check_scroll(): return self.s293() 

        return self.error()

    # SCROLL delimeter
    def s294(self):
        self.advance()
        if self.check_sdelim(): return self.s295()
        return self.error()

    # tokenize SCROLL literal
    def s295(self): return Token("SCROLL-lit", self.current_token_text(), self.token_start_line, self.token_start_col)

    # escape sequences in SCROLL literal
    def s296(self):
        self.advance()
        valid_escapes = ['d', 'n', 't', '0', '\\']

        if self.current_char in valid_escapes: return self.s293() 
        return self.error()