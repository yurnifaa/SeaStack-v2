from backend.lexical.token import Token
from backend.lexical.handlers.delimiters import Delimiters
from backend.lexical.lexer_errors import LexerErrors

# =================================================================================================
# SYMBOLS: must be a valid symbol with a valid delimeter
# =================================================================================================

class Symbols(LexerErrors):

    # =======================
    # SYMBOLS HELPERS
    # =======================

    # check if delimeter is valid
    def check_delim(self, delim_key):
        return self._is_valid_delimiter(delim_key)

    # =======================
    # RESERVED SYMBOLS
    # =======================

    # ADD '+' 
    def rs120(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs121()
        if self.current_char == "#": return self.rs122()
        if self.current_char == "=": return self.rs124()

        return self.error()

    def rs121(self): return Token("+", self.current_token_text(), self.token_start_line, self.token_start_col)

    # INCREMENT '+#'
    def rs122(self):
        self.advance()
        if self.check_delim("LOWLET"): return self.rs123()

        return self.error()

    def rs123(self): return Token("+#", self.current_token_text(), self.token_start_line, self.token_start_col)

    # ADD ASSIGN '+='
    def rs124(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs125()

        return self.error()

    def rs125(self): return Token("+=", self.current_token_text(), self.token_start_line, self.token_start_col)

    # SUBTRACT '-'
    def rs126(self):
        self.advance()

        if self.check_delim("MINUS_DELIM"): return self.rs127()
        if self.current_char == "#": return self.rs128()
        if self.current_char == "=": return self.rs130()
        if self.current_char == "0": return self.rs132()
        if self.current_char is not None and self.current_char in "123456789": return self.c238()

        return self.error()

    def rs127(self): return Token("-", self.current_token_text(), self.token_start_line, self.token_start_col)

    # DECREMENT '-#'
    def rs128(self):
        self.advance()
        if self.check_delim("LOWLET"): return self.rs129()

        return self.error()

    def rs129(self): return Token("-#", self.current_token_text(), self.token_start_line, self.token_start_col)

    # SUBTRACT ASSIGN '-='
    def rs130(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs131()

        return self.error()

    def rs131(self): return Token("-=", self.current_token_text(), self.token_start_line, self.token_start_col)

    # NEGATIVE DECIMAL '-0.'
    def rs132(self):
        self.advance()
        if self.current_char == ".": return self.d270()

        return self.error()

    # MULTIPLY '*'
    def rs133(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs134()
        if self.current_char == "=": return self.rs135()

        return self.error()

    def rs134(self): return Token("*", self.current_token_text(), self.token_start_line, self.token_start_col)

    # MULTIPLY ASSIGN '*='
    def rs135(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs136()

        return self.error()

    def rs136(self): return Token("*=", self.current_token_text(), self.token_start_line, self.token_start_col)

    # DIVIDE '/'
    def rs137(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs138()
        if self.current_char == "=": return self.rs139()

        return self.error()

    def rs138(self): return Token("/", self.current_token_text(), self.token_start_line, self.token_start_col)

    # DIVIDE ASSIGN '/='
    def rs139(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs140()

        return self.error()

    def rs140(self): return Token("/=", self.current_token_text(), self.token_start_line, self.token_start_col)

    # MODULO '%'
    def rs141(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs142()
        if self.current_char == "=": return self.rs143()

        return self.error()

    def rs142(self): return Token("%", self.current_token_text(), self.token_start_line, self.token_start_col)

    # MODULO ASSIGN '%='
    def rs143(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs144()

        return self.error()

    def rs144(self): return Token("%=", self.current_token_text(), self.token_start_line, self.token_start_col)

    # EXPONENT '^'
    def rs145(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs146()
        if self.current_char == "=": return self.rs147()

        return self.error()

    def rs146(self): return Token("^", self.current_token_text(), self.token_start_line, self.token_start_col)

    # EXPONENT ASSIGN '^'
    def rs147(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs148()

        return self.error()

    def rs148(self): return Token("^=", self.current_token_text(), self.token_start_line, self.token_start_col)

    # ASSIGN '='
    def rs149(self):
        self.advance()
        if self.check_delim("ASSIGN_DELIM"): return self.rs150()
        if self.current_char == "=": return self.rs151()

        return self.error()

    def rs150(self): return Token("=", self.current_token_text(), self.token_start_line, self.token_start_col)

    # EQUAL '=='
    def rs151(self):
        self.advance()
        if self.check_delim("LOG_OP_DELIM"): return self.rs152()

        return self.error()

    def rs152(self): return Token("==", self.current_token_text(), self.token_start_line, self.token_start_col)

    # NOT '!'
    def rs153(self):
        self.advance()
        if self.check_delim("NOT_DELIM"): return self.rs154()
        if self.current_char == "!": return self.rs155()
        if self.current_char == "#": return self.rs157()
        if self.current_char == "=": return self.rs159()

        return self.error()

    def rs154(self): return Token("!", self.current_token_text(), self.token_start_line, self.token_start_col)

    # TERMINATOR '!!'
    def rs155(self):
        self.advance()
        if self.check_delim("TERMINATOR_DELIM"): return self.rs156()

        return self.error()

    def rs156(self): return Token("!!", self.current_token_text(), self.token_start_line, self.token_start_col)

    # DOUBLE NOT '!#'
    def rs157(self):
        self.advance()
        if self.check_delim("NOT_DELIM"): return self.rs158()

        return self.error()

    def rs158(self): return Token("!#", self.current_token_text(), self.token_start_line, self.token_start_col)

    # NOT EQUAL '!='
    def rs159(self):
        self.advance()
        if self.check_delim("LOG_OP_DELIM"): return self.rs160()

        return self.error()

    def rs160(self): return Token("!=", self.current_token_text(), self.token_start_line, self.token_start_col)

    # LESS THAN '<'
    def rs161(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs162()
        if self.current_char == "=": return self.rs163()

        return self.error()

    def rs162(self): return Token("<", self.current_token_text(), self.token_start_line, self.token_start_col)

    # LESS or EQUAL '<='
    def rs163(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs164()

        return self.error()

    def rs164(self): return Token("<=", self.current_token_text(), self.token_start_line, self.token_start_col)

    # GREATER THAN '>'
    def rs165(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs166()
        if self.current_char == "=": return self.rs167()

        return self.error()

    def rs166(self): return Token(">", self.current_token_text(), self.token_start_line, self.token_start_col)

    # GREATER or EQUAL '>='
    def rs167(self):
        self.advance()
        if self.check_delim("GEN_OP_DELIM"): return self.rs168()

        return self.error()

    def rs168(self): return Token(">=", self.current_token_text(), self.token_start_line, self.token_start_col)

    # CONCATENATE '&'
    def rs169(self):
        self.advance()
        if self.check_delim("CONCAT_DELIM"): return self.rs170()
        if self.current_char == "&": return self.rs171()

        return self.error()

    def rs170(self): return Token("&", self.current_token_text(), self.token_start_line, self.token_start_col)

    # AND '&&'
    def rs171(self):
        self.advance()
        if self.check_delim("LOG_OP_DELIM"): return self.rs172()

        return self.error()

    def rs172(self): return Token("&&", self.current_token_text(), self.token_start_line, self.token_start_col)

    # OR '|'
    def rs173(self):
        self.advance()
        if self.current_char == "|": return self.rs174()
        return self.error()

    def rs174(self):
        self.advance()
        if self.check_delim("LOG_OP_DELIM"): return self.rs175()

        return self.error()

    def rs175(self): return Token("||", self.current_token_text(), self.token_start_line, self.token_start_col)

    # COLON ':'
    def rs176(self):
        self.advance()
        if self.check_delim("COLON_DELIM"): return self.rs177()

        return self.error()

    def rs177(self): return Token(":", self.current_token_text(), self.token_start_line, self.token_start_col)

    # ADDRESS '@'
    def rs178(self):
        self.advance()
        if self.check_delim("LOWLET"): return self.rs179()

        return self.error()

    def rs179(self): return Token("@", self.current_token_text(), self.token_start_line, self.token_start_col)

    # MEMBER '$'
    def rs180(self):
        self.advance()
        if self.check_delim("LOWLET"): return self.rs181()

        return self.error()

    def rs181(self): return Token("$", self.current_token_text(), self.token_start_line, self.token_start_col)

    # COMMA ','
    def rs182(self):
        self.advance()
        if self.check_delim("COMMA_DELIM"): return self.rs183()

        return self.error()

    def rs183(self): return Token(",", self.current_token_text(), self.token_start_line, self.token_start_col)

    # OPEN CURLY BRACKET '{'
    def rs184(self):
        self.advance()
        if self.check_delim("ALPHANUMERIC"): return self.rs185()

        return self.error()

    def rs185(self): return Token("{", self.current_token_text(), self.token_start_line, self.token_start_col)

    # CLOSED CURLY BRACKET '}'
    def rs186(self):
        self.advance()
        if self.check_delim("CLOSECB_DELIM"): return self.rs187()

        return self.error()

    def rs187(self): return Token("}", self.current_token_text(), self.token_start_line, self.token_start_col)

    # OPEN PARENTHESIS '('
    def rs188(self):
        self.advance()
        if self.check_delim("OPENP_DELIM"): return self.rs189()

        return self.error()

    def rs189(self): return Token("(", self.current_token_text(), self.token_start_line, self.token_start_col)

    # CLOSED PARENTHESIS ')'
    def rs190(self):
        self.advance()
        if self.check_delim("CLOSEP_DELIM"): return self.rs191()

        return self.error()

    def rs191(self): return Token(")", self.current_token_text(), self.token_start_line, self.token_start_col)

    # OPEN SQUARE BRACKET '['
    def rs192(self):
        self.advance()
        if self.check_delim("OPENSB_DELIM"): return self.rs193()

        return self.error()

    def rs193(self): return Token("[", self.current_token_text(), self.token_start_line, self.token_start_col)

    # CLOSED SQUARE BRACKET ']'
    def rs194(self):
        self.advance()
        if self.check_delim("CLOSESB_DELIM"): return self.rs195()

        return self.error()

    def rs195(self): return Token("]", self.current_token_text(), self.token_start_line, self.token_start_col)