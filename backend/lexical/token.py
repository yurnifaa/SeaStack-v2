# =============================================================================================
# TOKEN CLASS: Represents a single token with its type, value, line, and column.
# =============================================================================================

# After the lexer recognizes a character, the Token Class converts it into a token object.

class Token:

    def __init__(self, type, value, line, col, error_msg=None): 
        self.type = type        # identified token shown in the token column 
        self.value = value      # actual sequence of characters shown in the lexeme column
        self.line = line        # line no. of lexeme
        self.col = col          # column no. of lexeme
        self.error_msg = error_msg  # error messages

    def __repr__(self):      # token formatting
        return f"Token({self.type}, '{self.value}', L{self.line}:C{self.col})" # e.g. Token(id, 'total', L1:C1) 