import string

class Delimiters:
    
    @staticmethod 
    def delims():

    # =======================
    # REGULAR DEFINITION
    # =======================

        LOWLET = set(string.ascii_lowercase)
        UPLET = set("ABCDEHLMNPS")
        DIGIT = set("0123456789")
        NONZERO = set("123456789")
        ALPHANUMERIC = LOWLET | DIGIT
        ASCII = set(string.printable)

        WHITESPACE = {' ', '\t', '\n', '\r'} 

        ARITH_OP = set("+-*/%^")
        GEN_OP = ARITH_OP | set("<>=!&|")


    # =======================
    # DELIMETERS
    # =======================

        ID_DELIM = WHITESPACE | GEN_OP | set("()]{}$,")

        GEN_OP_DELIM = WHITESPACE | ALPHANUMERIC | set("-(")
        LOG_OP_DELIM = GEN_OP_DELIM | set(['A', 'N', "'", '"'])
        MINUS_DELIM = WHITESPACE | LOWLET | set("(")
        NOT_DELIM = LOWLET | set("AN(")
        CONCAT_DELIM = WHITESPACE | LOWLET | set('("')
        ASSIGN_DELIM = LOG_OP_DELIM | set(['[', '!'])

        DIGIT_DELIM = WHITESPACE | GEN_OP | set(")]}:,")
        BOOL_DELIM = WHITESPACE | set(")]&|!=,")
        PARCH_DELIM = BOOL_DELIM | set(":")
        SCR_DELIM = PARCH_DELIM | set("{")
        
        COMMA_DELIM = ASSIGN_DELIM | set(['@'])
        COLON_DELIM = WHITESPACE | LOWLET | set(['A', 'C', 'E', 'H', 'L', '+', '-'])
        TERMINATOR_DELIM = COLON_DELIM | set(['B', 'D', 'M', 'P', 'S', ']'])
        
        CLOSECB_DELIM = WHITESPACE | GEN_OP | set(")]{&:,")
        CLOSEP_DELIM = WHITESPACE | GEN_OP | set(")[],")
        OPENP_DELIM = LOG_OP_DELIM | set(['B', 'C', 'D', 'P', 'S', ')', '!'])
        CLOSESB_DELIM = WHITESPACE | LOWLET | UPLET | set(["]!+-,"])
        OPENSB_DELIM = CLOSESB_DELIM | DIGIT |set(['[', "'", '"'])
        

        return {
            "LOWLET": LOWLET,
            "UPLET": UPLET,
            "DIGIT": DIGIT,
            "NONZERO": NONZERO,
            "ALPHANUMERIC": ALPHANUMERIC,
            "ASCII": ASCII,
            "WHITESPACE": WHITESPACE,
            "ARITH_OP": ARITH_OP,
            "GEN_OP": GEN_OP,
            "ID_DELIM": ID_DELIM,
            "GEN_OP_DELIM": GEN_OP_DELIM,
            "LOG_OP_DELIM": LOG_OP_DELIM,
            "MINUS_DELIM": MINUS_DELIM,
            "NOT_DELIM": NOT_DELIM,
            "CONCAT_DELIM": CONCAT_DELIM,
            "ASSIGN_DELIM": ASSIGN_DELIM,
            "DIGIT_DELIM": DIGIT_DELIM,
            "BOOL_DELIM": BOOL_DELIM,
            "PARCH_DELIM": PARCH_DELIM,
            "SCR_DELIM": SCR_DELIM,
            "COMMA_DELIM": COMMA_DELIM,
            "COLON_DELIM": COLON_DELIM,
            "TERMINATOR_DELIM": TERMINATOR_DELIM,
            "CLOSECB_DELIM": CLOSECB_DELIM,
            "CLOSEP_DELIM": CLOSEP_DELIM,
            "OPENP_DELIM": OPENP_DELIM,
            "CLOSESB_DELIM": CLOSESB_DELIM,
            "OPENSB_DELIM": OPENSB_DELIM
        }
