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
    def _create_sym_error(self, expected_list):
        err_token = Token(
            "ERROR",
            self.current_token_text(),
            self.line,
            self.col - 1,
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

        # DELIMITERS
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs121(self): return Token("+", self.current_token_text(), self.line, self.col - 1)

    # --- INC '+#' ---
    def rs122(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]): return self.rs123()

        # DELIMITERS
        self.errors.append(self._create_sym_error(["lowlet"]))

    def rs123(self): return Token("+#", self.current_token_text(), self.line, self.col - 1)

    # --- ADD-ASSIGN '+=' ---
    def rs124(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs125()

        # DELIMITERS
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs125(self): return Token("+=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] SUB '-': -, -#, -=, -0, -nonzero
    # =============================================
    def rs126(self):
        self.advance()

        if self._comp_delims(Delimiters._get_delimiters()["MINUS_DELIM"]): return self.rs127()
        if self.current_char == "#": return self.rs128()
        if self.current_char == "=": return self.rs130()
        if self.current_char == "0": return self.rs132()
        if self.current_char is not None and self.current_char in "123456789": return self.c238()

        # DELIMITERS
        exp = ["#", "=", "(", "-", "0", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs127(self): return Token("-", self.current_token_text(), self.line, self.col - 1)

    # --- DEC '-#' ---
    def rs128(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]): return self.rs129()

        # DELIMITERS
        self.errors.append(self._create_sym_error(["lowlet"]))

    def rs129(self): return Token("-#", self.current_token_text(), self.line, self.col - 1)

    # --- SUB-ASSIGN '-=' ---
    def rs130(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs131()

        # DELIMITERS
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs131(self): return Token("-=", self.current_token_text(), self.line, self.col - 1)

    # --- NEGATIVE ZERO '-0' ---
    def rs132(self):
        self.advance()
        if self.current_char == ".": return self.d268()

        # DELIMITERS
        self.errors.append(self._create_sym_error(["."]))

    # =============================================
    # [ARITHMETIC] MULTI '*': *, *=
    # =============================================
    def rs133(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs134()
        if self.current_char == "=": return self.rs135()

        # DELIMITERS
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs134(self): return Token("*", self.current_token_text(), self.line, self.col - 1)

    # --- MULTI-ASSIGN '*=' ---
    def rs135(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs136()

        # DELIMITERS
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs136(self): return Token("*=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] DIVIDE '/': /, /=
    # =============================================
    def rs137(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs138()
        if self.current_char == "=": return self.rs139()

        # DELIMITERS
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs138(self): return Token("/", self.current_token_text(), self.line, self.col - 1)

    # --- DIV-ASSIGN '/=' ---
    def rs139(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs140()

        # DELIMITERS
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs140(self): return Token("/=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] MOD '%': %, %=
    # =============================================
    def rs141(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs142()
        if self.current_char == "=": return self.rs143()

        # DELIMITERS
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs142(self): return Token("%", self.current_token_text(), self.line, self.col - 1)

    # --- MOD-ASSIGN '%=' ---
    def rs143(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs144()

        # DELIMITERS
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs144(self): return Token("%=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] EXPONENT '^': ^, ^=
    # =============================================
    def rs145(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs146()
        if self.current_char == "=": return self.rs147()

        # DELIMITERS
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs146(self): return Token("^", self.current_token_text(), self.line, self.col - 1)

    # --- EXP-ASSIGN '^=' ---
    def rs147(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs148()

        # DELIMITERS
        exp = ["#", "=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs148(self): return Token("^=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [ARITHMETIC] ASSIGN '=': =, ==
    # =============================================
    def rs149(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["ASSIGN_DELIM"]): return self.rs150()
        if self.current_char == "=": return self.rs151()

        # DELIMITERS
        exp = ["=", "[", "(", "'", '"', "-", "A", "N", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs150(self): return Token("=", self.current_token_text(), self.line, self.col - 1)

    # --- EQUAL '==' ---
    def rs151(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]): return self.rs152()

        # DELIMITERS
        exp = ["[", "(", "'", '"', "-", "A", "N", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs152(self): return Token("==", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] NOT '!': !, !!, !#, !=
    # =============================================
    def rs153(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["NOT_DELIM"]): return self.rs154()
        if self.current_char == "!": return self.rs155()
        if self.current_char == "#": return self.rs157()
        if self.current_char == "=": return self.rs159()

        # DELIMITERS
        exp = ["!", "#", "=", "(", "A", "N", "lowlet"]
        self.errors.append(self._create_sym_error(exp))

    def rs154(self): return Token("!", self.current_token_text(), self.line, self.col - 1)

    # --- STMT TERM '!!' ---
    def rs155(self):
        self.advance()
        valid_delims = Delimiters._get_delimiters()["TERMINATOR_DELIM"] | set("]")

        if self._comp_delims(valid_delims): return self.rs156()

        # DELIMITERS
        self.errors.append(self._create_sym_error(["]", "+", "-", "A", "C", "E", "H", "L", "B", "D", "M", "P", "S", "lowlet", "whitespace"]))

    def rs156(self): return Token("!!", self.current_token_text(), self.line, self.col - 1)

    # --- DOUBLE-NOT '!#' ---
    def rs157(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["NOT_DELIM"]): return self.rs158()

        # DELIMITERS
        exp = ["(", "A", "N", "lowlet"]
        self.errors.append(self._create_sym_error(exp))

    def rs158(self): return Token("!#", self.current_token_text(), self.line, self.col - 1)

    # --- NOT-EQUAL '!=' ---
    def rs159(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]): return self.rs160()

        # DELIMITERS
        exp = ["[", "(", "'", '"', "-", "A", "N", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs160(self): return Token("!=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] LESS '<': <, <=
    # =============================================
    def rs161(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs162()
        if self.current_char == "=": return self.rs163()

        # DELIMITERS
        exp = ["=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs162(self): return Token("<", self.current_token_text(), self.line, self.col - 1)

    # --- LESS-EQ '<=' ---
    def rs163(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs164()

        # DELIMITERS
        exp = ["(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs164(self): return Token("<=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] GREAT '>': >, >=
    # =============================================
    def rs165(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs166()
        if self.current_char == "=": return self.rs167()

        # DELIMITERS
        exp = ["=", "(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs166(self): return Token(">", self.current_token_text(), self.line, self.col - 1)

    # --- GREAT-E '>=' ---
    def rs167(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs168()

        # DELIMITERS
        exp = ["(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs168(self): return Token(">=", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] CONCAT '&': &, &&
    # =============================================
    def rs169(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CONCAT_DELIM"]): return self.rs170()
        if self.current_char == "&": return self.rs171()

        # DELIMITERS
        exp = ["&", "'", "(", "lowlet", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs170(self): return Token("&", self.current_token_text(), self.line, self.col - 1)

    # --- AND '&&' ---
    def rs171(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["GEN_OP_DELIM"]): return self.rs172()

        # DELIMITERS
        exp = ["(", "-", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs172(self): return Token("&&", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] OR '||': ||
    # =============================================
    def rs173(self):
        self.advance()
        if self.current_char == "|": return self.rs174()
        self.errors.append(self._create_sym_error(["|"]))

    def rs174(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOG_OP_DELIM"]): return self.rs175()

        # DELIMITERS
        exp = ["(", "'", '"', "-", "A", "N", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs175(self): return Token("||", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [REL-LOG] COLON ':'
    # =============================================
    def rs176(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["COLON_DELIM"]): return self.rs177()

        # DELIMITERS
        exp = ["+", "-", "A", "C", "E", "H", "L", "lowlet", "newline", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs177(self): return Token(":", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] ADDR '@'
    # =============================================
    def rs178(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]): return self.rs179()

        # DELIMITERS
        self.errors.append(self._create_sym_error(["lowlet"]))

    def rs179(self): return Token("@", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] MEM '$'
    # =============================================
    def rs180(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["LOWLET"]): return self.rs181()

        # DELIMITERS
        self.errors.append(self._create_sym_error(["lowlet"]))

    def rs181(self): return Token("$", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] COMMA ','
    # =============================================
    def rs182(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["COMMA_DELIM"]): return self.rs183()

        # DELIMITERS
        exp = ["(", "@", '-', "'", '"', "A", "N", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs183(self): return Token(",", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] OPEN-CB '{'
    # =============================================
    def rs184(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["ALPHANUMERIC"]): return self.rs185()

        # DELIMITERS
        self.errors.append(self._create_sym_error(["alphanumeric"]))

    def rs185(self): return Token("{", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] CLOSED-CB '}'
    # =============================================
    def rs186(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CLOSECB_DELIM"]): return self.rs187()

        # DELIMITERS
        exp = ["+", ",", "-", "*", "/", "%", "^", "<", ">", "=", "!", "&", "|", "]", ")", "{", "&", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs187(self): return Token("}", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] OPEN-P '('
    # =============================================
    def rs188(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["OPENP_DELIM"]): return self.rs189()

        # DELIMITERS
        exp = ["(", ")", "!", '"', "-", "A", "B", "C", "D", "N", "P", "S", "alphanumeric"]
        self.errors.append(self._create_sym_error(exp))

    def rs189(self): return Token("(", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] CLOSED-P ')'
    # =============================================
    def rs190(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CLOSEP_DELIM"]): return self.rs191()

        # DELIMITERS
        exp = ["+", "-", "*", "/", "%", "^", "<", ">", "=", "!", "&", "|", ")", "[", "]", ",", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs191(self): return Token(")", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] OPEN-SB '['
    # =============================================
    def rs192(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["OPENSB_DELIM"]): return self.rs193()

        # DELIMITERS
        exp = ['(', '[', '!', "'", '"', '-', "A", "B", 'C', "D", "E", "H", "L", "M", 'N', "P", "S", "alphanumeric", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs193(self): return Token("[", self.current_token_text(), self.line, self.col - 1)

    # =============================================
    # [OTHERS] CLOSED-SB ']'
    # =============================================
    def rs194(self):
        self.advance()
        if self._comp_delims(Delimiters._get_delimiters()["CLOSESB_DELIM"]): return self.rs195()

        # DELIMITERS
        exp = [ "]", "}", "!", ",", "A", "B", "C", "D", "E", "H", "L", "S", "lowlet", "whitespace"]
        self.errors.append(self._create_sym_error(exp))

    def rs195(self): return Token("]", self.current_token_text(), self.line, self.col - 1)
