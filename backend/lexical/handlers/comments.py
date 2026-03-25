from backend.lexical.token import Token
from backend.lexical.lexer_errors import LexerErrors

# =================================================================================================
# COMMENTS: must start with ~ and end with newline OR start with ~( and end with )~
# =================================================================================================

class Comments(LexerErrors):

    # start of comment
    def cm295(self):
        self.advance()

        if self.char == '\n': return self.cm296()
        if self.char == '(': return self.cm298()
        if self.char is not None: return self.cm297()
            
        return self.error()

    # tokenize single-line comment
    def cm296(self):
        self.advance()  

        return Token(
            "single-comment",
            self.current_token_text(),
            self.token_start_line,
            self.token_start_col
        )

    # body of single-Line comment
    def cm297(self):
        self.advance() 

        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        if self.current_char == '\n': return self.cm296()

        return self.error()

    # start of multi-Line comment
    def cm298(self):
        self.advance() 

        if self.current_char == ')': return self.cm300()
        if self.current_char is not None: return self.cm299()

        return self.error()

    # body of multi-line comment
    def cm299(self):

        while self.current_char is not None and self.current_char != ')':
            self.advance()
        if self.current_char == ')': return self.cm300()

        return self.error()

    # close or continue multi-line comment
    def cm300(self):
        self.advance() 

        if self.current_char == '~': return self.cm301()
        if self.current_char is not None: return self.cm299()

        return self.error()
    
    # tokenize multi-line comment
    def cm301(self):
        self.advance() 

        return Token(
            "multi-comment",
            self.current_token_text(),
            self.token_start_line,
            self.token_start_col
        )
