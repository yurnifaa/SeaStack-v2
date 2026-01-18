import sys
import string
#
from backend.lexical.lexer_token import Token
from backend.lexical.handlers.comment_hndlr import CommentHandler
from backend.lexical.handlers.digit_hndlr import DigitHandler
from backend.lexical.handlers.identifier_hndlr import IdentifierHandler
from backend.lexical.handlers.resword_hndlr import ReservedWordHandler
from backend.lexical.handlers.sp_lits_hndlr import LiteralHandler
from backend.lexical.handlers.symbol_hndlr import SymbolHandler
from backend.lexical.handlers.delimiters import Delimiters

# IMPORT THE CENTRAL ERROR HANDLER
from backend.error_msg import ErrorHandler 

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

        self.token_start_pos = 0
        self.token_start_line = 1
        self.token_start_col = 1

    def mark_token_start(self):
        self.token_start_pos = self.pos
        self.token_start_line = self.line
        self.token_start_col = self.col

    def current_token_text(self):
        return self.text[self.token_start_pos:self.pos]

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
    
    # --- NEW HELPER: CLEANS UP THE EXPECTED LIST ---
    def _clean_expected_set(self, raw_set):
        working_set = set(raw_set)
        cleaned_list = []

        # 1. Condense Ranges
        if set(string.ascii_lowercase).issubset(working_set):
            cleaned_list.append("a-z")
            working_set -= set(string.ascii_lowercase)
        
        if set(string.ascii_uppercase).issubset(working_set):
            cleaned_list.append("A-Z")
            working_set -= set(string.ascii_uppercase)
            
        if set(string.digits).issubset(working_set):
            cleaned_list.append("0-9")
            working_set -= set(string.digits)

        # 2. Condense Whitespace (The "Weird Characters" Fix)
        # If the set contains generic whitespace characters, replace them with a label
        whitespace_subset = working_set.intersection(set(string.whitespace))
        if whitespace_subset:
            cleaned_list.append("whitespace")
            working_set -= whitespace_subset

        # 3. Format Remaining Characters
        for char in sorted(list(working_set)):
            if char == "\n": cleaned_list.append("\\n")
            elif char == "\t": cleaned_list.append("\\t")
            elif char == " ": cleaned_list.append("' '")
            else: cleaned_list.append(char)
            
        return sorted(cleaned_list)

    def _add_or_error(self, token_type, token_value, line, col, delim_set_name):
        """
        Validates if the current character (lookahead) is a valid delimiter for the token just scanned.
        If valid, adds the token. If not, generates a detailed error.
        """
        if self._is_valid_delimiter(delim_set_name):
            self.tokens.append(Token(token_type, token_value, line, col))
        else:
            char = self.current_char if self.current_char else "EOF"
            
            # Start with implicit delimiters
            # We use a SET now to prevent duplicates before cleaning
            valid_delims_set = set(["whitespace", "\n"]) 
            
            # Fetch specific delimiters
            all_delims = Delimiters._get_delimiters()
            if delim_set_name in all_delims:
                valid_delims_set.update(all_delims[delim_set_name])
            
            # USE THE CLEANING HELPER
            final_expected_list = self._clean_expected_set(valid_delims_set)

            error_dict = ErrorHandler.get_lexical_error(
                line=line,
                col=col,
                invalid_char=char, 
                expected_list=final_expected_list 
            )
            self.errors.append(error_dict)

    def state0(self):
        if self.current_char is None:
            return None 

        char = self.current_char

        # Reserved Words
        if char.isupper():
            return self._make_keyword()
        
        # Symbols / Operators
        if char == "+": return self.rs120()
        if char == "-": return self.rs126()
        if char == "*": return self.rs132()
        if char == "/": return self.rs136()
        if char == "%": return self.rs140()
        if char == "^": return self.rs144()
        if char == "=": return self.rs148()
        if char == "!": return self.rs152()
        if char == "<": return self.rs160()
        if char == ">": return self.rs164()
        if char == "&": return self.rs168()
        if char == "|": return self.rs172()
        if char == ":": return self.rs175()
        if char == "@": return self.rs177()
        if char == "$": return self.rs179()
        if char == ",": return self.rs181()
        if char == "\n": return self.rs183()
        if char == "{": return self.rs185()
        if char == "}": return self.rs187()
        if char == "(": return self.rs189()
        if char == ")": return self.rs191()
        if char == "[": return self.rs193()
        if char == "]": return self.rs195()
        
        # Identifiers
        if char.islower():
            self.advance() 
            return self._make_identifier()

        # Digits
        if char in Delimiters._get_delimiters().get("DIGIT", []): 
            self.mark_token_start()
            return self.c233() 

        # Literals
        if char == "'": return self.p283()
        if char == '"': return self.s287()

        # Comments
        if char == "~":
            return self.cm293()

        # Whitespace
        if char.isspace():
            token_type = "newline" if char == "\n" else "whitespace"
            lexeme = char
            l, c = self.line, self.col
            self.advance()
            return Token(token_type, lexeme, l, c)

        # --- CATCH-ALL FOR UNKNOWN CHARACTERS ---
        error_dict = ErrorHandler.get_lexical_error(
            line=self.line, 
            col=self.col, 
            invalid_char=char,
            expected_list=["Start of Statement", "Identifier", "Literal", "Symbol"]
        )
        self.errors.append(error_dict)
        self.advance()
        return None
    
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