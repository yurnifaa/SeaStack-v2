import sys

from backend.lexical.token import Token

from backend.lexical.handlers.comments import Comments
from backend.lexical.handlers.digits import Digits
from backend.lexical.handlers.identifiers import Identifiers
from backend.lexical.handlers.reserved_words import ReservedWords
from backend.lexical.handlers.texts import Texts
from backend.lexical.handlers.symbols import Symbols
from backend.lexical.handlers.delimiters import Delimiters
from backend.lexical.lexer_errors import LexerErrors

# =========================================================================
# Lexer Class
# =========================================================================
class Lexer(
    Comments,
    Digits,
    Identifiers,
    ReservedWords,
    Texts,
    Symbols,
    LexerErrors
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

    # ============================================================================================================
    # Transition Diagram State 0 
    # ============================================================================================================
    def state0(self):
        if self.current_char is None:
            return None 

        saved_state = self.save()
        char = self.current_char

        # Reserved Words
        if char == 'A': return self.rw1()
        if char == 'B': return self.rw23()
        if char == 'C': return self.rw32()
        if char == 'D': return self.rw47()
        if char == 'E': return self.rw61()
        if char == 'H': return self.rw66()
        if char == 'L': return self.rw81()
        if char == 'M': return self.rw94()
        if char == 'N': return self.rw99()
        if char == 'P': return self.rw103()
        if char == 'S': return self.rw109()
        
        # Symbols 
        if char == "+": return self.rs120()
        if char == "-": return self.rs126()
        if char == "*": return self.rs133()
        if char == "/": return self.rs137()
        if char == "%": return self.rs141()
        if char == "^": return self.rs145()

        if char == "=": return self.rs149()

        if char == "!": return self.rs153()
        if char == "<": return self.rs161()
        if char == ">": return self.rs165()
        if char == "&": return self.rs169()
        if char == "|": return self.rs173()

        if char == ":": return self.rs176()
        if char == "@": return self.rs178()
        if char == "$": return self.rs180()
        if char == ",": return self.rs182()

        if char == "{": return self.rs184()
        if char == "}": return self.rs186()
        if char == "(": return self.rs188()
        if char == ")": return self.rs190()
        if char == "[": return self.rs192()
        if char == "]": return self.rs194()
        
        # Identifiers
        if char.islower(): return self.i196()

        # COIN and DIME literals
        if char == "0": return self.c236()
        if char in "123456789": return self.c238()

        # PARCH and SCROLL Literals
        if char == "'": return self.p287()
        if char == '"': return self.s292()

        # Comments 
        if char == "~": return self.cm297()

        # Whitespaces
        if char.isspace():
            l, c = self.line, self.col
            self.advance()
            return Token("whitespace", char, l, c)

        # Unknown characters
        self.advance()
        return self.error()

    # ============================================================================================
    # TOKENIZE: tokenizes the sequence of valid characters
    # ============================================================================================
    def tokenize(self):                 
        while self.current_char is not None: 
            self.mark_token_start()          
            tok = self.state0()              
            if tok:                       
                self.tokens.append(tok)
        return self.tokens, self.errors