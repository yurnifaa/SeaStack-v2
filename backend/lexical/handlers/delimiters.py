import string

class Delimiters:
    
    @staticmethod 
    def _get_delimiters():

    # =========================================================================
    # Base Definition
    # =========================================================================
        LOWLET = set(string.ascii_lowercase)
        UPLET = set("ABCDEHLMNPS")
        DIGIT = set("0123456789")
        ALPHANUMERIC = LOWLET | DIGIT
        ASCII = set(string.printable)
        NONZERO = set("123456789")
        DECIMAL = set(".")

    # =========================================================================
    # Whitespace, Newline, Tab
    # =========================================================================
        WHITESPACE = {' ', '\t', '\n', '\r'} 

    # =========================================================================
    # Operators
    # =========================================================================
        ARITH_OP = set("+-*/%^")
        GEN_OP = ARITH_OP | set("<>=!&|")

    # =========================================================================
    # DELIMITIERS
    # =========================================================================
        ID_DELIM = WHITESPACE | GEN_OP | set("(){]}$,")
        DIGIT_DELIM = WHITESPACE | GEN_OP | set(")}]:,")

        GEN_OP_DELIM = WHITESPACE | ALPHANUMERIC | set("-(")
        LOG_OP_DELIM = WHITESPACE | GEN_OP_DELIM | set(['A', 'N', "'", '"'])
        ASSIGN_DELIM = LOG_OP_DELIM | set(['[', '!'])
        MOD_DELIM = GEN_OP_DELIM | set("BCDPS")
        NOT_DELIM = LOWLET | set("AN(")

        BACK_DELIM = WHITESPACE | set("(!")
        BOOL_DELIM = WHITESPACE | set(")]&!=,|")
        
        PARCH_DELIM = BOOL_DELIM | set(":")
        SCR_DELIM = BOOL_DELIM | set("{:")
        
        COMMA_DELIM = ASSIGN_DELIM | set(['@'])
        CONCAT_DELIM = WHITESPACE | LOWLET | set('"(')
        
        CLOSECB_DELIM = WHITESPACE | GEN_OP | set("]){&:,")
        OPENP_DELIM = WHITESPACE | ALPHANUMERIC | set(['A', 'B', 'C', 'D', 'N', 'P', 'S', '(', ')', '"', "'", '-', '!'])
        CLOSEP_DELIM = WHITESPACE | GEN_OP | set(")[],")

        OPENSB_DELIM = WHITESPACE | set("\n") | ALPHANUMERIC | UPLET | set(['(', '[', ']', '!', "'", '"', '-'])
        CLOSESB_DELIM = WHITESPACE | set("\n") | set(['A', 'B', 'C', 'D', 'E', 'H', 'L', 'S', ']', '!', '}', ','])
        
        COLON_DELIM = WHITESPACE | set("\n") | LOWLET | set(['A', 'C', 'E', 'H', 'L', '+', '-'])
        TERMINATOR_DELIM = COLON_DELIM | set(['B', 'D', 'M', 'P', 'S', ']'])

        MINUS_DELIM = WHITESPACE | LOWLET | set("-(")

        return {
            "LOWLET": LOWLET,
            "UPLET": UPLET,
            "DIGIT": DIGIT,
            "ALPHANUMERIC": ALPHANUMERIC,
            "ASCII": ASCII,
            "NONZERO": NONZERO,
            "DECIMAL": DECIMAL,
            "WHITESPACE": WHITESPACE,
            "ARITH_OP": ARITH_OP,
            "GEN_OP": GEN_OP,
            "ID_DELIM": ID_DELIM,
            "DIGIT_DELIM": DIGIT_DELIM,
            "GEN_OP_DELIM": GEN_OP_DELIM,
            "LOG_OP_DELIM": LOG_OP_DELIM,
            "ASSIGN_DELIM": ASSIGN_DELIM,
            "MOD_DELIM": MOD_DELIM,
            "NOT_DELIM": NOT_DELIM,
            "BACK_DELIM": BACK_DELIM,
            "PARCH_DELIM": PARCH_DELIM,
            "SCR_DELIM": SCR_DELIM,
            "BOOL_DELIM": BOOL_DELIM,
            "COMMA_DELIM": COMMA_DELIM,
            "CLOSECB_DELIM": CLOSECB_DELIM,
            "OPENP_DELIM": OPENP_DELIM,
            "CLOSEP_DELIM": CLOSEP_DELIM,
            "OPENSB_DELIM": OPENSB_DELIM,
            "CLOSESB_DELIM": CLOSESB_DELIM,
            "COLON_DELIM": COLON_DELIM,
            "CONCAT_DELIM": CONCAT_DELIM,
            "TERMINATOR_DELIM": TERMINATOR_DELIM,
            "MINUS_DELIM": MINUS_DELIM
        }
