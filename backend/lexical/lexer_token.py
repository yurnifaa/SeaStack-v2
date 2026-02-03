# =============================================================================================
# Contains the Token Class. Represents a single token with its type, value, line, and column.
# =============================================================================================

# After the lexer recognizes a character, the Token Class converts it into a Token object.
# from RAW TEXT to DATA for our future parser to process.
class Token:

    def __init__(self, type, value, line, col, error_msg=None): # Runs kapag may na successfully indentify si LEXER
        # Attribute Assignment - assign sa corrosponding instance variable nya 
        self.type = type        # Identifier that defines what the token is (like IDENTIFIER, INTEGER, PLUS, RESERVED_WORD)
        self.value = value      # Actual sequence of characters (sa lexeme column) the token represents ("count", "42", "+", "IF")
        self.line = line        # Yung line number nung lexeme
        self.col = col          # Yung col number nung lexeme 
        self.error_msg = error_msg  # Used for "ERROR" tokens. kapag VALID, returns NONE... else, i-papass kay error_msg

    def __repr__(self):         # yung official string representation. Finoformat yung token for readability
        return f"Token({self.type}, '{self.value}', L{self.line}:C{self.col})" # e.g. type="IDENTIFIER", value="total", line=1, col=1