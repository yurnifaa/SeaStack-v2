import sys
from syntax.Predict_Set import PREDICT
from backend.error_msg import ErrorHandler 

class Parser:
    def __init__(self, tokens, source_code):
        # Initializes the Parser.
        # :param tokens: List of Token objects
        # :param source_code: for error context
        ignored_types = [
            "whitespace", 
            "newline", 
            "single-comment", 
            "multi-comment"
        ]
        
        # Filter out junk tokens
        self.tokens = [t for t in tokens if t.type not in ignored_types]
        
        # Normalize id types
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
        # Consumes the current token if it matches `token_type, otherwise triggers 'Missing Token'
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            raise Exception(self.err_handler.get_missing_token_error(
                self.current_token, 
                token_type
            ))

    def get_production(self, non_terminal):
        # uses PREDICT_SET to return the Production Number based on current token
        if not self.current_token:
            return None
            
        productions = PREDICT.get(non_terminal, {})
        return productions.get(self.current_token.type)

    def error_invalid_token(self, non_terminal):
        # raise invalid token error with expected tokens from Predict Set
        expected = list(PREDICT.get(non_terminal, {}).keys())
        raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    # =========================================
    # Entry Point
    # =========================================
    def parse(self):
        try:
            # Missing start check
            if not self.tokens:
                raise Exception(self.err_handler.get_missing_start_error())

            self.program()
            
            # Expected EOF check
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
    # GRAMMAR PRODUCTIONS
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
            self.ahoy_local_dec()
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

    # ==================== COIN ====================

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
            self.neg()
            self.neg_coin_val()
        elif prod == 23:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<coin-val>")

    def neg(self):
        # <neg>
        prod = self.get_production("<neg>")
        if prod == 24: self.eat("-")
        elif prod == 25: pass # Lambda
        else: self.error_invalid_token("<neg>")

    def neg_coin_val(self):
        # <neg-coin-val>
        prod = self.get_production("<neg-coin-val>")
        if prod == 26:
            self.eat("id")
            self.id_tail()
        elif prod == 27:
            self.eat("(")
            self.coin_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-coin-val>")

    def coin_exp(self):
        # <coin-exp>
        prod = self.get_production("<coin-exp>")
        if prod == 28:
            self.arith_op()
            self.coin_val()
            self.coin_exp()
        elif prod == 29:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-exp>")

    def coin_grp_val(self):
        # <coin-grp-val>
        prod = self.get_production("<coin-grp-val>")
        if prod == 30:
            self.coin_grp_ope()
            self.coin_grp_exp()
        else:
            self.error_invalid_token("<coin-grp-val>")

    def coin_grp_ope(self):
        # <coin-grp-ope>
        prod = self.get_production("<coin-grp-ope>")
        if prod == 31:
            self.neg()
            self.neg_coin_grp_ope()
        elif prod == 32:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<coin-grp-ope>")

    def neg_coin_grp_ope(self):
        # <neg-coin-grp-ope>
        prod = self.get_production("<neg-coin-grp-ope>")
        if prod == 33:
            self.eat("id")
            self.id_tail()
        elif prod == 34:
            self.eat("(")
            self.coin_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-coin-grp-ope>")

    def coin_grp_exp(self):
        # <coin-grp-exp>
        prod = self.get_production("<coin-grp-exp>")
        if prod == 35:
            self.arith_op()
            self.coin_grp_ope()
            self.coin_grp_exp()
        elif prod == 36:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-grp-exp>")

    def arith_op(self):
        # <arith-op>
        prod = self.get_production("<arith-op>")
        if prod == 37: self.eat("+")
        elif prod == 38: self.eat("-")
        elif prod == 39: self.eat("*")
        elif prod == 40: self.eat("/")
        elif prod == 41: self.eat("%")
        elif prod == 42: self.eat("^")
        else:
            self.error_invalid_token("<arith-op>")

    def coin_arr(self):
        # <coin-arr>
        prod = self.get_production("<coin-arr>")
        if prod == 43:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.coin_arr_tail()
        else:
            self.error_invalid_token("<coin-arr>")

    def coin_arr_tail(self):
        # <coin-arr-tail>
        prod = self.get_production("<coin-arr-tail>")
        if prod == 44:
            self.eat("=")
            self.eat("[")
            self.coin_arr1()
            self.eat("]")
        elif prod == 45:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.coin_arr2_tail()
        elif prod == 46:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-arr-tail>")

    def coin_arr1(self):
        # <coin-arr1>
        prod = self.get_production("<coin-arr1>")
        if prod == 47:
            self.coin_arr_val()
            self.cav_tail()
        else:
            self.error_invalid_token("<coin-arr1>")

    def coin_arr_val(self):
        # <coin-arr-val>
        prod = self.get_production("<coin-arr-val>")
        if prod == 48:
            self.coin_arr_ope()
            self.coin_arr_exp()
        else:
            self.error_invalid_token("<coin-arr-val>")

    def coin_arr_ope(self):
        # <coin-arr-ope>
        prod = self.get_production("<coin-arr-ope>")
        if prod == 49:
            self.neg()
            self.neg_coin_arr_ope()
        elif prod == 50:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<coin-arr-ope>")

    def neg_coin_arr_ope(self):
        # <neg-coin-arr-ope>
        prod = self.get_production("<neg-coin-arr-ope>")
        if prod == 51:
            self.eat("id")
            self.id_tail()
        elif prod == 52:
            self.eat("(")
            self.coin_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-coin-arr-ope>")

    def coin_arr_exp(self):
        # <coin-arr-exp>
        prod = self.get_production("<coin-arr-exp>")
        if prod == 53:
            self.arith_op()
            self.coin_arr_ope()
            self.coin_arr_exp()
        elif prod == 54:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-arr-exp>")

    def cav_tail(self):
        # <cav-tail>
        prod = self.get_production("<cav-tail>")
        if prod == 55:
            self.eat(",")
            self.coin_arr1()
        elif prod == 56:
            pass # Lambda
        else:
            self.error_invalid_token("<cav-tail>")

    def coin_arr2_tail(self):
        # <coin-arr2-tail>
        prod = self.get_production("<coin-arr2-tail>")
        if prod == 57:
            self.eat("=")
            self.eat("[")
            self.coin_arr2()
            self.eat("]")
        elif prod == 58:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-arr2-tail>")

    def coin_arr2(self):
        # <coin-arr2>
        prod = self.get_production("<coin-arr2>")
        if prod == 59:
            self.eat("[")
            self.coin_arr1()
            self.eat("]")
            self.cav2_tail()
        else:
            self.error_invalid_token("<coin-arr2>")

    def cav2_tail(self):
        # <cav2-tail>
        prod = self.get_production("<cav2-tail>")
        if prod == 60:
            self.eat(",")
            self.coin_arr2()
        elif prod == 61:
            pass # Lambda
        else:
            self.error_invalid_token("<cav2-tail>")

    def coin_func(self):
        # <coin-func>
        prod = self.get_production("<coin-func>")
        if prod == 62:
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
        if prod == 63:
            self.coin_ret_ope()
            self.coin_ret_exp()
        else:
            self.error_invalid_token("<coin-retval>")

    def coin_ret_ope(self):
        # <coin-ret-ope>
        prod = self.get_production("<coin-ret-ope>")
        if prod == 64:
            self.neg()
            self.neg_coin_ret_ope()
        elif prod == 65:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<coin-ret-ope>")

    def neg_coin_ret_ope(self):
        # <neg-coin-ret-ope>
        prod = self.get_production("<neg-coin-ret-ope>")
        if prod == 66:
            self.eat("id")
            self.id_tail()
        elif prod == 67:
            self.eat("(")
            self.coin_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-coin-ret-ope>")

    def coin_ret_exp(self):
        # <coin-ret-exp>
        prod = self.get_production("<coin-ret-exp>")
        if prod == 68:
            self.arith_op()
            self.coin_ret_ope()
            self.coin_ret_exp()
        elif prod == 69:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-ret-exp>")

    # ==================== DIME ====================

    def dime_var_arr_func(self):
        # <dime-var-arr-func>
        prod = self.get_production("<dime-var-arr-func>")
        if prod == 70:
            self.dime_var_arr()
            self.global_dec()
        elif prod == 71:
            self.dime_func()
        else:
            self.error_invalid_token("<dime-var-arr-func>")

    def dime_var_arr(self):
        # <dime-var-arr>
        prod = self.get_production("<dime-var-arr>")
        if prod == 72:
            self.dime_var()
            self.eat("!!")
        elif prod == 73:
            self.dime_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<dime-var-arr>")

    def dime_var(self):
        # <dime-var>
        prod = self.get_production("<dime-var>")
        if prod == 74:
            self.dime_init()
            self.dime_init_mult()
        else:
            self.error_invalid_token("<dime-var>")

    def dime_init(self):
        # <dime-init>
        prod = self.get_production("<dime-init>")
        if prod == 75:
            self.eat("=")
            self.dime_init_val()
        elif prod == 76:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-init>")

    def dime_init_mult(self):
        # <dime-init-mult>
        prod = self.get_production("<dime-init-mult>")
        if prod == 77:
            self.eat(",")
            self.eat("id")
            self.dime_init()
            self.dime_init_mult()
        elif prod == 78:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-init-mult>")

    def dime_init_val(self):
        # <dime-init-val>
        prod = self.get_production("<dime-init-val>")
        if prod == 79:
            self.dime_val()
            self.dime_exp()
        else:
            self.error_invalid_token("<dime-init-val>")

    def dime_val(self):
        # <dime-val>
        prod = self.get_production("<dime-val>")
        if prod == 80:
            self.neg()
            self.neg_dime_val()
        elif prod == 81:
            self.eat("DIME-lit")
        elif prod == 82:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<dime-val>")

    def neg_dime_val(self):
        # <neg-dime-val>
        prod = self.get_production("<neg-dime-val>")
        if prod == 83:
            self.eat("id")
            self.id_tail()
        elif prod == 84:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-dime-val>")

    def dime_exp(self):
        # <dime-exp>
        prod = self.get_production("<dime-exp>")
        if prod == 85:
            self.arith_op()
            self.dime_val()
            self.dime_exp()
        elif prod == 86:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-exp>")

    def dime_grp_val(self):
        # <dime-grp-val>
        prod = self.get_production("<dime-grp-val>")
        if prod == 87:
            self.dime_grp_ope()
            self.dime_grp_exp()
        else:
            self.error_invalid_token("<dime-grp-val>")

    def dime_grp_ope(self):
        # <dime-grp-ope>
        prod = self.get_production("<dime-grp-ope>")
        if prod == 88:
            self.neg()
            self.neg_dime_grp_ope()
        elif prod == 89:
            self.eat("DIME-lit")
        elif prod == 90:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<dime-grp-ope>")

    def neg_dime_grp_ope(self):
        # <neg-dime-grp-ope>
        prod = self.get_production("<neg-dime-grp-ope>")
        if prod == 91:
            self.eat("id")
            self.id_tail()
        elif prod == 92:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-dime-grp-ope>")

    def dime_grp_exp(self):
        # <dime-grp-exp>
        prod = self.get_production("<dime-grp-exp>")
        if prod == 93:
            self.arith_op()
            self.dime_grp_ope()
            self.dime_grp_exp()
        elif prod == 94:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-grp-exp>")

    def dime_arr(self):
        # <dime-arr>
        prod = self.get_production("<dime-arr>")
        if prod == 95:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.dime_arr_tail()
        else:
            self.error_invalid_token("<dime-arr>")

    def dime_arr_tail(self):
        # <dime-arr-tail>
        prod = self.get_production("<dime-arr-tail>")
        if prod == 96:
            self.eat("=")
            self.eat("[")
            self.dime_arr1()
            self.eat("]")
        elif prod == 97:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.dime_arr2_tail()
        elif prod == 98:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-arr-tail>")

    def dime_arr1(self):
        # <dime-arr1>
        prod = self.get_production("<dime-arr1>")
        if prod == 99:
            self.dime_arr_val()
            self.dav_tail()
        else:
            self.error_invalid_token("<dime-arr1>")

    def dime_arr_val(self):
        # <dime-arr-val>
        prod = self.get_production("<dime-arr-val>")
        if prod == 100:
            self.dime_arr_ope()
            self.dime_arr_exp()
        else:
            self.error_invalid_token("<dime-arr-val>")

    def dime_arr_ope(self):
        # <dime-arr-ope>
        prod = self.get_production("<dime-arr-ope>")
        if prod == 101:
            self.neg()
            self.neg_dime_arr_ope()
        elif prod == 102:
            self.eat("DIME-lit")
        elif prod == 103:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<dime-arr-ope>")

    def neg_dime_arr_ope(self):
        # <neg-dime-arr-ope>
        prod = self.get_production("<neg-dime-arr-ope>")
        if prod == 104:
            self.eat("id")
            self.id_tail()
        elif prod == 105:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-dime-arr-ope>")

    def dime_arr_exp(self):
        # <dime-arr-exp>
        prod = self.get_production("<dime-arr-exp>")
        if prod == 106:
            self.arith_op()
            self.dime_arr_ope()
            self.dime_arr_exp()
        elif prod == 107:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-arr-exp>")

    def dav_tail(self):
        # <dav-tail>
        prod = self.get_production("<dav-tail>")
        if prod == 108:
            self.eat(",")
            self.dime_arr1()
        elif prod == 109:
            pass # Lambda
        else:
            self.error_invalid_token("<dav-tail>")

    def dime_arr2_tail(self):
        # <dime-arr2-tail>
        prod = self.get_production("<dime-arr2-tail>")
        if prod == 110:
            self.eat("=")
            self.eat("[")
            self.dime_arr2()
            self.eat("]")
        elif prod == 111:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-arr2-tail>")

    def dime_arr2(self):
        # <dime-arr2>
        prod = self.get_production("<dime-arr2>")
        if prod == 112:
            self.eat("[")
            self.dime_arr1()
            self.eat("]")
            self.dav2_tail()
        else:
            self.error_invalid_token("<dime-arr2>")

    def dav2_tail(self):
        # <dav2-tail>
        prod = self.get_production("<dav2-tail>")
        if prod == 113:
            self.eat(",")
            self.dime_arr2()
        elif prod == 114:
            pass # Lambda
        else:
            self.error_invalid_token("<dav2-tail>")

    def dime_func(self):
        # <dime-func>
        prod = self.get_production("<dime-func>")
        if prod == 115:
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
        if prod == 116:
            self.dime_ret_ope()
            self.dime_ret_exp()
        else:
            self.error_invalid_token("<dime-retval>")

    def dime_ret_ope(self):
        # <dime-ret-ope>
        prod = self.get_production("<dime-ret-ope>")
        if prod == 117:
            self.neg()
            self.neg_dime_ret_ope()
        elif prod == 118:
            self.eat("DIME-lit")
        elif prod == 119:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<dime-ret-ope>")

    def neg_dime_ret_ope(self):
        # <neg-dime-ret-ope>
        prod = self.get_production("<neg-dime-ret-ope>")
        if prod == 120:
            self.eat("id")
            self.id_tail()
        elif prod == 121:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-dime-ret-ope>")

    def dime_ret_exp(self):
        # <dime-ret-exp>
        prod = self.get_production("<dime-ret-exp>")
        if prod == 122:
            self.arith_op()
            self.dime_ret_ope()
            self.dime_ret_exp()
        elif prod == 123:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-ret-exp>")

    # ==================== PARCH ====================

    def parch_var_arr_func(self):
        # <parch-var-arr-func>
        prod = self.get_production("<parch-var-arr-func>")
        if prod == 124:
            self.parch_var_arr()
            self.global_dec()
        elif prod == 125:
            self.parch_func()
        else:
            self.error_invalid_token("<parch-var-arr-func>")

    def parch_var_arr(self):
        # <parch-var-arr>
        prod = self.get_production("<parch-var-arr>")
        if prod == 126:
            self.parch_var()
            self.eat("!!")
        elif prod == 127:
            self.parch_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<parch-var-arr>")

    def parch_var(self):
        # <parch-var>
        prod = self.get_production("<parch-var>")
        if prod == 128:
            self.parch_init()
            self.parch_init_mult()
        else:
            self.error_invalid_token("<parch-var>")

    def parch_init(self):
        # <parch-init>
        prod = self.get_production("<parch-init>")
        if prod == 129:
            self.eat("=")
            self.parch_init_val()
        elif prod == 130:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-init>")

    def parch_init_mult(self):
        # <parch-init-mult>
        prod = self.get_production("<parch-init-mult>")
        if prod == 131:
            self.eat(",")
            self.eat("id")
            self.parch_init()
            self.parch_init_mult()
        elif prod == 132:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-init-mult>")

    def parch_init_val(self):
        # <parch-init-val>
        prod = self.get_production("<parch-init-val>")
        if prod == 133:
            self.eat("id")
            self.id_tail()
        elif prod == 134:
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<parch-init-val>")

    def parch_arr(self):
        # <parch-arr>
        prod = self.get_production("<parch-arr>")
        if prod == 135:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.parch_arr_tail()
        else:
            self.error_invalid_token("<parch-arr>")

    def parch_arr_tail(self):
        # <parch-arr-tail>
        prod = self.get_production("<parch-arr-tail>")
        if prod == 136:
            self.eat("=")
            self.eat("[")
            self.parch_arr1()
            self.eat("]")
        elif prod == 137:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.parch_arr2_tail()
        elif prod == 138:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-arr-tail>")

    def parch_arr1(self):
        # <parch-arr1>
        prod = self.get_production("<parch-arr1>")
        if prod == 139:
            self.parch_arr_val()
            self.pav_tail()
        else:
            self.error_invalid_token("<parch-arr1>")

    def parch_arr_val(self):
        # <parch-arr-val>
        prod = self.get_production("<parch-arr-val>")
        if prod == 140:
            self.eat("id")
            self.id_tail()
        elif prod == 141:
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<parch-arr-val>")

    def pav_tail(self):
        # <pav-tail>
        prod = self.get_production("<pav-tail>")
        if prod == 142:
            self.eat(",")
            self.parch_arr1()
        elif prod == 143:
            pass # Lambda
        else:
            self.error_invalid_token("<pav-tail>")

    def parch_arr2_tail(self):
        # <parch-arr2-tail>
        prod = self.get_production("<parch-arr2-tail>")
        if prod == 144:
            self.eat("=")
            self.eat("[")
            self.parch_arr2()
            self.eat("]")
        elif prod == 145:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-arr2-tail>")

    def parch_arr2(self):
        # <parch-arr2>
        prod = self.get_production("<parch-arr2>")
        if prod == 146:
            self.eat("[")
            self.parch_arr1()
            self.eat("]")
            self.pav2_tail()
        else:
            self.error_invalid_token("<parch-arr2>")

    def pav2_tail(self):
        # <pav2-tail>
        prod = self.get_production("<pav2-tail>")
        if prod == 147:
            self.eat(",")
            self.parch_arr2()
        elif prod == 148:
            pass # Lambda
        else:
            self.error_invalid_token("<pav2-tail>")

    def parch_func(self):
        # <parch-func>
        prod = self.get_production("<parch-func>")
        if prod == 149:
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
        if prod == 150:
            self.eat("id")
            self.id_tail()
        elif prod == 151:
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<parch-retval>")

    # ==================== SCROLL ====================

    def scroll_var_arr_func(self):
        # <scroll-var-arr-func>
        prod = self.get_production("<scroll-var-arr-func>")
        if prod == 152:
            self.scroll_var_arr()
            self.global_dec()
        elif prod == 153:
            self.scroll_func()
            self.sub_func()
        else:
            self.error_invalid_token("<scroll-var-arr-func>")

    def scroll_var_arr(self):
        # <scroll-var-arr>
        prod = self.get_production("<scroll-var-arr>")
        if prod == 154:
            self.scroll_var()
            self.eat("!!")
        elif prod == 155:
            self.scroll_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<scroll-var-arr>")

    def scroll_var(self):
        # <scroll-var>
        prod = self.get_production("<scroll-var>")
        if prod == 156:
            self.scroll_init()
            self.scroll_init_mult()
        else:
            self.error_invalid_token("<scroll-var>")

    def scroll_init(self):
        # <scroll-init>
        prod = self.get_production("<scroll-init>")
        if prod == 157:
            self.eat("=")
            self.scroll_init_val()
        elif prod == 158:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-init>")

    def scroll_init_mult(self):
        # <scroll-init-mult>
        prod = self.get_production("<scroll-init-mult>")
        if prod == 159:
            self.eat(",")
            self.eat("id")
            self.scroll_init()
            self.scroll_init_mult()
        elif prod == 160:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-init-mult>")

    def scroll_init_val(self):
        # <scroll-init-val>
        prod = self.get_production("<scroll-init-val>")
        if prod == 161:
            self.scroll_val()
            self.scroll_exp()
        else:
            self.error_invalid_token("<scroll-init-val>")

    def scroll_val(self):
        # <scroll-val>
        prod = self.get_production("<scroll-val>")
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
            self.error_invalid_token("<scroll-val>")

    def scr_char(self):
        # <scr-char>
        prod = self.get_production("<scr-char>")
        if prod == 165:
            self.eat("{")
            self.index()
            self.eat("}")
        elif prod == 166:
            pass # Lambda
        else:
            self.error_invalid_token("<scr-char>")

    def index(self):
        # <index>
        prod = self.get_production("<index>")
        if prod == 167: self.eat("id")
        elif prod == 168: self.eat("COIN-lit")
        else:
            self.error_invalid_token("<index>")

    def scroll_exp(self):
        # <scroll-exp>
        prod = self.get_production("<scroll-exp>")
        if prod == 169:
            self.eat("&")
            self.scroll_val()
            self.scroll_exp()
        elif prod == 170:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-exp>")

    def scroll_grp_val(self):
        # <scroll-grp-val>
        prod = self.get_production("<scroll-grp-val>")
        if prod == 171:
            self.scroll_grp_ope()
            self.scroll_grp_exp()
        else:
            self.error_invalid_token("<scroll-grp-val>")

    def scroll_grp_ope(self):
        # <scroll-grp-ope>
        prod = self.get_production("<scroll-grp-ope>")
        if prod == 172:
            self.eat("id")
            self.id_tail()
        elif prod == 173:
            self.eat("(")
            self.scroll_grp_val()
            self.eat(")")
        elif prod == 174:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<scroll-grp-ope>")

    def scroll_grp_exp(self):
        # <scroll-grp-exp>
        prod = self.get_production("<scroll-grp-exp>")
        if prod == 175:
            self.eat("&")
            self.scroll_grp_ope()
            self.scroll_grp_exp()
        elif prod == 176:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-grp-exp>")

    def scroll_arr(self):
        # <scroll-arr>
        prod = self.get_production("<scroll-arr>")
        if prod == 177:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.scroll_arr_tail()
        else:
            self.error_invalid_token("<scroll-arr>")

    def scroll_arr_tail(self):
        # <scroll-arr-tail>
        prod = self.get_production("<scroll-arr-tail>")
        if prod == 178:
            self.eat("=")
            self.eat("[")
            self.scroll_arr1()
            self.eat("]")
        elif prod == 179:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.scroll_arr2_tail()
        elif prod == 180:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-arr-tail>")

    def scroll_arr1(self):
        # <scroll-arr1>
        prod = self.get_production("<scroll-arr1>")
        if prod == 181:
            self.scroll_arr_val()
            self.sav_tail()
        else:
            self.error_invalid_token("<scroll-arr1>")

    def scroll_arr_val(self):
        # <scroll-arr-val>
        prod = self.get_production("<scroll-arr-val>")
        if prod == 182:
            self.scroll_arr_ope()
            self.scroll_arr_exp()
        else:
            self.error_invalid_token("<scroll-arr-val>")

    def scroll_arr_ope(self):
        # <scroll-arr-ope>
        prod = self.get_production("<scroll-arr-ope>")
        if prod == 183:
            self.eat("id")
            self.id_tail()
        elif prod == 184:
            self.eat("(")
            self.scroll_grp_val()
            self.eat(")")
        elif prod == 185:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<scroll-arr-ope>")

    def scroll_arr_exp(self):
        # <scroll-arr-exp>
        prod = self.get_production("<scroll-arr-exp>")
        if prod == 186:
            self.eat("&")
            self.scroll_arr_ope()
            self.scroll_arr_exp()
        elif prod == 187:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-arr-exp>")

    def sav_tail(self):
        # <sav-tail>
        prod = self.get_production("<sav-tail>")
        if prod == 188:
            self.eat(",")
            self.scroll_arr1()
        elif prod == 189:
            pass # Lambda
        else:
            self.error_invalid_token("<sav-tail>")

    def scroll_arr2_tail(self):
        # <scroll-arr2-tail>
        prod = self.get_production("<scroll-arr2-tail>")
        if prod == 190:
            self.eat("=")
            self.eat("[")
            self.scroll_arr2()
            self.eat("]")
        elif prod == 191:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-arr2-tail>")

    def scroll_arr2(self):
        # <scroll-arr2>
        prod = self.get_production("<scroll-arr2>")
        if prod == 192:
            self.eat("[")
            self.scroll_arr1()
            self.eat("]")
            self.sav2_tail()
        else:
            self.error_invalid_token("<scroll-arr2>")

    def sav2_tail(self):
        # <sav2-tail>
        prod = self.get_production("<sav2-tail>")
        if prod == 193:
            self.eat(",")
            self.scroll_arr2()
        elif prod == 194:
            pass # Lambda
        else:
            self.error_invalid_token("<sav2-tail>")

    def scroll_func(self):
        # <scroll-func>
        prod = self.get_production("<scroll-func>")
        if prod == 195:
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
        if prod == 196:
            self.scroll_ret_ope()
            self.scroll_ret_exp()
        else:
            self.error_invalid_token("<scroll-retval>")

    def scroll_ret_ope(self):
        # <scroll-ret-ope>
        prod = self.get_production("<scroll-ret-ope>")
        if prod == 197:
            self.eat("id")
            self.id_tail()
        elif prod == 198:
            self.eat("(")
            self.scroll_grp_val()
            self.eat(")")
        elif prod == 199:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<scroll-ret-ope>")

    def scroll_ret_exp(self):
        # <scroll-ret-exp>
        prod = self.get_production("<scroll-ret-exp>")
        if prod == 200:
            self.eat("&")
            self.scroll_ret_ope()
            self.scroll_ret_exp()
        elif prod == 201:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-ret-exp>")

    # ==================== BOOL ====================

    def bool_var_arr_func(self):
        # <bool-var-arr-func>
        prod = self.get_production("<bool-var-arr-func>")
        if prod == 202:
            self.bool_var_arr()
            self.global_dec()
        elif prod == 203:
            self.bool_func()
        else:
            self.error_invalid_token("<bool-var-arr-func>")

    def bool_var_arr(self):
        # <bool-var-arr>
        prod = self.get_production("<bool-var-arr>")
        if prod == 204:
            self.bool_var()
            self.eat("!!")
        elif prod == 205:
            self.bool_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<bool-var-arr>")

    def bool_var(self):
        # <bool-var>
        prod = self.get_production("<bool-var>")
        if prod == 206:
            self.bool_init()
            self.bool_init_mult()
        else:
            self.error_invalid_token("<bool-var>")

    def bool_init(self):
        # <bool-init>
        prod = self.get_production("<bool-init>")
        if prod == 207:
            self.eat("=")
            self.bool_init_val()
        elif prod == 208:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-init>")

    def bool_init_mult(self):
        # <bool-init-mult>
        prod = self.get_production("<bool-init-mult>")
        if prod == 209:
            self.eat(",")
            self.eat("id")
            self.bool_init()
            self.bool_init_mult()
        elif prod == 210:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-init-mult>")

    def bool_init_val(self):
        # <bool-init-val>
        prod = self.get_production("<bool-init-val>")
        if prod == 211:
            self.bool_val()
            self.bool_exp()
        else:
            self.error_invalid_token("<bool-init-val>")

    def bool_val(self):
        # <bool-val>
        prod = self.get_production("<bool-val>")
        if prod == 212:
            self.eat("id")
            self.id_tail()
            self.bool_exp2()
        elif prod == 213:
            self.eat("(")
            self.value()
            self.eat(")")
            self.bool_exp2()
        elif prod == 214:
            self.bool_val_exp()
        elif prod == 215:
            self.bool_digit_exp()
        elif prod == 216:
            self.bool_parch_exp()
        elif prod == 217:
            self.bool_scroll_exp()
        else:
            self.error_invalid_token("<bool-val>")

    def bool_val_exp(self):
        # <bool-val-exp>
        prod = self.get_production("<bool-val-exp>")
        if prod == 218:
            self.bool()
            self.bool_eq()
        else:
            self.error_invalid_token("<bool-val-exp>")

    def bool(self):
        # <bool>
        prod = self.get_production("<bool>")
        if prod == 219: self.bool_lit()
        elif prod == 220:
            self.not_op()
            self.not_ope()
        else:
            self.error_invalid_token("<bool>")

    def bool_lit(self):
        # <bool-lit>
        prod = self.get_production("<bool-lit>")
        if prod == 221: self.eat("AYE")
        elif prod == 222: self.eat("NAY")
        else:
            self.error_invalid_token("<bool-lit>")

    def not_op(self):
        # <not-op>
        prod = self.get_production("<not-op>")
        if prod == 223: self.eat("!")
        elif prod == 224: self.eat("!#")
        else:
            self.error_invalid_token("<not-op>")

    def not_ope(self):
        # <not-ope>
        prod = self.get_production("<not-ope>")
        if prod == 225:
            self.eat("id")
            self.id_tail()
        elif prod == 226:
            self.eat("(")
            self.bool_grp_val()
            self.eat(")")
        elif prod == 227:
            self.bool_lit()
        else:
            self.error_invalid_token("<not-ope>")

    def bool_eq(self):
        # <bool-eq>
        prod = self.get_production("<bool-eq>")
        if prod == 228:
            self.eq_op()
            self.bool_val()
        elif prod == 229:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-eq>")

    def bool_digit_exp(self):
        # <bool-digit-exp>
        prod = self.get_production("<bool-digit-exp>")
        if prod == 230:
            self.bool_digit()
            self.bool_arith()
            self.rel_eq()
        else:
            self.error_invalid_token("<bool-digit-exp>")

    def bool_digit(self):
        # <bool-digit>
        prod = self.get_production("<bool-digit>")
        if prod == 231: self.eat("COIN-lit")
        elif prod == 232: self.eat("DIME-lit")
        elif prod == 233:
            self.eat("-")
            self.neg_bool_digit()
        else:
            self.error_invalid_token("<bool-digit>")

    def neg_bool_digit(self):
        # <neg-bool-digit>
        prod = self.get_production("<neg-bool-digit>")
        if prod == 234:
            self.eat("id")
            self.id_tail()
        elif prod == 235:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-bool-digit>")

    def bool_arith(self):
        # <bool-arith>
        prod = self.get_production("<bool-arith>")
        if prod == 236:
            self.arith()
            self.bool_arith()
        elif prod == 237:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arith>")

    def arith(self):
        # <arith>
        prod = self.get_production("<arith>")
        if prod == 238:
            self.arith_op()
            self.bool_arel_ope()
        else:
            self.error_invalid_token("<arith>")

    def bool_arel_ope(self):
        # <bool-arel-ope>
        prod = self.get_production("<bool-arel-ope>")
        if prod == 239:
            self.neg()
            self.neg_bool_arel_ope()
        elif prod == 240:
            self.eat("DIME-lit")
        elif prod == 241:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<bool-arel-ope>")

    def neg_bool_arel_ope(self):
        # <neg-bool-arel-ope>
        prod = self.get_production("<neg-bool-arel-ope>")
        if prod == 242:
            self.eat("id")
            self.id_tail()
        elif prod == 243:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-bool-arel-ope>")

    def rel_eq(self):
        # <rel-eq>
        prod = self.get_production("<rel-eq>")
        if prod == 244:
            self.rel()
        elif prod == 245:
            self.digit_eq()
        else:
            self.error_invalid_token("<rel-eq>")

    def rel(self):
        # <rel>
        prod = self.get_production("<rel>")
        if prod == 246:
            self.rel_op()
            self.bool_arel_ope()
            self.bool_arith()
            self.bool_eq()
        else:
            self.error_invalid_token("<rel>")

    def rel_op(self):
        # <rel-op>
        prod = self.get_production("<rel-op>")
        if prod == 247: self.eat("<")
        elif prod == 248: self.eat(">")
        elif prod == 249: self.eat("<=")
        elif prod == 250: self.eat(">=")
        else:
            self.error_invalid_token("<rel-op>")

    def digit_eq(self):
        # <digit-eq>
        prod = self.get_production("<digit-eq>")
        if prod == 251:
            self.eq_op()
            self.bool_arel_ope()
        else:
            self.error_invalid_token("<digit-eq>")

    def eq_op(self):
        # <eq-op>
        prod = self.get_production("<eq-op>")
        if prod == 252: self.eat("==")
        elif prod == 253: self.eat("!=")
        else:
            self.error_invalid_token("<eq-op>")

    def bool_parch_exp(self):
        # <bool-parch-exp>
        prod = self.get_production("<bool-parch-exp>")
        if prod == 254:
            self.eat("PARCH-lit")
            self.eq_op()
            self.bool_parch()
        else:
            self.error_invalid_token("<bool-parch-exp>")

    def bool_parch(self):
        # <bool-parch>
        prod = self.get_production("<bool-parch>")
        if prod == 255:
            self.eat("id")
            self.id_tail()
        elif prod == 256:
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<bool-parch>")

    def bool_scroll_exp(self):
        # <bool-scroll-exp>
        prod = self.get_production("<bool-scroll-exp>")
        if prod == 257:
            self.eat("SCROLL-lit")
            self.scr_char()
            self.eq_op()
            self.bool_scroll()
        else:
            self.error_invalid_token("<bool-scroll-exp>")

    def bool_scroll(self):
        # <bool-scroll>
        prod = self.get_production("<bool-scroll>")
        if prod == 258:
            self.eat("id")
            self.id_tail()
        elif prod == 259:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<bool-scroll>")

    def bool_exp2(self):
        # <bool-exp2>
        prod = self.get_production("<bool-exp2>")
        if prod == 260:
            self.arith()
            self.bool_arith()
            self.rel_eq()
        elif prod == 261:
            self.rel()
        elif prod == 262:
            self.eq_op()
            self.eq_ope()
        elif prod == 263:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-exp2>")

    def eq_ope(self):
        # <eq-ope>
        prod = self.get_production("<eq-ope>")
        if prod == 264:
            self.eat("id")
            self.id_tail()
            self.bool_exp3()
        elif prod == 265:
            self.eat("(")
            self.eq_ope_grp()
        elif prod == 266:
            self.bool_digit()
            self.bool_arith()
            self.bool_rel()
        elif prod == 267:
            self.eat("PARCH-lit")
        elif prod == 268:
            self.eat("SCROLL-lit")
            self.scr_char()
        elif prod == 269:
            self.bool()
        else:
            self.error_invalid_token("<eq-ope>")

    def bool_exp3(self):
        # <bool-exp3>
        prod = self.get_production("<bool-exp3>")
        if prod == 270:
            self.arith()
            self.bool_arith()
            self.bool_rel()
        elif prod == 271:
            self.rel_op()
            self.bool_arel_ope()
        elif prod == 272:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-exp3>")

    def bool_rel(self):
        # <bool-rel>
        prod = self.get_production("<bool-rel>")
        if prod == 273:
            self.rel_op()
            self.bool_arel_ope()
        elif prod == 274:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-rel>")

    def bool_exp(self):
        # <bool-exp>
        prod = self.get_production("<bool-exp>")
        if prod == 275:
            self.log_op()
            self.bool_val()
            self.bool_exp()
        elif prod == 276:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-exp>")

    def log_op(self):
        # <log-op>
        prod = self.get_production("<log-op>")
        if prod == 277: self.eat("||")
        elif prod == 278: self.eat("&&")
        else:
            self.error_invalid_token("<log-op>")

    def bool_grp_val(self):
        # <bool-grp-val>
        prod = self.get_production("<bool-grp-val>")
        if prod == 279:
            self.bool_grp_ope()
            self.bool_grp_exp()
        else:
            self.error_invalid_token("<bool-grp-val>")

    def bool_grp_ope(self):
        # <bool-grp-ope>
        prod = self.get_production("<bool-grp-ope>")
        if prod == 280:
            self.eat("id")
            self.id_tail()
            self.bool_grp_exp2()
        elif prod == 281:
            self.eat("(")
            self.value()
            self.eat(")")
            self.bool_grp_exp2()
        elif prod == 282:
            self.bool_val_exp_grp()
        elif prod == 283:
            self.bool_digit_exp_grp()
        elif prod == 284:
            self.bool_parch_exp_grp()
        elif prod == 285:
            self.bool_scroll_exp_grp()
        else:
            self.error_invalid_token("<bool-grp-ope>")

    def bool_val_exp_grp(self):
        # <bool-val-exp-grp>
        prod = self.get_production("<bool-val-exp-grp>")
        if prod == 286:
            self.bool_grp()
            self.bool_eq_grp()
        else:
            self.error_invalid_token("<bool-val-exp-grp>")

    def bool_grp(self):
        # <bool-grp>
        prod = self.get_production("<bool-grp>")
        if prod == 287:
            self.bool_lit_grp()
        elif prod == 288:
            self.not_op()
            self.not_ope_grp()
        else:
            self.error_invalid_token("<bool-grp>")

    def bool_lit_grp(self):
        # <bool-lit-grp>
        prod = self.get_production("<bool-lit-grp>")
        if prod == 289: self.eat("AYE")
        elif prod == 290: self.eat("NAY")
        else:
            self.error_invalid_token("<bool-lit-grp>")

    def not_ope_grp(self):
        # <not-ope-grp>
        prod = self.get_production("<not-ope-grp>")
        if prod == 291:
            self.eat("id")
            self.id_tail()
        elif prod == 292:
            self.eat("(")
            self.bool_grp_val()
            self.eat(")")
        elif prod == 293:
            self.bool_lit_grp()
        else:
            self.error_invalid_token("<not-ope-grp>")

    def bool_eq_grp(self):
        # <bool-eq-grp>
        prod = self.get_production("<bool-eq-grp>")
        if prod == 294:
            self.eq_op()
            self.bool_grp_ope()
        elif prod == 295:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-eq-grp>")

    def bool_digit_exp_grp(self):
        # <bool-digit-exp-grp>
        prod = self.get_production("<bool-digit-exp-grp>")
        if prod == 296:
            self.bool_digit_grp()
            self.bool_arith_grp()
            self.rel_eq_grp()
        else:
            self.error_invalid_token("<bool-digit-exp-grp>")

    def bool_digit_grp(self):
        # <bool-digit-grp>
        prod = self.get_production("<bool-digit-grp>")
        if prod == 297: self.eat("COIN-lit")
        elif prod == 298: self.eat("DIME-lit")
        elif prod == 299: 
            self.eat("-")
            self.neg_bool_digit_grp()
        else:
            self.error_invalid_token("<bool-digit-grp>")

    def neg_bool_digit_grp(self):
        # <neg-bool-digit-grp>
        prod = self.get_production("<neg-bool-digit-grp>")
        if prod == 300:
            self.eat("id")
            self.id_tail()
        elif prod == 301:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-bool-digit-grp>")

    def bool_arith_grp(self):
        # <bool-arith-grp>
        prod = self.get_production("<bool-arith-grp>")
        if prod == 302:
            self.arith_grp()
            self.bool_arith_grp()
        elif prod == 303:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arith-grp>")

    def arith_grp(self):
        # <arith-grp>
        prod = self.get_production("<arith-grp>")
        if prod == 304:
            self.arith_op()
            self.bool_arel_ope_grp()
        else:
            self.error_invalid_token("<arith-grp>")

    def bool_arel_ope_grp(self):
        # <bool-arel-ope-grp>
        prod = self.get_production("<bool-arel-ope-grp>")
        if prod == 305:
            self.neg()
            self.neg_bool_arel_ope_grp()
        elif prod == 306:
            self.eat("DIME-lit")
        elif prod == 307:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<bool-arel-ope-grp>")

    def neg_bool_arel_ope_grp(self):
        # <neg-bool-arel-ope-grp>
        prod = self.get_production("<neg-bool-arel-ope-grp>")
        if prod == 308:
            self.eat("id")
            self.id_tail()
        elif prod == 309:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-bool-arel-ope-grp>")

    def rel_eq_grp(self):
        # <rel-eq-grp>
        prod = self.get_production("<rel-eq-grp>")
        if prod == 310:
            self.rel_grp()
        elif prod == 311:
            self.digit_eq_grp()
        else:
            self.error_invalid_token("<rel-eq-grp>")

    def rel_grp(self):
        # <rel-grp>
        prod = self.get_production("<rel-grp>")
        if prod == 312:
            self.rel_op()
            self.bool_arel_ope_grp()
            self.bool_arith_grp()
            self.bool_eq_grp()
        else:
            self.error_invalid_token("<rel-grp>")

    def digit_eq_grp(self):
        # <digit-eq-grp>
        prod = self.get_production("<digit-eq-grp>")
        if prod == 313:
            self.eq_op()
            self.bool_arel_ope_grp()
        else:
            self.error_invalid_token("<digit-eq-grp>")

    def bool_parch_exp_grp(self):
        # <bool-parch-exp-grp>
        prod = self.get_production("<bool-parch-exp-grp>")
        if prod == 314:
            self.eat("PARCH-lit")
            self.eq_op()
            self.bool_parch_grp()
        else:
            self.error_invalid_token("<bool-parch-exp-grp>")

    def bool_parch_grp(self):
        # <bool-parch-grp>
        prod = self.get_production("<bool-parch-grp>")
        if prod == 315:
            self.eat("id")
            self.id_tail()
        elif prod == 316:
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<bool-parch-grp>")

    def bool_scroll_exp_grp(self):
        # <bool-scroll-exp-grp>
        prod = self.get_production("<bool-scroll-exp-grp>")
        if prod == 317:
            self.eat("SCROLL-lit")
            self.scr_char()
            self.eq_op()
            self.bool_scroll_grp()
        else:
            self.error_invalid_token("<bool-scroll-exp-grp>")

    def bool_scroll_grp(self):
        # <bool-scroll-grp>
        prod = self.get_production("<bool-scroll-grp>")
        if prod == 318:
            self.eat("id")
            self.id_tail()
        elif prod == 319:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<bool-scroll-grp>")

    def bool_grp_exp2(self):
        # <bool-grp-exp2>
        prod = self.get_production("<bool-grp-exp2>")
        if prod == 320:
            self.arith_grp()
            self.bool_arith_grp()
            self.rel_eq_grp()
        elif prod == 321:
            self.rel_grp()
        elif prod == 322:
            self.eq_op()
            self.eq_ope_grp()
        elif prod == 323:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-grp-exp2>")

    def eq_ope_grp(self):
        # <eq-ope-grp>
        prod = self.get_production("<eq-ope-grp>")
        if prod == 324:
            self.eat("id")
            self.id_tail()
            self.bool_grp_exp3()
        elif prod == 325:
            self.eat("(")
            self.eq_ope_grp()
            self.eat(")")
        elif prod == 326:
            self.bool_digit_grp()
            self.bool_arith_grp()
            self.bool_rel_grp()
        elif prod == 327:
            self.eat("PARCH-lit")
        elif prod == 328:
            self.eat("SCROLL-lit")
            self.scr_char()
        elif prod == 329:
            self.bool_grp()
        else:
            self.error_invalid_token("<eq-ope-grp>")

    def bool_grp_exp3(self):
        # <bool-grp-exp3>
        prod = self.get_production("<bool-grp-exp3>")
        if prod == 330:
            self.arith_grp()
            self.bool_arith_grp()
            self.bool_rel_grp()
        elif prod == 331:
            self.rel_op()
            self.bool_arel_ope_grp()
        elif prod == 332:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-grp-exp3>")

    def bool_rel_grp(self):
        # <bool-rel-grp>
        prod = self.get_production("<bool-rel-grp>")
        if prod == 333:
            self.rel_op()
            self.bool_arel_ope_grp()
        elif prod == 334:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-rel-grp>")

    def bool_grp_exp(self):
        # <bool-grp-exp>
        prod = self.get_production("<bool-grp-exp>")
        if prod == 335:
            self.log_op()
            self.bool_grp_ope()
            self.bool_grp_exp()
        elif prod == 336:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-grp-exp>")

    def bool_array(self):
        # <bool-array>
        prod = self.get_production("<bool-array>")
        if prod == 337:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.bool_arr_tail()
        elif prod == 352:
            self.bool_lit_arr()
        elif prod == 353:
            self.not_op()
            self.not_ope_arr()
        else:
            self.error_invalid_token("<bool-array>")

    def bool_arr_tail(self):
        # <bool-arr-tail>
        prod = self.get_production("<bool-arr-tail>")
        if prod == 338:
            self.eat("=")
            self.eat("[")
            self.bool_arr1()
            self.eat("]")
        elif prod == 339:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.bool_arr2_tail()
        elif prod == 340:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arr-tail>")

    def bool_arr1(self):
        # <bool-arr1>
        prod = self.get_production("<bool-arr1>")
        if prod == 341:
            self.bool_arr_val()
            self.bav_tail()
        else:
            self.error_invalid_token("<bool-arr1>")

    def bav_tail(self):
        # <bav-tail>
        prod = self.get_production("<bav-tail>")
        if prod == 342:
            self.eat(",")
            self.bool_arr1()
        elif prod == 343:
            pass # Lambda
        else:
            self.error_invalid_token("<bav-tail>")

    def bool_arr_val(self):
        # <bool-arr-val>
        prod = self.get_production("<bool-arr-val>")
        if prod == 344:
            self.bool_arr_ope()
            self.bool_arr_exp()
        else:
            self.error_invalid_token("<bool-arr-val>")

    def bool_arr_ope(self):
        # <bool-arr-ope>
        prod = self.get_production("<bool-arr-ope>")
        if prod == 345:
            self.eat("id")
            self.id_tail()
            self.bool_arr_exp2()
        elif prod == 346:
            self.eat("(")
            self.bool_grp_val()
            self.eat(")")
        elif prod == 347:
            self.bool_val_exp_arr()
        elif prod == 348:
            self.bool_digit_exp_arr()
        elif prod == 349:
            self.bool_parch_exp_arr()
        elif prod == 350:
            self.bool_scroll_exp_arr()
        else:
            self.error_invalid_token("<bool-arr-ope>")

    def bool_val_exp_arr(self):
        # <bool-val-exp-arr>
        prod = self.get_production("<bool-val-exp-arr>")
        if prod == 351:
            self.bool_array() 
            self.bool_eq_arr()
        else:
            self.error_invalid_token("<bool-val-exp-arr>")

    def bool_lit_arr(self):
        # <bool-lit-arr>
        prod = self.get_production("<bool-lit-arr>")
        if prod == 354: self.eat("AYE")
        elif prod == 355: self.eat("NAY")
        else:
            self.error_invalid_token("<bool-lit-arr>")

    def not_ope_arr(self):
        # <not-ope-arr>
        prod = self.get_production("<not-ope-arr>")
        if prod == 356:
            self.eat("id")
            self.id_tail()
        elif prod == 357:
            self.eat("(")
            self.bool_grp_val()
            self.eat(")")
        elif prod == 358:
            self.bool_lit_arr()
        else:
            self.error_invalid_token("<not-ope-arr>")

    def bool_eq_arr(self):
        # <bool-eq-arr>
        prod = self.get_production("<bool-eq-arr>")
        if prod == 359:
            self.eq_op()
            self.bool_arr_ope()
        elif prod == 360:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-eq-arr>")

    def bool_digit_exp_arr(self):
        # <bool-digit-exp-arr>
        prod = self.get_production("<bool-digit-exp-arr>")
        if prod == 361:
            self.bool_digit_arr()
            self.bool_arith_arr()
            self.rel_eq_arr()
        else:
            self.error_invalid_token("<bool-digit-exp-arr>")

    def bool_digit_arr(self):
        # <bool-digit-arr>
        prod = self.get_production("<bool-digit-arr>")
        if prod == 362: self.eat("COIN-lit")
        elif prod == 363: self.eat("DIME-lit")
        elif prod == 364:
            self.eat("-")
            self.neg_bool_digit_arr()
        else:
            self.error_invalid_token("<bool-digit-arr>")

    def neg_bool_digit_arr(self):
        # <neg-bool-digit-arr>
        prod = self.get_production("<neg-bool-digit-arr>")
        if prod == 365:
            self.eat("id")
            self.id_tail()
        elif prod == 366:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-bool-digit-arr>")

    def bool_arith_arr(self):
        # <bool-arith-arr>
        prod = self.get_production("<bool-arith-arr>")
        if prod == 367:
            self.arith_arr()
            self.bool_arith_arr()
        elif prod == 368:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arith-arr>")

    def arith_arr(self):
        # <arith-arr>
        prod = self.get_production("<arith-arr>")
        if prod == 369:
            self.arith_op()
            self.bool_arel_ope_arr()
        else:
            self.error_invalid_token("<arith-arr>")

    def bool_arel_ope_arr(self):
        # <bool-arel-ope-arr>
        prod = self.get_production("<bool-arel-ope-arr>")
        if prod == 370:
            self.neg()
            self.neg_bool_arel_ope_arr()
        elif prod == 371:
            self.eat("DIME-lit")
        elif prod == 372:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<bool-arel-ope-arr>")

    def neg_bool_arel_ope_arr(self):
        # <neg-bool-arel-ope-arr>
        prod = self.get_production("<neg-bool-arel-ope-arr>")
        if prod == 373:
            self.eat("id")
            self.id_tail()
        elif prod == 374:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-bool-arel-ope-arr>")

    def rel_eq_arr(self):
        # <rel-eq-arr>
        prod = self.get_production("<rel-eq-arr>")
        if prod == 375:
            self.rel_arr()
        elif prod == 376:
            self.digit_eq_arr()
        else:
            self.error_invalid_token("<rel-eq-arr>")

    def rel_arr(self):
        # <rel-arr>
        prod = self.get_production("<rel-arr>")
        if prod == 377:
            self.rel_op()
            self.bool_arel_ope_arr()
            self.bool_arith_arr()
            self.bool_eq_arr()
        else:
            self.error_invalid_token("<rel-arr>")

    def digit_eq_arr(self):
        # <digit-eq-arr>
        prod = self.get_production("<digit-eq-arr>")
        if prod == 378:
            self.eq_op()
            self.bool_arel_ope_arr()
        else:
            self.error_invalid_token("<digit-eq-arr>")

    def bool_parch_exp_arr(self):
        # <bool-parch-exp-arr>
        prod = self.get_production("<bool-parch-exp-arr>")
        if prod == 379:
            self.eat("PARCH-lit")
            self.eq_op()
            self.bool_parch_arr()
        else:
            self.error_invalid_token("<bool-parch-exp-arr>")

    def bool_parch_arr(self):
        # <bool-parch-arr>
        prod = self.get_production("<bool-parch-arr>")
        if prod == 380:
            self.eat("id")
            self.id_tail()
        elif prod == 381:
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<bool-parch-arr>")

    def bool_scroll_exp_arr(self):
        # <bool-scroll-exp-arr>
        prod = self.get_production("<bool-scroll-exp-arr>")
        if prod == 382:
            self.eat("SCROLL-lit")
            self.scr_char()
            self.eq_op()
            self.bool_scroll_arr()
        else:
            self.error_invalid_token("<bool-scroll-exp-arr>")

    def bool_scroll_arr(self):
        # <bool-scroll-arr>
        prod = self.get_production("<bool-scroll-arr>")
        if prod == 383:
            self.eat("id")
            self.id_tail()
        elif prod == 384:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<bool-scroll-arr>")

    def bool_arr_exp2(self):
        # <bool-arr-exp2>
        prod = self.get_production("<bool-arr-exp2>")
        if prod == 385:
            self.arith_arr()
            self.bool_arith_arr()
            self.rel_eq_arr()
        elif prod == 386:
            self.rel_arr()
        elif prod == 387:
            self.eq_op()
            self.eq_ope_arr()
        elif prod == 388:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arr-exp2>")

    def eq_ope_arr(self):
        # <eq-ope-arr>
        prod = self.get_production("<eq-ope-arr>")
        if prod == 389:
            self.eat("id")
            self.id_tail()
            self.bool_arr_exp3()
        elif prod == 390:
            self.eat("(")
            self.eq_ope_grp()
        elif prod == 391:
            self.bool_digit_arr()
            self.bool_arith_arr()
            self.bool_rel_arr()
        elif prod == 392:
            self.eat("PARCH-lit")
        elif prod == 393:
            self.eat("SCROLL-lit")
            self.scr_char()
        elif prod == 394:
            self.bool_array()
        else:
            self.error_invalid_token("<eq-ope-arr>")

    def bool_arr_exp3(self):
        # <bool-arr-exp3>
        prod = self.get_production("<bool-arr-exp3>")
        if prod == 395:
            self.arith_arr()
            self.bool_arith_arr()
            self.bool_rel_arr()
        elif prod == 396:
            self.rel_op()
            self.bool_arel_ope_arr()
        elif prod == 397:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arr-exp3>")

    def bool_rel_arr(self):
        # <bool-rel-arr>
        prod = self.get_production("<bool-rel-arr>")
        if prod == 398:
            self.rel_op()
            self.bool_arel_ope_arr()
        elif prod == 399:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-rel-arr>")

    def bool_arr_exp(self):
        # <bool-arr-exp>
        prod = self.get_production("<bool-arr-exp>")
        if prod == 400:
            self.log_op()
            self.bool_arr_ope()
            self.bool_arr_exp()
        elif prod == 401:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arr-exp>")

    def bool_arr2_tail(self):
        # <bool-arr2-tail>
        prod = self.get_production("<bool-arr2-tail>")
        if prod == 402:
            self.eat("=")
            self.eat("[")
            self.bool_arr2()
            self.eat("]")
        elif prod == 403:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arr2-tail>")

    def bool_arr2(self):
        # <bool-arr2>
        prod = self.get_production("<bool-arr2>")
        if prod == 404:
            self.eat("[")
            self.bool_arr1()
            self.eat("]")
            self.bav2_tail()
        else:
            self.error_invalid_token("<bool-arr2>")

    def bav2_tail(self):
        # <bav2-tail>
        prod = self.get_production("<bav2-tail>")
        if prod == 405:
            self.eat(",")
            self.bool_arr2()
        elif prod == 406:
            pass # Lambda
        else:
            self.error_invalid_token("<bav2-tail>")

    def bool_func(self):
        # <bool-func>
        prod = self.get_production("<bool-func>")
        if prod == 407:
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
        if prod == 408:
            self.bool_var_ope()
            self.bool_ret_exp()
        else:
            self.error_invalid_token("<bool-retval>")

    def bool_ret_exp(self):
        # <bool-ret-exp>
        prod = self.get_production("<bool-ret-exp>")
        if prod == 409:
            self.log_op()
            self.bool_var_ope()
            self.bool_ret_exp()
        elif prod == 410:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-ret-exp>")

    # ==================== PARAMS & COMMON ====================

    def params(self):
        # <params>
        prod = self.get_production("<params>")
        if prod == 411:
            self.d_type()
            self.eat("id")
            self.param_mult()
        elif prod == 412:
            pass # Lambda
        else:
            self.error_invalid_token("<params>")

    def param_mult(self):
        # <param-mult>
        prod = self.get_production("<param-mult>")
        if prod == 413:
            self.eat(",")
            self.params()
        elif prod == 414:
            pass # Lambda
        else:
            self.error_invalid_token("<param-mult>")

    def d_type(self):
        # <d-type>
        prod = self.get_production("<d-type>")
        if prod == 415: self.eat("COIN")
        elif prod == 416: self.eat("DIME")
        elif prod == 417: self.eat("PARCH")
        elif prod == 418: self.eat("SCROLL")
        elif prod == 419: self.eat("BOOL")
        else:
            self.error_invalid_token("<d-type>")

    def ret_stmnts(self):
        # <ret-stmnts>
        prod = self.get_production("<ret-stmnts>")
        if prod == 420:
            self.ret_stmnt()
            self.ret_stmnts()
        elif prod == 421:
            pass # Lambda
        else:
            self.error_invalid_token("<ret-stmnts>")

    def ret_stmnt(self):
        # <ret-stmnt>
        prod = self.get_production("<ret-stmnt>")
        if prod == 422:
            self.statements()
        else:
            self.error_invalid_token("<ret-stmnt>")

    def id_tail(self):
        # <id-tail>
        prod = self.get_production("<id-tail>")
        if prod == 423: self.elmt()
        elif prod == 424: self.mem()
        elif prod == 425: self.func()
        elif prod == 426:
            pass # Lambda
        else:
            self.error_invalid_token("<id-tail>")

    def elmt(self):
        # <elmt>
        prod = self.get_production("<elmt>")
        if prod == 427:
            self.eat("{")
            self.index()
            self.eat("}")
            self.elmt_tail()
        else:
            self.error_invalid_token("<elmt>")

    def elmt_tail(self):
        # <elmt-tail>
        prod = self.get_production("<elmt-tail>")
        if prod == 428:
            self.eat("{")
            self.index()
            self.eat("}")
        elif prod == 429:
            pass # Lambda
        else:
            self.error_invalid_token("<elmt-tail>")

    def mem(self):
        # <mem>
        prod = self.get_production("<mem>")
        if prod == 430:
            self.eat("$")
            self.eat("id")
        else:
            self.error_invalid_token("<mem>")

    def func(self):
        # <func>
        prod = self.get_production("<func>")
        if prod == 431:
            self.eat("(")
            self.args()
            self.eat(")")
        else:
            self.error_invalid_token("<func>")

    def args(self):
        # <args>
        prod = self.get_production("<args>")
        if prod == 432:
            self.args_val()
            self.args_mult()
        elif prod == 433:
            pass # Lambda
        else:
            self.error_invalid_token("<args>")

    def args_val(self):
        # <args-val>
        prod = self.get_production("<args-val>")
        if prod == 434:
            self.value()
        else:
            self.error_invalid_token("<args-val>")

    def args_mult(self):
        # <args-mult>
        prod = self.get_production("<args-mult>")
        if prod == 435:
            self.eat(",")
            self.args()
        elif prod == 436:
            pass # Lambda
        else:
            self.error_invalid_token("<args-mult>")

    def var_val(self):
        # <var-val>
        prod = self.get_production("<var-val>")
        if prod == 437:
            self.value()
        else:
            self.error_invalid_token("<var-val>")

    def value(self):
        # <value>
        prod = self.get_production("<value>")
        if prod == 438:
            self.eat("id")
            self.id_tail()
            self.var_exp()
        elif prod == 439:
            self.eat("(")
            self.value()
            self.eat(")")
            self.var_exp()
        elif prod == 440:
            self.var_digit()
            self.digit_tail()
        elif prod == 441:
            self.eat("PARCH-lit")
            self.eq_parch()
        elif prod == 442:
            self.eat("SCROLL-lit")
            self.scr_char()
            self.var_scroll_eq()
        elif prod == 443:
            self.var_bool()
        else:
            self.error_invalid_token("<value>")

    def var_digit(self):
        # <var-digit>
        prod = self.get_production("<var-digit>")
        if prod == 444: self.eat("COIN-lit")
        elif prod == 445: self.eat("DIME-lit")
        elif prod == 446:
            self.eat("-")
            self.neg_var_digit()
        else:
            self.error_invalid_token("<var-digit>")

    def neg_var_digit(self):
        # <neg-var-digit>
        prod = self.get_production("<neg-var-digit>")
        if prod == 447:
            self.eat("id")
            self.id_tail()
        elif prod == 448:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-var-digit>")

    def digit_tail(self):
        # <digit-tail>
        prod = self.get_production("<digit-tail>")
        if prod == 449:
            self.var_arith()
            self.var_releq()
        elif prod == 450:
            pass # Lambda
        else:
            self.error_invalid_token("<digit-tail>")

    def var_arith(self):
        # <var-arith>
        prod = self.get_production("<var-arith>")
        if prod == 451:
            self.arith_op()
            self.var_arel_ope()
            self.var_arith()
        elif prod == 452:
            pass # Lambda
        else:
            self.error_invalid_token("<var-arith>")

    def var_arel_ope(self):
        # <var-arel-ope>
        prod = self.get_production("<var-arel-ope>")
        if prod == 453:
            self.neg()
            self.neg_var_arel_ope()
        elif prod == 454:
            self.eat("DIME-lit")
        elif prod == 455:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<var-arel-ope>")

    def neg_var_arel_ope(self):
        # <neg-var-arel-ope>
        prod = self.get_production("<neg-var-arel-ope>")
        if prod == 456:
            self.eat("id")
            self.id_tail()
        elif prod == 457:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-var-arel-ope>")

    def var_releq(self):
        # <var-releq>
        prod = self.get_production("<var-releq>")
        if prod == 458:
            self.var_rel()
        elif prod == 459:
            self.eq_op()
            self.var_arel_ope()
            self.var_log()
        elif prod == 460:
            pass # Lambda
        else:
            self.error_invalid_token("<var-releq>")

    def var_rel(self):
        # <var-rel>
        prod = self.get_production("<var-rel>")
        if prod == 461:
            self.rel_op()
            self.var_arel_ope()
            self.var_arith()
            self.var_logeq()
        elif prod == 462:
            pass # Lambda
        else:
            self.error_invalid_token("<var-rel>")

    def var_logeq(self):
        # <var-logeq>
        prod = self.get_production("<var-logeq>")
        if prod == 463:
            self.logeq_op()
            self.log_ope()
            self.var_log()
        elif prod == 464:
            pass # Lambda
        else:
            self.error_invalid_token("<var-logeq>")

    def logeq_op(self):
        # <logeq-op>
        prod = self.get_production("<logeq-op>")
        if prod == 465: self.log_op()
        elif prod == 466: self.eq_op()
        else:
            self.error_invalid_token("<logeq-op>")

    def var_log(self):
        # <var-log>
        prod = self.get_production("<var-log>")
        if prod == 467:
            self.log_op()
            self.log_ope()
            self.var_log()
        elif prod == 468:
            pass # Lambda
        else:
            self.error_invalid_token("<var-log>")

    def log_ope(self):
        # <log-ope>
        prod = self.get_production("<log-ope>")
        if prod == 469:
            self.bool_grp_ope()
        else:
            self.error_invalid_token("<log-ope>")

    def eq_parch(self):
        # <eq-parch>
        prod = self.get_production("<eq-parch>")
        if prod == 470:
            self.eq_op()
            self.eat("PARCH-lit")
            self.var_log()
        elif prod == 471:
            pass # Lambda
        else:
            self.error_invalid_token("<eq-parch>")

    def var_scroll_eq(self):
        # <var-scroll-eq>
        prod = self.get_production("<var-scroll-eq>")
        if prod == 472:
            self.var_scroll()
        elif prod == 473:
            self.eq_scroll()
        elif prod == 474:
            pass # Lambda
        else:
            self.error_invalid_token("<var-scroll-eq>")

    def var_scroll(self):
        # <var-scroll>
        prod = self.get_production("<var-scroll>")
        if prod == 475:
            self.eat("&")
            self.concat_ope()
            self.var_scroll()
        elif prod == 476:
            pass # Lambda
        else:
            self.error_invalid_token("<var-scroll>")

    def concat_ope(self):
        # <concat-ope>
        prod = self.get_production("<concat-ope>")
        if prod == 477:
            self.eat("id")
            self.id_tail()
        elif prod == 478:
            self.eat("(")
            self.scroll_grp_val()
            self.eat(")")
        elif prod == 479:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<concat-ope>")

    def eq_scroll(self):
        # <eq-scroll>
        prod = self.get_production("<eq-scroll>")
        if prod == 480:
            self.eq_op()
            self.eq_scroll_ope()
            self.var_log()
        else:
            self.error_invalid_token("<eq-scroll>")

    def eq_scroll_ope(self):
        # <eq-scroll-ope>
        prod = self.get_production("<eq-scroll-ope>")
        if prod == 481:
            self.eat("id")
            self.id_tail()
        elif prod == 482:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<eq-scroll-ope>")

    def var_bool(self):
        # <var-bool>
        prod = self.get_production("<var-bool>")
        if prod == 483:
            self.bool_lit_var()
        elif prod == 484:
            self.not_op()
            self.not_val_var()
        else:
            self.error_invalid_token("<var-bool>")

    def bool_lit_var(self):
        # <bool-lit-var>
        prod = self.get_production("<bool-lit-var>")
        if prod == 485: self.eat("AYE")
        elif prod == 486: self.eat("NAY")
        else:
            self.error_invalid_token("<bool-lit-var>")

    def not_val_var(self):
        # <not-val-var>
        prod = self.get_production("<not-val-var>")
        if prod == 487:
            self.eat("id")
            self.id_tail()
        elif prod == 488:
            self.eat("(")
            self.bool_grp_val()
            self.eat(")")
        elif prod == 489:
            self.bool_lit_var()
        else:
            self.error_invalid_token("<not-val-var>")

    def var_exp(self):
        # <var-exp>
        prod = self.get_production("<var-exp>")
        if prod == 490:
            self.expressions()
        elif prod == 491:
            pass # Lambda
        else:
            self.error_invalid_token("<var-exp>")

    def expressions(self):
        # <expressions>
        prod = self.get_production("<expressions>")
        if prod == 492:
            self.arith_op()
            self.var_arel_ope()
            self.var_arith()
            self.var_releq()
        elif prod == 493:
            self.rel_op()
            self.var_arel_ope()
            self.var_arith()
            self.var_logeq()
        elif prod == 494:
            self.log_op()
            self.log_ope()
            self.var_log()
        elif prod == 495:
            self.eq_op()
            self.eq_ope_grp()
            self.var_log()
        elif prod == 496:
            self.eat("&")
            self.concat_ope()
            self.var_scroll()
        else:
            self.error_invalid_token("<expressions>")

    def const(self):
        # <const>
        prod = self.get_production("<const>")
        if prod == 497:
            self.eat("LOCKE")
            self.const_init()
            self.eat("!!")
        else:
            self.error_invalid_token("<const>")

    def const_init(self):
        # <const-init>
        prod = self.get_production("<const-init>")
        if prod == 498:
            self.eat("COIN")
            self.coin_locke()
            self.coin_locke_mult()
        elif prod == 499:
            self.eat("DIME")
            self.dime_locke()
            self.dime_locke_mult()
        elif prod == 500:
            self.eat("PARCH")
            self.parch_locke()
            self.parch_locke_mult()
        elif prod == 501:
            self.eat("SCROLL")
            self.scroll_locke()
            self.scroll_locke_mult()
        elif prod == 502:
            self.eat("BOOL")
            self.bool_locke()
            self.bool_locke_mult()
        else:
            self.error_invalid_token("<const-init>")

    def coin_locke(self):
        # <coin-locke>
        prod = self.get_production("<coin-locke>")
        if prod == 503:
            self.eat("id")
            self.eat("=")
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<coin-locke>")

    def coin_locke_mult(self):
        # <coin-locke-mult>
        prod = self.get_production("<coin-locke-mult>")
        if prod == 504:
            self.eat(",")
            self.coin_locke()
            self.coin_locke_mult()
        elif prod == 505:
            pass # Lambda
        else:
            self.error_invalid_token("<coin-locke-mult>")

    def dime_locke(self):
        # <dime-locke>
        prod = self.get_production("<dime-locke>")
        if prod == 506:
            self.eat("id")
            self.eat("=")
            self.locke_digit()
        else:
            self.error_invalid_token("<dime-locke>")

    def locke_digit(self):
        # <locke-digit>
        prod = self.get_production("<locke-digit>")
        if prod == 507:
            self.eat("COIN-lit")
        elif prod == 508:
            self.eat("DIME-lit")
        else:
            self.error_invalid_token("<locke-digit>")

    def dime_locke_mult(self):
        # <dime-locke-mult>
        prod = self.get_production("<dime-locke-mult>")
        if prod == 509:
            self.eat(",")
            self.dime_locke()
            self.dime_locke_mult()
        elif prod == 510:
            pass # Lambda
        else:
            self.error_invalid_token("<dime-locke-mult>")

    def parch_locke(self):
        # <parch-locke>
        prod = self.get_production("<parch-locke>")
        if prod == 511:
            self.eat("id")
            self.eat("=")
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<parch-locke>")

    def parch_locke_mult(self):
        # <parch-locke-mult>
        prod = self.get_production("<parch-locke-mult>")
        if prod == 512:
            self.eat(",")
            self.parch_locke()
            self.parch_locke_mult()
        elif prod == 513:
            pass # Lambda
        else:
            self.error_invalid_token("<parch-locke-mult>")

    def scroll_locke(self):
        # <scroll-locke>
        prod = self.get_production("<scroll-locke>")
        if prod == 514:
            self.eat("id")
            self.eat("=")
            self.eat("SCROLL-lit")
            self.scr_id()
        else:
            self.error_invalid_token("<scroll-locke>")

    def scr_id(self):
        # <scr-id>
        prod = self.get_production("<scr-id>")
        if prod == 515:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
        elif prod == 516:
            pass # Lambda
        else:
            self.error_invalid_token("<scr-id>")

    def scroll_locke_mult(self):
        # <scroll-locke-mult>
        prod = self.get_production("<scroll-locke-mult>")
        if prod == 517:
            self.eat(",")
            self.scroll_locke()
            self.scroll_locke_mult()
        elif prod == 518:
            pass # Lambda
        else:
            self.error_invalid_token("<scroll-locke-mult>")

    def bool_locke(self):
        # <bool-locke>
        prod = self.get_production("<bool-locke>")
        if prod == 519:
            self.eat("id")
            self.eat("=")
            self.locke_bool()
        else:
            self.error_invalid_token("<bool-locke>")

    def locke_bool(self):
        # <locke-bool>
        prod = self.get_production("<locke-bool>")
        if prod == 520:
            self.eat("AYE")
        elif prod == 521:
            self.eat("NAY")
        else:
            self.error_invalid_token("<locke-bool>")

    def bool_locke_mult(self):
        # <bool-locke-mult>
        prod = self.get_production("<bool-locke-mult>")
        if prod == 522:
            self.eat(",")
            self.bool_locke()
            self.bool_locke_mult()
        elif prod == 523:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-locke-mult>")

    def struct(self):
        # <struct>
        prod = self.get_production("<struct>")
        if prod == 524:
            self.eat("MAST")
            self.eat("id")
            self.eat("[")
            self.mem_dec()
            self.mem_dec_tail()
            self.eat("]")
            self.eat("!!")
            self.struct()
            self.sub_func()
        elif prod == 525:
            pass # Lambda
        else:
            self.error_invalid_token("<struct>")

    def mem_dec(self):
        # <mem-dec>
        prod = self.get_production("<mem-dec>")
        if prod == 526:
            self.d_type()
            self.eat("id")
            self.mem_mult()
            self.eat("!!")
        else:
            self.error_invalid_token("<mem-dec>")

    def mem_mult(self):
        # <mem-mult>
        prod = self.get_production("<mem-mult>")
        if prod == 527:
            self.eat(",")
            self.eat("id")
            self.mem_mult()
        elif prod == 528:
            pass # Lambda
        else:
            self.error_invalid_token("<mem-mult>")

    def mem_dec_tail(self):
        # <mem-dec-tail>
        prod = self.get_production("<mem-dec-tail>")
        if prod == 529:
            self.mem_dec()
            self.mem_dec_tail()
        elif prod == 530:
            pass # Lambda
        else:
            self.error_invalid_token("<mem-dec-tail>")

    def sub_func(self):
        # <sub-func>
        prod = self.get_production("<sub-func>")
        if prod == 531: self.return_func()
        elif prod == 532: self.nonreturn_func()
        elif prod == 533: pass # Lambda
        else:
            self.error_invalid_token("<sub-func>")

    def return_func(self):
        # <return-func>
        prod = self.get_production("<return-func>")
        if prod == 534: 
            self.eat("COIN")
            self.eat("id")
            self.coin_func()
        elif prod == 535:
            self.eat("DIME")
            self.eat("id")
            self.dime_func()
        elif prod == 536:
            self.eat("PARCH")
            self.eat("id")
            self.parch_func()
        elif prod == 537:
            self.eat("SCROLL")
            self.eat("id")
            self.scroll_func()
        elif prod == 538:
            self.eat("BOOL")
            self.eat("id")
            self.bool_func()
        else:
            self.error_invalid_token("<return-func>")

    def nonreturn_func(self):
        # <nonreturn-func>
        prod = self.get_production("<nonreturn-func>")
        if prod == 539:
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
        if prod == 540:
            self.nonret_stmnt()
            self.nonret_tail()
        else:
            self.error_invalid_token("<nonret-stmnts>")
    
    def nonret_stmnt(self):
        # <nonret-stmnt>
        prod = self.get_production("<nonret-stmnt>")
        if prod == 541:
            self.statements()
        else:
            self.error_invalid_token("<nonret-stmnt>")

    def nonret_tail(self):
        # <nonret-tail>
        prod = self.get_production("<nonret-tail>")
        if prod == 542:
            self.nonret_stmnts()
        elif prod == 543:
            pass # Lambda
        else:
             self.error_invalid_token("<nonret-tail>")

    def nonret_back(self):
        # <nonret-back>
        prod = self.get_production("<nonret-back>")
        if prod == 544:
            self.eat("BACK")
            self.eat("!!")
        elif prod == 545:
            pass # Lambda
        else:
            self.error_invalid_token("<nonret-back>")

    def local_dec(self):
        # <local-dec>
        prod = self.get_production("<local-dec>")
        if prod == 546:
            self.var_arr()
            self.local_dec()
        elif prod == 547:
            self.struct_dec()
        elif prod == 548:
            pass # Lambda
        else:
            self.error_invalid_token("<local-dec>")

    def var_arr(self):
        # <var-arr>
        prod = self.get_production("<var-arr>")
        if prod == 549:
            self.eat("COIN")
            self.eat("id")
            self.coin_local()
        elif prod == 550:
            self.eat("DIME")
            self.eat("id")
            self.dime_local()
        elif prod == 551:
            self.eat("PARCH")
            self.eat("id")
            self.parch_local()
        elif prod == 552:
            self.eat("SCROLL")
            self.eat("id")
            self.scroll_local()
        elif prod == 553:
            self.eat("BOOL")
            self.eat("id")
            self.bool_local()
        else:
            self.error_invalid_token("<var-arr>")

    def coin_local(self):
        # <coin-local>
        prod = self.get_production("<coin-local>")
        if prod == 554: 
            self.coin_var()
            self.eat("!!")
        elif prod == 555:
            self.coin_arr()
            self.eat("!!")
        else: self.error_invalid_token("<coin-local>")

    def dime_local(self):
        # <dime-local>
        prod = self.get_production("<dime-local>")
        if prod == 556: 
            self.dime_var()
            self.eat("!!")
        elif prod == 557:
            self.dime_arr()
            self.eat("!!")
        else: self.error_invalid_token("<dime-local>")

    def parch_local(self):
        # <parch-local>
        prod = self.get_production("<parch-local>")
        if prod == 558: 
            self.parch_var()
            self.eat("!!")
        elif prod == 559:
            self.parch_arr()
            self.eat("!!")
        else: self.error_invalid_token("<parch-local>")

    def scroll_local(self):
        # <scroll-local>
        prod = self.get_production("<scroll-local>")
        if prod == 560: 
            self.scroll_var()
            self.eat("!!")
        elif prod == 561:
            self.scroll_arr()
            self.eat("!!")
        else: self.error_invalid_token("<scroll-local>")

    def bool_local(self):
        # <bool-local>
        prod = self.get_production("<bool-local>")
        if prod == 562: 
            self.bool_var()
            self.eat("!!")
        elif prod == 563:
            self.bool_arr()
            self.eat("!!")
        else: self.error_invalid_token("<bool-local>")

    def struct_dec(self):
        # <struct-dec>
        prod = self.get_production("<struct-dec>")
        if prod == 564:
            self.eat("MAST")
            self.eat("id")
            self.eat("id")
            self.str_dec_init()
            self.eat("!!")
            self.struct_dec()
        elif prod == 565:
            pass # Lambda
        else:
            self.error_invalid_token("<struct-dec>")

    def str_dec_init(self):
        # <str-dec-init>
        prod = self.get_production("<str-dec-init>")
        if prod == 566:
            self.eat(",")
            self.eat("id")
            self.str_dec_tail()
        elif prod == 567:
            self.eat("=")
            self.eat("[")
            self.str_val()
            self.str_val_tail()
            self.eat("]")
        elif prod == 568:
            pass # Lambda
        else:
            self.error_invalid_token("<str-dec-init>")

    def str_dec_tail(self):
        # <str-dec-tail>
        prod = self.get_production("<str-dec-tail>")
        if prod == 569:
            self.eat(",")
            self.eat("id")
            self.str_dec_tail()
        elif prod == 570:
            pass # Lambda
        else:
            self.error_invalid_token("<str-dec-tail>")

    def str_val(self):
        # <str-val>
        prod = self.get_production("<str-val>")
        if prod == 571:
            self.var_val_2()
        elif prod == 572:
            self.eat("$")
            self.eat("id")
            self.eat("=")
            self.value_2()
        else:
            self.error_invalid_token("<str-val>")

    def var_val_2(self):
        # <var-val-2>
        prod = self.get_production("<var-val-2>")
        if prod == 573:
            self.value_2()
        else:
            self.error_invalid_token("<var-val-2>")

    def value_2(self):
        # <value-2>
        prod = self.get_production("<value-2>")
        if prod == 574:
            self.eat("id")
            self.id_tail()
            self.var_exp_2()
        elif prod == 575:
            self.eat("(")
            self.value()
            self.eat(")")
            self.var_exp_2()
        elif prod == 576:
            self.var_digit_2()
            self.digit_tail_2()
        elif prod == 577:
            self.eat("PARCH-lit")
            self.eq_parch_2()
        elif prod == 578:
            self.eat("SCROLL-lit")
            self.scr_char()
            self.var_scroll_eq_2()
        elif prod == 579:
            self.var_bool_2()
        else:
            self.error_invalid_token("<value-2>")

    def var_digit_2(self):
        # <var-digit-2>
        prod = self.get_production("<var-digit-2>")
        if prod == 580: self.eat("COIN-lit")
        elif prod == 581: self.eat("DIME-lit")
        elif prod == 582:
            self.eat("-")
            self.neg_var_digit_2()
        else:
            self.error_invalid_token("<var-digit-2>")

    def neg_var_digit_2(self):
        # <neg-var-digit-2>
        prod = self.get_production("<neg-var-digit-2>")
        if prod == 583:
            self.eat("id")
            self.id_tail()
        elif prod == 584:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-var-digit-2>")

    def digit_tail_2(self):
        # <digit-tail-2>
        prod = self.get_production("<digit-tail-2>")
        if prod == 585:
            self.var_arith_2()
            self.var_releq_2()
        elif prod == 586:
            pass # Lambda
        else:
            self.error_invalid_token("<digit-tail-2>")

    def var_arith_2(self):
        # <var-arith-2>
        prod = self.get_production("<var-arith-2>")
        if prod == 587:
            self.arith_op()
            self.var_arel_ope_2()
            self.var_arith_2()
        elif prod == 588:
            pass # Lambda
        else:
            self.error_invalid_token("<var-arith-2>")

    def var_arel_ope_2(self):
        # <var-arel-ope-2>
        prod = self.get_production("<var-arel-ope-2>")
        if prod == 589:
            self.neg()
            self.neg_var_arel_ope_2()
        elif prod == 590:
            self.eat("DIME-lit")
        elif prod == 591:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<var-arel-ope-2>")

    def neg_var_arel_ope_2(self):
        # <neg-var-arel-ope-2>
        prod = self.get_production("<neg-var-arel-ope-2>")
        if prod == 592:
            self.eat("id")
            self.id_tail()
        elif prod == 593:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-var-arel-ope-2>")

    def var_releq_2(self):
        # <var-releq-2>
        prod = self.get_production("<var-releq-2>")
        if prod == 594:
            self.var_rel_2()
        elif prod == 595:
            self.eq_op()
            self.var_arel_ope_2()
            self.var_log_2()
        elif prod == 596:
            pass # Lambda
        else:
            self.error_invalid_token("<var-releq-2>")

    def var_rel_2(self):
        # <var-rel-2>
        prod = self.get_production("<var-rel-2>")
        if prod == 597:
            self.rel_op()
            self.var_arel_ope_2()
            self.var_arith_2()
            self.var_logeq_2()
        elif prod == 598:
            pass # Lambda
        else:
            self.error_invalid_token("<var-rel-2>")

    def var_logeq_2(self):
        # <var-logeq-2>
        prod = self.get_production("<var-logeq-2>")
        if prod == 599:
            self.logeq_op()
            self.log_ope_2()
            self.var_log_2()
        elif prod == 600:
            pass # Lambda
        else:
            self.error_invalid_token("<var-logeq-2>")

    def var_log_2(self):
        # <var-log-2>
        prod = self.get_production("<var-log-2>")
        if prod == 601:
            self.log_op()
            self.log_ope_2()
            self.var_log_2()
        elif prod == 602:
            pass # Lambda
        else:
            self.error_invalid_token("<var-log-2>")

    def log_ope_2(self):
        # <log-ope-2>
        prod = self.get_production("<log-ope-2>")
        if prod == 603:
            self.bool_arr_ope()
        else:
            self.error_invalid_token("<log-ope-2>")

    def eq_parch_2(self):
        # <eq-parch-2>
        prod = self.get_production("<eq-parch-2>")
        if prod == 604:
            self.eq_op()
            self.eat("PARCH-lit")
            self.var_log_2()
        elif prod == 605:
            pass # Lambda
        else:
            self.error_invalid_token("<eq-parch-2>")

    def var_scroll_eq_2(self):
        # <var-scroll-eq-2>
        prod = self.get_production("<var-scroll-eq-2>")
        if prod == 606:
            self.var_scroll_2()
        elif prod == 607:
            self.eq_scroll_2()
        elif prod == 608:
            pass # Lambda
        else:
            self.error_invalid_token("<var-scroll-eq-2>")

    def var_scroll_2(self):
        # <var-scroll-2>
        prod = self.get_production("<var-scroll-2>")
        if prod == 609:
            self.eat("&")
            self.concat_ope_2()
            self.var_scroll_2()
        elif prod == 610:
            pass # Lambda
        else:
            self.error_invalid_token("<var-scroll-2>")

    def concat_ope_2(self):
        # <concat-ope-2>
        prod = self.get_production("<concat-ope-2>")
        if prod == 611:
            self.eat("id")
            self.id_tail()
        elif prod == 612:
            self.eat("(")
            self.scroll_grp_val()
            self.eat(")")
        elif prod == 613:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<concat-ope-2>")

    def eq_scroll_2(self):
        # <eq-scroll-2>
        prod = self.get_production("<eq-scroll-2>")
        if prod == 614:
            self.eq_op()
            self.eq_scroll_ope_2()
            self.var_log_2()
        else:
            self.error_invalid_token("<eq-scroll-2>")

    def eq_scroll_ope_2(self):
        # <eq-scroll-ope-2>
        prod = self.get_production("<eq-scroll-ope-2>")
        if prod == 615:
            self.eat("id")
            self.id_tail()
        elif prod == 616:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<eq-scroll-ope-2>")

    def var_bool_2(self):
        # <var-bool-2>
        prod = self.get_production("<var-bool-2>")
        if prod == 617:
            self.bool_lit_var_2()
        elif prod == 618:
            self.not_op()
            self.not_val_var_2()
        else:
            self.error_invalid_token("<var-bool-2>")

    def bool_lit_var_2(self):
        # <bool-lit-var-2>
        prod = self.get_production("<bool-lit-var-2>")
        if prod == 619: self.eat("AYE")
        elif prod == 620: self.eat("NAY")
        else:
            self.error_invalid_token("<bool-lit-var-2>")

    def not_val_var_2(self):
        # <not-val-var-2>
        prod = self.get_production("<not-val-var-2>")
        if prod == 621:
            self.eat("id")
            self.id_tail()
        elif prod == 622:
            self.eat("(")
            self.bool_grp_val()
            self.eat(")")
        elif prod == 623:
            self.bool_lit_var_2()
        else:
            self.error_invalid_token("<not-val-var-2>")

    def var_exp_2(self):
        # <var-exp-2>
        prod = self.get_production("<var-exp-2>")
        if prod == 624:
            self.expressions_2()
        elif prod == 625:
            pass # Lambda
        else:
            self.error_invalid_token("<var-exp-2>")

    def expressions_2(self):
        # <expressions-2>
        prod = self.get_production("<expressions-2>")
        if prod == 626:
            self.arith_op()
            self.var_arel_ope_2()
            self.var_arith_2()
            self.var_releq_2()
        elif prod == 627:
            self.rel_op()
            self.var_arel_ope_2()
            self.var_arith_2()
            self.var_logeq_2()
        elif prod == 628:
            self.log_op()
            self.log_ope_2()
            self.var_log_2()
        elif prod == 629:
            self.eq_op()
            self.eq_ope_2()
            self.var_log_2()
        elif prod == 630:
            self.eat("&")
            self.concat_ope_2()
            self.var_scroll_2()
        else:
            self.error_invalid_token("<expressions-2>")

    def str_val_tail(self):
        # <str-val-tail>
        prod = self.get_production("<str-val-tail>")
        if prod == 631:
            self.eat(",")
            self.str_val()
            self.str_val_tail()
        elif prod == 632:
            pass # Lambda
        else:
            self.error_invalid_token("<str-val-tail>")

    # ==================== STATEMENTS ====================

    def statements(self):
        # <statements>
        prod = self.get_production("<statements>")
        if prod == 633: self.assign_stmnt()
        elif prod == 634: self.ask_stmnt()
        elif prod == 635: self.echo_stmnt()
        elif prod == 636: self.look_stmnt()
        elif prod == 637: self.chart_stmnt()
        elif prod == 638: self.hoist_stmnt()
        elif prod == 639: self.heave_stmnt()
        elif prod == 640: self.haul_stmnt()
        elif prod == 641:
            self.unary_exp()
            self.eat("!!")
        else:
            self.error_invalid_token("<statements>")

    def assign_stmnt(self):
        # <assign-stmnt>
        prod = self.get_production("<assign-stmnt>")
        if prod == 642:
            self.eat("id")
            self.assign_tail()
            self.eat("!!")
        else:
            self.error_invalid_token("<assign-stmnt>")

    def assign_tail(self):
        # <assign-tail>
        prod = self.get_production("<assign-tail>")
        if prod == 643:
            # Check First Set for <arr-str> (Predict check)
            if self.current_token.type in ["{", "$"]:
                self.arr_str()
            self.assign_body()
        elif prod == 644:
            self.eat("(")
            self.args()
            self.eat(")")
        else:
            self.error_invalid_token("<assign-tail>")

    def arr_str(self):
        # <arr-str>
        prod = self.get_production("<arr-str>")
        if prod == 645:
            self.eat("{")
            self.index()
            self.eat("}")
            self.arr_str_tail()
        elif prod == 646:
            self.eat("$")
            self.eat("id")
        elif prod == 647:
            pass # Lambda
        else:
            self.error_invalid_token("<arr-str>")

    def arr_str_tail(self):
        # <arr-str-tail>
        prod = self.get_production("<arr-str-tail>")
        if prod == 648:
            self.eat("{")
            self.index()
            self.eat("}")
        elif prod == 649:
            pass # Lambda
        else:
            self.error_invalid_token("<arr-str-tail>")

    def assign_body(self):
        # <assign-body>
        prod = self.get_production("<assign-body>")
        if prod == 650:
            self.eat("=")
            self.assign_val()
        elif prod == 651:
            self.arith_assign_op()
            self.arith_ope()
            self.arith_exp()
        else:
            self.error_invalid_token("<assign-body>")

    def assign_val(self):
        # <assign-val>
        prod = self.get_production("<assign-val>")
        if prod == 652:
            self.var_val_3()
        else:
            self.error_invalid_token("<assign-val>")

    def var_val_3(self):
        # <var-val-3>
        prod = self.get_production("<var-val-3>")
        if prod == 653:
            self.value_3()
        else:
            self.error_invalid_token("<var-val-3>")

    def value_3(self):
        # <value-3>
        prod = self.get_production("<value-3>")
        if prod == 654:
            self.eat("id")
            self.id_tail()
            self.var_exp_3()
        elif prod == 655:
            self.eat("(")
            self.value()
            self.eat(")")
            self.var_exp_3()
        elif prod == 656:
            self.var_digit_3()
            self.digit_tail_3()
        elif prod == 657:
            self.eat("PARCH-lit")
            self.eq_parch_3()
        elif prod == 658:
            self.eat("SCROLL-lit")
            self.scr_char()
            self.var_scroll_eq_3()
        elif prod == 659:
            self.var_bool_3()
        else:
            self.error_invalid_token("<value-3>")

    def var_digit_3(self):
        # <var-digit-3>
        prod = self.get_production("<var-digit-3>")
        if prod == 660: self.eat("COIN-lit")
        elif prod == 661: self.eat("DIME-lit")
        elif prod == 662:
            self.eat("-")
            self.neg_var_digit_3()
        else:
            self.error_invalid_token("<var-digit-3>")

    def neg_var_digit_3(self):
        # <neg-var-digit-3>
        prod = self.get_production("<neg-var-digit-3>")
        if prod == 663:
            self.eat("id")
            self.id_tail()
        elif prod == 664:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-var-digit-3>")

    def digit_tail_3(self):
        # <digit-tail-3>
        prod = self.get_production("<digit-tail-3>")
        if prod == 665:
            self.var_arith_3()
            self.var_releq_3()
        elif prod == 666:
            pass # Lambda
        else:
            self.error_invalid_token("<digit-tail-3>")

    def var_arith_3(self):
        # <var-arith-3>
        prod = self.get_production("<var-arith-3>")
        if prod == 667:
            self.arith_op()
            self.var_arel_ope_3()
            self.var_arith_3()
        elif prod == 668:
            pass # Lambda
        else:
            self.error_invalid_token("<var-arith-3>")

    def var_arel_ope_3(self):
        # <var-arel-ope-3>
        prod = self.get_production("<var-arel-ope-3>")
        if prod == 669:
            self.neg()
            self.neg_var_arel_ope_3()
        elif prod == 670:
            self.eat("DIME-lit")
        elif prod == 671:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<var-arel-ope-3>")

    def neg_var_arel_ope_3(self):
        # <neg-var-arel-ope-3>
        prod = self.get_production("<neg-var-arel-ope-3>")
        if prod == 672:
            self.eat("id")
            self.id_tail()
        elif prod == 673:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-var-arel-ope-3>")

    def var_releq_3(self):
        # <var-releq-3>
        prod = self.get_production("<var-releq-3>")
        if prod == 674:
            self.var_rel_3()
        elif prod == 675:
            self.eq_op()
            self.var_arel_ope_3()
            self.var_log_3()
        elif prod == 676:
            pass # Lambda
        else:
            self.error_invalid_token("<var-releq-3>")

    def var_rel_3(self):
        # <var-rel-3>
        prod = self.get_production("<var-rel-3>")
        if prod == 677:
            self.rel_op()
            self.var_arel_ope_3()
            self.var_arith_3()
            self.var_logeq_3()
        elif prod == 678:
            pass # Lambda
        else:
            self.error_invalid_token("<var-rel-3>")

    def var_logeq_3(self):
        # <var-logeq-3>
        prod = self.get_production("<var-logeq-3>")
        if prod == 679:
            self.logeq_op()
            self.log_ope_3()
            self.var_log_3()
        elif prod == 680:
            pass # Lambda
        else:
            self.error_invalid_token("<var-logeq-3>")

    def var_log_3(self):
        # <var-log-3>
        prod = self.get_production("<var-log-3>")
        if prod == 681:
            self.log_op()
            self.log_ope_3()
            self.var_log_3()
        elif prod == 682:
            pass # Lambda
        else:
            self.error_invalid_token("<var-log-3>")

    def log_ope_3(self):
        # <log-ope-3>
        prod = self.get_production("<log-ope-3>")
        if prod == 683:
            self.bool_var_ope()
        else:
            self.error_invalid_token("<log-ope-3>")

    def eq_parch_3(self):
        # <eq-parch-3>
        prod = self.get_production("<eq-parch-3>")
        if prod == 684:
            self.eq_op()
            self.eat("PARCH-lit")
            self.var_log_3()
        elif prod == 685:
            pass # Lambda
        else:
            self.error_invalid_token("<eq-parch-3>")

    def var_scroll_eq_3(self):
        # <var-scroll-eq-3>
        prod = self.get_production("<var-scroll-eq-3>")
        if prod == 686:
            self.var_scroll_3()
        elif prod == 687:
            self.eq_scroll_3()
        elif prod == 688:
            pass # Lambda
        else:
            self.error_invalid_token("<var-scroll-eq-3>")

    def var_scroll_3(self):
        # <var-scroll-3>
        prod = self.get_production("<var-scroll-3>")
        if prod == 689:
            self.eat("&")
            self.concat_ope_3()
            self.var_scroll_3()
        elif prod == 690:
            pass # Lambda
        else:
            self.error_invalid_token("<var-scroll-3>")

    def concat_ope_3(self):
        # <concat-ope-3>
        prod = self.get_production("<concat-ope-3>")
        if prod == 691:
            self.eat("id")
            self.id_tail()
        elif prod == 692:
            self.eat("(")
            self.scroll_grp_val()
            self.eat(")")
        elif prod == 693:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<concat-ope-3>")

    def eq_scroll_3(self):
        # <eq-scroll-3>
        prod = self.get_production("<eq-scroll-3>")
        if prod == 694:
            self.eq_op()
            self.eq_scroll_ope_3()
            self.var_log_3()
        else:
            self.error_invalid_token("<eq-scroll-3>")

    def eq_scroll_ope_3(self):
        # <eq-scroll-ope-3>
        prod = self.get_production("<eq-scroll-ope-3>")
        if prod == 695:
            self.eat("id")
            self.id_tail()
        elif prod == 696:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<eq-scroll-ope-3>")

    def var_bool_3(self):
        # <var-bool-3>
        prod = self.get_production("<var-bool-3>")
        if prod == 697:
            self.bool_lit_var_3()
        elif prod == 698:
            self.not_op()
            self.not_val_var_3()
        else:
            self.error_invalid_token("<var-bool-3>")

    def bool_lit_var_3(self):
        # <bool-lit-var-3>
        prod = self.get_production("<bool-lit-var-3>")
        if prod == 699: self.eat("AYE")
        elif prod == 700: self.eat("NAY")
        else:
            self.error_invalid_token("<bool-lit-var-3>")

    def not_val_var_3(self):
        # <not-val-var-3>
        prod = self.get_production("<not-val-var-3>")
        if prod == 701:
            self.eat("id")
            self.id_tail()
        elif prod == 702:
            self.eat("(")
            self.bool_grp_val()
            self.eat(")")
        elif prod == 703:
            self.bool_lit_var_3()
        else:
            self.error_invalid_token("<not-val-var-3>")

    def var_exp_3(self):
        # <var-exp-3>
        prod = self.get_production("<var-exp-3>")
        if prod == 704:
            self.expressions_3()
        elif prod == 705:
            pass # Lambda
        else:
            self.error_invalid_token("<var-exp-3>")

    def expressions_3(self):
        # <expressions-3>
        prod = self.get_production("<expressions-3>")
        if prod == 706:
            self.arith_op()
            self.var_arel_ope_3()
            self.var_arith_3()
            self.var_releq_3()
        elif prod == 707:
            self.rel_op()
            self.var_arel_ope_3()
            self.var_arith_3()
            self.var_logeq_3()
        elif prod == 708:
            self.log_op()
            self.log_ope_3()
            self.var_log_3()
        elif prod == 709:
            self.eq_op()
            self.eq_ope_var()
            self.var_log_3()
        elif prod == 710:
            self.eat("&")
            self.concat_ope_3()
            self.var_scroll_3()
        else:
            self.error_invalid_token("<expressions-3>")

    def bool_var_ope(self):
        # <bool-var-ope>
        prod = self.get_production("<bool-var-ope>")
        if prod == 711:
            self.eat("id")
            self.id_tail()
            self.bool_var_exp2()
        elif prod == 712:
            self.eat("(")
            self.value()
            self.eat(")")
            self.bool_var_exp2()
        elif prod == 713:
            self.bool_val_exp_var()
        elif prod == 714:
            self.bool_digit_exp_var()
        elif prod == 715:
            self.bool_parch_exp_var()
        elif prod == 716:
            self.bool_scroll_exp_var()
        else:
            self.error_invalid_token("<bool-var-ope>")

    def bool_val_exp_var(self):
        # <bool-val-exp-var>
        prod = self.get_production("<bool-val-exp-var>")
        if prod == 717:
            self.bool_var2()
            self.bool_eq_var()
        else:
            self.error_invalid_token("<bool-val-exp-var>")

    def bool_var2(self):
        # <bool-var2>
        prod = self.get_production("<bool-var2>")
        if prod == 718:
            self.bool_lit_var2()
        elif prod == 719:
            self.not_op()
            self.not_ope_var()
        else:
            self.error_invalid_token("<bool-var2>")

    def bool_lit_var2(self):
        # <bool-lit-var2>
        prod = self.get_production("<bool-lit-var2>")
        if prod == 720: self.eat("AYE")
        elif prod == 721: self.eat("NAY")
        else:
            self.error_invalid_token("<bool-lit-var2>")

    def not_ope_var(self):
        # <not-ope-var>
        prod = self.get_production("<not-ope-var>")
        if prod == 722:
            self.eat("id")
            self.id_tail()
        elif prod == 723:
            self.eat("(")
            self.bool_grp_val()
            self.eat(")")
        elif prod == 724:
            self.bool_lit_var2()
        else:
            self.error_invalid_token("<not-ope-var>")

    def bool_eq_var(self):
        # <bool-eq-var>
        prod = self.get_production("<bool-eq-var>")
        if prod == 725:
            self.eq_op()
            self.bool_var_ope()
        elif prod == 726:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-eq-var>")

    def bool_digit_exp_var(self):
        # <bool-digit-exp-var>
        prod = self.get_production("<bool-digit-exp-var>")
        if prod == 727:
            self.bool_digit_var()
            self.bool_arith_var()
            self.rel_eq_var()
        else:
            self.error_invalid_token("<bool-digit-exp-var>")

    def bool_digit_var(self):
        # <bool-digit-var>
        prod = self.get_production("<bool-digit-var>")
        if prod == 728: self.eat("COIN-lit")
        elif prod == 729: self.eat("DIME-lit")
        elif prod == 730:
            self.eat("-")
            self.neg_bool_digit_var()
        else:
            self.error_invalid_token("<bool-digit-var>")

    def neg_bool_digit_var(self):
        # <neg-bool-digit-var>
        prod = self.get_production("<neg-bool-digit-var>")
        if prod == 731:
            self.eat("id")
            self.id_tail()
        elif prod == 732:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-bool-digit-var>")

    def bool_arith_var(self):
        # <bool-arith-var>
        prod = self.get_production("<bool-arith-var>")
        if prod == 733:
            self.arith_var()
            self.bool_arith_var()
        elif prod == 734:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-arith-var>")

    def arith_var(self):
        # <arith-var>
        prod = self.get_production("<arith-var>")
        if prod == 735:
            self.arith_op()
            self.bool_arel_ope_var()
        else:
            self.error_invalid_token("<arith-var>")

    def bool_arel_ope_var(self):
        # <bool-arel-ope-var>
        prod = self.get_production("<bool-arel-ope-var>")
        if prod == 736:
            self.neg()
            self.neg_bool_arel_ope_var()
        elif prod == 737:
            self.eat("DIME-lit")
        elif prod == 738:
            self.eat("COIN-lit")
        else:
            self.error_invalid_token("<bool-arel-ope-var>")

    def neg_bool_arel_ope_var(self):
        # <neg-bool-arel-ope-var>
        prod = self.get_production("<neg-bool-arel-ope-var>")
        if prod == 739:
            self.eat("id")
            self.id_tail()
        elif prod == 740:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-bool-arel-ope-var>")

    def rel_eq_var(self):
        # <rel-eq-var>
        prod = self.get_production("<rel-eq-var>")
        if prod == 741:
            self.rel_var()
        elif prod == 742:
            self.digit_eq_var()
        else:
            self.error_invalid_token("<rel-eq-var>")

    def rel_var(self):
        # <rel-var>
        prod = self.get_production("<rel-var>")
        if prod == 743:
            self.rel_op()
            self.bool_arel_ope_var()
            self.bool_arith_var()
            self.bool_eq_var()
        else:
            self.error_invalid_token("<rel-var>")

    def digit_eq_var(self):
        # <digit-eq-var>
        prod = self.get_production("<digit-eq-var>")
        if prod == 744:
            self.eq_op()
            self.bool_arel_ope_var()
        else:
            self.error_invalid_token("<digit-eq-var>")

    def bool_parch_exp_var(self):
        # <bool-parch-exp-var>
        prod = self.get_production("<bool-parch-exp-var>")
        if prod == 745:
            self.eat("PARCH-lit")
            self.eq_op()
            self.bool_parch_var()
        else:
            self.error_invalid_token("<bool-parch-exp-var>")

    def bool_parch_var(self):
        # <bool-parch-var>
        prod = self.get_production("<bool-parch-var>")
        if prod == 746:
            self.eat("id")
            self.id_tail()
        elif prod == 747:
            self.eat("PARCH-lit")
        else:
            self.error_invalid_token("<bool-parch-var>")

    def bool_scroll_exp_var(self):
        # <bool-scroll-exp-var>
        prod = self.get_production("<bool-scroll-exp-var>")
        if prod == 748:
            self.eat("SCROLL-lit")
            self.scr_char()
            self.eq_op()
            self.bool_scroll_var()
        else:
            self.error_invalid_token("<bool-scroll-exp-var>")

    def bool_scroll_var(self):
        # <bool-scroll-var>
        prod = self.get_production("<bool-scroll-var>")
        if prod == 749:
            self.eat("id")
            self.id_tail()
        elif prod == 750:
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<bool-scroll-var>")

    def bool_var_exp2(self):
        # <bool-var-exp2>
        prod = self.get_production("<bool-var-exp2>")
        if prod == 751:
            self.arith_var()
            self.bool_arith_var()
            self.rel_eq_var()
        elif prod == 752:
            self.rel_var()
        elif prod == 753:
            self.eq_op()
            self.eq_ope_var()
        elif prod == 754:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-var-exp2>")

    def eq_ope_var(self):
        # <eq-ope-var>
        prod = self.get_production("<eq-ope-var>")
        if prod == 755:
            self.eat("id")
            self.id_tail()
            self.bool_var_exp3()
        elif prod == 756:
            self.eat("(")
            self.eq_ope_grp()
        elif prod == 757:
            self.bool_digit_var()
            self.bool_arith_var()
            self.bool_rel_var()
        elif prod == 758:
            self.eat("PARCH-lit")
        elif prod == 759:
            self.eat("SCROLL-lit")
            self.scr_char()
        elif prod == 760:
            self.bool_var2()
        else:
            self.error_invalid_token("<eq-ope-var>")

    def bool_var_exp3(self):
        # <bool-var-exp3>
        prod = self.get_production("<bool-var-exp3>")
        if prod == 761:
            self.arith_var()
            self.bool_arith_var()
            self.bool_rel_var()
        elif prod == 762:
            self.rel_op()
            self.bool_arel_ope_var()
        elif prod == 763:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-var-exp3>")

    def bool_rel_var(self):
        # <bool-rel-var>
        prod = self.get_production("<bool-rel-var>")
        if prod == 764:
            self.rel_op()
            self.bool_arel_ope_var()
        elif prod == 765:
            pass # Lambda
        else:
            self.error_invalid_token("<bool-rel-var>")

    def arith_assign_op(self):
        # <arith-assign-op>
        prod = self.get_production("<arith-assign-op>")
        if prod == 766: self.eat("+=")
        elif prod == 767: self.eat("-=")
        elif prod == 768: self.eat("*=")
        elif prod == 769: self.eat("/=")
        elif prod == 770: self.eat("%=")
        elif prod == 771: self.eat("^=")
        else:
            self.error_invalid_token("<arith-assign-op>")

    def arith_ope(self):
        # <arith-ope>
        prod = self.get_production("<arith-ope>")
        if prod == 772:
            self.eat("id")
            self.id_tail()
        elif prod == 773:
            self.neg()
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        elif prod == 774:
            self.eat("COIN-lit")
        elif prod == 775:
            self.eat("DIME-lit")
        else:
            self.error_invalid_token("<arith-ope>")

    def arith_exp(self):
        # <arith-exp>
        prod = self.get_production("<arith-exp>")
        if prod == 776:
            self.arith_op()
            self.arith_ope()
            self.arith_exp()
        elif prod == 777:
            pass # Lambda
        else:
            self.error_invalid_token("<arith-exp>")

    def ask_stmnt(self):
        # <ask-stmnt>
        prod = self.get_production("<ask-stmnt>")
        if prod == 778:
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
        if prod == 779:
            self.eat("@")
            self.eat("id")
            # First set check for arr_str
            if self.current_token.type in ["{", "$"]:
                self.arr_str()
            self.addr_tail()
        else:
            self.error_invalid_token("<addr>")

    def addr_tail(self):
        # <addr-tail>
        prod = self.get_production("<addr-tail>")
        if prod == 780:
            self.eat(",")
            self.addr()
        elif prod == 781:
            pass # Lambda
        else:
            self.error_invalid_token("<addr-tail>")

    def echo_stmnt(self):
        # <echo-stmnt>
        prod = self.get_production("<echo-stmnt>")
        if prod == 782:
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
        if prod == 783:
            self.eat(",")
            self.echo_val()
            self.echo_arg()
        elif prod == 784:
            pass # Lambda
        else:
            self.error_invalid_token("<echo-arg>")

    def echo_val(self):
        # <echo-val>
        prod = self.get_production("<echo-val>")
        if prod == 785:
            self.var_val()
        else:
            self.error_invalid_token("<echo-val>")

    def look_stmnt(self):
        # <look-stmnt>
        prod = self.get_production("<look-stmnt>")
        if prod == 786:
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
        if prod == 787:
            self.bool_grp_val()
        else:
            self.error_invalid_token("<condition>")

    def look_body(self):
        # <look-body>
        prod = self.get_production("<look-body>")
        if prod == 788:
            self.look_body_stmnt()
            self.look_body()
        elif prod == 789:
            pass # Lambda
        else:
            self.error_invalid_token("<look-body>")

    def look_body_stmnt(self):
        # <look-body-stmnt>
        prod = self.get_production("<look-body-stmnt>")
        if prod == 790:
            self.statements()
        else:
            self.error_invalid_token("<look-body-stmnt>")

    def jump_stmnt(self):
        # <jump-stmnt>
        prod = self.get_production("<jump-stmnt>")
        if prod == 791:
            self.eat("SAIL")
            self.eat("!!")
        elif prod == 792:
            self.eat("LAND")
            self.eat("!!")
        elif prod == 793:
            pass # Lambda
        else:
            self.error_invalid_token("<jump-stmnt>")

    def look_tail(self):
        # <look-tail>
        prod = self.get_production("<look-tail>")
        if prod == 794:
            self.eat("DROPLOOK")
            self.eat("(")
            self.condition()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
            self.look_tail()
        elif prod == 795:
            self.eat("DROP")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
        elif prod == 796:
            pass # Lambda
        else:
            self.error_invalid_token("<look-tail>")

    def chart_stmnt(self):
        # <chart-stmnt>
        prod = self.get_production("<chart-stmnt>")
        if prod == 797:
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
        if prod == 798: 
            self.eat("id")
            self.id_tail()
        elif prod == 799: 
            self.chart_const()
        else:
            self.error_invalid_token("<chart-cond>")

    def chart_const(self):
        # <chart-const>
        prod = self.get_production("<chart-const>")
        if prod == 800: self.eat("COIN-lit")
        elif prod == 801: self.eat("PARCH-lit")
        elif prod == 802: 
            self.eat("SCROLL-lit")
            self.scr_char()
        else:
            self.error_invalid_token("<chart-const>")

    def courses(self):
        # <courses>
        prod = self.get_production("<courses>")
        if prod == 803:
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
        if prod == 804:
            self.course_stmnt()
            self.course_body()
        elif prod == 805:
            pass # Lambda
        else:
            self.error_invalid_token("<course-body>")

    def course_stmnt(self):
        # <course-stmnt>
        prod = self.get_production("<course-stmnt>")
        if prod == 806:
            self.statements()
        else:
            self.error_invalid_token("<course-stmnt>")
    
    def course_jmp(self):
        # <course-jmp>
        prod = self.get_production("<course-jmp>")
        if prod == 807:
             self.eat("SAIL")
             self.eat("!!")
        elif prod == 808:
             self.eat("LAND")
             self.eat("!!")
        elif prod == 809:
            pass # Lambda
        else:
             self.error_invalid_token("<course-jmp>")

    def course_tail(self):
        # <course-tail>
        prod = self.get_production("<course-tail>")
        if prod == 810:
            self.courses()
            self.course_tail()
        elif prod == 811:
            pass # Lambda
        else:
            self.error_invalid_token("<course-tail>")

    def adrift_case(self):
        # <adrift-case>
        prod = self.get_production("<adrift-case>")
        if prod == 812:
            self.eat("ADRIFT")
            self.eat(":")
            self.adrift_body()
            self.eat("LAND")
            self.eat("!!")
        elif prod == 813:
            pass # Lambda
        else:
            self.error_invalid_token("<adrift-case>")

    def adrift_body(self):
        # <adrift-body>
        prod = self.get_production("<adrift-body>")
        if prod == 814:
            self.statements()
            self.adrift_body()
        elif prod == 815:
            pass # Lambda
        else:
            self.error_invalid_token("<adrift-body>")

    def hoist_stmnt(self):
        # <hoist-stmnt>
        prod = self.get_production("<hoist-stmnt>")
        if prod == 816:
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
        if prod == 817:
            self.eat("COIN")
            self.eat("id")
            self.eat("=")
            self.eat("COIN-lit")
            self.init1_mult()
        elif prod == 818:
            self.eat("id")
            # First set check for arr_str
            if self.current_token.type in ["{", "$"]:
                self.arr_str()
            self.eat("=")
            self.eat("COIN-lit")
            self.init2_mult()
        elif prod == 819:
            pass # Lambda
        else:
            self.error_invalid_token("<hoist-init>")

    def init1_mult(self):
        # <init1-mult>
        prod = self.get_production("<init1-mult>")
        if prod == 820:
            self.eat(",")
            self.eat("id")
            self.eat("=")
            self.eat("COIN-lit")
            self.init1_mult()
        elif prod == 821:
            pass # Lambda
        else:
            self.error_invalid_token("<init1-mult>")

    def init2_mult(self):
        # <init2-mult>
        prod = self.get_production("<init2-mult>")
        if prod == 822:
            self.eat(",")
            self.eat("id")
            # First set check for arr_str
            if self.current_token.type in ["{", "$"]:
                self.arr_str()
            self.eat("=")
            self.eat("COIN-lit")
            self.init2_mult()
        elif prod == 823:
            pass # Lambda
        else:
            self.error_invalid_token("<init2-mult>")

    def hoist_cond(self):
        # <hoist-cond>
        prod = self.get_production("<hoist-cond>")
        if prod == 824:
            self.hoist_ope()
            self.hoist_cond_arith()
            self.releq_op()
            self.hoist_ope()
            self.hoist_cond_arith()
            self.hoist_log()
        else:
            self.error_invalid_token("<hoist-cond>")

    def releq_op(self):
        # <releq-op>
        prod = self.get_production("<releq-op>")
        if prod == 825: self.rel_op()
        elif prod == 826: self.eq_op()
        else:
            self.error_invalid_token("<releq-op>")

    def hoist_ope(self):
        # <hoist-ope>
        prod = self.get_production("<hoist-ope>")
        if prod == 827:
            self.neg()
            self.neg_hoist_ope()
        elif prod == 828:
            self.eat("COIN-lit")
        elif prod == 829:
            self.eat("DIME-lit")
        else:
            self.error_invalid_token("<hoist-ope>")

    def neg_hoist_ope(self):
        # <neg-hoist-ope>
        prod = self.get_production("<neg-hoist-ope>")
        if prod == 830:
            self.eat("id")
            self.id_tail()
        elif prod == 831:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
            self.error_invalid_token("<neg-hoist-ope>")

    def hoist_cond_arith(self):
        # <hoist-cond-arith>
        prod = self.get_production("<hoist-cond-arith>")
        if prod == 832:
            self.arith_op()
            self.hoist_ope()
            self.hoist_cond_arith()
        elif prod == 833:
            pass # Lambda
        else:
            self.error_invalid_token("<hoist-cond-arith>")

    def hoist_log(self):
        # <hoist-log>
        prod = self.get_production("<hoist-log>")
        if prod == 834:
            self.log_op()
            self.hoist_cond()
        elif prod == 835:
            pass # Lambda
        else:
            self.error_invalid_token("<hoist-log>")

    def hoist_upd(self):
        # <hoist-upd>
        prod = self.get_production("<hoist-upd>")
        if prod == 836:
            self.upd()
            self.upd_mult()
        else:
            self.error_invalid_token("<hoist-upd>")

    def upd(self):
        # <upd>
        prod = self.get_production("<upd>")
        if prod == 837:
            self.hoist_unary()
        elif prod == 838:
            self.hoist_assign()
        else:
            self.error_invalid_token("<upd>")

    def hoist_unary(self):
        # <hoist-unary>
        prod = self.get_production("<hoist-unary>")
        if prod == 839:
            self.unary_op()
            self.eat("id")
            # First set check for arr_str
            if self.current_token.type in ["{", "$"]:
                self.arr_str()
        else:
            self.error_invalid_token("<hoist-unary>")

    def hoist_assign(self):
        # <hoist-assign>
        prod = self.get_production("<hoist-assign>")
        if prod == 840:
            self.eat("id")
            # First set check for arr_str
            if self.current_token.type in ["{", "$"]:
                self.arr_str()
            self.arith_assign_op()
            self.hoist_arith_ope()
            self.hoist_arith()
        else:
            self.error_invalid_token("<hoist-assign>")

    def hoist_arith_ope(self):
        # <hoist-arith-ope>
        prod = self.get_production("<hoist-arith-ope>")
        if prod == 841:
            self.neg()
            self.neg_hoist_arith_ope()
        elif prod == 842:
            self.eat("COIN-lit")
        elif prod == 843:
            self.eat("DIME-lit")
        else:
            self.error_invalid_token("<hoist-arith-ope>")

    def neg_hoist_arith_ope(self):
        # <neg-hoist-arith-ope>
        prod = self.get_production("<neg-hoist-arith-ope>")
        if prod == 844:
            self.eat("id")
            self.id_tail()
        elif prod == 845:
            self.eat("(")
            self.dime_grp_val()
            self.eat(")")
        else:
             self.error_invalid_token("<neg-hoist-arith-ope>")

    def hoist_arith(self):
        # <hoist-arith>
        prod = self.get_production("<hoist-arith>")
        if prod == 846:
            self.arith_op()
            self.hoist_arith_ope()
            self.hoist_arith()
        elif prod == 847:
            pass # Lambda
        else:
            self.error_invalid_token("<hoist-arith>")

    def upd_mult(self):
        # <upd-mult>
        prod = self.get_production("<upd-mult>")
        if prod == 848:
            self.eat(",")
            self.upd()
            self.upd_mult()
        elif prod == 849:
            pass # Lambda
        else:
            self.error_invalid_token("<upd-mult>")

    def heave_stmnt(self):
        # <heave-stmnt>
        prod = self.get_production("<heave-stmnt>")
        if prod == 850:
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
        if prod == 851:
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
        if prod == 852:
            self.unary_op()
            self.eat("id")
            # First set check for arr_str
            if self.current_token.type in ["{", "$"]:
                self.arr_str()
        else:
            self.error_invalid_token("<unary-exp>")

    def unary_op(self):
        # <unary-op>
        prod = self.get_production("<unary-op>")
        if prod == 853: self.eat("+#")
        elif prod == 854: self.eat("-#")
        else:
            self.error_invalid_token("<unary-op>")

    # =========================================
    # AHOY PRODUCTIONS
    # =========================================

    def ahoy_local_dec(self):
        # <ahoy-local-dec>
        prod = self.get_production("<ahoy-local-dec>")
        if prod == 855:
            self.ahoy_var_arr()
            self.ahoy_local_dec()
        elif prod == 856:
            self.ahoy_struct_dec()
        elif prod == 857:
            pass # Lambda
        else:
            self.error_invalid_token("<ahoy-local-dec>")

    def ahoy_var_arr(self):
        # <ahoy-var-arr>
        prod = self.get_production("<ahoy-var-arr>")
        if prod == 858:
            self.eat("COIN")
            self.eat("id")
            self.ahoy_coin_local()
        elif prod == 859:
            self.eat("DIME")
            self.eat("id")
            self.ahoy_dime_local()
        elif prod == 860:
            self.eat("PARCH")
            self.eat("id")
            self.ahoy_parch_local()
        elif prod == 861:
            self.eat("SCROLL")
            self.eat("id")
            self.ahoy_scroll_local()
        elif prod == 862:
            self.eat("BOOL")
            self.eat("id")
            self.ahoy_bool_local()
        else:
            self.error_invalid_token("<ahoy-var-arr>")

    def ahoy_coin_local(self):
        # <ahoy-coin-local>
        prod = self.get_production("<ahoy-coin-local>")
        if prod == 863:
            self.coin_var()
            self.eat("!!")
        elif prod == 864:
            self.coin_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<ahoy-coin-local>")

    def ahoy_dime_local(self):
        # <ahoy-dime-local>
        prod = self.get_production("<ahoy-dime-local>")
        if prod == 865:
            self.dime_var()
            self.eat("!!")
        elif prod == 866:
            self.dime_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<ahoy-dime-local>")

    def ahoy_parch_local(self):
        # <ahoy-parch-local>
        prod = self.get_production("<ahoy-parch-local>")
        if prod == 867:
            self.parch_var()
            self.eat("!!")
        elif prod == 868:
            self.parch_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<ahoy-parch-local>")

    def ahoy_scroll_local(self):
        # <ahoy-scroll-local>
        prod = self.get_production("<ahoy-scroll-local>")
        if prod == 869:
            self.scroll_var()
            self.eat("!!")
        elif prod == 870:
            self.scroll_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<ahoy-scroll-local>")

    def ahoy_bool_local(self):
        # <ahoy-bool-local>
        prod = self.get_production("<ahoy-bool-local>")
        if prod == 871:
            self.bool_var()
            self.eat("!!")
        elif prod == 872:
            self.bool_arr()
            self.eat("!!")
        else:
            self.error_invalid_token("<ahoy-bool-local>")

    def ahoy_struct_dec(self):
        # <ahoy-struct-dec>
        prod = self.get_production("<ahoy-struct-dec>")
        if prod == 873:
            self.eat("MAST")
            self.eat("id")
            self.eat("id")
            self.str_dec_init()
            self.eat("!!")
            self.ahoy_struct_dec()
        elif prod == 874:
            pass # Lambda
        else:
            self.error_invalid_token("<ahoy-struct-dec>")

    def ahoy_stmnts(self):
        # <ahoy-stmnts>
        prod = self.get_production("<ahoy-stmnts>")
        if prod == 875:
            self.ahoy_stmnt()
            self.ahoy_tail()
        else:
            self.error_invalid_token("<ahoy-stmnts>")

    def ahoy_tail(self):
        # <ahoy-tail>
        prod = self.get_production("<ahoy-tail>")
        if prod == 876:
            self.ahoy_stmnts()
        elif prod == 877:
            pass # Lambda
        else:
            self.error_invalid_token("<ahoy-tail>")

    def ahoy_stmnt(self):
        # <ahoy-stmnt>
        prod = self.get_production("<ahoy-stmnt>")
        if prod == 878: self.ahoy_assign()
        elif prod == 879: self.ahoy_ask()
        elif prod == 880: self.ahoy_echo()
        elif prod == 881: self.ahoy_look()
        elif prod == 882: self.ahoy_chart()
        elif prod == 883: self.ahoy_hoist()
        elif prod == 884: self.ahoy_heave()
        elif prod == 885: self.ahoy_haul()
        elif prod == 886:
            self.unary_exp()
            self.eat("!!")
        else:
            self.error_invalid_token("<ahoy-stmnt>")

    def ahoy_assign(self):
        # <ahoy-assign>
        prod = self.get_production("<ahoy-assign>")
        if prod == 887:
            self.eat("id")
            self.assign_tail()
            self.eat("!!")
        else:
            self.error_invalid_token("<ahoy-assign>")

    def ahoy_ask(self):
        # <ahoy-ask>
        prod = self.get_production("<ahoy-ask>")
        if prod == 888:
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
        if prod == 889:
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
        if prod == 890:
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
        if prod == 891:
            self.eat("DROPLOOK")
            self.eat("(")
            self.condition()
            self.eat(")")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
            self.ahoy_look_tail()
        elif prod == 892:
            self.eat("DROP")
            self.eat("[")
            self.look_body()
            self.jump_stmnt()
            self.eat("]")
        elif prod == 893:
            pass # Lambda
        else:
            self.error_invalid_token("<ahoy-look-tail>")

    def ahoy_chart(self):
        # <ahoy-chart>
        prod = self.get_production("<ahoy-chart>")
        if prod == 894:
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
        if prod == 895:
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
        if prod == 896:
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
        if prod == 897:
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

    def eq_ope_2(self):
        # <eq-ope-2>
        prod = self.get_production("<eq-ope-2>")
        if prod == 898:
            self.eq_ope_arr()
        else:
            self.error_invalid_token("<eq-ope-2>")