from backend.lexical.token import Token
from backend.lexical.lexer_errors import LexerErrors

# =================================================================================================
# COMMENTS: must start with ~ and end with newline OR start with ~( and end with )~
# =================================================================================================

class Comments(LexerErrors):

    # =======================
    # SINGLE-LINE COMMENT
    # =======================

    def cm297(self):
        self.advance()

        if self.current_char == '\n' or self.current_char is None: return self.cm298()
        if self.current_char == '(': return self.cm300()
        if self.current_char is not None: return self.cm299()

        return self.error()

    # tokenize single-line comment
    def cm298(self):
        self.advance()  
        return Token(
            "single-comment",
            self.current_token_text(),
            self.token_start_line,
            self.token_start_col
        )

    # body of single-Line comment
    def cm299(self):
        self.advance() 

        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        if self.current_char == '\n' or self.current_char is None: return self.cm298()

        return self.error()
    

    # =======================
    # MULTI-LINE COMMENT
    # =======================

    def cm300(self):
        self.advance() 

        if self.current_char == ')': return self.cm302()
        if self.current_char is not None: return self.cm301()

        return self.error()

    # body of multi-line comment
    def cm301(self):
        while self.current_char is not None and self.current_char != ')':
            self.advance()
        if self.current_char == ')': return self.cm302()

        return self.error()

    # close or continue multi-line comment
    def cm302(self):
        self.advance() 

        if self.current_char == '~': return self.cm303()
        if self.current_char is not None: return self.cm301()

        return self.error()
    
    # tokenize multi-line comment
    def cm303(self):
        self.advance() 

        return Token(
            "multi-comment",
            self.current_token_text(),
            self.token_start_line,
            self.token_start_col
        )
