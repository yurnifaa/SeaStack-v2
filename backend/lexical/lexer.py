import sys

from backend.lexical.lexer_token import Token

from backend.lexical.handlers.comment_hndlr import CommentHandler
from backend.lexical.handlers.digit_hndlr import DigitHandler
from backend.lexical.handlers.identifier_hndlr import IdentifierHandler
from backend.lexical.handlers.resword_hndlr import ReservedWordHandler
from backend.lexical.handlers.sp_lits_hndlr import LiteralHandler
from backend.lexical.handlers.symbol_hndlr import SymbolHandler
from backend.lexical.handlers.delimiters import Delimiters

# =========================================================================
# Lexer Class
# =========================================================================
class Lexer(
    CommentHandler,
    DigitHandler,
    IdentifierHandler,
    ReservedWordHandler,
    LiteralHandler,
    SymbolHandler
):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        self.identifier_table = {}
        self.tokens = []
        self.errors = []

        # --- Token start tracking ---
        self.token_start_pos = 0
        self.token_start_line = 1
        self.token_start_col = 1

    def mark_token_start(self):
        self.token_start_pos = self.pos
        self.token_start_line = self.line
        self.token_start_col = self.col

    def current_token_text(self):
        return self.text[self.token_start_pos:self.pos]

    # =========================================================================
    # Helper Methods
    # =========================================================================
    def advance(self):          
        if self.current_char == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1

        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def peek(self):             
        peek_pos = self.pos + 1
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        return None

    def save(self): 
        return (self.pos, self.line, self.col, self.current_char)

    def restore(self, state): 
        self.pos, self.line, self.col, self.current_char = state

    # =========================================================================
    # Delimiter Comparison & Sanitization
    # =========================================================================
    def _comp_delims(self, delimiter_set): 
        return self.current_char in delimiter_set or self.current_char is None

    def _is_valid_delimiter(self, delim_set_name):  
        char = self.current_char
        delims = Delimiters._get_delimiters()

        if char is None or char.isspace():
            return True

        if delim_set_name in delims:
            return char in delims[delim_set_name]

        return False

    # --- NEW HELPER: Replaces invisible chars with "whitespace" ---
    def _sanitize_delims(self, delim_set):
        delims = list(delim_set) if isinstance(delim_set, set) else delim_set
        cleaned_list = []
        has_whitespace = False
        
        for d in delims:
            # Check for space, tab, newline, return, vertical tab, form feed
            if d in [' ', '\t', '\n', '\r', '\v', '\f']:
                has_whitespace = True
            else:
                cleaned_list.append(d)
        
        if has_whitespace:
            cleaned_list.append("whitespace")
            
        cleaned_list.sort(key=str)
        return cleaned_list
        
    def _add_or_error(self, token_type, token_value, line, col, delim_set_name): 
        if self._is_valid_delimiter(delim_set_name):
            self.tokens.append(Token(token_type, token_value, line, col))
        else:
            char = self.current_char if self.current_char else "EOF"
            error_msg = f"Invalid Identifier"

            if delim_set_name == "ID_DELIM":
                 error_msg = f"Invalid Identifier"
            
            err_token = Token(
                "ERROR",
                token_value + (char if char != "End Of File" else ""),
                line,
                col,
                error_msg
            )
            
            # Fetch valid delimiters dynamically AND SANITIZE
            raw_delims = Delimiters._get_delimiters().get(delim_set_name, ["Valid Delimiter"])
            err_token.expected = self._sanitize_delims(raw_delims)
            
            self.errors.append(err_token)

    # ============================================================================================================
    # Transition Diagram State 0 
    # ============================================================================================================
    def state0(self):
        if self.current_char is None:
            return None 

        saved_state = self.save()
        char = self.current_char

        # --- Reserved Words ---
        if char.isupper():
            return self._make_keyword()
        
        # --- Symbols / Operators ---
        if char == "+": return self.rs120()
        if char == "-": return self.rs126()
        if char == "*": return self.rs133()
        if char == "/": return self.rs137()
        if char == "%": return self.rs141()
        if char == "^": return self.rs145()

        # Assignment & Equality
        if char == "=": return self.rs149()

        # Logical / Relational
        if char == "!": return self.rs153()
        if char == "<": return self.rs161()
        if char == ">": return self.rs165()
        if char == "&": return self.rs169()
        if char == "|": return self.rs173()

        # Others
        if char == ":": return self.rs176()
        if char == "@": return self.rs178()
        if char == "$": return self.rs180()
        if char == ",": return self.rs182()

        # Brackets (States 184-195)
        if char == "{": return self.rs184()
        if char == "}": return self.rs186()
        if char == "(": return self.rs188()
        if char == ")": return self.rs190()
        if char == "[": return self.rs192()
        if char == "]": return self.rs194()
        
        # --- Identifiers (Start at State 196) ---
        if char.islower():
            self.advance()
            return self.id196()

        # --- Digits (Start at State 236) ---
        if char.isdigit():
            self.mark_token_start()
            return self.c236()

        # --- Literals (Start at State 285) ---
        if char == "'": return self.p285() # State 285 is PARCH
        if char == '"': return self.s290() # State 290 is SCROLL

        # --- Comments (Start at State 295) ---
        if char == "~":
            return self.cm295()

        # --- Whitespace ---
        if char.isspace():
            token_type = "whitespace"
            lexeme = char
            l, c = self.line, self.col
            self.advance()
            return Token(token_type, lexeme, l, c)

        # Catch-all for unknown characters
        err_msg = f"Unknown Character '{char}'"
        err_token = Token("ERROR", char, self.line, self.col, err_msg)
        self.errors.append(err_token)
        self.advance()
        return None

    # ============================================================================================
    # PUBLIC MAIN METHOD
    # ============================================================================================
    def tokenize(self):                 
        while self.current_char is not None: 
            self.mark_token_start()          
            
            tok = self.state0()              
            if tok:                          
                if isinstance(tok, list):    
                    self.tokens.extend(tok)  
                else:                        
                    self.tokens.append(tok)
        return self.tokens, self.errors