# syn_parser.py
import sys
from syntax.Predict_Set import PREDICT
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
    # GRAMMAR PRODUCTIONS (1 - 573)
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
            self.coin_var_arr_func()
        elif prod == 8:
            self.eat("DIME")
            self.eat("id")
            self.dime_var_arr_func()
        elif prod == 9:
            self.eat("PARCH")
            self.eat("id")
            self.parch_var_arr_func()
        elif prod == 10:
            self.eat("SCROLL")
            self.eat("id")
            self.scroll_var_arr_func()
        elif prod == 11:
            self.eat("BOOL")
            self.eat("id")
            self.bool_var_arr_func()
        else:
            self.error_invalid_token("<var-arr-func>")

    # ==================== COIN PRODUCTIONS ====================

    def coin_var_arr_func(self):
        # <coin-var-arr-func>
        prod = self.get_production("<coin-var-arr-func>")
        if prod == 12:
            self.coin_var_arr()
            self.global_dec()
        elif prod == 13:
            self.coin_func()
        else:
            self.error_invalid_token("<coin-var-arr-func>")

    def coin_var_arr(self):
        # <coin-var-arr>
        prod = self.get_production("<coin-var-arr>")
        if prod == 14:
            self.coin_var()
            self.eat("!!")
        elif prod == 15:
            self.coin_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<coin-var-arr>")

    def coin_var(self):
        # <coin-var>
        prod = self.get_production("<coin-var>")
        if prod == 16:
            self.coin_init()
            self.coin_init_mult()
        else:
            self.error_invalid_token("<coin-var>")

    def coin_init(self):
        # <coin-init>
        prod = self.get_production("<coin-init>")
        if prod == 17:
            self.eat("=")
            self.coin_init_val()
        elif prod == 18:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-init>")

    def coin_init_mult(self):
        # <coin-init-mult>
        prod = self.get_production("<coin-init-mult>")
        if prod == 19:
            self.eat(",")
            self.eat("id")
            self.coin_init()
            self.coin_init_mult()
        elif prod == 20:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-init-mult>")

    def coin_init_val(self):
        # <coin-init-val>
        prod = self.get_production("<coin-init-val>")
        if prod == 21:
            self.coin_val()
            self.coin_exp()
        else:
            self.error_invalid_token("<coin-init-val>")

    def coin_val(self):
        # <coin-val>
        prod = self.get_production("<coin-val>")
        if prod == 22:
            self.eat("id")
            self.id_tail()
        elif prod == 23:
            self.eat("(")
            self.coin_grp_val()
            self.eat(")")
        elif prod == 24:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<coin-val>")

    def coin_exp(self):
        # <coin-exp>
        prod = self.get_production("<coin-exp>")
        if prod == 25:
            self.arith_op()
            self.coin_val()
            self.coin_exp()
        elif prod == 26:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-exp>")

    def coin_grp_val(self):
        # <coin-grp-val>
        prod = self.get_production("<coin-grp-val>")
        if prod == 27:
            self.coin_grp_ope()
            self.coin_grp_exp()
        else:
            self.error_invalid_token("<coin-grp-val>")

    def coin_grp_ope(self):
        # <coin-grp-ope>
        prod = self.get_production("<coin-grp-ope>")
        if prod == 28:
            self.eat("id")
            self.id_tail()
        elif prod == 29:
            self.eat("(")
            self.coin_grp_val()
            self.eat(")")
        elif prod == 30:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<coin-grp-ope>")

    def coin_grp_exp(self):
        # <coin-grp-exp>
        prod = self.get_production("<coin-grp-exp>")
        if prod == 31:
            self.arith_op()
            self.coin_grp_ope()
            self.coin_grp_exp()
        elif prod == 32:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-grp-exp>")

    def arith_op(self):
        # <arith-op>
        prod = self.get_production("<arith-op>")
        if prod == 33: self.eat("+")
        elif prod == 34: self.eat("-")
        elif prod == 35: self.eat("*")
        elif prod == 36: self.eat("/")
        elif prod == 37: self.eat("%")
        elif prod == 38: self.eat("^")
        else:
            self.error_invalid_token("<arith-op>")

    def coin_arr(self):
        # <coin-arr>
        prod = self.get_production("<coin-arr>")
        if prod == 39:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.coin_arr_tail()
        else:
            self.error_invalid_token("<coin-arr>")

    def coin_arr_tail(self):
        # <coin-arr-tail>
        prod = self.get_production("<coin-arr-tail>")
        if prod == 40:
            self.eat("=")
            self.eat("[")
            self.coin_arr1()
            self.eat("]")
        elif prod == 41:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.coin_arr2_tail()
        elif prod == 42:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-arr-tail>")

    def coin_arr1(self):
        # <coin-arr1>
        prod = self.get_production("<coin-arr1>")
        if prod == 43:
            self.coin_arr_val()
            self.cav_tail()
        else:
            self.error_invalid_token("<coin-arr1>")

    def coin_arr_val(self):
        # <coin-arr-val>
        prod = self.get_production("<coin-arr-val>")
        if prod == 44:
            self.coin_arr_ope()
            self.coin_arr_exp()
        else:
            self.error_invalid_token("<coin-arr-val>")

    def coin_arr_ope(self):
        # <coin-arr-ope>
        prod = self.get_production("<coin-arr-ope>")
        if prod == 45:
            self.eat("id")
            self.id_tail()
        elif prod == 46:
            self.eat("(")
            self.coin_grp_val()
            self.eat(")")
        elif prod == 47:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<coin-arr-ope>")

    def coin_arr_exp(self):
        # <coin-arr-exp>
        prod = self.get_production("<coin-arr-exp>")
        if prod == 48:
            self.arith_op()
            self.coin_arr_ope()
            self.coin_arr_exp()
        elif prod == 49:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-arr-exp>")

    def cav_tail(self):
        # <cav-tail>
        prod = self.get_production("<cav-tail>")
        if prod == 50:
            self.eat(",")
            self.coin_arr1()
        elif prod == 51:
            pass # Lambda
        else:
            self.error_invalid_token("<cav-tail>")

    def coin_arr2_tail(self):
        # <coin-arr2-tail>
        prod = self.get_production("<coin-arr2-tail>")
        if prod == 52:
            self.eat("=")
            self.eat("[")
            self.coin_arr2()
            self.eat("]")
        elif prod == 53:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-arr2-tail>")

    def coin_arr2(self):
        # <coin-arr2>
        prod = self.get_production("<coin-arr2>")
        if prod == 54:
            self.eat("[")
            self.coin_arr1()
            self.eat("]")
            self.cav2_tail()
        else:
            self.error_invalid_token("<coin-arr2>")

    def cav2_tail(self):
        # <cav2-tail>
        prod = self.get_production("<cav2-tail>")
        if prod == 55:
            self.eat(",")
            self.coin_arr2()
        elif prod == 56:
            pass # Lambda
        else:
            self.error_invalid_token("<cav2-tail>")

    def coin_func(self):
        # <coin-func>
        prod = self.get_production("<coin-func>")
        if prod == 57:
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

    def coin_retval(self):
        # <coin-retval>
        prod = self.get_production("<coin-retval>")
        if prod == 58:
            self.coin_ret_ope()
            self.coin_ret_exp()
        else:
            self.error_invalid_token("<coin-retval>")

    def coin_ret_ope(self):
        # <coin-ret-ope>
        prod = self.get_production("<coin-ret-ope>")
        if prod == 59:
            self.eat("id")
            self.id_tail()
        elif prod == 60:
            self.eat("(")
            self.coin_grp_val()
            self.eat(")")
        elif prod == 61:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<coin-ret-ope>")

    def coin_ret_exp(self):
        # <coin-ret-exp>
        prod = self.get_production("<coin-ret-exp>")
        if prod == 62:
            self.arith_op()
            self.coin_ret_ope()
            self.coin_ret_exp()
        elif prod == 63:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-ret-exp>")

    # ==================== DIME PRODUCTIONS ====================

    def dime_var_arr_func(self):
        # <dime-var-arr-func>
        prod = self.get_production("<dime-var-arr-func>")
        if prod == 64:
            self.dime_var_arr()
            self.global_dec()
        elif prod == 65:
            self.dime_func()
        else:
            self.error_invalid_token("<dime-var-arr-func>")

    def dime_var_arr(self):
        # <dime-var-arr>
        prod = self.get_production("<dime-var-arr>")
        if prod == 66:
            self.dime_var()
            self.eat("!!")
        elif prod == 67:
            self.dime_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<dime-var-arr>")

    def dime_var(self):
        # <dime-var>
        prod = self.get_production("<dime-var>")
        if prod == 68:
            self.dime_init()
            self.dime_init_mult()
        else:
            self.error_invalid_token("<dime-var>")

    def dime_init(self):
        # <dime-init>
        prod = self.get_production("<dime-init>")
        if prod == 69:
            self.eat("=")
            self.dime_init_val()
        elif prod == 70:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-init>")

    def dime_init_mult(self):
        # <dime-init-mult>
        prod = self.get_production("<dime-init-mult>")
        if prod == 71:
            self.eat(",")
            self.eat("id")
            self.dime_init()
            self.dime_init_mult()
        elif prod == 72:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-init-mult>")

    def dime_init_val(self):
        # <dime-init-val>
        prod = self.get_production("<dime-init-val>")
        if prod == 73:
            self.dime_val()
            self.dime_exp()
        else:
            self.error_invalid_token("<dime-init-val>")

    def dime_val(self):
        # <dime-val>
        prod = self.get_production("<dime-val>")
        if prod == 74:
            self.eat("id")
            self.id_tail()
        elif prod == 75:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        elif prod == 76:
            self.eat("DIME-lit")
        elif prod == 77:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<dime-val>")

    def dime_exp(self):
        # <dime-exp>
        prod = self.get_production("<dime-exp>")
        if prod == 78:
            self.arith_op()
            self.dime_val()
            self.dime_exp()
        elif prod == 79:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-exp>")

    def dime_grp_val(self):
        # <dime-grp-val>
        prod = self.get_production("<dime-grp-val>")
        if prod == 80:
            self.dime_grp_ope()
            self.dime_grp_exp()
        else:
            self.error_invalid_token("<dime-grp-val>")

    def dime_grp_ope(self):
        # <dime-grp-ope>
        prod = self.get_production("<dime-grp-ope>")
        if prod == 81:
            self.eat("id")
            self.id_tail()
        elif prod == 82:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        elif prod == 83:
            self.eat("DIME-lit")
        elif prod == 84:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<dime-grp-ope>")

    def dime_grp_exp(self):
        # <dime-grp-exp>
        prod = self.get_production("<dime-grp-exp>")
        if prod == 85:
            self.arith_op()
            self.dime_grp_ope()
            self.dime_grp_exp()
        elif prod == 86:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-grp-exp>")

    def dime_arr(self):
        # <dime-arr>
        prod = self.get_production("<dime-arr>")
        if prod == 87:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.dime_arr_tail()
        else:
            self.error_invalid_token("<dime-arr>")

    def dime_arr_tail(self):
        # <dime-arr-tail>
        prod = self.get_production("<dime-arr-tail>")
        if prod == 88:
            self.eat("=")
            self.eat("[")
            self.dime_arr1()
            self.eat("]")
        elif prod == 89:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.dime_arr2_tail()
        elif prod == 90:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-arr-tail>")

    def dime_arr1(self):
        # <dime-arr1>
        prod = self.get_production("<dime-arr1>")
        if prod == 91:
            self.dime_arr_val()
            self.dav_tail()
        else:
            self.error_invalid_token("<dime-arr1>")

    def dime_arr_val(self):
        # <dime-arr-val>
        prod = self.get_production("<dime-arr-val>")
        if prod == 92:
            self.dime_arr_ope()
            self.dime_arr_exp()
        else:
            self.error_invalid_token("<dime-arr-val>")

    def dime_arr_ope(self):
        # <dime-arr-ope>
        prod = self.get_production("<dime-arr-ope>")
        if prod == 93:
            self.eat("id")
            self.id_tail()
        elif prod == 94:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        elif prod == 95:
            self.eat("DIME-lit")
        elif prod == 96:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<dime-arr-ope>")

    def dime_arr_exp(self):
        # <dime-arr-exp>
        prod = self.get_production("<dime-arr-exp>")
        if prod == 97:
            self.arith_op()
            self.dime_arr_ope()
            self.dime_arr_exp()
        elif prod == 98:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-arr-exp>")

    def dav_tail(self):
        # <dav-tail>
        prod = self.get_production("<dav-tail>")
        if prod == 99:
            self.eat(",")
            self.dime_arr1()
        elif prod == 100:
            pass # Lambda
        else:
            self.error_invalid_token("<dav-tail>")

    def dime_arr2_tail(self):
        # <dime-arr2-tail>
        prod = self.get_production("<dime-arr2-tail>")
        if prod == 101:
            self.eat("=")
            self.eat("[")
            self.dime_arr2()
            self.eat("]")
        elif prod == 102:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-arr2-tail>")

    def dime_arr2(self):
        # <dime-arr2>
        prod = self.get_production("<dime-arr2>")
        if prod == 103:
            self.eat("[")
            self.dime_arr1()
            self.eat("]")
            self.dav2_tail()
        else:
            self.error_invalid_token("<dime-arr2>")

    def dav2_tail(self):
        # <dav2-tail>
        prod = self.get_production("<dav2-tail>")
        if prod == 104:
            self.eat(",")
            self.dime_arr2()
        elif prod == 105:
            pass # Lambda
        else:
            self.error_invalid_token("<dav2-tail>")

    def dime_func(self):
        # <dime-func>
        prod = self.get_production("<dime-func>")
        if prod == 106:
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

    def dime_retval(self):
        # <dime-retval>
        prod = self.get_production("<dime-retval>")
        if prod == 107:
            self.dime_ret_ope()
            self.dime_ret_exp()
        else:
            self.error_invalid_token("<dime-retval>")

    def dime_ret_ope(self):
        # <dime-ret-ope>
        prod = self.get_production("<dime-ret-ope>")
        if prod == 108:
            self.eat("id")
            self.id_tail()
        elif prod == 109:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        elif prod == 110:
            self.eat("DIME-lit")
        elif prod == 111:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<dime-ret-ope>")

    def dime_ret_exp(self):
        # <dime-ret-exp>
        prod = self.get_production("<dime-ret-exp>")
        if prod == 112:
            self.arith_op()
            self.dime_ret_ope()
            self.dime_ret_exp()
        elif prod == 113:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-ret-exp>")

    # ==================== PARCH PRODUCTIONS ====================

    def parch_var_arr_func(self):
        # <parch-var-arr-func>
        prod = self.get_production("<parch-var-arr-func>")
        if prod == 114:
            self.parch_var_arr()
            self.global_dec()
        elif prod == 115:
            self.parch_func()
        else:
            self.error_invalid_token("<parch-var-arr-func>")

    def parch_var_arr(self):
        # <parch-var-arr>
        prod = self.get_production("<parch-var-arr>")
        if prod == 116:
            self.parch_var()
            self.eat("!!")
        elif prod == 117:
            self.parch_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<parch-var-arr>")

    def parch_var(self):
        # <parch-var>
        prod = self.get_production("<parch-var>")
        if prod == 118:
            self.parch_init()
            self.parch_init_mult()
        else:
            self.error_invalid_token("<parch-var>")

    def parch_init(self):
        # <parch-init>
        prod = self.get_production("<parch-init>")
        if prod == 119:
            self.eat("=")
            self.parch_init_val()
        elif prod == 120:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-init>")

    def parch_init_mult(self):
        # <parch-init-mult>
        prod = self.get_production("<parch-init-mult>")
        if prod == 121:
            self.eat(",")
            self.eat("id")
            self.parch_init()
            self.parch_init_mult()
        elif prod == 122:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-init-mult>")

    def parch_init_val(self):
        # <parch-init-val>
        prod = self.get_production("<parch-init-val>")
        if prod == 123:
            self.eat("id")
            self.id_tail()
        elif prod == 124:
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<parch-init-val>")

    def parch_arr(self):
        # <parch-arr>
        prod = self.get_production("<parch-arr>")
        if prod == 125:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.parch_arr_tail()
        else:
            self.error_invalid_token("<parch-arr>")

    def parch_arr_tail(self):
        # <parch-arr-tail>
        prod = self.get_production("<parch-arr-tail>")
        if prod == 126:
            self.eat("=")
            self.eat("[")
            self.parch_arr1()
            self.eat("]")
        elif prod == 127:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.parch_arr2_tail()
        elif prod == 128:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-arr-tail>")

    def parch_arr1(self):
        # <parch-arr1>
        prod = self.get_production("<parch-arr1>")
        if prod == 129:
            self.parch_arr_val()
            self.pav_tail()
        else:
            self.error_invalid_token("<parch-arr1>")

    def parch_arr_val(self):
        # <parch-arr-val>
        prod = self.get_production("<parch-arr-val>")
        if prod == 130:
            self.eat("id")
            self.id_tail()
        elif prod == 131:
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<parch-arr-val>")

    def pav_tail(self):
        # <pav-tail>
        prod = self.get_production("<pav-tail>")
        if prod == 132:
            self.eat(",")
            self.parch_arr1()
        elif prod == 133:
            pass # Lambda
        else:
            self.error_invalid_token("<pav-tail>")

    def parch_arr2_tail(self):
        # <parch-arr2-tail>
        prod = self.get_production("<parch-arr2-tail>")
        if prod == 134:
            self.eat("=")
            self.eat("[")
            self.parch_arr2()
            self.eat("]")
        elif prod == 135:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-arr2-tail>")

    def parch_arr2(self):
        # <parch-arr2>
        prod = self.get_production("<parch-arr2>")
        if prod == 136:
            self.eat("[")
            self.parch_arr1()
            self.eat("]")
            self.pav2_tail()
        else:
            self.error_invalid_token("<parch-arr2>")

    def pav2_tail(self):
        # <pav2-tail>
        prod = self.get_production("<pav2-tail>")
        if prod == 137:
            self.eat(",")
            self.parch_arr2()
        elif prod == 138:
            pass # Lambda
        else:
            self.error_invalid_token("<pav2-tail>")

    def parch_func(self):
        # <parch-func>
        prod = self.get_production("<parch-func>")
        if prod == 139:
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

    def parch_retval(self):
        # <parch-retval>
        prod = self.get_production("<parch-retval>")
        if prod == 140:
            self.eat("id")
            self.id_tail()
        elif prod == 141:
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<parch-retval>")

    # ==================== SCROLL PRODUCTIONS ====================

    def scroll_var_arr_func(self):
        # <scroll-var-arr-func>
        prod = self.get_production("<scroll-var-arr-func>")
        if prod == 142:
            self.scroll_var_arr()
            self.global_dec()
        elif prod == 143:
            self.scroll_func()
            self.sub_func()
        else:
            self.error_invalid_token("<scroll-var-arr-func>")

    def scroll_var_arr(self):
        # <scroll-var-arr>
        prod = self.get_production("<scroll-var-arr>")
        if prod == 144:
            self.scroll_var()
            self.eat("!!")
        elif prod == 145:
            self.scroll_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<scroll-var-arr>")

    def scroll_var(self):
        # <scroll-var>
        prod = self.get_production("<scroll-var>")
        if prod == 146:
            self.scroll_init()
            self.scroll_init_mult()
        else:
            self.error_invalid_token("<scroll-var>")

    def scroll_init(self):
        # <scroll-init>
        prod = self.get_production("<scroll-init>")
        if prod == 147:
            self.eat("=")
            self.scroll_init_val()
        elif prod == 148:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-init>")

    def scroll_init_mult(self):
        # <scroll-init-mult>
        prod = self.get_production("<scroll-init-mult>")
        if prod == 149:
            self.eat(",")
            self.eat("id")
            self.scroll_init()
            self.scroll_init_mult()
        elif prod == 150:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-init-mult>")

    def scroll_init_val(self):
        # <scroll-init-val>
        prod = self.get_production("<scroll-init-val>")
        if prod == 151:
            self.scroll_val()
            self.scroll_exp()
        else:
            self.error_invalid_token("<scroll-init-val>")

    def scroll_val(self):
        # <scroll-val>
        prod = self.get_production("<scroll-val>")
        if prod == 152:
            self.eat("id")
            self.id_tail()
        elif prod == 153:
            self.eat("(")
            self.scroll_grp_val()
            self.eat(")")
        elif prod == 154:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<scroll-val>")

    def scr_char(self):
        # <scr-char>
        prod = self.get_production("<scr-char>")
        if prod == 155:
            self.eat("{")
            self.index()
            self.eat("}")
        elif prod == 156:
            pass # Lambda
        else:
            self.error_invalid_token("<scr-char>")

    def index(self):
        # <index>
        prod = self.get_production("<index>")
        if prod == 157: self.eat("id")
        elif prod == 158: self.eat("COIN-lit")
        else:
            self.error_invalid_token("<index>")

    def scroll_exp(self):
        # <scroll-exp>
        prod = self.get_production("<scroll-exp>")
        if prod == 159:
            self.concat_op()
            self.scroll_val()
            self.scroll_exp()
        elif prod == 160:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-exp>")

    def scroll_grp_val(self):
        # <scroll-grp-val>
        prod = self.get_production("<scroll-grp-val>")
        if prod == 161:
            self.scroll_grp_ope()
            self.scroll_grp_exp()
        else:
            self.error_invalid_token("<scroll-grp-val>")

    def scroll_grp_ope(self):
        # <scroll-grp-ope>
        prod = self.get_production("<scroll-grp-ope>")
        if prod == 162:
            self.eat("id")
            self.id_tail()
        elif prod == 163:
            self.eat("(")
            self.scroll_grp_val()
            self.eat(")")
        elif prod == 164:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<scroll-grp-ope>")

    def scroll_grp_exp(self):
        # <scroll-grp-exp>
        prod = self.get_production("<scroll-grp-exp>")
        if prod == 165:
            self.concat_op()
            self.scroll_grp_ope()
            self.scroll_grp_exp()
        elif prod == 166:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-grp-exp>")

    def concat_op(self):
        # <concat-op>
        prod = self.get_production("<concat-op>")
        if prod == 167: self.eat("&")
        else:
            self.error_invalid_token("<concat-op>")

    def scroll_arr(self):
        # <scroll-arr>
        prod = self.get_production("<scroll-arr>")
        if prod == 168:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.scroll_arr_tail()
        else:
            self.error_invalid_token("<scroll-arr>")

    def scroll_arr_tail(self):
        # <scroll-arr-tail>
        prod = self.get_production("<scroll-arr-tail>")
        if prod == 169:
            self.eat("=")
            self.eat("[")
            self.scroll_arr1()
            self.eat("]")
        elif prod == 170:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.scroll_arr2_tail()
        elif prod == 171:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-arr-tail>")

    def scroll_arr1(self):
        # <scroll-arr1>
        prod = self.get_production("<scroll-arr1>")
        if prod == 172:
            self.scroll_arr_val()
            self.sav_tail()
        else:
            self.error_invalid_token("<scroll-arr1>")

    def scroll_arr_val(self):
        # <scroll-arr-val>
        prod = self.get_production("<scroll-arr-val>")
        if prod == 173:
            self.scroll_arr_ope()
            self.scroll_arr_exp()
        else:
            self.error_invalid_token("<scroll-arr-val>")

    def scroll_arr_ope(self):
        # <scroll-arr-ope>
        prod = self.get_production("<scroll-arr-ope>")
        if prod == 174:
            self.eat("id")
            self.id_tail()
        elif prod == 175:
            self.eat("(")
            self.scroll_grp_val()
            self.eat(")")
        elif prod == 176:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<scroll-arr-ope>")

    def scroll_arr_exp(self):
        # <scroll-arr-exp>
        prod = self.get_production("<scroll-arr-exp>")
        if prod == 177:
            self.concat_op()
            self.scroll_arr_ope()
            self.scroll_arr_exp()
        elif prod == 178:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-arr-exp>")

    def sav_tail(self):
        # <sav-tail>
        prod = self.get_production("<sav-tail>")
        if prod == 179:
            self.eat(",")
            self.scroll_arr1()
        elif prod == 180:
            pass # Lambda
        else:
            self.error_invalid_token("<sav-tail>")

    def scroll_arr2_tail(self):
        # <scroll-arr2-tail>
        prod = self.get_production("<scroll-arr2-tail>")
        if prod == 181:
            self.eat("=")
            self.eat("[")
            self.scroll_arr2()
            self.eat("]")
        elif prod == 182:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-arr2-tail>")

    def scroll_arr2(self):
        # <scroll-arr2>
        prod = self.get_production("<scroll-arr2>")
        if prod == 183:
            self.eat("[")
            self.scroll_arr1()
            self.eat("]")
            self.sav2_tail()
        else:
            self.error_invalid_token("<scroll-arr2>")

    def sav2_tail(self):
        # <sav2-tail>
        prod = self.get_production("<sav2-tail>")
        if prod == 184:
            self.eat(",")
            self.scroll_arr2()
        elif prod == 185:
            pass # Lambda
        else:
            self.error_invalid_token("<sav2-tail>")

    def scroll_func(self):
        # <scroll-func>
        prod = self.get_production("<scroll-func>")
        if prod == 186:
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

    def scroll_retval(self):
        # <scroll-retval>
        prod = self.get_production("<scroll-retval>")
        if prod == 187:
            self.scroll_ret_ope()
            self.scroll_ret_exp()
        else:
            self.error_invalid_token("<scroll-retval>")

    def scroll_ret_ope(self):
        # <scroll-ret-ope>
        prod = self.get_production("<scroll-ret-ope>")
        if prod == 188:
            self.eat("id")
            self.id_tail()
        elif prod == 189:
            self.eat("(")
            self.scroll_grp_val()
            self.eat(")")
        elif prod == 190:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<scroll-ret-ope>")

    def scroll_ret_exp(self):
        # <scroll-ret-exp>
        prod = self.get_production("<scroll-ret-exp>")
        if prod == 191:
            self.concat_op()
            self.scroll_ret_ope()
            self.scroll_ret_exp()
        elif prod == 192:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-ret-exp>")

    # ==================== BOOL PRODUCTIONS ====================

    def bool_var_arr_func(self):
        # <bool-var-arr-func>
        prod = self.get_production("<bool-var-arr-func>")
        if prod == 193:
            self.bool_var_arr()
            self.global_dec()
        elif prod == 194:
            self.bool_func()
        else:
            self.error_invalid_token("<bool-var-arr-func>")

    def bool_var_arr(self):
        # <bool-var-arr>
        prod = self.get_production("<bool-var-arr>")
        if prod == 195:
            self.bool_var()
            self.eat("!!")
        elif prod == 196:
            self.bool_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<bool-var-arr>")

    def bool_var(self):
        # <bool-var>
        prod = self.get_production("<bool-var>")
        if prod == 197:
            self.bool_init()
            self.bool_init_mult()
        else:
            self.error_invalid_token("<bool-var>")

    def bool_init(self):
        # <bool-init>
        prod = self.get_production("<bool-init>")
        if prod == 198:
            self.eat("=")
            self.bool_init_val()
        elif prod == 199:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-init>")

    def bool_init_mult(self):
        # <bool-init-mult>
        prod = self.get_production("<bool-init-mult>")
        if prod == 200:
            self.eat(",")
            self.eat("id")
            self.bool_init()
            self.bool_init_mult()
        elif prod == 201:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-init-mult>")

    def bool_init_val(self):
        # <bool-init-val>
        prod = self.get_production("<bool-init-val>")
        if prod == 202:
            self.bool_val()
            self.bool_exp()
        else:
            self.error_invalid_token("<bool-init-val>")

    def bool_val(self):
        # <bool-val>
        prod = self.get_production("<bool-val>")
        if prod == 203:
            self.eat("id")
            self.id_tail()
            self.bool_exp2()
        elif prod == 204:
            self.eat("(")
            self.bool_grp_val()
            self.eat(")")
        elif prod == 205:
            self.bool_val_exp()
        elif prod == 206:
            self.bool_digit_exp()
        elif prod == 207:
            self.bool_parch_exp()
        elif prod == 208:
            self.bool_scroll_exp()
        else:
            self.error_invalid_token("<bool-val>")

    def bool_val_exp(self):
        # <bool-val-exp>
        prod = self.get_production("<bool-val-exp>")
        if prod == 209:
            self.bool_rule()
            self.bool_eq()
        else:
            self.error_invalid_token("<bool-val-exp>")

    def bool_rule(self):
        # <bool>
        prod = self.get_production("<bool>")
        if prod == 210: self.bool_lit()
        elif prod == 211:
            self.not_op()
            self.not_ope()
        else:
            self.error_invalid_token("<bool>")

    def bool_lit(self):
        # <bool-lit>
        prod = self.get_production("<bool-lit>")
        if prod == 212: self.eat("AYE")
        elif prod == 213: self.eat("NAY")
        else:
            self.error_invalid_token("<bool-lit>")

    def not_op(self):
        # <not-op>
        prod = self.get_production("<not-op>")
        if prod == 214: self.eat("!")
        elif prod == 215: self.eat("!#")
        else:
            self.error_invalid_token("<not-op>")

    def not_ope(self):
        # <not-ope>
        prod = self.get_production("<not-ope>")
        if prod == 216:
            self.eat("id")
            self.id_tail()
        elif prod == 217:
            self.eat("(")
            self.bool_grp_val()
            self.eat(")")
        elif prod == 218:
            self.bool_lit()
        else:
            self.error_invalid_token("<not-ope>")

    def bool_eq(self):
        # <bool-eq>
        prod = self.get_production("<bool-eq>")
        if prod == 219:
            self.eq_op()
            self.bool_val()
        elif prod == 220:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-eq>")

    def bool_digit_exp(self):
        # <bool-digit-exp>
        prod = self.get_production("<bool-digit-exp>")
        if prod == 221:
            self.bool_digit()
            self.bool_arith()
            self.rel_eq()
        else:
            self.error_invalid_token("<bool-digit-exp>")

    def bool_digit(self):
        # <bool-digit>
        prod = self.get_production("<bool-digit>")
        if prod == 222: self.eat("COIN-lit")
        elif prod == 223: self.eat("DIME-lit")
        else:
            self.error_invalid_token("<bool-digit>")

    def bool_arith(self):
        # <bool-arith>
        prod = self.get_production("<bool-arith>")
        if prod == 224:
            self.arith()
            self.bool_arith()
        elif prod == 225:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arith>")

    def arith(self):
        # <arith>
        prod = self.get_production("<arith>")
        if prod == 226:
            self.arith_op()
            self.bool_arel_ope()
        else:
            self.error_invalid_token("<arith>")

    def bool_arel_ope(self):
        # <bool-arel-ope>
        prod = self.get_production("<bool-arel-ope>")
        if prod == 227:
            self.eat("id")
            self.id_tail()
        elif prod == 228:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        elif prod == 229:
            self.eat("COIN-lit")
        elif prod == 230:
            self.eat("DIME-lit")
        else:
            self.error_invalid_token("<bool-arel-ope>")

    def rel_eq(self):
        # <rel-eq>
        prod = self.get_production("<rel-eq>")
        if prod == 231:
            self.rel()
        elif prod == 232:
            self.digit_eq()
        else:
            self.error_invalid_token("<rel-eq>")

    def rel(self):
        # <rel>
        prod = self.get_production("<rel>")
        if prod == 233:
            self.rel_op()
            self.bool_arel_ope()
            self.bool_arith()
            self.bool_eq()
        else:
            self.error_invalid_token("<rel>")

    def rel_op(self):
        # <rel-op>
        prod = self.get_production("<rel-op>")
        if prod == 234: self.eat("<")
        elif prod == 235: self.eat(">")
        elif prod == 236: self.eat("<=")
        elif prod == 237: self.eat(">=")
        else:
            self.error_invalid_token("<rel-op>")

    def digit_eq(self):
        # <digit-eq>
        prod = self.get_production("<digit-eq>")
        if prod == 238:
            self.eq_op()
            self.arel_ope() # note: logic maps to arel_ope from context of prev grammar or assumed
        else:
            self.error_invalid_token("<digit-eq>")

    def eq_op(self):
        # <eq-op>
        prod = self.get_production("<eq-op>")
        if prod == 239: self.eat("==")
        elif prod == 240: self.eat("!=")
        else:
            self.error_invalid_token("<eq-op>")

    def bool_parch_exp(self):
        # <bool-parch-exp>
        prod = self.get_production("<bool-parch-exp>")
        if prod == 241:
            self.eat("PARCH-lit")
            self.eq_op()
            self.bool_parch()
        else:
            self.error_invalid_token("<bool-parch-exp>")

    def bool_parch(self):
        # <bool-parch>
        prod = self.get_production("<bool-parch>")
        if prod == 242:
            self.eat("id")
            self.id_tail()
        elif prod == 243:
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<bool-parch>")

    def bool_scroll_exp(self):
        # <bool-scroll-exp>
        prod = self.get_production("<bool-scroll-exp>")
        if prod == 244:
            self.bool_scroll()
            self.bool_concat()
            self.scroll_eq()
        else:
            self.error_invalid_token("<bool-scroll-exp>")

    def bool_scroll(self):
        # <bool-scroll>
        prod = self.get_production("<bool-scroll>")
        if prod == 245:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<bool-scroll>")

    def bool_concat(self):
        # <bool-concat>
        prod = self.get_production("<bool-concat>")
        if prod == 246:
            self.concat()
            self.bool_concat()
        elif prod == 247:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-concat>")

    def concat(self):
        # <concat>
        prod = self.get_production("<concat>")
        if prod == 248:
            self.concat_op()
            self.bool_concat_ope()
        else:
            self.error_invalid_token("<concat>")

    def bool_concat_ope(self):
        # <bool-concat-ope>
        prod = self.get_production("<bool-concat-ope>")
        if prod == 249:
            self.eat("id")
            self.id_tail()
        elif prod == 250:
            self.eat("(")
            self.scroll_grp_val()
            self.eat(")")
        elif prod == 251:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<bool-concat-ope>")

    def scroll_eq(self):
        # <scroll-eq>
        prod = self.get_production("<scroll-eq>")
        if prod == 252:
            self.eq_op()
            self.bool_concat_ope()
            self.bool_concat()
        elif prod == 253:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-eq>")

    def bool_exp2(self):
        # <bool-exp2>
        prod = self.get_production("<bool-exp2>")
        if prod == 254:
            self.arith()
            self.bool_arith()
            self.rel_eq()
        elif prod == 255:
            self.rel()
        elif prod == 256:
            self.eq_op()
            self.eq_ope()
        elif prod == 257:
            self.concat()
            self.bool_concat()
            self.scroll_eq()
        elif prod == 258:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-exp2>")

    def eq_ope(self):
        # <eq-ope>
        prod = self.get_production("<eq-ope>")
        if prod == 259:
            self.eat("id")
            self.id_tail()
            self.bool_exp3()
        elif prod == 260:
            self.eat("(")
            self.eq_ope()
            self.eat(")")
        elif prod == 261:
            self.bool_digit()
            self.bool_arith()
            self.bool_rel()
        elif prod == 262:
            self.eat("PARCH-lit")
        elif prod == 263:
            self.eat("SCROLL-lit")
            self.scr_char()
            self.bool_concat()
        elif prod == 264:
            self.bool_rule()
        else:
            self.error_invalid_token("<eq-ope>")

    def bool_exp3(self):
        # <bool-exp3>
        prod = self.get_production("<bool-exp3>")
        if prod == 265:
            self.arith()
            self.bool_arith()
            self.bool_rel()
        elif prod == 266:
            self.rel_op()
            self.bool_arel_ope()
        elif prod == 267:
            self.concat()
            self.bool_concat()
        elif prod == 268:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-exp3>")

    def bool_rel(self):
        # <bool-rel>
        prod = self.get_production("<bool-rel>")
        if prod == 269:
            self.rel_op()
            self.bool_arel_ope()
        elif prod == 270:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-rel>")

    def bool_exp(self):
        # <bool-exp>
        prod = self.get_production("<bool-exp>")
        if prod == 271:
            self.log_op()
            self.bool_val()
            self.bool_exp()
        elif prod == 272:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-exp>")

    def log_op(self):
        # <log-op>
        prod = self.get_production("<log-op>")
        if prod == 273: self.eat("||")
        elif prod == 274: self.eat("&&")
        else:
            self.error_invalid_token("<log-op>")

    def bool_grp_val(self):
        # <bool-grp-val>
        prod = self.get_production("<bool-grp-val>")
        if prod == 275:
            self.bool_grp_ope()
            self.bool_grp_exp()
        else:
            self.error_invalid_token("<bool-grp-val>")

    def bool_grp_ope(self):
        # <bool-grp-ope>
        prod = self.get_production("<bool-grp-ope>")
        if prod == 276:
            self.bool_val()
        else:
            self.error_invalid_token("<bool-grp-ope>")

    def bool_grp_exp(self):
        # <bool-grp-exp>
        prod = self.get_production("<bool-grp-exp>")
        if prod == 277:
            self.bool_exp()
        elif prod == 278:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-grp-exp>")

    def bool_arr(self):
        # <bool-arr>
        prod = self.get_production("<bool-arr>")
        if prod == 279:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.bool_arr_tail()
        else:
            self.error_invalid_token("<bool-arr>")

    def bool_arr_tail(self):
        # <bool-arr-tail>
        prod = self.get_production("<bool-arr-tail>")
        if prod == 280:
            self.eat("=")
            self.eat("[")
            self.bool_arr1()
            self.eat("]")
        elif prod == 281:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.bool_arr2_tail()
        elif prod == 282:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arr-tail>")

    def bool_arr1(self):
        # <bool-arr1>
        prod = self.get_production("<bool-arr1>")
        if prod == 283:
            self.bool_arr_val()
            self.bav_tail()
        else:
            self.error_invalid_token("<bool-arr1>")

    def bav_tail(self):
        # <bav-tail>
        prod = self.get_production("<bav-tail>")
        if prod == 284:
            self.eat(",")
            self.bool_arr1()
        elif prod == 285:
            pass # Lambda
        else:
            self.error_invalid_token("<bav-tail>")

    def bool_arr_val(self):
        # <bool-arr-val>
        prod = self.get_production("<bool-arr-val>")
        if prod == 286:
            self.bool_val()
            self.bool_arr_exp()
        else:
            self.error_invalid_token("<bool-arr-val>")

    def bool_arr_exp(self):
        # <bool-arr-exp>
        prod = self.get_production("<bool-arr-exp>")
        if prod == 287:
            self.log_op()
            self.bool_val()
            self.bool_arr_exp()
        elif prod == 288:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arr-exp>")

    def bool_arr2_tail(self):
        # <bool-arr2-tail>
        prod = self.get_production("<bool-arr2-tail>")
        if prod == 289:
            self.eat("=")
            self.eat("[")
            self.bool_arr2()
            self.eat("]")
        elif prod == 290:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arr2-tail>")

    def bool_arr2(self):
        # <bool-arr2>
        prod = self.get_production("<bool-arr2>")
        if prod == 291:
            self.eat("[")
            self.bool_arr1()
            self.eat("]")
            self.bav2_tail()
        else:
            self.error_invalid_token("<bool-arr2>")

    def bav2_tail(self):
        # <bav2-tail>
        prod = self.get_production("<bav2-tail>")
        if prod == 292:
            self.eat(",")
            self.bool_arr2()
        elif prod == 293:
            pass # Lambda
        else:
            self.error_invalid_token("<bav2-tail>")

    def bool_func(self):
        # <bool-func>
        prod = self.get_production("<bool-func>")
        if prod == 294:
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

    def bool_retval(self):
        # <bool-retval>
        prod = self.get_production("<bool-retval>")
        if prod == 295:
            self.bool_val()
            self.bool_ret_exp()
        else:
            self.error_invalid_token("<bool-retval>")

    def bool_ret_exp(self):
        # <bool-ret-exp>
        prod = self.get_production("<bool-ret-exp>")
        if prod == 296:
            self.log_op()
            self.bool_val()
            self.bool_ret_exp()
        elif prod == 297:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-ret-exp>")

    # ==================== COMMON FUNCTION PARAMS ====================

    def params(self):
        # <params>
        prod = self.get_production("<params>")
        if prod == 298:
            self.d_type()
            self.eat("id")
            self.param_mult()
        elif prod == 299:
            pass # Lambda
        else:
            self.error_invalid_token("<params>")

    def param_mult(self):
        # <param-mult>
        prod = self.get_production("<param-mult>")
        if prod == 300:
            self.eat(",")
            self.params()
        elif prod == 301:
            pass # Lambda
        else:
            self.error_invalid_token("<param-mult>")

    def d_type(self):
        # <d-type>
        prod = self.get_production("<d-type>")
        if prod == 302: self.eat("COIN")
        elif prod == 303: self.eat("DIME")
        elif prod == 304: self.eat("PARCH")
        elif prod == 305: self.eat("SCROLL")
        elif prod == 306: self.eat("BOOL")
        else:
            self.error_invalid_token("<d-type>")

    def ret_stmnts(self):
        # <ret-stmnts>
        prod = self.get_production("<ret-stmnts>")
        if prod == 307:
            self.ret_stmnt()
            self.ret_stmnts()
        elif prod == 308:
            pass # Lambda
        else:
            self.error_invalid_token("<ret-stmnts>")

    def ret_stmnt(self):
        # <ret-stmnt>
        prod = self.get_production("<ret-stmnt>")
        if prod == 309:
            self.statements()
        else:
            self.error_invalid_token("<ret-stmnt>")

    # ==================== ID TAILS & ELEMENTS ====================

    def id_tail(self):
        # <id-tail>
        prod = self.get_production("<id-tail>")
        if prod == 310: self.elmt()
        elif prod == 311: self.mem()
        elif prod == 312: self.func()
        elif prod == 313:
            pass # Lambda
        else:
            self.error_invalid_token("<id-tail>")

    def elmt(self):
        # <elmt>
        prod = self.get_production("<elmt>")
        if prod == 314:
            self.eat("{")
            self.index()
            self.eat("}")
            self.elmt_tail()
        else:
            self.error_invalid_token("<elmt>")

    def elmt_tail(self):
        # <elmt-tail>
        prod = self.get_production("<elmt-tail>")
        if prod == 315:
            self.eat("{")
            self.index()
            self.eat("}")
        elif prod == 316:
            pass # Lambda
        else:
            self.error_invalid_token("<elmt-tail>")

    def mem(self):
        # <mem>
        prod = self.get_production("<mem>")
        if prod == 317:
            self.eat("$")
            self.eat("id")
        else:
            self.error_invalid_token("<mem>")

    def func(self):
        # <func>
        prod = self.get_production("<func>")
        if prod == 318:
            self.eat("(")
            self.args()
            self.eat(")")
        else:
            self.error_invalid_token("<func>")

    def args(self):
        # <args>
        prod = self.get_production("<args>")
        if prod == 319:
            self.args_val()
            self.args_mult()
        elif prod == 320:
            pass # Lambda
        else:
            self.error_invalid_token("<args>")

    def args_val(self):
        # <args-val>
        prod = self.get_production("<args-val>")
        if prod == 321:
            self.value()
        else:
            self.error_invalid_token("<args-val>")

    def args_mult(self):
        # <args-mult>
        prod = self.get_production("<args-mult>")
        if prod == 322:
            self.eat(",")
            self.args()
        elif prod == 323:
            pass # Lambda
        else:
            self.error_invalid_token("<args-mult>")

    # ==================== GENERAL VALUES & EXPRESSIONS ====================

    def var_val(self):
        # <var-val>
        prod = self.get_production("<var-val>")
        if prod == 324:
            self.value()
        else:
            self.error_invalid_token("<var-val>")

    def value(self):
        # <value>
        prod = self.get_production("<value>")
        if prod == 325:
            self.eat("id")
            self.id_tail()
            self.var_exp()
        elif prod == 326:
            self.eat("(")
            self.value()
            self.eat(")")
            self.var_exp()
        elif prod == 327:
            self.var_digit()
            self.digit_tail()
        elif prod == 328:
            self.eat("PARCH-lit")
            self.eq_parch()
        elif prod == 329:
            self.eat("SCROLL-lit")
            self.scr_char()
            self.var_scroll()
            self.eq_scroll()
        elif prod == 330:
            self.var_bool()
        else:
            self.error_invalid_token("<value>")

    def var_digit(self):
        # <var-digit>
        prod = self.get_production("<var-digit>")
        if prod == 331: self.eat("COIN-lit")
        elif prod == 332: self.eat("DIME-lit")
        else:
            self.error_invalid_token("<var-digit>")

    def digit_tail(self):
        # <digit-tail>
        prod = self.get_production("<digit-tail>")
        if prod == 333:
            self.var_arith()
            self.var_releq()
        elif prod == 334:
            pass # Lambda
        else:
            self.error_invalid_token("<digit-tail>")

    def var_arith(self):
        # <var-arith>
        prod = self.get_production("<var-arith>")
        if prod == 335:
            self.arith_op()
            self.var_arel_ope()
            self.var_arith()
        elif prod == 336:
            pass # Lambda
        else:
            self.error_invalid_token("<var-arith>")

    def var_arel_ope(self):
        # <var-arel-ope>
        prod = self.get_production("<var-arel-ope>")
        if prod == 337:
            self.eat("id")
            self.id_tail()
        elif prod == 338:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        elif prod == 339:
            self.eat("COIN-lit")
        elif prod == 340:
            self.eat("DIME-lit")
        else:
            self.error_invalid_token("<var-arel-ope>")

    def var_releq(self):
        # <var-releq>
        prod = self.get_production("<var-releq>")
        if prod == 341:
            self.var_rel()
        elif prod == 342:
            self.eq_op()
            self.var_arel_ope()
            self.var_log()
        elif prod == 343:
            pass # Lambda
        else:
            self.error_invalid_token("<var-releq>")

    def var_rel(self):
        # <var-rel>
        prod = self.get_production("<var-rel>")
        if prod == 344:
            self.rel_op()
            self.arel_ope() # Note: 'arel-ope' from bool section, check strict naming 238
            self.var_arith()
            self.var_logeq()
        elif prod == 345:
            pass # Lambda
        else:
            self.error_invalid_token("<var-rel>")
            
    def arel_ope(self):
        # Helper for 238 <digit-eq> and 344 <var-rel> if strictly mapped
        # In bool section: 169-172
        prod = self.get_production("<arel-ope>") # Reusing from bool section
        if prod == 169:
            self.eat("id")
            self.id_tail()
        elif prod == 170:
            self.eat("(")
            self.dime_val()
            self.eat(")")
        elif prod == 171:
            self.eat("COIN-lit")
        elif prod == 172:
            self.eat("DIME-lit")
        else:
             # If logic requires specific var_arel_ope here, swap call. 
             # Assuming shared non-terminal logic for <arel-ope>
            self.error_invalid_token("<arel-ope>")

    def var_logeq(self):
        # <var-logeq>
        prod = self.get_production("<var-logeq>")
        if prod == 346:
            self.logeq_op()
            self.log_ope()
            self.var_log()
        elif prod == 347:
            pass # Lambda
        else:
            self.error_invalid_token("<var-logeq>")

    def logeq_op(self):
        # <logeq-op>
        prod = self.get_production("<logeq-op>")
        if prod == 348: self.log_op()
        elif prod == 349: self.eq_op()
        else:
            self.error_invalid_token("<logeq-op>")

    def var_log(self):
        # <var-log>
        prod = self.get_production("<var-log>")
        if prod == 350:
            self.log_op()
            self.log_ope()
            self.var_log()
        elif prod == 351:
            pass # Lambda
        else:
            self.error_invalid_token("<var-log>")

    def log_ope(self):
        # <log-ope>
        prod = self.get_production("<log-ope>")
        if prod == 352:
            self.bool_val()
        else:
            self.error_invalid_token("<log-ope>")

    def eq_parch(self):
        # <eq-parch>
        prod = self.get_production("<eq-parch>")
        if prod == 353:
            self.eq_op()
            self.eat("PARCH-lit")
            self.var_log()
        elif prod == 354:
            pass # Lambda
        else:
            self.error_invalid_token("<eq-parch>")

    def eq_scroll(self):
        # <eq-scroll>
        prod = self.get_production("<eq-scroll>")
        if prod == 355:
            self.eq_op()
            self.bool_scroll()
            self.bool_concat()
            self.var_log()
        elif prod == 356:
            pass # Lambda
        else:
            self.error_invalid_token("<eq-scroll>")

    def var_scroll(self):
        # <var-scroll>
        prod = self.get_production("<var-scroll>")
        if prod == 357:
            self.concat_op()
            self.concat_ope()
            self.var_scroll()
        elif prod == 358:
            pass # Lambda
        else:
            self.error_invalid_token("<var-scroll>")

    def concat_ope(self):
        # <concat-ope>
        prod = self.get_production("<concat-ope>")
        if prod == 359:
            self.eat("id")
            self.id_tail()
        elif prod == 360:
            self.eat("(")
            self.scroll_grp_val()
            self.eat(")")
        elif prod == 361:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<concat-ope>")

    def var_bool(self):
        # <var-bool>
        prod = self.get_production("<var-bool>")
        if prod == 362:
            self.bool_rule()
        else:
            self.error_invalid_token("<var-bool>")

    def var_exp(self):
        # <var-exp>
        prod = self.get_production("<var-exp>")
        if prod == 363:
            self.expressions()
        elif prod == 364:
            pass # Lambda
        else:
            self.error_invalid_token("<var-exp>")

    def expressions(self):
        # <expressions>
        prod = self.get_production("<expressions>")
        if prod == 365:
            self.arith_op()
            self.var_arel_ope()
            self.var_arith()
            self.var_releq()
        elif prod == 366:
            self.rel_op()
            self.var_arel_ope()
            self.var_arith()
            self.var_logeq()
        elif prod == 367:
            self.log_op()
            self.log_ope()
            self.var_log()
        elif prod == 368:
            self.eq_op()
            self.eq_ope()
            self.var_log()
        elif prod == 369:
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
        if prod == 370:
            self.eat("LOCKE")
            self.const_init()
            self.eat("!!")
        else:
            self.error_invalid_token("<const>")

    def const_init(self):
        # <const-init>
        prod = self.get_production("<const-init>")
        if prod == 371:
            self.eat("COIN")
            self.coin_locke()
            self.coin_locke_mult()
        elif prod == 372:
            self.eat("DIME")
            self.dime_locke()
            self.dime_locke_mult()
        elif prod == 373:
            self.eat("PARCH")
            self.parch_locke()
            self.parch_locke_mult()
        elif prod == 374:
            self.eat("SCROLL")
            self.scroll_locke()
            self.scroll_locke_mult()
        elif prod == 375:
            self.eat("BOOL")
            self.bool_locke()
            self.bool_locke_mult()
        else:
            self.error_invalid_token("<const-init>")

    def coin_locke(self):
        # <coin-locke>
        prod = self.get_production("<coin-locke>")
        if prod == 376:
            self.eat("id")
            self.eat("=")
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<coin-locke>")

    def coin_locke_mult(self):
        # <coin-locke-mult>
        prod = self.get_production("<coin-locke-mult>")
        if prod == 377:
            self.eat(",")
            self.coin_locke()
            self.coin_locke_mult()
        elif prod == 378:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-locke-mult>")

    def dime_locke(self):
        # <dime-locke>
        prod = self.get_production("<dime-locke>")
        if prod == 379:
            self.eat("id")
            self.eat("=")
            self.locke_digit()
        else:
            self.error_invalid_token("<dime-locke>")

    def locke_digit(self):
        # <locke-digit>
        prod = self.get_production("<locke-digit>")
        if prod == 380:
            self.eat("COIN-lit")
        elif prod == 381:
            self.eat("DIME-lit")
        else:
            self.error_invalid_token("<locke-digit>")

    def dime_locke_mult(self):
        # <dime-locke-mult>
        prod = self.get_production("<dime-locke-mult>")
        if prod == 382:
            self.eat(",")
            self.dime_locke()
            self.dime_locke_mult()
        elif prod == 383:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-locke-mult>")

    def parch_locke(self):
        # <parch-locke>
        prod = self.get_production("<parch-locke>")
        if prod == 384:
            self.eat("id")
            self.eat("=")
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<parch-locke>")

    def parch_locke_mult(self):
        # <parch-locke-mult>
        prod = self.get_production("<parch-locke-mult>")
        if prod == 385:
            self.eat(",")
            self.parch_locke()
            self.parch_locke_mult()
        elif prod == 386:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-locke-mult>")

    def scroll_locke(self):
        # <scroll-locke>
        prod = self.get_production("<scroll-locke>")
        if prod == 387:
            self.eat("id")
            self.eat("=")
            self.eat("SCROLL-lit")
            self.scr_id()
        else:
            self.error_invalid_token("<scroll-locke>")

    def scr_id(self):
        # <scr-id>
        prod = self.get_production("<scr-id>")
        if prod == 388:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
        elif prod == 389:
            pass # Lambda
        else:
            self.error_invalid_token("<scr-id>")

    def scroll_locke_mult(self):
        # <scroll-locke-mult>
        prod = self.get_production("<scroll-locke-mult>")
        if prod == 390:
            self.eat(",")
            self.scroll_locke()
            self.scroll_locke_mult()
        elif prod == 391:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-locke-mult>")

    def bool_locke(self):
        # <bool-locke>
        prod = self.get_production("<bool-locke>")
        if prod == 392:
            self.eat("id")
            self.eat("=")
            self.locke_bool()
        else:
            self.error_invalid_token("<bool-locke>")

    def locke_bool(self):
        # <locke-bool>
        prod = self.get_production("<locke-bool>")
        if prod == 393:
            self.eat("AYE")
        elif prod == 394:
            self.eat("NAY")
        else:
            self.error_invalid_token("<locke-bool>")

    def bool_locke_mult(self):
        # <bool-locke-mult>
        prod = self.get_production("<bool-locke-mult>")
        if prod == 395:
            self.eat(",")
            self.bool_locke()
            self.bool_locke_mult()
        elif prod == 396:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-locke-mult>")

    # ==================== STRUCT & SUB-FUNCS ====================

    def struct(self):
        # <struct>
        prod = self.get_production("<struct>")
        if prod == 397:
            self.eat("MAST")
            self.eat("id")
            self.eat("[")
            self.mem_dec()
            self.mem_dec_tail()
            self.eat("]")
            self.eat("!!")
            self.struct()
            self.sub_func()
        elif prod == 398:
            pass # Lambda
        else:
            self.error_invalid_token("<struct>")

    def mem_dec(self):
        # <mem-dec>
        prod = self.get_production("<mem-dec>")
        if prod == 399:
            self.d_type()
            self.eat("id")
            self.mem_mult()
            self.eat("!!")
        else:
            self.error_invalid_token("<mem-dec>")

    def mem_mult(self):
        # <mem-mult>
        prod = self.get_production("<mem-mult>")
        if prod == 400:
            self.eat(",")
            self.eat("id")
            self.mem_mult()
        elif prod == 401:
            pass # Lambda
        else:
            self.error_invalid_token("<mem-mult>")

    def mem_dec_tail(self):
        # <mem-dec-tail>
        prod = self.get_production("<mem-dec-tail>")
        if prod == 402:
            self.mem_dec()
            self.mem_dec_tail()
        elif prod == 403:
            pass # Lambda
        else:
            self.error_invalid_token("<mem-dec-tail>")

    def sub_func(self):
        # <sub-func>
        prod = self.get_production("<sub-func>")
        if prod == 404: self.return_func()
        elif prod == 405: self.nonreturn_func()
        elif prod == 406: pass # Lambda
        else:
            self.error_invalid_token("<sub-func>")

    def return_func(self):
        # <return-func>
        prod = self.get_production("<return-func>")
        if prod == 407: 
            self.eat("COIN")
            self.eat("id")
            self.coin_func()
        elif prod == 408:
            self.eat("DIME")
            self.eat("id")
            self.dime_func()
        elif prod == 409:
            self.eat("PARCH")
            self.eat("id")
            self.parch_func()
        elif prod == 410:
            self.eat("SCROLL")
            self.eat("id")
            self.scroll_func()
        elif prod == 411:
            self.eat("BOOL")
            self.eat("id")
            self.bool_func()
        else:
            self.error_invalid_token("<return-func>")

    def nonreturn_func(self):
        # <nonreturn-func>
        prod = self.get_production("<nonreturn-func>")
        if prod == 412:
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
        if prod == 413:
            self.nonret_stmnt()
            self.nonret_tail()
        else:
            self.error_invalid_token("<nonret-stmnts>")
    
    def nonret_stmnt(self):
        # <nonret-stmnt>
        prod = self.get_production("<nonret-stmnt>")
        if prod == 414:
            self.statements()
        else:
            self.error_invalid_token("<nonret-stmnt>")

    def nonret_tail(self):
        # <nonret-tail>
        prod = self.get_production("<nonret-tail>")
        if prod == 415:
            self.nonret_stmnts()
        elif prod == 416:
            pass # Lambda
        else:
             self.error_invalid_token("<nonret-tail>")

    def nonret_back(self):
        # <nonret-back>
        prod = self.get_production("<nonret-back>")
        if prod == 417:
            self.eat("BACK")
            self.eat("!!")
        elif prod == 418:
            pass # Lambda
        else:
            self.error_invalid_token("<nonret-back>")

    def local_dec(self):
        # <local-dec>
        prod = self.get_production("<local-dec>")
        if prod == 419:
            self.var_arr()
            self.local_dec()
        elif prod == 420:
            self.struct_dec()
        elif prod == 421:
            pass # Lambda
        else:
            self.error_invalid_token("<local-dec>")

    def var_arr(self):
        # <var-arr>
        prod = self.get_production("<var-arr>")
        if prod == 422:
            self.eat("COIN")
            self.eat("id")
            self.coin_local()
        elif prod == 423:
            self.eat("DIME")
            self.eat("id")
            self.dime_local()
        elif prod == 424:
            self.eat("PARCH")
            self.eat("id")
            self.parch_local()
        elif prod == 425:
            self.eat("SCROLL")
            self.eat("id")
            self.scroll_local()
        elif prod == 426:
            self.eat("BOOL")
            self.eat("id")
            self.bool_local()
        else:
            self.error_invalid_token("<var-arr>")

    def coin_local(self):
        # <coin-local>
        prod = self.get_production("<coin-local>")
        if prod == 427: 
            self.coin_var()
            self.eat("!!")
        elif prod == 428:
            self.coin_arr()
            self.eat("!!")
        else: self.error_invalid_token("<coin-local>")

    def dime_local(self):
        # <dime-local>
        prod = self.get_production("<dime-local>")
        if prod == 429: 
            self.dime_var()
            self.eat("!!")
        elif prod == 430:
            self.dime_arr()
            self.eat("!!")
        else: self.error_invalid_token("<dime-local>")

    def parch_local(self):
        # <parch-local>
        prod = self.get_production("<parch-local>")
        if prod == 431: 
            self.parch_var()
            self.eat("!!")
        elif prod == 432:
            self.parch_arr()
            self.eat("!!")
        else: self.error_invalid_token("<parch-local>")

    def scroll_local(self):
        # <scroll-local>
        prod = self.get_production("<scroll-local>")
        if prod == 433: 
            self.scroll_var()
            self.eat("!!")
        elif prod == 434:
            self.scroll_arr()
            self.eat("!!")
        else: self.error_invalid_token("<scroll-local>")

    def bool_local(self):
        # <bool-local>
        prod = self.get_production("<bool-local>")
        if prod == 435: 
            self.bool_var()
            self.eat("!!")
        elif prod == 436:
            self.bool_arr()
            self.eat("!!")
        else: self.error_invalid_token("<bool-local>")

    def struct_dec(self):
        # <struct-dec>
        prod = self.get_production("<struct-dec>")
        if prod == 437:
            self.eat("MAST")
            self.eat("id")
            self.eat("id")
            self.str_dec_init()
            self.eat("!!")
            self.struct_dec()
        elif prod == 438:
            pass # Lambda
        else:
            self.error_invalid_token("<struct-dec>")

    def str_dec_init(self):
        # <str-dec-init>
        prod = self.get_production("<str-dec-init>")
        if prod == 439:
            self.eat(",")
            self.eat("id")
            self.str_dec_tail()
        elif prod == 440:
            self.eat("=")
            self.eat("[")
            self.str_val()
            self.str_val_tail()
            self.eat("]")
        elif prod == 441:
            pass # Lambda
        else:
            self.error_invalid_token("<str-dec-init>")

    def str_dec_tail(self):
        # <str-dec-tail>
        prod = self.get_production("<str-dec-tail>")
        if prod == 442:
            self.eat(",")
            self.eat("id")
            self.str_dec_tail()
        elif prod == 443:
            pass # Lambda
        else:
            self.error_invalid_token("<str-dec-tail>")

    def str_val(self):
        # <str-val>
        prod = self.get_production("<str-val>")
        if prod == 444:
            self.var_val()
        elif prod == 445:
            self.eat("$")
            self.eat("id")
            self.eat("=")
            self.var_val()
        else:
            self.error_invalid_token("<str-val>")

    def str_val_tail(self):
        # <str-val-tail>
        prod = self.get_production("<str-val-tail>")
        if prod == 446:
            self.eat(",")
            self.str_val()
            self.str_val_tail()
        elif prod == 447:
            pass # Lambda
        else:
            self.error_invalid_token("<str-val-tail>")

    # ==================== STATEMENTS ====================

    def statements(self):
        # <statements>
        prod = self.get_production("<statements>")
        if prod == 448: self.assign_stmnt()
        elif prod == 449: self.ask_stmnt()
        elif prod == 450: self.echo_stmnt()
        elif prod == 451: self.look_stmnt()
        elif prod == 452: self.chart_stmnt()
        elif prod == 453: self.hoist_stmnt()
        elif prod == 454: self.heave_stmnt()
        elif prod == 455: self.haul_stmnt()
        elif prod == 456:
            self.unary_exp()
            self.eat("!!")
        else:
            self.error_invalid_token("<statements>")

    def assign_stmnt(self):
        # <assign-stmnt>
        prod = self.get_production("<assign-stmnt>")
        if prod == 457:
            self.eat("id")
            self.assign_tail()
            self.eat("!!")
        else:
            self.error_invalid_token("<assign-stmnt>")

    def assign_tail(self):
        # <assign-tail>
        prod = self.get_production("<assign-tail>")
        if prod == 458:
            self.arr_str()
            self.assign_body()
        elif prod == 459:
            self.eat("(")
            self.args()
            self.eat(")")
        else:
            self.error_invalid_token("<assign-tail>")

    def arr_str(self):
        # <arr-str>
        prod = self.get_production("<arr-str>")
        if prod == 460:
            self.eat("{")
            self.index()
            self.eat("}")
            self.arr_str_tail()
        elif prod == 461:
            self.eat("$")
            self.eat("id")
        elif prod == 462:
            pass # Lambda
        else:
            self.error_invalid_token("<arr-str>")

    def arr_str_tail(self):
        # <arr-str-tail>
        prod = self.get_production("<arr-str-tail>")
        if prod == 463:
            self.eat("{")
            self.index()
            self.eat("}")
        elif prod == 464:
            pass # Lambda
        else:
            self.error_invalid_token("<arr-str-tail>")

    def assign_body(self):
        # <assign-body>
        prod = self.get_production("<assign-body>")
        if prod == 465:
            self.eat("=")
            self.assign_val()
        elif prod == 466:
            self.arith_assign_op()
            self.arith_ope()
            self.arith_exp()
        else:
            self.error_invalid_token("<assign-body>")

    def assign_val(self):
        # <assign-val>
        prod = self.get_production("<assign-val>")
        if prod == 467:
            self.var_val()
        else:
            self.error_invalid_token("<assign-val>")

    def arith_assign_op(self):
        # <arith-assign-op>
        prod = self.get_production("<arith-assign-op>")
        if prod == 468: self.eat("+=")
        elif prod == 469: self.eat("-=")
        elif prod == 470: self.eat("*=")
        elif prod == 471: self.eat("/=")
        elif prod == 472: self.eat("%=")
        elif prod == 473: self.eat("^=")
        else:
            self.error_invalid_token("<arith-assign-op>")

    def arith_ope(self):
        # <arith-ope>
        prod = self.get_production("<arith-ope>")
        if prod == 474:
            self.eat("id")
            self.id_tail()
        elif prod == 475:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        elif prod == 476:
            self.eat("COIN-lit")
        elif prod == 477:
            self.eat("DIME-lit")
        else:
            self.error_invalid_token("<arith-ope>")

    def arith_exp(self):
        # <arith-exp>
        prod = self.get_production("<arith-exp>")
        if prod == 478:
            self.arith_op()
            self.arith_ope()
            self.arith_exp()
        elif prod == 479:
            pass # Lambda
        else:
            self.error_invalid_token("<arith-exp>")

    def ask_stmnt(self):
        # <ask-stmnt>
        prod = self.get_production("<ask-stmnt>")
        if prod == 480:
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
        if prod == 481:
            self.eat("@")
            self.eat("id")
            self.arr_str()
            self.addr_tail()
        else:
            self.error_invalid_token("<addr>")

    def addr_tail(self):
        # <addr-tail>
        prod = self.get_production("<addr-tail>")
        if prod == 482:
            self.eat(",")
            self.addr()
        elif prod == 483:
            pass # Lambda
        else:
            self.error_invalid_token("<addr-tail>")

    def echo_stmnt(self):
        # <echo-stmnt>
        prod = self.get_production("<echo-stmnt>")
        if prod == 484:
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
        if prod == 485:
            self.eat(",")
            self.echo_val()
            self.echo_arg()
        elif prod == 486:
            pass # Lambda
        else:
            self.error_invalid_token("<echo-arg>")

    def echo_val(self):
        # <echo-val>
        prod = self.get_production("<echo-val>")
        if prod == 487:
            self.var_val()
        else:
            self.error_invalid_token("<echo-val>")

    def look_stmnt(self):
        # <look-stmnt>
        prod = self.get_production("<look-stmnt>")
        if prod == 488:
            self.eat("LOOK")
            self.eat("(")
            self.condition()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
            self.look_tail()
        else:
            self.error_invalid_token("<look-stmnt>")

    def condition(self):
        # <condition>
        prod = self.get_production("<condition>")
        if prod == 489:
            self.bool_val()
        else:
            self.error_invalid_token("<condition>")

    def look_body(self):
        # <look-body>
        prod = self.get_production("<look-body>")
        if prod == 490:
            self.look_body_stmnt()
            self.look_body()
        elif prod == 491:
            pass # Lambda
        else:
            self.error_invalid_token("<look-body>")

    def look_body_stmnt(self):
        # <look-body-stmnt>
        prod = self.get_production("<look-body-stmnt>")
        if prod == 492:
            self.statements()
        else:
            self.error_invalid_token("<look-body-stmnt>")

    def jump_stmnt(self):
        # <jump-stmnt>
        prod = self.get_production("<jump-stmnt>")
        if prod == 493:
            self.eat("SAIL")
            self.eat("!!")
        elif prod == 494:
            self.eat("LAND")
            self.eat("!!")
        elif prod == 495:
            pass # Lambda
        else:
            self.error_invalid_token("<jump-stmnt>")

    def look_tail(self):
        # <look-tail>
        prod = self.get_production("<look-tail>")
        if prod == 496:
            self.eat("DROPLOOK")
            self.eat("(")
            self.condition()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
            self.look_tail()
        elif prod == 497:
            self.eat("DROP")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
        elif prod == 498:
            pass # Lambda
        else:
            self.error_invalid_token("<look-tail>")

    def chart_stmnt(self):
        # <chart-stmnt>
        prod = self.get_production("<chart-stmnt>")
        if prod == 499:
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
        if prod == 500: 
            self.eat("id")
            self.id_tail()
        elif prod == 501: 
            self.chart_const()
        else:
            self.error_invalid_token("<chart-cond>")

    def chart_const(self):
        # <chart-const>
        prod = self.get_production("<chart-const>")
        if prod == 502: self.eat("COIN-lit")
        elif prod == 503: self.eat("PARCH-lit")
        elif prod == 504: 
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<chart-const>")

    def courses(self):
        # <courses>
        prod = self.get_production("<courses>")
        if prod == 505:
            self.eat("COURSE")
            self.chart_const()
            self.eat(":")
            self.course_body()
            self.course_jmp()
        else:
            self.error_invalid_token("<courses>")

    def course_body(self):
        # <course-body>
        prod = self.get_production("<course-body>")
        if prod == 506:
            self.course_stmnt()
            self.course_body()
        elif prod == 507:
            pass # Lambda
        else:
            self.error_invalid_token("<course-body>")

    def course_stmnt(self):
        # <course-stmnt>
        prod = self.get_production("<course-stmnt>")
        if prod == 508:
            self.statements()
        else:
            self.error_invalid_token("<course-stmnt>")
    
    def course_jmp(self):
        # <course-jmp>
        prod = self.get_production("<course-jmp>")
        if prod == 509:
             self.eat("SAIL")
             self.eat("!!")
        elif prod == 510:
             self.eat("LAND")
             self.eat("!!")
        elif prod == 511:
            pass # Lambda
        else:
             self.error_invalid_token("<course-jmp>")

    def course_tail(self):
        # <course-tail>
        prod = self.get_production("<course-tail>")
        if prod == 512:
            self.courses()
            self.course_tail()
        elif prod == 513:
            pass # Lambda
        else:
            self.error_invalid_token("<course-tail>")

    def adrift_case(self):
        # <adrift-case>
        prod = self.get_production("<adrift-case>")
        if prod == 514:
            self.eat("ADRIFT")
            self.eat(":")
            self.adrift_body()
            self.eat("LAND")
            self.eat("!!")
        elif prod == 515:
            pass # Lambda
        else:
            self.error_invalid_token("<adrift-case>")

    def adrift_body(self):
        # <adrift-body>
        prod = self.get_production("<adrift-body>")
        if prod == 516:
            self.statements()
            self.adrift_body()
        elif prod == 517:
            pass # Lambda
        else:
            self.error_invalid_token("<adrift-body>")

    def hoist_stmnt(self):
        # <hoist-stmnt>
        prod = self.get_production("<hoist-stmnt>")
        if prod == 518:
            self.eat("HOIST")
            self.eat("(")
            self.hoist_init()
            self.eat("!!")
            self.hoist_cond()
            self.eat("!!")
            self.hoist_upd()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
        else:
            self.error_invalid_token("<hoist-stmnt>")

    def hoist_init(self):
        # <hoist-init>
        prod = self.get_production("<hoist-init>")
        if prod == 519:
            self.eat("COIN")
            self.eat("id")
            self.eat("=")
            self.eat("COIN-lit")
            self.init1_mult()
        elif prod == 520:
            self.eat("id")
            self.arr_str()
            self.eat("=")
            self.eat("COIN-lit")
            self.init2_mult()
        elif prod == 521:
            pass # Lambda
        else:
            self.error_invalid_token("<hoist-init>")

    def init1_mult(self):
        # <init1-mult>
        prod = self.get_production("<init1-mult>")
        if prod == 522:
            self.eat(",")
            self.eat("id")
            self.eat("=")
            self.eat("COIN-lit")
            self.init1_mult()
        elif prod == 523:
            pass # Lambda
        else:
            self.error_invalid_token("<init1-mult>")

    def init2_mult(self):
        # <init2-mult>
        prod = self.get_production("<init2-mult>")
        if prod == 524:
            self.eat(",")
            self.eat("id")
            self.arr_str()
            self.eat("=")
            self.eat("COIN-lit")
            self.init2_mult()
        elif prod == 525:
            pass # Lambda
        else:
            self.error_invalid_token("<init2-mult>")

    def hoist_cond(self):
        # <hoist-cond>
        prod = self.get_production("<hoist-cond>")
        if prod == 526:
            self.eat("id")
            self.arr_str()
            self.releq_op()
            self.hoist_ope()
            self.hoist_log()
        else:
            self.error_invalid_token("<hoist-cond>")

    def releq_op(self):
        # <releq-op>
        prod = self.get_production("<releq-op>")
        if prod == 527: self.rel_op()
        elif prod == 528: self.eq_op()
        else:
            self.error_invalid_token("<releq-op>")

    def hoist_ope(self):
        # <hoist-ope>
        prod = self.get_production("<hoist-ope>")
        if prod == 529:
            self.eat("id")
            self.id_tail()
        elif prod == 530:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<hoist-ope>")

    def hoist_log(self):
        # <hoist-log>
        prod = self.get_production("<hoist-log>")
        if prod == 531:
            self.log_op()
            self.hoist_cond()
        elif prod == 532:
            pass # Lambda
        else:
            self.error_invalid_token("<hoist-log>")

    def hoist_upd(self):
        # <hoist-upd>
        prod = self.get_production("<hoist-upd>")
        if prod == 533:
            self.upd()
            self.upd_mult()
        else:
            self.error_invalid_token("<hoist-upd>")

    def upd(self):
        # <upd>
        prod = self.get_production("<upd>")
        if prod == 534:
            self.hoist_unary()
        elif prod == 535:
            self.hoist_assign()
        else:
            self.error_invalid_token("<upd>")

    def hoist_unary(self):
        # <hoist-unary>
        prod = self.get_production("<hoist-unary>")
        if prod == 536:
            self.unary_op()
            self.eat("id")
            self.arr_str()
        else:
            self.error_invalid_token("<hoist-unary>")

    def hoist_assign(self):
        # <hoist-assign>
        prod = self.get_production("<hoist-assign>")
        if prod == 537:
            self.eat("id")
            self.arr_str()
            self.arith_assign_op()
            self.hoist_arith_ope()
            self.hoist_arith()
        else:
            self.error_invalid_token("<hoist-assign>")

    def hoist_arith_ope(self):
        # <hoist-arith-ope>
        prod = self.get_production("<hoist-arith-ope>")
        if prod == 538:
            self.eat("id")
            self.id_tail()
        elif prod == 539:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        elif prod == 540:
            self.eat("COIN-lit")
        elif prod == 541:
            self.eat("DIME-lit")
        else:
            self.error_invalid_token("<hoist-arith-ope>")

    def hoist_arith(self):
        # <hoist-arith>
        prod = self.get_production("<hoist-arith>")
        if prod == 542:
            self.arith_op()
            self.hoist_arith_ope()
            self.hoist_arith()
        elif prod == 543:
            pass # Lambda
        else:
            self.error_invalid_token("<hoist-arith>")

    def upd_mult(self):
        # <upd-mult>
        prod = self.get_production("<upd-mult>")
        if prod == 544:
            self.eat(",")
            self.upd()
            self.upd_mult()
        elif prod == 545:
            pass # Lambda
        else:
            self.error_invalid_token("<upd-mult>")

    def heave_stmnt(self):
        # <heave-stmnt>
        prod = self.get_production("<heave-stmnt>")
        if prod == 546:
            self.eat("HEAVE")
            self.eat("(")
            self.condition()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
        else:
            self.error_invalid_token("<heave-stmnt>")

    def haul_stmnt(self):
        # <haul-stmnt>
        prod = self.get_production("<haul-stmnt>")
        if prod == 547:
            self.eat("HAUL")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
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
        if prod == 548:
            self.unary_op()
            self.eat("id")
            self.arr_str()
        else:
            self.error_invalid_token("<unary-exp>")

    def unary_op(self):
        # <unary-op>
        prod = self.get_production("<unary-op>")
        if prod == 549: self.eat("+#")
        elif prod == 550: self.eat("-#")
        else:
            self.error_invalid_token("<unary-op>")

    def ahoy_stmnts(self):
        # <ahoy-stmnts>
        prod = self.get_production("<ahoy-stmnts>")
        if prod == 551:
            self.ahoy_stmnt()
            self.ahoy_tail()
        else:
            self.error_invalid_token("<ahoy-stmnts>")

    def ahoy_tail(self):
        # <ahoy-tail>
        prod = self.get_production("<ahoy-tail>")
        if prod == 552:
            self.ahoy_stmnts()
        elif prod == 553:
            pass # Lambda
        else:
            self.error_invalid_token("<ahoy-tail>")

    def ahoy_stmnt(self):
        # <ahoy-stmnt>
        prod = self.get_production("<ahoy-stmnt>")
        if prod == 554: self.ahoy_assign()
        elif prod == 555: self.ahoy_ask()
        elif prod == 556: self.ahoy_echo()
        elif prod == 557: self.ahoy_look()
        elif prod == 558: self.ahoy_chart()
        elif prod == 559: self.ahoy_hoist()
        elif prod == 560: self.ahoy_heave()
        elif prod == 561: self.ahoy_haul()
        elif prod == 562: 
            self.unary_exp()
            self.eat("!!")
        else:
            self.error_invalid_token("<ahoy-stmnt>")

    def ahoy_assign(self):
        # <ahoy-assign>
        prod = self.get_production("<ahoy-assign>")
        if prod == 563:
            self.eat("id")
            self.assign_tail()
            self.eat("!!")
        else:
            self.error_invalid_token("<ahoy-assign>")

    def ahoy_ask(self):
        # <ahoy-ask>
        prod = self.get_production("<ahoy-ask>")
        if prod == 564:
            self.eat("ASK")
            self.eat("(")
            self.eat("SCROLL-lit")
            self.eat(",")
            self.addr()
            self.eat(")")
            self.eat("!!")
        else:
            self.error_invalid_token("<ahoy-ask>")

    def ahoy_echo(self):
        # <ahoy-echo>
        prod = self.get_production("<ahoy-echo>")
        if prod == 565:
            self.eat("ECHO")
            self.eat("(")
            self.eat("SCROLL-lit")
            self.echo_arg()
            self.eat(")")
            self.eat("!!")
        else:
            self.error_invalid_token("<ahoy-echo>")

    def ahoy_look(self):
        # <ahoy-look>
        prod = self.get_production("<ahoy-look>")
        if prod == 566:
            self.eat("LOOK")
            self.eat("(")
            self.condition()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
            self.ahoy_look_tail()
        else:
            self.error_invalid_token("<ahoy-look>")

    def ahoy_look_tail(self):
        # <ahoy-look-tail>
        prod = self.get_production("<ahoy-look-tail>")
        if prod == 567:
            self.eat("DROPLOOK")
            self.eat("(")
            self.condition()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
            self.ahoy_look_tail()
        elif prod == 568:
            self.eat("DROP")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
        elif prod == 569:
            pass # Lambda
        else:
            self.error_invalid_token("<ahoy-look-tail>")

    def ahoy_chart(self):
        # <ahoy-chart>
        prod = self.get_production("<ahoy-chart>")
        if prod == 570:
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
            self.error_invalid_token("<ahoy-chart>")

    def ahoy_hoist(self):
        # <ahoy-hoist>
        prod = self.get_production("<ahoy-hoist>")
        if prod == 571:
            self.eat("HOIST")
            self.eat("(")
            self.hoist_init()
            self.eat("!!")
            self.hoist_cond()
            self.eat("!!")
            self.hoist_upd()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
        else:
            self.error_invalid_token("<ahoy-hoist>")

    def ahoy_heave(self):
        # <ahoy-heave>
        prod = self.get_production("<ahoy-heave>")
        if prod == 572:
            self.eat("HEAVE")
            self.eat("(")
            self.condition()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
        else:
            self.error_invalid_token("<ahoy-heave>")

    def ahoy_haul(self):
        # <ahoy-haul>
        prod = self.get_production("<ahoy-haul>")
        if prod == 573:
            self.eat("HAUL")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
            self.eat("HEAVE")
            self.eat("(")
            self.condition()
            self.eat(")")
            self.eat("!!")
        else:
            self.error_invalid_token("<ahoy-haul>")