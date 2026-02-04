# syn_parser.py
import sys
from syntax.First_Set import FIRST
from syntax.Predict_Set import PREDICT
from syntax.Follow_Set import FOLLOW
from backend.error_msg import ErrorHandler 

class Parser:
    def __init__(self, tokens, source_code):
        """
        Initializes the Parser.
        :param tokens: List of Token objects.
        :param source_code: Raw source string (required for error context).
        """
        # Define tokens to ignore
        ignored_types = [
            "whitespace", 
            "newline", 
            "single-comment", 
            "multi-comment"
        ]
        
        # Filter out junk tokens
        self.tokens = [t for t in tokens if t.type not in ignored_types]
        
        # NORMALIZE IDENTIFIERS
        # Ensures IDs like "id1", "id2" from lexical analysis are treated as generic "id"
        for t in self.tokens:
            if t.type.startswith("id") and t.type[2:].isdigit():
                t.type = "id"
        
        # Initialize state
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.errors = []
        
        # Initialize ErrorHandler with source code
        self.err_handler = ErrorHandler(source_code)

    # =========================================
    # Utility Methods
    # =========================================
    def advance(self):
        """Moves to the next token."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def eat(self, token_type):
        """
        Consumes the current token if it matches `token_type`.
        Strictly enforces matching; otherwise triggers 'Missing Token'.
        """
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            # Trigger 'Missing Token' error
            raise Exception(self.err_handler.get_missing_token_error(
                self.current_token, 
                token_type
            ))

    def get_production(self, non_terminal):
        """Uses PREDICT_SET to return the Production Number based on current token."""
        if not self.current_token:
            return None
            
        productions = PREDICT.get(non_terminal, {})
        return productions.get(self.current_token.type)

    def error_invalid_token(self, non_terminal):
        """Helper to raise invalid token error with expected tokens from Predict Set."""
        expected = list(PREDICT.get(non_terminal, {}).keys())
        raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    # =========================================
    # Entry Point
    # =========================================
    def parse(self):
        try:
            # 1. Missing start check
            if not self.tokens:
                raise Exception(self.err_handler.get_missing_start_error())

            self.program()
            
            # 3. Expected EOF check
            if self.current_token is not None:
                raise Exception(self.err_handler.get_expected_eof_error(self.current_token))
                
        except Exception as e:
            # Catch the dictionary raised by ErrorHandler
            if e.args and isinstance(e.args[0], dict):
                self.errors.append(e.args[0])
            else:
                # Fallback for unexpected python crashes
                self.errors.append({
                    "type": "Parser Crash",
                    "line": "?",
                    "col": "?",
                    "found": "CRASH",
                    "expected": [],
                    "message": f"{str(e)}"
                })

        return self.errors

    # =========================================
    # GRAMMAR PRODUCTIONS (UPDATED)
    # =========================================

    def program(self):
        # <program>
        prod = self.get_production("<program>")
        if prod == 1:
            self.global_dec()
            self.eat("AHOY")
            self.eat("(")
            self.eat(")")
            self.eat("[")
            self.local_dec()
            self.ahoy_stmnts()
            self.eat("]")
        else:
            self.error_invalid_token("<program>")

    def global_dec(self):
        # <global-dec>
        prod = self.get_production("<global-dec>")
        if prod == 2:
            self.var_arr_func()
        elif prod == 3:
            self.const()
            self.global_dec()
        elif prod == 4:
            self.struct()
        elif prod == 5:
            self.nonreturn_func()
        elif prod == 6:
            pass # Lambda
        else:
            self.error_invalid_token("<global-dec>")

    def var_arr_func(self):
        # <var-arr-func>
        prod = self.get_production("<var-arr-func>")
        if prod == 7:
            self.eat("COIN")
            self.eat("id")
            self.coin_tail()
        elif prod == 8:
            self.eat("DIME")
            self.eat("id")
            self.dime_tail()
        elif prod == 9:
            self.eat("PARCH")
            self.eat("id")
            self.parch_tail()
        elif prod == 10:
            self.eat("SCROLL")
            self.eat("id")
            self.scroll_tail()
        elif prod == 11:
            self.eat("BOOL")
            self.eat("id")
            self.bool_tail()
        else:
            self.error_invalid_token("<var-arr-func>")

    # ==================== COIN PRODUCTIONS ====================

    def coin_tail(self):
        # <coin-tail>
        prod = self.get_production("<coin-tail>")
        if prod == 12:
            self.coin_dec()
            self.global_dec()
        elif prod == 13:
            self.coin_func()
        else:
            self.error_invalid_token("<coin-tail>")

    def coin_dec(self):
        # <coin-dec>
        prod = self.get_production("<coin-dec>")
        if prod == 14:
            self.coin_init()
            self.coin_mult()
            self.eat("!!")
        elif prod == 15:
            self.coin_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<coin-dec>")

    def coin_init(self):
        # <coin-init>
        prod = self.get_production("<coin-init>")
        if prod == 16:
            self.eat("=")
            self.coin_init_val()
        elif prod == 17:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-init>")

    def coin_mult(self):
        # <coin-mult>
        prod = self.get_production("<coin-mult>")
        if prod == 18:
            self.eat(",")
            self.eat("id")
            self.coin_init()
            self.coin_mult()
        elif prod == 19:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-mult>")

    def coin_init_val(self):
        # <coin-init-val>
        prod = self.get_production("<coin-init-val>")
        if prod == 20:
            self.coin_val()
        else:
            self.error_invalid_token("<coin-init-val>")

    def coin_val(self):
        # <coin-val>
        prod = self.get_production("<coin-val>")
        if prod == 21:
            self.coin_ope()
            self.coin_exp()
        else:
            self.error_invalid_token("<coin-val>")

    def coin_ope(self):
        # <coin-ope>
        prod = self.get_production("<coin-ope>")
        if prod == 22:
            self.eat("id")
            self.id_tail()
        elif prod == 23:
            self.eat("(")
            self.coin_val()
            self.eat(")")
        elif prod == 24:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<coin-ope>")

    def coin_exp(self):
        # <coin-exp>
        prod = self.get_production("<coin-exp>")
        if prod == 25:
            self.arith_op()
            self.coin_ope()
            self.coin_exp()
        elif prod == 26:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-exp>")

    def arith_op(self):
        # <arith-op>
        prod = self.get_production("<arith-op>")
        if prod == 27: self.eat("+")
        elif prod == 28: self.eat("-")
        elif prod == 29: self.eat("*")
        elif prod == 30: self.eat("/")
        elif prod == 31: self.eat("%")
        elif prod == 32: self.eat("^")
        else:
            self.error_invalid_token("<arith-op>")

    def coin_arr(self):
        # <coin-arr>
        prod = self.get_production("<coin-arr>")
        if prod == 33:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.coin_arr_tail()
        else:
            self.error_invalid_token("<coin-arr>")

    def coin_arr_tail(self):
        # <coin-arr-tail>
        prod = self.get_production("<coin-arr-tail>")
        if prod == 34:
            self.eat("=")
            self.eat("[")
            self.coin_arr1()
            self.eat("]")
        elif prod == 35:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.coin_arr2_tail()
        elif prod == 36:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-arr-tail>")

    def coin_arr1(self):
        # <coin-arr1>
        prod = self.get_production("<coin-arr1>")
        if prod == 37:
            self.coin_arr_val()
            self.cav_tail()
        else:
            self.error_invalid_token("<coin-arr1>")

    def coin_arr_val(self):
        # <coin-arr-val>
        prod = self.get_production("<coin-arr-val>")
        if prod == 38:
            self.coin_val()
        else:
            self.error_invalid_token("<coin-arr-val>")

    def cav_tail(self):
        # <cav-tail>
        prod = self.get_production("<cav-tail>")
        if prod == 39:
            self.eat(",")
            self.coin_arr1()
        elif prod == 40:
            pass # Lambda
        else:
            self.error_invalid_token("<cav-tail>")

    def coin_arr2_tail(self):
        # <coin-arr2-tail>
        prod = self.get_production("<coin-arr2-tail>")
        if prod == 41:
            self.eat("=")
            self.eat("[")
            self.coin_arr2()
            self.eat("]")
        elif prod == 42:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-arr2-tail>")

    def coin_arr2(self):
        # <coin-arr2>
        prod = self.get_production("<coin-arr2>")
        if prod == 43:
            self.eat("[")
            self.coin_arr1()
            self.eat("]")
            self.cav2_tail()
        else:
            self.error_invalid_token("<coin-arr2>")

    def cav2_tail(self):
        # <cav2-tail>
        prod = self.get_production("<cav2-tail>")
        if prod == 44:
            self.eat(",")
            self.coin_arr2()
        elif prod == 45:
            pass # Lambda
        else:
            self.error_invalid_token("<cav2-tail>")

    def coin_func(self):
        # <coin-func>
        prod = self.get_production("<coin-func>")
        if prod == 46:
            self.eat("(")
            self.params()
            self.eat(")")
            self.eat("[")
            self.local_dec()
            self.ret_stmnts()
            self.eat("BACK")
            self.coin_retval()
            self.eat("!!")
            self.eat("]")
            self.sub_func()
        else:
            self.error_invalid_token("<coin-func>")

    # ==================== DIME PRODUCTIONS ====================

    def dime_tail(self):
        # <dime-tail>
        prod = self.get_production("<dime-tail>")
        if prod == 47:
            self.dime_dec()
            self.global_dec()
        elif prod == 48:
            self.dime_func()
        else:
            self.error_invalid_token("<dime-tail>")

    def dime_dec(self):
        # <dime-dec>
        prod = self.get_production("<dime-dec>")
        if prod == 49:
            self.dime_init()
            self.dime_mult()
            self.eat("!!")
        elif prod == 50:
            self.dime_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<dime-dec>")

    def dime_init(self):
        # <dime-init>
        prod = self.get_production("<dime-init>")
        if prod == 51:
            self.eat("=")
            self.dime_init_val()
        elif prod == 52:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-init>")

    def dime_mult(self):
        # <dime-mult>
        prod = self.get_production("<dime-mult>")
        if prod == 53:
            self.eat(",")
            self.eat("id")
            self.dime_init()
            self.dime_mult()
        elif prod == 54:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-mult>")

    def dime_init_val(self):
        # <dime-init-val>
        prod = self.get_production("<dime-init-val>")
        if prod == 55:
            self.dime_val()
        else:
            self.error_invalid_token("<dime-init-val>")

    def dime_val(self):
        # <dime-val>
        prod = self.get_production("<dime-val>")
        if prod == 56:
            self.dime_ope()
            self.dime_exp()
        else:
            self.error_invalid_token("<dime-val>")

    def dime_ope(self):
        # <dime-ope>
        prod = self.get_production("<dime-ope>")
        if prod == 57:
            self.eat("id")
            self.id_tail()
        elif prod == 58:
            self.eat("(")
            self.dime_val()
            self.eat(")")
        elif prod == 59:
            self.digits()
        else:
            self.error_invalid_token("<dime-ope>")

    def digits(self):
        # <digits>
        prod = self.get_production("<digits>")
        if prod == 60: self.eat("COIN-lit")
        elif prod == 61: self.eat("DIME-lit")
        else:
            self.error_invalid_token("<digits>")

    def dime_exp(self):
        # <dime-exp>
        prod = self.get_production("<dime-exp>")
        if prod == 62:
            self.arith_op()
            self.dime_ope()
            self.dime_exp()
        elif prod == 63:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-exp>")

    def dime_arr(self):
        # <dime-arr>
        prod = self.get_production("<dime-arr>")
        if prod == 64:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.dime_arr_tail()
        else:
            self.error_invalid_token("<dime-arr>")

    def dime_arr_tail(self):
        # <dime-arr-tail>
        prod = self.get_production("<dime-arr-tail>")
        if prod == 65:
            self.eat("=")
            self.eat("[")
            self.dime_arr1()
            self.eat("]")
        elif prod == 66:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.dime_arr2_tail()
        elif prod == 67:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-arr-tail>")

    def dime_arr1(self):
        # <dime-arr1>
        prod = self.get_production("<dime-arr1>")
        if prod == 68:
            self.dime_arr_val()
            self.dav_tail()
        else:
            self.error_invalid_token("<dime-arr1>")

    def dime_arr_val(self):
        # <dime-arr-val>
        prod = self.get_production("<dime-arr-val>")
        if prod == 69:
            self.dime_val()
        else:
            self.error_invalid_token("<dime-arr-val>")

    def dav_tail(self):
        # <dav-tail>
        prod = self.get_production("<dav-tail>")
        if prod == 70:
            self.eat(",")
            self.dime_arr1()
        elif prod == 71:
            pass # Lambda
        else:
            self.error_invalid_token("<dav-tail>")

    def dime_arr2_tail(self):
        # <dime-arr2-tail>
        prod = self.get_production("<dime-arr2-tail>")
        if prod == 72:
            self.eat("=")
            self.eat("[")
            self.dime_arr2()
            self.eat("]")
        elif prod == 73:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-arr2-tail>")

    def dime_arr2(self):
        # <dime-arr2>
        prod = self.get_production("<dime-arr2>")
        if prod == 74:
            self.eat("[")
            self.dime_arr1()
            self.eat("]")
            self.dav2_tail()
        else:
            self.error_invalid_token("<dime-arr2>")

    def dav2_tail(self):
        # <dav2-tail>
        prod = self.get_production("<dav2-tail>")
        if prod == 75:
            self.eat(",")
            self.dime_arr2()
        elif prod == 76:
            pass # Lambda
        else:
            self.error_invalid_token("<dav2-tail>")

    def dime_func(self):
        # <dime-func>
        prod = self.get_production("<dime-func>")
        if prod == 77:
            self.eat("(")
            self.params()
            self.eat(")")
            self.eat("[")
            self.local_dec()
            self.ret_stmnts()
            self.eat("BACK")
            self.dime_retval()
            self.eat("!!")
            self.eat("]")
            self.sub_func()
        else:
            self.error_invalid_token("<dime-func>")

    # ==================== PARCH PRODUCTIONS ====================

    def parch_tail(self):
        # <parch-tail>
        prod = self.get_production("<parch-tail>")
        if prod == 78:
            self.parch_dec()
            self.global_dec()
        elif prod == 79:
            self.parch_func()
        else:
            self.error_invalid_token("<parch-tail>")

    def parch_dec(self):
        # <parch-dec>
        prod = self.get_production("<parch-dec>")
        if prod == 80:
            self.parch_init()
            self.parch_mult()
            self.eat("!!")
        elif prod == 81:
            self.parch_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<parch-dec>")

    def parch_init(self):
        # <parch-init>
        prod = self.get_production("<parch-init>")
        if prod == 82:
            self.eat("=")
            self.parch_init_val()
        elif prod == 83:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-init>")

    def parch_mult(self):
        # <parch-mult>
        prod = self.get_production("<parch-mult>")
        if prod == 84:
            self.eat(",")
            self.eat("id")
            self.parch_init()
            self.parch_mult()
        elif prod == 85:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-mult>")

    def parch_init_val(self):
        # <parch-init-val>
        prod = self.get_production("<parch-init-val>")
        if prod == 86:
            self.parch_val()
        else:
            self.error_invalid_token("<parch-init-val>")

    def parch_val(self):
        # <parch-val>
        prod = self.get_production("<parch-val>")
        if prod == 87:
            self.eat("id")
            self.id_tail()
        elif prod == 88:
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<parch-val>")

    def parch_arr(self):
        # <parch-arr>
        prod = self.get_production("<parch-arr>")
        if prod == 89:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.parch_arr_tail()
        else:
            self.error_invalid_token("<parch-arr>")

    def parch_arr_tail(self):
        # <parch-arr-tail>
        prod = self.get_production("<parch-arr-tail>")
        if prod == 90:
            self.eat("=")
            self.eat("[")
            self.parch_arr1()
            self.eat("]")
        elif prod == 91:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.parch_arr2_tail()
        elif prod == 92:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-arr-tail>")

    def parch_arr1(self):
        # <parch-arr1>
        prod = self.get_production("<parch-arr1>")
        if prod == 93:
            self.parch_arr_val()
            self.pav_tail()
        else:
            self.error_invalid_token("<parch-arr1>")

    def parch_arr_val(self):
        # <parch-arr-val>
        prod = self.get_production("<parch-arr-val>")
        if prod == 94:
            self.parch_val()
        else:
            self.error_invalid_token("<parch-arr-val>")

    def pav_tail(self):
        # <pav-tail>
        prod = self.get_production("<pav-tail>")
        if prod == 95:
            self.eat(",")
            self.parch_arr1()
        elif prod == 96:
            pass # Lambda
        else:
            self.error_invalid_token("<pav-tail>")

    def parch_arr2_tail(self):
        # <parch-arr2-tail>
        prod = self.get_production("<parch-arr2-tail>")
        if prod == 97:
            self.eat("=")
            self.eat("[")
            self.parch_arr2()
            self.eat("]")
        elif prod == 98:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-arr2-tail>")

    def parch_arr2(self):
        # <parch-arr2>
        prod = self.get_production("<parch-arr2>")
        if prod == 99:
            self.eat("[")
            self.parch_arr1()
            self.eat("]")
            self.pav2_tail()
        else:
            self.error_invalid_token("<parch-arr2>")

    def pav2_tail(self):
        # <pav2-tail>
        prod = self.get_production("<pav2-tail>")
        if prod == 100:
            self.eat(",")
            self.parch_arr2()
        elif prod == 101:
            pass # Lambda
        else:
            self.error_invalid_token("<pav2-tail>")

    def parch_func(self):
        # <parch-func>
        prod = self.get_production("<parch-func>")
        if prod == 102:
            self.eat("(")
            self.params()
            self.eat(")")
            self.eat("[")
            self.local_dec()
            self.ret_stmnts()
            self.eat("BACK")
            self.parch_retval()
            self.eat("!!")
            self.eat("]")
            self.sub_func()
        else:
            self.error_invalid_token("<parch-func>")

    # ==================== SCROLL PRODUCTIONS ====================

    def scroll_tail(self):
        # <scroll-tail>
        prod = self.get_production("<scroll-tail>")
        if prod == 103:
            self.scroll_dec()
            self.global_dec()
        elif prod == 104:
            self.scroll_func()
            self.sub_func()
        else:
            self.error_invalid_token("<scroll-tail>")

    def scroll_dec(self):
        # <scroll-dec>
        prod = self.get_production("<scroll-dec>")
        if prod == 105:
            self.scroll_init()
            self.scroll_mult()
            self.eat("!!")
        elif prod == 106:
            self.scroll_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<scroll-dec>")

    def scroll_init(self):
        # <scroll-init>
        prod = self.get_production("<scroll-init>")
        if prod == 107:
            self.eat("=")
            self.scroll_init_val()
        elif prod == 108:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-init>")

    def scroll_mult(self):
        # <scroll-mult>
        prod = self.get_production("<scroll-mult>")
        if prod == 109:
            self.eat(",")
            self.eat("id")
            self.scroll_init()
            self.scroll_mult()
        elif prod == 110:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-mult>")

    def scroll_init_val(self):
        # <scroll-init-val>
        prod = self.get_production("<scroll-init-val>")
        if prod == 111:
            self.scroll_val()
        else:
            self.error_invalid_token("<scroll-init-val>")

    def scroll_val(self):
        # <scroll-val>
        prod = self.get_production("<scroll-val>")
        if prod == 112:
            self.scroll_ope()
            self.scroll_exp()
        else:
            self.error_invalid_token("<scroll-val>")

    def scroll_ope(self):
        # <scroll-ope>
        prod = self.get_production("<scroll-ope>")
        if prod == 113:
            self.eat("id")
            self.id_tail()
        elif prod == 114:
            self.eat("(")
            self.scroll_val()
            self.eat(")")
        elif prod == 115:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<scroll-ope>")

    def scr_char(self):
        # <scr-char>
        prod = self.get_production("<scr-char>")
        if prod == 116:
            self.eat("{")
            self.index()
            self.eat("}")
        elif prod == 117:
            pass # Lambda
        else:
            self.error_invalid_token("<scr-char>")

    def index(self):
        # <index>
        prod = self.get_production("<index>")
        if prod == 118: self.eat("id")
        elif prod == 119: self.eat("COIN-lit")
        else:
            self.error_invalid_token("<index>")

    def scroll_exp(self):
        # <scroll-exp>
        prod = self.get_production("<scroll-exp>")
        if prod == 120:
            self.concat_op()
            self.scroll_ope()
            self.scroll_exp()
        elif prod == 121:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-exp>")

    def concat_op(self):
        # <concat-op>
        prod = self.get_production("<concat-op>")
        if prod == 122: self.eat("&")
        else:
            self.error_invalid_token("<concat-op>")

    def scroll_arr(self):
        # <scroll-arr>
        prod = self.get_production("<scroll-arr>")
        if prod == 123:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.scroll_arr_tail()
        else:
            self.error_invalid_token("<scroll-arr>")

    def scroll_arr_tail(self):
        # <scroll-arr-tail>
        prod = self.get_production("<scroll-arr-tail>")
        if prod == 124:
            self.eat("=")
            self.eat("[")
            self.scroll_arr1()
            self.eat("]")
        elif prod == 125:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.scroll_arr2_tail()
        elif prod == 126:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-arr-tail>")

    def scroll_arr1(self):
        # <scroll-arr1>
        prod = self.get_production("<scroll-arr1>")
        if prod == 127:
            self.scroll_arr_val()
            self.sav_tail()
        else:
            self.error_invalid_token("<scroll-arr1>")

    def scroll_arr_val(self):
        # <scroll-arr-val>
        prod = self.get_production("<scroll-arr-val>")
        if prod == 128:
            self.scroll_val()
        else:
            self.error_invalid_token("<scroll-arr-val>")

    def sav_tail(self):
        # <sav-tail>
        prod = self.get_production("<sav-tail>")
        if prod == 129:
            self.eat(",")
            self.scroll_arr1()
        elif prod == 130:
            pass # Lambda
        else:
            self.error_invalid_token("<sav-tail>")

    def scroll_arr2_tail(self):
        # <scroll-arr2-tail>
        prod = self.get_production("<scroll-arr2-tail>")
        if prod == 131:
            self.eat("=")
            self.eat("[")
            self.scroll_arr2()
            self.eat("]")
        elif prod == 132:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-arr2-tail>")

    def scroll_arr2(self):
        # <scroll-arr2>
        prod = self.get_production("<scroll-arr2>")
        if prod == 133:
            self.eat("[")
            self.scroll_arr1()
            self.eat("]")
            self.sav2_tail()
        else:
            self.error_invalid_token("<scroll-arr2>")

    def sav2_tail(self):
        # <sav2-tail>
        prod = self.get_production("<sav2-tail>")
        if prod == 134:
            self.eat(",")
            self.scroll_arr2()
        elif prod == 135:
            pass # Lambda
        else:
            self.error_invalid_token("<sav2-tail>")

    def scroll_func(self):
        # <scroll-func>
        prod = self.get_production("<scroll-func>")
        if prod == 136:
            self.eat("(")
            self.params()
            self.eat(")")
            self.eat("[")
            self.local_dec()
            self.ret_stmnts()
            self.eat("BACK")
            self.scroll_retval()
            self.eat("!!")
            self.eat("]")
            self.sub_func()
        else:
            self.error_invalid_token("<scroll-func>")

    # ==================== BOOL PRODUCTIONS ====================

    def bool_tail(self):
        # <bool-tail>
        prod = self.get_production("<bool-tail>")
        if prod == 137:
            self.bool_dec()
            self.global_dec()
        elif prod == 138:
            self.bool_func()
        else:
            self.error_invalid_token("<bool-tail>")

    def bool_dec(self):
        # <bool-dec>
        prod = self.get_production("<bool-dec>")
        if prod == 139:
            self.bool_init()
            self.bool_mult()
            self.eat("!!")
        elif prod == 140:
            self.bool_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<bool-dec>")

    def bool_init(self):
        # <bool-init>
        prod = self.get_production("<bool-init>")
        if prod == 141:
            self.eat("=")
            self.bool_init_val()
        elif prod == 142:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-init>")

    def bool_mult(self):
        # <bool-mult>
        prod = self.get_production("<bool-mult>")
        if prod == 143:
            self.eat(",")
            self.eat("id")
            self.bool_init()
            self.bool_mult()
        elif prod == 144:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-mult>")

    def bool_init_val(self):
        # <bool-init-val>
        prod = self.get_production("<bool-init-val>")
        if prod == 145:
            self.bool_val()
        else:
            self.error_invalid_token("<bool-init-val>")

    def bool_val(self):
        # <bool-val>
        prod = self.get_production("<bool-val>")
        if prod == 146:
            self.bool_ope()
            self.bool_exp()
        else:
            self.error_invalid_token("<bool-val>")

    def bool_ope(self):
        # <bool-ope>
        prod = self.get_production("<bool-ope>")
        if prod == 147:
            self.eat("id")
            self.id_tail()
            self.bool_exp2()
        elif prod == 148:
            self.eat("(")
            self.bool_val()
            self.eat(")")
        elif prod == 149:
            self.bool_rule() # Renamed to avoid reserved word conflict
            self.log_tail()
        elif prod == 150:
            self.bool_digit()
            self.bool_arith()
            self.rel_eq()
        elif prod == 151:
            self.eat("PARCH-lit")
            self.eq_op()
            self.bool_parch()
        elif prod == 152:
            self.scroll()
            self.eq_op()
            self.bool_scroll()
            self.bool_concat()
        else:
            self.error_invalid_token("<bool-ope>")

    def bool_rule(self):
        # <bool>
        prod = self.get_production("<bool>")
        if prod == 153: self.bool_lit()
        elif prod == 154:
            self.not_op()
            self.not_val()
        else:
            self.error_invalid_token("<bool>")

    def bool_lit(self):
        # <bool-lit>
        prod = self.get_production("<bool-lit>")
        if prod == 155: self.eat("AYE")
        elif prod == 156: self.eat("NAY")
        else:
            self.error_invalid_token("<bool-lit>")

    def not_op(self):
        # <not-op>
        prod = self.get_production("<not-op>")
        if prod == 157: self.eat("!")
        elif prod == 158: self.eat("!#")
        else:
            self.error_invalid_token("<not-op>")

    def not_val(self):
        # <not-val>
        prod = self.get_production("<not-val>")
        if prod == 159:
            self.eat("id")
            self.id_tail()
        elif prod == 160:
            self.eat("(")
            self.bool_val()
            self.eat(")")
        elif prod == 161:
            self.bool_lit()
        else:
            self.error_invalid_token("<not-val>")

    def log_tail(self):
        # <log-tail>
        prod = self.get_production("<log-tail>")
        if prod == 162:
            self.eq_op()
            self.bool_ope()
        elif prod == 163:
            pass # Lambda
        else:
            self.error_invalid_token("<log-tail>")

    def bool_digit(self):
        # <bool-digit>
        prod = self.get_production("<bool-digit>")
        if prod == 164:
            self.digits()
        else:
            self.error_invalid_token("<bool-digit>")

    def bool_arith(self):
        # <bool-arith>
        prod = self.get_production("<bool-arith>")
        if prod == 165:
            self.arith_op()
            self.arel_ope()
            self.bool_arith()
        elif prod == 166:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arith>")

    def arel_ope(self):
        # <arel-ope>
        prod = self.get_production("<arel-ope>")
        if prod == 167:
            self.eat("id")
            self.id_tail()
        elif prod == 168:
            self.eat("(")
            self.dime_val()
            self.eat(")")
        elif prod == 169:
            self.eat("COIN-lit")
        elif prod == 170:
            self.eat("DIME-lit")
        else:
            self.error_invalid_token("<arel-ope>")

    def rel_eq(self):
        # <rel-eq>
        prod = self.get_production("<rel-eq>")
        if prod == 171:
            self.rel()
        elif prod == 172:
            self.eq_op()
            self.arel_ope()
        else:
            self.error_invalid_token("<rel-eq>")

    def rel(self):
        # <rel>
        prod = self.get_production("<rel>")
        if prod == 173:
            self.rel_op()
            self.arel_ope()
            self.rel_tail()
        else:
            self.error_invalid_token("<rel>")

    def rel_op(self):
        # <rel-op>
        prod = self.get_production("<rel-op>")
        if prod == 174: self.eat("<")
        elif prod == 175: self.eat(">")
        elif prod == 176: self.eat("<=")
        elif prod == 177: self.eat(">=")
        else:
            self.error_invalid_token("<rel-op>")

    def rel_tail(self):
        # <rel-tail>
        prod = self.get_production("<rel-tail>")
        if prod == 178:
            self.eq_op()
            self.bool_ope()
        elif prod == 179:
            pass # Lambda
        else:
            self.error_invalid_token("<rel-tail>")

    def eq_op(self):
        # <eq-op>
        prod = self.get_production("<eq-op>")
        if prod == 180: self.eat("==")
        elif prod == 181: self.eat("!=")
        else:
            self.error_invalid_token("<eq-op>")

    def bool_parch(self):
        # <bool-parch>
        prod = self.get_production("<bool-parch>")
        if prod == 182:
            self.parch_val()
        else:
            self.error_invalid_token("<bool-parch>")

    def scroll(self):
        # <scroll>
        prod = self.get_production("<scroll>")
        if prod == 183:
            self.eat("SCROLL-lit")
            self.scr_char()
            self.bool_concat()
        else:
            self.error_invalid_token("<scroll>")

    def bool_scroll(self):
        # <bool-scroll>
        prod = self.get_production("<bool-scroll>")
        if prod == 184:
            self.scroll_ope()
        else:
            self.error_invalid_token("<bool-scroll>")

    def bool_concat(self):
        # <bool-concat>
        prod = self.get_production("<bool-concat>")
        if prod == 185:
            self.concat()
            self.bool_concat()
        elif prod == 186:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-concat>")

    def concat(self):
        # <concat>
        prod = self.get_production("<concat>")
        if prod == 187:
            self.concat_op()
            self.bool_scroll()
        else:
            self.error_invalid_token("<concat>")

    def bool_exp2(self):
        # <bool-exp2>
        prod = self.get_production("<bool-exp2>")
        if prod == 188:
            self.bool_arith()
            self.rel()
        elif prod == 189:
            self.eq_op()
            self.eq_ope()
        elif prod == 190:
            self.concat()
            self.bool_concat()
            self.concat_tail()
        elif prod == 191:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-exp2>")

    def concat_tail(self):
        # <concat-tail>
        prod = self.get_production("<concat-tail>")
        if prod == 192:
            self.eq_op()
            self.bool_scroll()
            self.bool_concat()
        else:
            self.error_invalid_token("<concat-tail>")

    def eq_ope(self):
        # <eq-ope>
        prod = self.get_production("<eq-ope>")
        if prod == 193:
            self.value()
        else:
            self.error_invalid_token("<eq-ope>")

    def bool_exp(self):
        # <bool-exp>
        prod = self.get_production("<bool-exp>")
        if prod == 194:
            self.log_op()
            self.bool_ope()
            self.bool_exp()
        elif prod == 195:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-exp>")

    def log_op(self):
        # <log-op>
        prod = self.get_production("<log-op>")
        if prod == 196: self.eat("||")
        elif prod == 197: self.eat("&&")
        else:
            self.error_invalid_token("<log-op>")

    def bool_arr(self):
        # <bool-arr>
        prod = self.get_production("<bool-arr>")
        if prod == 198:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("bool-arr-tail")
            self.eat("!!") # Note: Grammar says !! here in prod 198
        else:
            self.error_invalid_token("<bool-arr>")

    def bool_arr_tail(self):
        # <bool-arr-tail>
        prod = self.get_production("<bool-arr-tail>")
        if prod == 199:
            self.eat("=")
            self.eat("[")
            self.bool_arr1()
            self.eat("]")
        elif prod == 200:
            self.eat("{")
            self.eat("COIN-lit")
            self.bool_arr2_tail()
        elif prod == 201:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arr-tail>")

    def bool_arr1(self):
        # <bool-arr1>
        prod = self.get_production("<bool-arr1>")
        if prod == 202:
            self.bool_arr_val()
            self.bav_tail()
        else:
            self.error_invalid_token("<bool-arr1>")

    def bav_tail(self):
        # <bav-tail>
        prod = self.get_production("<bav-tail>")
        if prod == 203:
            self.eat(",")
            self.bool_arr1()
        elif prod == 204:
            pass # Lambda
        else:
            self.error_invalid_token("<bav-tail>")

    def bool_arr_val(self):
        # <bool-arr-val>
        prod = self.get_production("<bool-arr-val>")
        if prod == 205:
            self.bool_val()
        else:
            self.error_invalid_token("<bool-arr-val>")

    def bool_arr2_tail(self):
        # <bool-arr2-tail>
        prod = self.get_production("<bool-arr2-tail>")
        if prod == 206:
            self.eat("=")
            self.eat("[")
            self.bool_arr2()
            self.eat("]")
        elif prod == 207:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arr2-tail>")

    def bool_arr2(self):
        # <bool-arr2>
        prod = self.get_production("<bool-arr2>")
        if prod == 208:
            self.eat("[")
            self.bool_arr1()
            self.eat("]")
            self.bav2_tail()
        else:
            self.error_invalid_token("<bool-arr2>")

    def bav2_tail(self):
        # <bav2-tail>
        prod = self.get_production("<bav2-tail>")
        if prod == 209:
            self.eat(",")
            self.bool_arr2()
        elif prod == 210:
            pass # Lambda
        else:
            self.error_invalid_token("<bav2-tail>")

    def bool_func(self):
        # <bool-func>
        prod = self.get_production("<bool-func>")
        if prod == 211:
            self.eat("(")
            self.params()
            self.eat(")")
            self.eat("[")
            self.local_dec()
            self.ret_stmnts()
            self.eat("BACK")
            self.bool_retval()
            self.eat("!!")
            self.eat("]")
            self.sub_func()
        else:
            self.error_invalid_token("<bool-func>")

    # ==================== COMMON FUNCTION PARAMS ====================

    def params(self):
        # <params>
        prod = self.get_production("<params>")
        if prod == 212:
            self.d_type()
            self.eat("id")
            self.param_mult()
        else:
            # Not nullable in grammar, but usually empty params are handled via Lambda in parent
            # Assuming strictly as per grammar prod 212
             self.error_invalid_token("<params>")

    def param_mult(self):
        # <param-mult>
        prod = self.get_production("<param-mult>")
        if prod == 213:
            self.eat(",")
            self.params()
        elif prod == 214:
            pass # Lambda
        else:
            self.error_invalid_token("<param-mult>")

    def d_type(self):
        # <d-type>
        prod = self.get_production("<d-type>")
        if prod == 215: self.eat("COIN")
        elif prod == 216: self.eat("DIME")
        elif prod == 217: self.eat("PARCH")
        elif prod == 218: self.eat("SCROLL")
        elif prod == 219: self.eat("BOOL")
        else:
            self.error_invalid_token("<d-type>")

    def ret_stmnts(self):
        # <ret-stmnts>
        prod = self.get_production("<ret-stmnts>")
        if prod == 220:
            self.stmnt_tail()
        else:
            self.error_invalid_token("<ret-stmnts>")

    def coin_retval(self):
        # <coin-retval>
        prod = self.get_production("<coin-retval>")
        if prod == 221: self.coin_val()
        else: self.error_invalid_token("<coin-retval>")

    def dime_retval(self):
        # <dime-retval>
        prod = self.get_production("<dime-retval>")
        if prod == 222: self.dime_val()
        else: self.error_invalid_token("<dime-retval>")
        
    def parch_retval(self):
        # <parch-retval>
        prod = self.get_production("<parch-retval>")
        if prod == 223: self.parch_val()
        else: self.error_invalid_token("<parch-retval>")

    def scroll_retval(self):
        # <scroll-retval>
        prod = self.get_production("<scroll-retval>")
        if prod == 224: self.scroll_val()
        else: self.error_invalid_token("<scroll-retval>")

    def bool_retval(self):
        # <bool-retval>
        prod = self.get_production("<bool-retval>")
        if prod == 225: self.bool_val()
        else: self.error_invalid_token("<bool-retval>")

    # ==================== ID TAILS & ELEMENTS ====================

    def id_tail(self):
        # <id-tail>
        prod = self.get_production("<id-tail>")
        if prod == 226: self.elmt()
        elif prod == 227: self.mem()
        elif prod == 228: self.func()
        else: self.error_invalid_token("<id-tail>")

    def elmt(self):
        # <elmt>
        prod = self.get_production("<elmt>")
        if prod == 229:
            self.eat("{")
            self.index()
            self.eat("}")
            self.elmt_tail()
        else:
            self.error_invalid_token("<elmt>")

    def elmt_tail(self):
        # <elmt-tail>
        prod = self.get_production("<elmt-tail>")
        if prod == 230:
            self.eat("{")
            self.index()
            self.eat("}")
        elif prod == 231:
            pass # Lambda
        else:
            self.error_invalid_token("<elmt-tail>")

    def mem(self):
        # <mem>
        prod = self.get_production("<mem>")
        if prod == 232:
            self.eat("$")
            self.eat("id")
        else:
            self.error_invalid_token("<mem>")

    def func(self):
        # <func>
        prod = self.get_production("<func>")
        if prod == 233:
            self.eat("(")
            self.args()
            self.eat(")")
        else:
            self.error_invalid_token("<func>")

    def args(self):
        # <args>
        prod = self.get_production("<args>")
        if prod == 234:
            self.args_val()
            self.args_mult()
        elif prod == 235:
            pass # Lambda
        else:
            self.error_invalid_token("<args>")

    def args_val(self):
        # <args-val>
        prod = self.get_production("<args-val>")
        if prod == 236:
            self.value()
        else:
            self.error_invalid_token("<args-val>")

    def args_mult(self):
        # <args-mult>
        prod = self.get_production("<args-mult>")
        if prod == 237:
            self.eat(",")
            self.args()
        elif prod == 238:
            pass # Lambda
        else:
            self.error_invalid_token("<args-mult>")

    # ==================== GENERAL VALUES & EXPRESSIONS ====================

    def var_val(self):
        # <var-val>
        prod = self.get_production("<var-val>")
        if prod == 239:
            self.value()
        else:
            self.error_invalid_token("<var-val>")

    def value(self):
        # <value>
        prod = self.get_production("<value>")
        if prod == 240:
            self.eat("id")
            self.id_tail()
            self.var_exp()
        elif prod == 241:
            self.eat("(")
            self.value()
            self.eat(")")
            self.var_exp()
        elif prod == 242:
            self.var_digit()
            self.digit_tail()
        elif prod == 243:
            self.eat("PARCH-lit")
            self.eq_parch()
        elif prod == 244:
            self.eat("SCROLL-lit")
            self.scr_char()
            self.var_scroll()
            self.eq_scroll()
        elif prod == 245:
            self.var_bool()
        else:
            self.error_invalid_token("<value>")

    def var_digit(self):
        # <var-digit>
        prod = self.get_production("<var-digit>")
        if prod == 246: self.eat("COIN-lit")
        elif prod == 247: self.eat("DIME-lit")
        else:
            self.error_invalid_token("<var-digit>")

    def digit_tail(self):
        # <digit-tail>
        prod = self.get_production("<digit-tail>")
        if prod == 248:
            self.var_arith()
            self.var_releq()
        elif prod == 249:
            pass # Lambda
        else:
            self.error_invalid_token("<digit-tail>")

    def var_arith(self):
        # <var-arith>
        prod = self.get_production("<var-arith>")
        if prod == 250:
            self.arith_op()
            self.arel_ope()
            self.var_arith()
        elif prod == 251:
            pass # Lambda
        else:
            self.error_invalid_token("<var-arith>")

    def var_releq(self):
        # <var-releq>
        prod = self.get_production("<var-releq>")
        if prod == 252:
            self.var_rel()
        elif prod == 253:
            self.eq_op()
            self.arel_ope()
            self.var_log()
        elif prod == 254:
            pass # Lambda
        else:
            self.error_invalid_token("<var-releq>")

    def var_rel(self):
        # <var-rel>
        prod = self.get_production("<var-rel>")
        if prod == 255:
            self.rel_op()
            self.arel_ope()
            self.var_arith()
            self.var_logeq()
        elif prod == 256:
            pass # Lambda
        else:
            self.error_invalid_token("<var-rel>")

    def var_logeq(self):
        # <var-logeq>
        prod = self.get_production("<var-logeq>")
        if prod == 257:
            self.logeq_op()
            self.log_ope()
            self.var_log()
        elif prod == 258:
            pass # Lambda
        else:
            self.error_invalid_token("<var-logeq>")

    def logeq_op(self):
        # <logeq-op>
        prod = self.get_production("<logeq-op>")
        if prod == 259: self.log_op()
        elif prod == 260: self.eq_op()
        else:
            self.error_invalid_token("<logeq-op>")

    def var_log(self):
        # <var-log>
        prod = self.get_production("<var-log>")
        if prod == 261:
            self.log_op()
            self.log_ope()
            self.var_log()
        elif prod == 262:
            pass # Lambda
        else:
            self.error_invalid_token("<var-log>")

    def log_ope(self):
        # <log-ope>
        prod = self.get_production("<log-ope>")
        if prod == 263:
            self.bool_ope()
        else:
            self.error_invalid_token("<log-ope>")

    def eq_parch(self):
        # <eq-parch>
        prod = self.get_production("<eq-parch>")
        if prod == 264:
            self.eq_op()
            self.eat("PARCH-lit")
            self.var_log()
        elif prod == 265:
            pass # Lambda
        else:
            self.error_invalid_token("<eq-parch>")

    def eq_scroll(self):
        # <eq-scroll>
        prod = self.get_production("<eq-scroll>")
        if prod == 266:
            self.eq_op()
            self.bool_scroll()
            self.bool_concat()
            self.var_log()
        elif prod == 267:
            pass # Lambda
        else:
            self.error_invalid_token("<eq-scroll>")

    def var_scroll(self):
        # <var-scroll>
        prod = self.get_production("<var-scroll>")
        if prod == 268:
            self.concat_op()
            self.concat_ope()
            self.var_scroll()
        elif prod == 269:
            pass # Lambda
        else:
            self.error_invalid_token("<var-scroll>")

    def concat_ope(self):
        # <concat-ope>
        prod = self.get_production("<concat-ope>")
        if prod == 270:
            self.scroll_ope()
        else:
            self.error_invalid_token("<concat-ope>")

    def var_bool(self):
        # <var-bool>
        prod = self.get_production("<var-bool>")
        if prod == 271:
            self.bool_rule()
        else:
            self.error_invalid_token("<var-bool>")

    def var_exp(self):
        # <var-exp>
        prod = self.get_production("<var-exp>")
        if prod == 272:
            self.expressions()
        elif prod == 273:
            pass # Lambda
        else:
            self.error_invalid_token("<var-exp>")

    def expressions(self):
        # <expressions>
        prod = self.get_production("<expressions>")
        if prod == 274:
            self.var_arith()
            self.var_rel()
        elif prod == 275:
            self.log_op()
            self.log_ope()
            self.var_log()
        elif prod == 276:
            self.eq_op()
            self.eq_ope()
            self.var_log()
        elif prod == 277:
            self.concat_op()
            self.concat_ope()
            self.var_scroll()
            self.eq_scroll()
        else:
            self.error_invalid_token("<expressions>")

    # ==================== CONSTANT DECLARATIONS (LOCKE) ====================

    def const(self):
        # <const>
        prod = self.get_production("<const>")
        if prod == 278:
            self.eat("LOCKE")
            self.const_init()
            self.eat("!!")
        else:
            self.error_invalid_token("<const>")

    def const_init(self):
        # <const-init>
        prod = self.get_production("<const-init>")
        if prod == 279:
            self.eat("COIN")
            self.coin_locke()
            self.coin_locke_mult()
        elif prod == 280:
            self.eat("DIME")
            self.dime_locke()
            self.dime_locke_mult()
        elif prod == 281:
            self.eat("PARCH")
            self.parch_locke()
            self.parch_locke_mult()
        elif prod == 282:
            self.eat("SCROLL")
            self.scroll_locke()
            self.scroll_locke_mult()
        elif prod == 283:
            self.eat("BOOL")
            self.bool_locke()
            self.bool_locke_mult()
        else:
            self.error_invalid_token("<const-init>")

    def coin_locke(self):
        # <coin-locke>
        prod = self.get_production("<coin-locke>")
        if prod == 284:
            self.eat("id")
            self.eat("=")
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<coin-locke>")

    def coin_locke_mult(self):
        # <coin-locke-mult>
        prod = self.get_production("<coin-locke-mult>")
        if prod == 285:
            self.eat(",")
            self.coin_locke()
            self.coin_locke_mult()
        elif prod == 286:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-locke-mult>")

    def dime_locke(self):
        # <dime-locke>
        prod = self.get_production("<dime-locke>")
        if prod == 287:
            self.eat("id")
            self.eat("=")
            self.locke_digit()
        else:
            self.error_invalid_token("<dime-locke>")

    def locke_digit(self):
        # <locke-digit>
        prod = self.get_production("<locke-digit>")
        if prod == 288:
            self.digits()
        else:
            self.error_invalid_token("<locke-digit>")

    def dime_locke_mult(self):
        # <dime-locke-mult>
        prod = self.get_production("<dime-locke-mult>")
        if prod == 289:
            self.eat(",")
            self.dime_locke()
            self.dime_locke_mult()
        elif prod == 290:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-locke-mult>")

    def parch_locke(self):
        # <parch-locke>
        prod = self.get_production("<parch-locke>")
        if prod == 291:
            self.eat("id")
            self.eat("=")
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<parch-locke>")

    def parch_locke_mult(self):
        # <parch-locke-mult>
        prod = self.get_production("<parch-locke-mult>")
        if prod == 292:
            self.eat(",")
            self.parch_locke()
            self.parch_locke_mult()
        elif prod == 293:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-locke-mult>")

    def scroll_locke(self):
        # <scroll-locke>
        prod = self.get_production("<scroll-locke>")
        if prod == 294:
            self.eat("id")
            self.eat("=")
            self.eat("SCROLL-lit")
            self.scr_id()
        else:
            self.error_invalid_token("<scroll-locke>")

    def scr_id(self):
        # <scr-id>
        prod = self.get_production("<scr-id>")
        if prod == 295:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
        elif prod == 296:
            pass # Lambda
        else:
            self.error_invalid_token("<scr-id>")

    def scroll_locke_mult(self):
        # <scroll-locke-mult>
        prod = self.get_production("<scroll-locke-mult>")
        if prod == 297:
            self.eat(",")
            self.scroll_locke()
            self.scroll_locke_mult()
        elif prod == 298:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-locke-mult>")

    def bool_locke(self):
        # <bool-locke>
        prod = self.get_production("<bool-locke>")
        if prod == 299:
            self.eat("id")
            self.eat("=")
            self.locke_bool()
        else:
            self.error_invalid_token("<bool-locke>")

    def locke_bool(self):
        # <locke-bool>
        prod = self.get_production("<locke-bool>")
        if prod == 300:
            self.bool_lit()
        else:
            self.error_invalid_token("<locke-bool>")

    def bool_locke_mult(self):
        # <bool-locke-mult>
        prod = self.get_production("<bool-locke-mult>")
        if prod == 301:
            self.eat(",")
            self.bool_locke()
            self.bool_locke_mult()
        elif prod == 302:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-locke-mult>")

    # ==================== STRUCT & SUB-FUNCS ====================

    def struct(self):
        # <struct>
        prod = self.get_production("<struct>")
        if prod == 303:
            self.eat("MAST")
            self.eat("id")
            self.eat("[")
            self.mem_dec()
            self.mem_dec_tail()
            self.eat("]")
            self.eat("!!")
            self.struct()
            self.sub_func()
        elif prod == 304:
            pass # Lambda
        else:
            self.error_invalid_token("<struct>")

    def mem_dec(self):
        # <mem-dec>
        prod = self.get_production("<mem-dec>")
        if prod == 305:
            self.d_type()
            self.eat("id")
            self.mem_mult()
            self.eat("!!")
        else:
            self.error_invalid_token("<mem-dec>")

    def mem_mult(self):
        # <mem-mult>
        prod = self.get_production("<mem-mult>")
        if prod == 306:
            self.eat(",")
            self.eat("id")
            self.mem_mult()
        elif prod == 307:
            pass # Lambda
        else:
            self.error_invalid_token("<mem-mult>")

    def mem_dec_tail(self):
        # <mem-dec-tail>
        prod = self.get_production("<mem-dec-tail>")
        if prod == 308:
            self.mem_dec()
            self.mem_dec_tail()
        elif prod == 309:
            pass # Lambda
        else:
            self.error_invalid_token("<mem-dec-tail>")

    def sub_func(self):
        # <sub-func>
        prod = self.get_production("<sub-func>")
        if prod == 310: self.return_func()
        elif prod == 311: self.nonreturn_func()
        elif prod == 312: pass # Lambda
        else:
            self.error_invalid_token("<sub-func>")

    def return_func(self):
        # <return-func>
        prod = self.get_production("<return-func>")
        if prod == 313: 
            self.eat("COIN")
            self.eat("id")
            self.coin_func()
        elif prod == 314:
            self.eat("DIME")
            self.eat("id")
            self.dime_func()
        elif prod == 315:
            self.eat("PARCH")
            self.eat("id")
            self.parch_func()
        elif prod == 316:
            self.eat("SCROLL")
            self.eat("id")
            self.scroll_func()
        elif prod == 317:
            self.eat("BOOL")
            self.eat("id")
            self.bool_func()
        else:
            self.error_invalid_token("<return-func>")

    def nonreturn_func(self):
        # <nonreturn-func>
        prod = self.get_production("<nonreturn-func>")
        if prod == 318:
            self.eat("ABYSS")
            self.eat("id")
            self.eat("(")
            self.params()
            self.eat(")")
            self.eat("[")
            self.local_dec()
            self.nonret_stmnts()
            self.nonret_back()
            self.eat("]")
            self.sub_func()
        else:
            self.error_invalid_token("<nonreturn-func>")

    def nonret_stmnts(self):
        # <nonret-stmnts>
        prod = self.get_production("<nonret-stmnts>")
        if prod == 319:
            self.stmnt_tail()
        else:
            self.error_invalid_token("<nonret-stmnts>")

    def nonret_back(self):
        # <nonret-back>
        prod = self.get_production("<nonret-back>")
        if prod == 320:
            self.eat("BACK")
            self.eat("!!")
        elif prod == 321:
            pass # Lambda
        else:
            self.error_invalid_token("<nonret-back>")

    def local_dec(self):
        # <local-dec>
        prod = self.get_production("<local-dec>")
        if prod == 322:
            self.var_arr()
            self.local_dec()
        elif prod == 323:
            self.struct_dec()
        elif prod == 324:
            pass # Lambda
        else:
            self.error_invalid_token("<local-dec>")

    def var_arr(self):
        # <var-arr>
        prod = self.get_production("<var-arr>")
        if prod == 325:
            self.eat("COIN")
            self.eat("id")
            self.coin_local()
        elif prod == 326:
            self.eat("DIME")
            self.eat("id")
            self.dime_local()
        elif prod == 327:
            self.eat("PARCH")
            self.eat("id")
            self.parch_local()
        elif prod == 328:
            self.eat("SCROLL")
            self.eat("id")
            self.scroll_local()
        elif prod == 329:
            self.eat("BOOL")
            self.eat("id")
            self.bool_local()
        else:
            self.error_invalid_token("<var-arr>")

    def coin_local(self):
        # <coin-local>
        prod = self.get_production("<coin-local>")
        if prod == 330: self.coin_dec()
        else: self.error_invalid_token("<coin-local>")

    def dime_local(self):
        # <dime-local>
        prod = self.get_production("<dime-local>")
        if prod == 331: self.dime_dec()
        else: self.error_invalid_token("<dime-local>")

    def parch_local(self):
        # <parch-local>
        prod = self.get_production("<parch-local>")
        if prod == 332: self.parch_dec()
        else: self.error_invalid_token("<parch-local>")

    def scroll_local(self):
        # <scroll-local>
        prod = self.get_production("<scroll-local>")
        if prod == 333: self.scroll_dec()
        else: self.error_invalid_token("<scroll-local>")

    def bool_local(self):
        # <bool-local>
        prod = self.get_production("<bool-local>")
        if prod == 334: self.bool_dec()
        else: self.error_invalid_token("<bool-local>")

    def struct_dec(self):
        # <struct-dec>
        prod = self.get_production("<struct-dec>")
        if prod == 335:
            self.eat("MAST")
            self.eat("id")
            self.eat("id")
            self.str_dec_init()
            self.eat("!!")
            self.struct_dec()
        elif prod == 336:
            pass # Lambda
        else:
            self.error_invalid_token("<struct-dec>")

    def str_dec_init(self):
        # <str-dec-init>
        prod = self.get_production("<str-dec-init>")
        if prod == 337:
            self.eat(",")
            self.eat("id")
            self.str_dec_tail()
        elif prod == 338:
            self.eat("=")
            self.eat("[")
            self.str_val()
            self.str_val_tail()
            self.eat("]")
        elif prod == 339:
            pass # Lambda
        else:
            self.error_invalid_token("<str-dec-init>")

    def str_dec_tail(self):
        # <str-dec-tail>
        prod = self.get_production("<str-dec-tail>")
        if prod == 340:
            self.eat(",")
            self.eat("id")
            self.str_dec_tail()
        elif prod == 341:
            pass # Lambda
        else:
            self.error_invalid_token("<str-dec-tail>")

    def str_val(self):
        # <str-val>
        prod = self.get_production("<str-val>")
        if prod == 342:
            self.var_val()
        elif prod == 343:
            self.eat("$")
            self.eat("id")
            self.eat("=")
            self.var_val()
        else:
            self.error_invalid_token("<str-val>")

    def str_val_tail(self):
        # <str-val-tail>
        prod = self.get_production("<str-val-tail>")
        if prod == 344:
            self.eat(",")
            self.str_val()
            self.str_val_tail()
        elif prod == 345:
            pass # Lambda
        else:
            self.error_invalid_token("<str-val-tail>")

    # ==================== STATEMENTS ====================

    def ahoy_stmnts(self):
        # <ahoy-stmnts>
        prod = self.get_production("<ahoy-stmnts>")
        if prod == 346:
            self.statements()
        else:
            self.error_invalid_token("<ahoy-stmnts>")

    def statements(self):
        # <statements>
        prod = self.get_production("<statements>")
        if prod == 347: self.assign_stmnt()
        elif prod == 348: self.ask_stmnt()
        elif prod == 349: self.echo_stmnt()
        elif prod == 350: self.look_stmnt()
        elif prod == 351: self.chart_stmnt()
        elif prod == 352: self.hoist_stmnt()
        elif prod == 353: self.heave_stmnt()
        elif prod == 354: self.haul_stmnt()
        elif prod == 355:
            self.unary_exp()
            self.eat("!!")
        else:
            self.error_invalid_token("<statements>")

    def stmnt_tail(self):
        # <stmnt-tail>
        prod = self.get_production("<stmnt-tail>")
        if prod == 356:
            self.statements()
            self.stmnt_tail()
        elif prod == 357:
            pass # Lambda
        else:
            self.error_invalid_token("<stmnt-tail>")

    def assign_stmnt(self):
        # <assign-stmnt>
        prod = self.get_production("<assign-stmnt>")
        if prod == 358:
            self.eat("id")
            self.assign_tail()
            self.eat("!!")
        else:
            self.error_invalid_token("<assign-stmnt>")

    def assign_tail(self):
        # <assign-tail>
        prod = self.get_production("<assign-tail>")
        if prod == 359:
            self.arr_str()
            self.assign_body()
        elif prod == 360:
            self.eat("(")
            self.args()
            self.eat(")")
        else:
            self.error_invalid_token("<assign-tail>")

    def arr_str(self):
        # <arr-str>
        prod = self.get_production("<arr-str>")
        if prod == 361:
            self.eat("{")
            self.index()
            self.eat("}")
            self.elmt_tail2()
        elif prod == 362:
            self.eat("$")
            self.eat("id")
        elif prod == 363:
            pass # Lambda
        else:
            self.error_invalid_token("<arr-str>")

    def elmt_tail2(self):
        # <elmt-tail2>
        prod = self.get_production("<elmt-tail2>")
        if prod == 364:
            self.eat("{")
            self.index()
            self.eat("}")
        elif prod == 365:
            pass # Lambda
        else:
            self.error_invalid_token("<elmt-tail2>")

    def assign_body(self):
        # <assign-body>
        prod = self.get_production("<assign-body>")
        if prod == 366:
            self.eat("=")
            self.assign_val()
        elif prod == 367:
            self.arith_assign_op()
            self.arith_ope()
            self.arith_tail()
        else:
            self.error_invalid_token("<assign-body>")

    def assign_val(self):
        # <assign-val>
        prod = self.get_production("<assign-val>")
        if prod == 368:
            self.var_val()
        else:
            self.error_invalid_token("<assign-val>")

    def arith_assign_op(self):
        # <arith-assign-op>
        prod = self.get_production("<arith-assign-op>")
        if prod == 369: self.eat("+=")
        elif prod == 370: self.eat("-=")
        elif prod == 371: self.eat("*=")
        elif prod == 372: self.eat("/=")
        elif prod == 373: self.eat("%=")
        elif prod == 374: self.eat("^=")
        else:
            self.error_invalid_token("<arith-assign-op>")

    def arith_ope(self):
        # <arith-ope>
        prod = self.get_production("<arith-ope>")
        if prod == 375:
            self.dime_ope()
        else:
            self.error_invalid_token("<arith-ope>")

    def arith_tail(self):
        # <arith-tail>
        prod = self.get_production("<arith-tail>")
        if prod == 376:
            self.arith_op()
            self.arith_ope()
            self.arith_tail()
        elif prod == 377:
            pass # Lambda
        else:
            self.error_invalid_token("<arith-tail>")

    def ask_stmnt(self):
        # <ask-stmnt>
        prod = self.get_production("<ask-stmnt>")
        if prod == 378:
            self.eat("ASK")
            self.eat("(")
            self.eat("SCROLL-lit")
            self.eat(",")
            self.addr()
            self.eat(")")
            self.eat("!!")
        else:
            self.error_invalid_token("<ask-stmnt>")

    def addr(self):
        # <addr>
        prod = self.get_production("<addr>")
        if prod == 379:
            self.eat("@")
            self.eat("id")
            self.id_addr()
            self.addr_tail()
        else:
            self.error_invalid_token("<addr>")

    def id_addr(self):
        # <id-addr>
        prod = self.get_production("<id-addr>")
        if prod == 380: self.arr_str()
        elif prod == 381: pass # Lambda
        else: self.error_invalid_token("<id-addr>")

    def addr_tail(self):
        # <addr-tail>
        prod = self.get_production("<addr-tail>")
        if prod == 382:
            self.eat(",")
            self.addr()
        elif prod == 383:
            pass # Lambda
        else:
            self.error_invalid_token("<addr-tail>")

    def echo_stmnt(self):
        # <echo-stmnt>
        prod = self.get_production("<echo-stmnt>")
        if prod == 384:
            self.eat("ECHO")
            self.eat("(")
            self.eat("SCROLL-lit")
            self.echo_arg()
            self.eat(")")
            self.eat("!!")
        else:
            self.error_invalid_token("<echo-stmnt>")

    def echo_arg(self):
        # <echo-arg>
        prod = self.get_production("<echo-arg>")
        if prod == 385:
            self.eat(",")
            self.echo_val()
            self.echo_arg()
        elif prod == 386:
            pass # Lambda
        else:
            self.error_invalid_token("<echo-arg>")

    def echo_val(self):
        # <echo-val>
        prod = self.get_production("<echo-val>")
        if prod == 387:
            self.var_val()
        else:
            self.error_invalid_token("<echo-val>")

    def look_stmnt(self):
        # <look-stmnt>
        prod = self.get_production("<look-stmnt>")
        if prod == 388:
            self.eat("LOOK")
            self.eat("(")
            self.condition()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.eat("]")
            self.look_tail()
        else:
            self.error_invalid_token("<look-stmnt>")

    def condition(self):
        # <condition>
        prod = self.get_production("<condition>")
        if prod == 389:
            self.bool_val()
        else:
            self.error_invalid_token("<condition>")

    def look_body(self):
        # <look-body>
        prod = self.get_production("<look-body>")
        if prod == 390:
            self.stmnt_tail()
            self.jump_stmnt()
        else:
            self.error_invalid_token("<look-body>")

    def jump_stmnt(self):
        # <jump-stmnt>
        prod = self.get_production("<jump-stmnt>")
        if prod == 391:
            self.eat("SAIL")
            self.eat("!!")
        elif prod == 392:
            self.eat("LAND")
            self.eat("!!")
        elif prod == 393:
            pass # Lambda
        else:
            self.error_invalid_token("<jump-stmnt>")

    def look_tail(self):
        # <look-tail>
        prod = self.get_production("<look-tail>")
        if prod == 394:
            self.eat("DROPLOOK")
            self.eat("(")
            self.condition()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.eat("]")
            self.look_tail()
        elif prod == 395:
            self.eat("DROP")
            self.eat("[")
            self.look_body()
            self.eat("]")
        elif prod == 396:
            pass # Lambda
        else:
            self.error_invalid_token("<look-tail>")

    def chart_stmnt(self):
        # <chart-stmnt>
        prod = self.get_production("<chart-stmnt>")
        if prod == 397:
            self.eat("CHART")
            self.eat("(")
            self.chart_cond()
            self.eat(")")
            self.eat("[")
            self.courses()
            self.course_tail()
            self.adrift_case()
            self.eat("]")
        else:
            self.error_invalid_token("<chart-stmnt>")

    def chart_cond(self):
        # <chart-cond>
        prod = self.get_production("<chart-cond>")
        if prod == 398: self.eat("id")
        elif prod == 399: self.chart_const()
        else:
            self.error_invalid_token("<chart-cond>")

    def chart_const(self):
        # <chart-const>
        prod = self.get_production("<chart-const>")
        if prod == 400: self.eat("COIN-lit")
        elif prod == 401: self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<chart-const>")

    def courses(self):
        # <courses>
        prod = self.get_production("<courses>")
        if prod == 402:
            self.eat("COURSE")
            self.chart_const()
            self.eat(":")
            self.course_body()
        else:
            self.error_invalid_token("<courses>")

    def course_body(self):
        # <course-body>
        prod = self.get_production("<course-body>")
        if prod == 403:
            self.stmnt_tail()
            self.jump_stmnt()
        else:
            self.error_invalid_token("<course-body>")

    def course_tail(self):
        # <course-tail>
        prod = self.get_production("<course-tail>")
        if prod == 404:
            self.courses()
            self.course_tail()
        elif prod == 405:
            pass # Lambda
        else:
            self.error_invalid_token("<course-tail>")

    def adrift_case(self):
        # <adrift-case>
        prod = self.get_production("<adrift-case>")
        if prod == 406:
            self.eat("ADRIFT")
            self.eat(":")
            self.adrift_body()
            self.eat("LAND")
            self.eat("!!")
        elif prod == 407:
            pass # Lambda
        else:
            self.error_invalid_token("<adrift-case>")

    def adrift_body(self):
        # <adrift-body>
        prod = self.get_production("<adrift-body>")
        if prod == 408:
            self.stmnt_tail()
        else:
            self.error_invalid_token("<adrift-body>")

    def hoist_stmnt(self):
        # <hoist-stmnt>
        prod = self.get_production("<hoist-stmnt>")
        if prod == 409:
            self.eat("HOIST")
            self.eat("(")
            self.init()
            self.eat("!!")
            self.hoist_cond()
            self.eat("!!")
            self.inc_dec()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.eat("]")
        else:
            self.error_invalid_token("<hoist-stmnt>")

    def init(self):
        # <init>
        prod = self.get_production("<init>")
        if prod == 410:
            self.eat("COIN")
            self.eat("id")
            self.eat("=")
            self.eat("COIN-lit")
            self.init1()
        elif prod == 411:
            self.eat("id")
            self.id_init()
            self.eat("=")
            self.eat("COIN-lit")
            self.init2()
        elif prod == 412:
            pass # Lambda
        else:
            self.error_invalid_token("<init>")

    def id_init(self):
        # <id-init>
        prod = self.get_production("<id-init>")
        if prod == 413:
            self.arr_str()
        else:
            self.error_invalid_token("<id-init>")

    def init1(self):
        # <init1>
        prod = self.get_production("<init1>")
        if prod == 414:
            self.eat(",")
            self.eat("id")
            self.eat("=")
            self.eat("COIN-lit")
            self.init1()
        elif prod == 415:
            pass # Lambda
        else:
            self.error_invalid_token("<init1>")

    def init2(self):
        # <init2>
        prod = self.get_production("<init2>")
        if prod == 416:
            self.eat(",")
            self.eat("id")
            self.arr_str()
            self.eat("=")
            self.var_val()
            self.init2()
        elif prod == 417:
            pass # Lambda
        else:
            self.error_invalid_token("<init2>")

    def hoist_cond(self):
        # <hoist-cond>
        prod = self.get_production("<hoist-cond>")
        if prod == 418:
            self.eat("id")
            self.id_cond()
            self.releq_op()
            self.hoist_ope()
            self.hoist_log()
        else:
            self.error_invalid_token("<hoist-cond>")

    def id_cond(self):
        # <id-cond>
        prod = self.get_production("<id-cond>")
        if prod == 419:
            self.arr_str()
        else:
            self.error_invalid_token("<id-cond>")

    def releq_op(self):
        # <releq-op>
        prod = self.get_production("<releq-op>")
        if prod == 420: self.rel_op()
        elif prod == 421: self.eq_op()
        else:
            self.error_invalid_token("<releq-op>")

    def hoist_ope(self):
        # <hoist-ope>
        prod = self.get_production("<hoist-ope>")
        if prod == 422:
            self.eat("id")
            self.id_tail()
        elif prod == 423:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<hoist-ope>")

    def hoist_log(self):
        # <hoist-log>
        prod = self.get_production("<hoist-log>")
        if prod == 424:
            self.log_op()
            self.hoist_cond()
        elif prod == 425:
            pass # Lambda
        else:
            self.error_invalid_token("<hoist-log>")

    def inc_dec(self):
        # <inc-dec>
        prod = self.get_production("<inc-dec>")
        if prod == 426:
            self.in_de()
            self.in_de2()
        else:
            self.error_invalid_token("<inc-dec>")

    def in_de(self):
        # <in-de>
        prod = self.get_production("<in-de>")
        if prod == 427:
            self.unary_exp()
        elif prod == 428:
            self.eat("id")
            self.arr_str()
            self.arith_assign_op()
            self.arith_ope()
            self.arith_tail()
        else:
            self.error_invalid_token("<in-de>")

    def in_de2(self):
        # <in-de2>
        prod = self.get_production("<in-de2>")
        if prod == 429:
            self.eat(",")
            self.in_de()
            self.in_de2()
        elif prod == 430:
            pass # Lambda
        else:
            self.error_invalid_token("<in-de2>")

    def heave_stmnt(self):
        # <heave-stmnt>
        prod = self.get_production("<heave-stmnt>")
        if prod == 431:
            self.eat("HEAVE")
            self.eat("(")
            self.condition()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.eat("]")
        else:
            self.error_invalid_token("<heave-stmnt>")

    def haul_stmnt(self):
        # <haul-stmnt>
        prod = self.get_production("<haul-stmnt>")
        if prod == 432:
            self.eat("HAUL")
            self.eat("[")
            self.look_body()
            self.eat("]")
            self.eat("HEAVE")
            self.eat("(")
            self.condition()
            self.eat(")")
            self.eat("!!")
        else:
            self.error_invalid_token("<haul-stmnt>")

    def unary_exp(self):
        # <unary-exp>
        prod = self.get_production("<unary-exp>")
        if prod == 433:
            self.unary_op()
            self.eat("id")
        else:
            self.error_invalid_token("<unary-exp>")

    def unary_op(self):
        # <unary-op>
        prod = self.get_production("<unary-op>")
        if prod == 434: self.eat("+#")
        elif prod == 435: self.eat("-#")
        else:
            self.error_invalid_token("<unary-op>")