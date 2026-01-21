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
# Lexer Class (uses inheritance to call each handler)
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

    # --- Token start tracking (for lexeme extraction) ---
        self.token_start_pos = 0
        self.token_start_line = 1
        self.token_start_col = 1

    # Mark the start of a new token
    def mark_token_start(self):
        self.token_start_pos = self.pos
        self.token_start_line = self.line
        self.token_start_col = self.col

    # Extract the current token lexeme
    def current_token_text(self):
        return self.text[self.token_start_pos:self.pos]

    # =========================================================================
    # Helper Methods
    # =========================================================================
    def advance(self):          # FOR STATE MOVEMENT: Moves the position forward after recognizing the previous one and updates line/column counts
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

    def peek(self):             # Looks at the next character without changing the position
        peek_pos = self.pos + 1
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        return None

    def save(self): #Saves the current lexer position state for backtracking
        return (self.pos, self.line, self.col, self.current_char)

    def restore(self, state): #Restores the lexer state from a saved point
        self.pos, self.line, self.col, self.current_char = state

    # =========================================================================
    # Delimiter Comparison
    # =========================================================================
    def _comp_delims(self, delimiter_set):  #Checks if the current character is within the provided delimiter set
            return self.current_char in delimiter_set or self.current_char is None

    def _is_valid_delimiter(self, delim_set_name):  #Checks if the current character is a valid delimiter for the preceding token type
        char = self.current_char
        delims = Delimiters._get_delimiters()

        # Universal delimiters: End of File or whitespace
        if char is None or char.isspace():
            return True

        # Check against named set
        if delim_set_name in delims:
            return char in delims[delim_set_name]

        # Fallback for generic/unlisted symbols
        return False
        
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
            
            valid_delims = Delimiters._get_delimiters().get(delim_set_name, ["Valid Delimiter"])
            
            err_token.expected = valid_delims
            
            self.errors.append(err_token)

    # ============================================================================================================
    # 3. Transition Diagram State 0 (Looks at the current character and branches out to its designated state)
    # ============================================================================================================
    def state0(self):
        if self.current_char is None:
            return None 

        saved_state = self.save()
        char = self.current_char

    # =========================================================================
    # Reserved Words (rw0-rw119)
    # =========================================================================
        if char.isupper():
            return self._make_keyword()
        
    # =========================================================================
    # Symbols / Operators (rs120-rs196)
    # =========================================================================
        delims = Delimiters._get_delimiters()
        
        # Arithmetic
        if char == "+": return self.rs120()
        if char == "-": return self.rs126()
        if char == "*": return self.rs132()
        if char == "/": return self.rs136()
        if char == "%": return self.rs140()
        if char == "^": return self.rs144()

        # Assignment & Equality
        if char == "=": return self.rs148()

        # Logical / Relational
        if char == "!": return self.rs152()
        if char == "<": return self.rs160()
        if char == ">": return self.rs164()
        if char == "&": return self.rs168()
        if char == "|": return self.rs172()

        # Others
        if char == ":": return self.rs175()
        if char == "@": return self.rs177()
        if char == "$": return self.rs179()
        if char == ",": return self.rs181()
        if char == "\n": return self.rs183()

        # Brackets and Parentheses
        if char == "{": return self.rs185()
        if char == "}": return self.rs187()
        if char == "(": return self.rs189()
        if char == ")": return self.rs191()
        if char == "[": return self.rs193()
        if char == "]": return self.rs195()
        
    # =========================================================================
    # Identifiers (i197-i232)
    # =========================================================================
        if char.islower():
            self.advance() 
            return self._make_identifier()

    # =========================================================================
    # Digits (COIN and DIME) (c233-c265/d266-d282)
    # =========================================================================
        if char in Delimiters._get_delimiters()["DIGIT"]:
            self.mark_token_start()
            # FIX: Must advance to consume the first digit, otherwise Infinite Loop!
            self.advance() 
            return self.c233()  # NULL ENTRY

    # =========================================================================
    # PARCH and SCROLL Literals (p283-p286/s287-s290)
    # =========================================================================
        if char == "'": return self.p283()  # PARCH literal
        if char == '"': return self.s287()  # SCROLL literal

    # =========================================================================
    # Comments (cm293-cm300)
    # =========================================================================
        if char == "~":
            return self.cm293()

    # =========================================================================
    # Whitespace & Newline
    # =========================================================================
        if char.isspace():
            # Identify type
            token_type = "newline" if char == "\n" else "whitespace"
            lexeme = char
            
            l, c = self.line, self.col
            
            self.advance()
            
            # Return token instead of None
            return Token(token_type, lexeme, l, c)

        # --- CATCH-ALL for UNKNOWN characters ---
        # If we get here, no handler recognized the character.
        err_token = Token("ERROR", char, self.line, self.col, "Unknown Character")
        self.errors.append(err_token)
        self.advance()
        return None # Return None so it's not tokenized
    
    # ============================================================================================
    # 1. PUBLIC MAIN METHOD (Tokenizes the entire input using the state0 Transition Diagram)
    # ============================================================================================
    def tokenize(self):                 
        while self.current_char is not None: #1. Initialize Loop as long the current character is not at the end of the file
            self.mark_token_start()          #2. saves the current position of the character before starting to scan a new token
            
            tok = self.state0()              #3. Decision Point: where the current character determines which state to pasok into
            if tok:                          
                if isinstance(tok, list):    #4. IF token was recognized, it's added in self.token
                    self.tokens.extend(tok)  #5. IF state0 returns NONE,
                else:                        #   - its a comment
                    self.tokens.append(tok)  #   - INVALID Character
        return self.tokens, self.errors      #6. Keeps looping starting the process of the next character
                                             #7. IF EOF na, the loop terminates and the method returns the list of valid tokens and errors