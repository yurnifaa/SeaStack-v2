# syn_parser.py
import sys
from syntax.First_Set import FIRST
from syntax.Predict_Set import PREDICT
from syntax.Follow_Set import FOLLOW

# IMPORT THE ERROR HANDLER
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
        expected = list(PREDICT[non_terminal].keys())
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
    # Program Structure
    # =========================================

    def program(self):
        # <program>
        # Prod 1: <global-dec> AHOY ( ) [ <local-dec> <statements> ]
        production = self.get_production("<program>")
        if production == 1:
            self.global_dec()
            self.eat("AHOY")
            self.eat("(")
            self.eat(")")
            self.eat("[")
            self.local_dec()
            
            # FIX: Check if the next token actually starts a statement.
            # If it is ']', skip self.statements() entirely.
            # stmnt_tokens = ["id", "ASK", "ECHO", "LOOK", "CHART", "HOIST", "HEAVE", "HAUL", "+#", "-#"]
            # if self.current_token and self.current_token.type in stmnt_tokens:
            self.statements()
            
            self.eat("]")
        else:
            self.error_invalid_token("<program>")

    def global_dec(self):
        # <global-dec>
        production = self.get_production("<global-dec>")
        if production == 2: # <d-type> id <dtype-tail>
            self.d_type()
            self.eat("id")
            self.dtype_tail()
        elif production == 3: # <locke-dec> <global-dec>
            self.locke_dec()
            self.global_dec()
        elif production == 4: # <struct-def>
            self.struct_def()
        elif production == 5: # <nonreturn-func> <sub-func>
            self.nonreturn_func()
            self.sub_func()
        elif production == 6: # Lambda
            pass 
        else:
            self.error_invalid_token("<global-dec>")

    def d_type(self):
        # <d-type>
        production = self.get_production("<d-type>")
        if production == 7: self.eat("COIN")
        elif production == 8: self.eat("DIME")
        elif production == 9: self.eat("PARCH")
        elif production == 10: self.eat("SCROLL")
        elif production == 11: self.eat("BOOL")
        else:
            self.error_invalid_token("<d-type>")

    def dtype_tail(self):
        # <dtype-tail>
        production = self.get_production("<dtype-tail>")
        if production == 12: # <var-arr-dec> <global-dec>
            self.var_arr_dec()
            self.global_dec()
        elif production == 13: # <return-func> <sub-func>
            self.return_func()
            self.sub_func()
        else:
            self.error_invalid_token("<dtype-tail>")

    def var_arr_dec(self):
        # <var-arr-dec>
        production = self.get_production("<var-arr-dec>")
        if production == 14: self.variable()
        elif production == 15: self.array()
        else:
            self.error_invalid_token("<var-arr-dec>")

    def variable(self):
        # <variable>
        production = self.get_production("<variable>")
        if production == 16:
            self.var_init()
            self.multi_var_init()
            self.eat("!!")
        else:
            self.error_invalid_token("<variable>")

    def var_init(self):
        # <var-init>
        production = self.get_production("<var-init>")
        if production == 17:
            self.eat("=")
            self.var_val()
        elif production == 18: pass # Lambda
        else:
            self.error_invalid_token("<var-init>")

    def multi_var_init(self):
        # <multi-var-init>
        production = self.get_production("<multi-var-init>")
        if production == 19:
            self.eat(",")
            self.eat("id")
            self.var_init()
            self.multi_var_init()
        elif production == 20: pass # Lambda
        else:
            self.error_invalid_token("<multi-var-init>")

    def array(self):
        # <array>
        production = self.get_production("<array>")
        if production == 21:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}") # FIX: Added eat("}")
            self.arr_tail()
            self.eat("!!")
        else:
            self.error_invalid_token("<array>")

    def arr_tail(self):
        # <arr-tail>
        production = self.get_production("<arr-tail>")
        if production == 22:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}") # FIX: Added eat("}")
            self.arr2_tail()
        elif production == 23:
            self.eat("=")
            self.eat("[")
            self.arr_val()
            self.eat("]")
        elif production == 24: pass # Lambda
        else:
            self.error_invalid_token("<arr-tail>")

    def arr_val(self):
        # <arr-val>
        production = self.get_production("<arr-val>")
        if production == 25:
            self.var_val()
            self.arr_val_tail()
        else:
            self.error_invalid_token("<arr-val>")

    def arr_val_tail(self):
        # <arr-val-tail>
        production = self.get_production("<arr-val-tail>")
        if production == 26:
            self.eat(",")
            self.var_val()
            self.arr_val_tail()
        elif production == 27: pass # Lambda
        else:
            self.error_invalid_token("<arr-val-tail>")
    
    def arr2_tail(self):
        # <arr2-tail>
        production = self.get_production("<arr2-tail>")
        if production == 28:
            self.eat("=")
            self.eat("[")
            self.arr2_val()
            self.eat("]")
        elif production == 29: pass # Lambda
        else:
            self.error_invalid_token("<arr2-tail>")

    def arr2_val(self):
        # <arr2-val>
        production = self.get_production("<arr2-val>")
        if production == 30:
            self.eat("[")
            self.arr_val()
            self.eat("]")
            self.arr2_val_tail()
        else:
            self.error_invalid_token("<arr2-val>")

    def arr2_val_tail(self):
        # <arr2-val-tail>
        production = self.get_production("<arr2-val-tail>")
        if production == 31:
            self.eat(",")
            self.arr2_val()
            self.arr2_val_tail()
        elif production == 32: pass # Lambda
        else:
            self.error_invalid_token("<arr2-val-tail>")

    def locke_dec(self):
        # <locke-dec>
        production = self.get_production("<locke-dec>")
        if production == 33:
            self.eat("LOCKE")
            self.locke_init()
            self.eat("!!")
        else:
            self.error_invalid_token("<locke-dec>")

    def locke_init(self):
        # <locke-init>
        production = self.get_production("<locke-init>")
        if production == 34:
            self.eat("COIN")
            self.eat("id")
            self.eat("=")
            self.eat("COIN-lit")
        elif production == 35:
            self.eat("DIME")
            self.eat("id")
            self.eat("=")
            self.digits()
        elif production == 36:
            self.eat("PARCH")
            self.eat("id")
            self.eat("=")
            self.eat("PARCH-lit")
        elif production == 37:
            self.eat("SCROLL")
            self.eat("id")
            self.eat("=")
            self.eat("SCROLL-lit")
            self.scr_id()
        elif production == 38:
            self.eat("BOOL")
            self.eat("id")
            self.eat("=")
            self.bool_lit()
        else:
            self.error_invalid_token("<locke-init>")

    def scr_id(self):
        # <scr-id>
        production = self.get_production("<scr-id>")
        if production == 39:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
        elif production == 40: pass # Lambda
        else:
            self.error_invalid_token("<scr-id>")

    def struct_def(self):
        # <struct-def>
        production = self.get_production("<struct-def>")
        if production == 41:
            self.eat("MAST")
            self.eat("id")
            self.eat("[")
            self.mem_dec()
            self.more_mem()
            self.eat("]")
            self.eat("!!")
            self.struct_def()
            self.sub_func()
        elif production == 42: pass # Lambda
        else:
            self.error_invalid_token("<struct-def>")

    def mem_dec(self):
        # <mem-dec>
        production = self.get_production("<mem-dec>")
        if production == 43:
            self.d_type()
            self.eat("id")
            self.mem_dec_tail()
            self.eat("!!")
        else:
            self.error_invalid_token("<mem-dec>")

    def mem_dec_tail(self):
        # <mem-dec-tail>
        production = self.get_production("<mem-dec-tail>")
        if production == 44:
            self.eat(",")
            self.eat("id")
            self.mem_dec_tail()
        elif production == 45: pass # Lambda
        else:
            self.error_invalid_token("<mem-dec-tail>")

    def more_mem(self):
        # <more-mem>
        production = self.get_production("<more-mem>")
        if production == 46:
            self.mem_dec()
            self.more_mem() # allow 3+ members
        elif production == 47: pass # Lambda
        else:
            self.error_invalid_token("<more-mem>")

    # =========================================
    # Expressions & Values
    # =========================================

    def var_val(self):
        # <var-val>
        production = self.get_production("<var-val>")
        if production == 48:
            self.operands()
            self.exp_tail()
        elif production == 49:
            self.literals()
        elif production == 50:
            self.not_rule()
            self.not_val()
            self.log_eq()
        else:
            self.error_invalid_token("<var-val>")

    def operands(self):
        # <operands>
        production = self.get_production("<operands>")
        if production == 51:
            self.eat("id")
            self.id_tail()
        elif production == 52:
            self.eat("(")
            self.var_val()
            self.eat(")")
        else:
            self.error_invalid_token("<operands>")

    def id_tail(self):
        # <id-tail>
        production = self.get_production("<id-tail>")
        if production == 53: self.arr_elmt()
        elif production == 54: self.str_mem()
        elif production == 55: self.func_args()
        elif production == 56: pass # Lambda
        else:
            self.error_invalid_token("<id-tail>")

    def arr_elmt(self):
        # <arr-elmt>
        production = self.get_production("<arr-elmt>")
        if production == 57:
            self.eat("{")
            self.arr_index()
            self.eat("}")
            self.arr_elmt_tail()
        else:
            self.error_invalid_token("<arr-elmt>")

    def arr_index(self):
        # <arr-index>
        production = self.get_production("<arr-index>")
        if production == 58: self.eat("id")
        elif production == 59: self.eat("COIN-lit")
        else:
            self.error_invalid_token("<arr-index>")

    def arr_elmt_tail(self):
        # <arr-elmt-tail>
        production = self.get_production("<arr-elmt-tail>")
        if production == 60:
            self.eat("{")
            self.arr_index()
            self.eat("}")
            self.arr_elmt_tail()
        elif production == 61: pass # Lambda
        else:
            self.error_invalid_token("<arr-elmt-tail>")

    def str_mem(self):
        # <str-mem>
        production = self.get_production("<str-mem>")
        if production == 62:
            self.eat("$")
            self.eat("id")
        else:
            self.error_invalid_token("<str-mem>")

    def func_args(self):
        # <func-args>
        production = self.get_production("<func-args>")
        if production == 63:
            self.eat("(")
            self.args()
            self.eat(")")
        else:
            self.error_invalid_token("<func-args>")

    def args(self):
        # <args>
        production = self.get_production("<args>")
        if production == 64: self.arr_val()
        elif production == 65: pass # Lambda
        else:
            self.error_invalid_token("<args>")

    def literals(self):
        # <literals>
        production = self.get_production("<literals>")
        if production == 66:
            self.digits()
            self.digit_tail()
        elif production == 67:
            self.bool_lit()
            self.log_eq()
        elif production == 68:
            self.scroll()
            self.scroll_tail()
        elif production == 69:
            self.eat("PARCH-lit")
            self.eq_parch()
        else:
            self.error_invalid_token("<literals>")

    def digits(self):
        # <digits>
        production = self.get_production("<digits>")
        if production == 70: self.eat("COIN-lit")
        elif production == 71: self.eat("DIME-lit")
        else:
            self.error_invalid_token("<digits>")

    def bool_lit(self):
        # <bool-lit>
        production = self.get_production("<bool-lit>")
        if production == 72: self.eat("AYE")
        elif production == 73: self.eat("NAY")
        else:
            self.error_invalid_token("<bool-lit>")
    
    def scroll(self):
        # <scroll>
        production = self.get_production("<scroll>")
        if production == 74:
            self.eat("SCROLL-lit")
            self.arr_elmt_tail()
        else:
            self.error_invalid_token("<scroll>")

    # =========================================
    # Operations & Logic
    # =========================================

    def exp_tail(self):
        # <exp-tail>
        production = self.get_production("<exp-tail>")
        if production == 75: self.arith_exp()
        elif production == 76: self.rel_exp()
        elif production == 77: self.log_exp()
        elif production == 78: self.eq_exp()
        elif production == 79: self.scroll_exp()
        elif production == 80: pass # Lambda
        else:
            self.error_invalid_token("<exp-tail>")

    def digit_tail(self):
        # <digit-tail>
        production = self.get_production("<digit-tail>")
        if production == 81: self.arith_exp()
        elif production == 82: self.rel_exp()
        elif production == 83: self.eq_arith()
        elif production == 84: pass # Lambda
        else:
            self.error_invalid_token("<digit-tail>")

    def arith_exp(self):
        # <arith-exp>
        production = self.get_production("<arith-exp>")
        if production == 85:
            self.arith()
            self.rel_eq()
        else:
            self.error_invalid_token("<arith-exp>")

    def arith(self):
        # <arith>
        production = self.get_production("<arith>")
        if production == 86:
            self.arith_op()
            self.arel_ope()
            self.arith_tail()
        else:
            self.error_invalid_token("<arith>")

    def arith_tail(self):
        # <arith-tail>
        production = self.get_production("<arith-tail>")
        if production == 87: self.arith()
        elif production == 88: pass # Lambda
        else:
            self.error_invalid_token("<arith-tail>")

    def arith_op(self):
        # <arith-op>
        production = self.get_production("<arith-op>")
        if production == 89: self.eat("+")
        elif production == 90: self.eat("-")
        elif production == 91: self.eat("*")
        elif production == 92: self.eat("/")
        elif production == 93: self.eat("%")
        elif production == 94: self.eat("^")
        else:
            self.error_invalid_token("<arith-op>")

    def arel_ope(self):
        # <arel-ope>
        production = self.get_production("<arel-ope>")
        if production == 95:
            self.eat("id")
            self.id_tail()
        elif production == 96:
            self.digits()
        elif production == 97:
            self.eat("(")
            self.arel_ope()
            self.arith()
            self.eat(")")
        else:
            self.error_invalid_token("<arel-ope>")

    def rel_exp(self):
        # <rel-exp>
        production = self.get_production("<rel-exp>")
        if production == 98:
            self.rel()
            self.log_eq()
        else:
            self.error_invalid_token("<rel-exp>")

    def rel(self):
        # <rel>
        production = self.get_production("<rel>")
        if production == 99:
            self.rel_op()
            self.arel_ope()
            self.arith_tail()
        else:
            self.error_invalid_token("<rel>")

    def rel_op(self):
        # <rel-op>
        production = self.get_production("<rel-op>")
        if production == 100: self.eat("<")
        elif production == 101: self.eat(">")
        elif production == 102: self.eat("<=")
        elif production == 103: self.eat(">=")
        else:
            self.error_invalid_token("<rel-op>")

    def rel_eq(self):
        # <rel-eq>
        production = self.get_production("<rel-eq>")
        if production == 104: self.rel_eq_exp()
        elif production == 105: pass # Lambda
        else:
            self.error_invalid_token("<rel-eq>")

    def rel_eq_exp(self):
        # <rel-eq-exp>
        production = self.get_production("<rel-eq-exp>")
        if production == 106: self.rel_exp()
        elif production == 107: self.eq_arith()
        else:
            self.error_invalid_token("<rel-eq-exp>")

    def eq_arith(self):
        # <eq-arith>
        production = self.get_production("<eq-arith>")
        if production == 108:
            self.eq_op()
            self.arel_ope()
            self.arith_tail()
            self.log_exp()
        else:
            self.error_invalid_token("<eq-arith>")

    def eq_op(self):
        # <eq-op>
        production = self.get_production("<eq-op>")
        if production == 109: self.eat("==")
        elif production == 110: self.eat("!=")
        else:
            self.error_invalid_token("<eq-op>")

    def log_eq(self):
        # <log-eq>
        production = self.get_production("<log-eq>")
        if production == 111: self.log_exp()
        elif production == 112: self.eq_exp()
        elif production == 113: pass # Lambda
        else:
            self.error_invalid_token("<log-eq>")

    def log_exp(self):
        # <log-exp>
        production = self.get_production("<log-exp>")
        if production == 114:
            self.log_op()
            self.log_ope()
        elif production == 115: pass # Lambda
        else:
            self.error_invalid_token("<log-exp>")

    def log_op(self):
        # <log-op>
        production = self.get_production("<log-op>")
        if production == 116: self.eat("||")
        elif production == 117: self.eat("&&")
        else:
            self.error_invalid_token("<log-op>")

    def log_ope(self):
        # <log-ope>
        production = self.get_production("<log-ope>")
        if production == 118:
            self.operands()
            self.exp_tail()
        elif production == 119:
            self.digits()
            self.arith_tail()
            self.rel_eq_exp()
        elif production == 120:
            self.eat("PARCH-lit")
            self.eq_op()
            self.eat("PARCH-lit")
            self.log_exp()
        elif production == 121:
            self.scroll()
            self.concat_tail()
            self.eq_op()
            self.scroll_ope()
            self.concat_tail()
            self.log_exp()
        elif production == 122:
            self.bool_lit()
            self.log_eq()
        elif production == 123: # NEW PRODUCTION (Prods 123-240 shifted to 124-241)
            self.not_rule()
            self.not_val()
            self.log_eq()
        else:
            self.error_invalid_token("<log-ope>")

    def eq_exp(self):
        # <eq-exp>
        production = self.get_production("<eq-exp>")
        if production == 124: # SHIFTED 123 -> 124
            self.eq_op()
            self.var_val()
        else:
            self.error_invalid_token("<eq-exp>")

    def not_rule(self):
        # <not>
        production = self.get_production("<not>")
        if production == 125: self.eat("!") # SHIFTED 124 -> 125
        elif production == 126: self.eat("!#") # SHIFTED 125 -> 126
        else:
            self.error_invalid_token("<not>")

    def not_val(self):
        # <not-val>
        production = self.get_production("<not-val>")
        if production == 127: # SHIFTED 126 -> 127
            self.eat("id")
            self.id_tail()
        elif production == 128: self.bool_lit() # SHIFTED 127 -> 128
        elif production == 129: # SHIFTED 128 -> 129
            self.eat("(")
            self.log_ope()
            self.eat(")")
        else:
            self.error_invalid_token("<not-val>")

    def scroll_tail(self):
        # <scroll-tail>
        production = self.get_production("<scroll-tail>")
        if production == 130: self.scroll_exp() # SHIFTED 129 -> 130
        elif production == 131: self.eq_scroll() # SHIFTED 130 -> 131
        elif production == 132: pass # Lambda # SHIFTED 131 -> 132
        else:
            self.error_invalid_token("<scroll-tail>")

    def scroll_exp(self):
        # <scroll-exp>
        production = self.get_production("<scroll-exp>")
        if production == 133: # SHIFTED 132 -> 133
            self.concat()
            self.eq_scroll()
        else:
            self.error_invalid_token("<scroll-exp>")

    def concat(self):
        # <concat>
        production = self.get_production("<concat>")
        if production == 134: # SHIFTED 133 -> 134
            self.eat("&")
            self.scroll_ope()
            self.concat_tail()
        else:
            self.error_invalid_token("<concat>")

    def concat_tail(self):
        # <concat-tail>
        production = self.get_production("<concat-tail>")
        if production == 135: self.concat() # SHIFTED 134 -> 135
        elif production == 136: pass # Lambda # SHIFTED 135 -> 136
        else:
            self.error_invalid_token("<concat-tail>")

    def scroll_ope(self):
        # <scroll-ope>
        production = self.get_production("<scroll-ope>")
        if production == 137: self.scroll() # SHIFTED 136 -> 137
        elif production == 138: # SHIFTED 137 -> 138
            self.eat("id")
            self.id_tail()
        elif production == 139: # SHIFTED 138 -> 139
            self.eat("(")
            self.scroll_ope()
            self.concat()
            self.eat(")")
        else:
            self.error_invalid_token("<scroll-ope>")

    def eq_scroll(self):
        # <eq-scroll>
        production = self.get_production("<eq-scroll>")
        if production == 140: # SHIFTED 139 -> 140
            self.eq_op()
            self.scroll_ope()
            self.concat_tail()
            self.log_exp()
        elif production == 141: pass # Lambda # SHIFTED 140 -> 141
        else:
            self.error_invalid_token("<eq-scroll>")

    def eq_parch(self):
        # <eq-parch>
        production = self.get_production("<eq-parch>")
        if production == 142: # SHIFTED 141 -> 142
            self.eq_op()
            self.eat("PARCH-lit")
            self.log_exp()
        elif production == 143: pass # Lambda # SHIFTED 142 -> 143
        else:
            self.error_invalid_token("<eq-parch>")

    # =========================================
    # Functions
    # =========================================

    def sub_func(self):
        # <sub-func>
        production = self.get_production("<sub-func>")
        if production == 144: # SHIFTED 143 -> 144
            self.d_type()
            self.eat("id")
            self.return_func()
        elif production == 145: # SHIFTED 144 -> 145
            self.nonreturn_func()
            self.sub_func()
        elif production == 146: pass # Lambda # SHIFTED 145 -> 146
        else:
            self.error_invalid_token("<sub-func>")

    def return_func(self):
        # <return-func>
        production = self.get_production("<return-func>")
        if production == 147: # SHIFTED 146 -> 147
            self.eat("(")
            self.func_parameters()
            self.eat(")")
            self.eat("[")
            self.local_dec()
            self.stmnt_tail()
            self.eat("BACK")
            self.var_val()
            self.eat("!!")
            self.eat("]")
        else:
            self.error_invalid_token("<return-func>")

    def func_parameters(self):
        # <func-parameters>
        production = self.get_production("<func-params>")
        if production == 148: # SHIFTED 147 -> 148
            self.d_type()
            self.eat("id")
            self.func_tail()
        elif production == 149: pass # Lambda # SHIFTED 148 -> 149
        else:
            self.error_invalid_token("<func-params>")

    def func_tail(self):
        # <func-tail>
        production = self.get_production("<func-tail>")
        if production == 150: # SHIFTED 149 -> 150
            self.eat(",")
            self.func_parameters()
        elif production == 151: pass # Lambda # SHIFTED 150 -> 151
        else:
            self.error_invalid_token("<func-tail>")

    def nonreturn_func(self):
        # <nonreturn-func>
        production = self.get_production("<nonreturn-func>")
        if production == 152: # SHIFTED 151 -> 152
            self.eat("ABYSS")
            self.eat("id")
            self.eat("(")
            self.func_parameters()
            self.eat(")")
            self.eat("[")
            self.local_dec()
            self.statements()
            self.nonreturn_back()
            self.eat("]")
            self.sub_func()
        else:
            self.error_invalid_token("<nonreturn-func>")

    def nonreturn_back(self):
        # <nonreturn-back>
        production = self.get_production("<nonreturn-back>")
        if production == 153: # SHIFTED 152 -> 153
            self.eat("BACK")
            self.eat("!!")
        elif production == 154: pass # Lambda # SHIFTED 153 -> 154
        else:
            self.error_invalid_token("<nonreturn-back>")

    def local_dec(self):
        # <local-dec>
        production = self.get_production("<local-dec>")
        if production == 155: # SHIFTED 154 -> 155
            self.d_type()
            self.eat("id")
            self.var_arr_dec()
            self.local_dec()
        elif production == 156: # SHIFTED 155 -> 156
            self.struct()
        elif production == 157: # SHIFTED 156 -> 157
            pass # Lambda
        else:
            self.error_invalid_token("<local-dec>")

    def struct(self):
        # <struct>
        production = self.get_production("<struct>")
        if production == 158: # SHIFTED 157 -> 158
            self.str_dec()
            self.struct()
        elif production == 159: pass # Lambda # SHIFTED 158 -> 159
        else:
            self.error_invalid_token("<struct>")

    def str_dec(self):
        # <str-dec>
        production = self.get_production("<str-dec>")
        if production == 160: # SHIFTED 159 -> 160
            self.eat("MAST")
            self.eat("id")
            self.eat("id")
            self.str_dec_init()
            self.eat("!!")
        else:
            self.error_invalid_token("<str-dec>")

    def str_dec_init(self):
        # <str-dec-init>
        production = self.get_production("<str-dec-init>")
        if production == 161: # SHIFTED 160 -> 161
            # FIX: Do not eat("id") here. Just call the tail to handle ", id"
            self.str_dec_tail()
        elif production == 162: # SHIFTED 161 -> 162
            self.eat("=")
            self.eat("[")
            self.str_val()
            self.str_val_tail()
            self.eat("]")
        elif production == 163: pass # Lambda # SHIFTED 162 -> 163
        else:
            self.error_invalid_token("<str-dec-init>")

    def str_dec_tail(self):
        # <str-dec-tail>
        production = self.get_production("<str-dec-tail>")
        if production == 164: # SHIFTED 163 -> 164
            # FIX: Eat the comma, then the ID, then recurse
            self.eat(",") 
            self.eat("id")
            self.str_dec_tail()
        elif production == 165: pass # Lambda # SHIFTED 164 -> 165
        else:
            self.error_invalid_token("<str-dec-tail>")

    def str_val(self):
        # <str-val>
        production = self.get_production("<str-val>")
        if production == 166: # SHIFTED 165 -> 166
            self.var_val()
        elif production == 167: # SHIFTED 166 -> 167
            self.eat("$")
            self.eat("id")
            self.eat("=")
            self.var_val()
        else:
            self.error_invalid_token("<str-val>")

    def str_val_tail(self):
        # <str-val-tail>
        production = self.get_production("<str-val-tail>")
        if production == 168: # SHIFTED 167 -> 168
            # FIX: Must consume the comma that triggered this rule!
            self.eat(",")       
            self.str_val()
            # FIX: Must recurse to allow lists like ["a", "b", "c"]
            self.str_val_tail() 
        elif production == 169: pass # Lambda # SHIFTED 168 -> 169
        else:
            self.error_invalid_token("<str-val-tail>")

    # =========================================
    # Statements
    # =========================================

    def statements(self):
        # <statements>
        production = self.get_production("<statements>")
        if production == 170: # SHIFTED 169 -> 170
            self.assign_stmnt()
            self.stmnt_tail()
        elif production == 171: # SHIFTED 170 -> 171
            self.ask_stmnt()
            self.stmnt_tail()
        elif production == 172: # SHIFTED 171 -> 172
            self.echo_stmnt()
            self.stmnt_tail()
        elif production == 173: # SHIFTED 172 -> 173
            self.look_stmnt()
            self.stmnt_tail()
        elif production == 174: # SHIFTED 173 -> 174
            self.chart_stmnt()
            self.stmnt_tail()
        elif production == 175: # SHIFTED 174 -> 175
            self.hoist_stmnt()
            self.stmnt_tail()
        elif production == 176: # SHIFTED 175 -> 176
            self.heave_stmnt()
            self.stmnt_tail()
        elif production == 177: # SHIFTED 176 -> 177
            self.haul_stmnt()
            self.stmnt_tail()
        elif production == 178: # SHIFTED 177 -> 178
            self.unary_exp()
            self.eat("!!")
            self.stmnt_tail()
        else:
            self.error_invalid_token("<statements>")

    def stmnt_tail(self):
        # <stmnt-tail>
        production = self.get_production("<stmnt-tail>")
        if production == 179: # SHIFTED 178 -> 179
            # UPDATED: Rule is <stmnt-tail> -> <statements>
            self.statements() 
        elif production == 180: pass # Lambda # SHIFTED 179 -> 180
        else:
            self.error_invalid_token("<stmnt-tail>")

    def assign_stmnt(self):
        # <assign-stmnt>
        production = self.get_production("<assign-stmnt>")
        if production == 181: # SHIFTED 180 -> 181
            self.eat("id")
            self.assign_tail()
            self.eat("!!")
        else:
            self.error_invalid_token("<assign-stmnt>")

    def assign_tail(self):
        # <assign-tail>
        production = self.get_production("<assign-tail>")
        if production == 182: # SHIFTED 181 -> 182
            self.arr_str()
            self.assign_body()
        elif production == 183: # SHIFTED 182 -> 183
            self.func_args()
        else:
            self.error_invalid_token("<assign-tail>")

    def arr_str(self):
        # <arr-str>
        production = self.get_production("<arr-str>")
        if production == 184: self.arr_elmt() # SHIFTED 183 -> 184
        elif production == 185: self.str_mem() # SHIFTED 184 -> 185
        elif production == 186: pass # Lambda # SHIFTED 185 -> 186
        else:
            self.error_invalid_token("<arr-str>")

    def assign_body(self):
        # <assign-body>
        production = self.get_production("<assign-body>")
        if production == 187: # SHIFTED 186 -> 187
            # FIX: You must consume the "=" token here!
            self.eat("=") 
            self.assign_val()
        elif production == 188: # SHIFTED 187 -> 188
            self.arith_assign_op()
            self.arel_ope()
            self.arith_tail()
        else:
            self.error_invalid_token("<assign-body>")

    def assign_val(self):
        # <assign-val>
        production = self.get_production("<assign-val>")
        if production == 189: self.var_val() # SHIFTED 188 -> 189
        elif production == 190: # SHIFTED 189 -> 190
            self.eat("[")
            self.arr_assign()
            self.eat("]")
        else:
            self.error_invalid_token("<assign-val>")

    def arr_assign(self):
        # <arr-assign>
        production = self.get_production("<arr-assign>")
        if production == 191: self.arr_val() # SHIFTED 190 -> 191
        elif production == 192: self.arr2_val() # SHIFTED 191 -> 192
        else:
            self.error_invalid_token("<arr-assign>")

    def arith_assign_op(self):
        # <arith-assign-op>
        production = self.get_production("<arith-assign-op>")
        if production == 193: self.eat("+=") # SHIFTED 192 -> 193
        elif production == 194: self.eat("-=") # SHIFTED 193 -> 194
        elif production == 195: self.eat("*=") # SHIFTED 194 -> 195
        elif production == 196: self.eat("/=") # SHIFTED 195 -> 196
        elif production == 197: self.eat("%=") # SHIFTED 196 -> 197
        elif production == 198: self.eat("^=") # SHIFTED 197 -> 198
        else:
            self.error_invalid_token("<arith-assign-op>")

    def ask_stmnt(self):
        # <ask-stmnt>
        production = self.get_production("<ask-stmnt>")
        if production == 199: # SHIFTED 198 -> 199
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
        production = self.get_production("<addr>")
        if production == 200: # SHIFTED 199 -> 200
            self.eat("@")
            self.eat("id")
            self.arr_str()
            self.addr_tail()
        else:
            self.error_invalid_token("<addr>")

    def addr_tail(self):
        # <addr-tail>
        production = self.get_production("<addr-tail>")
        if production == 201: # SHIFTED 200 -> 201
            self.eat(",")
            self.eat("@")
            self.eat("id")
            self.arr_str()
            self.addr_tail()
        elif production == 202: pass # Lambda # SHIFTED 201 -> 202
        else:
            self.error_invalid_token("<addr-tail>")

    def echo_stmnt(self):
        # <echo-stmnt>
        production = self.get_production("<echo-stmnt>")
        if production == 203: # SHIFTED 202 -> 203
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
        production = self.get_production("<echo-arg>")
        if production == 204: # SHIFTED 203 -> 204
            self.eat(",")
            self.var_val()
            self.echo_arg()
        elif production == 205: pass # Lambda # SHIFTED 204 -> 205
        else:
            self.error_invalid_token("<echo-arg>")

    def look_stmnt(self):
        # <look-stmnt>
        production = self.get_production("<look-stmnt>")
        if production == 206: # SHIFTED 205 -> 206
            self.eat("LOOK")
            self.eat("(")
            self.cond_exp()
            self.eat(")")
            self.eat("[")
            self.stmnt_tail() 
            self.jump_stmnt()
            self.eat("]")
            self.look_tail()
        else:
            self.error_invalid_token("<look-stmnt>")

    def cond_exp(self):
        # <cond-exp>
        production = self.get_production("<cond-exp>")
        if production == 207: # SHIFTED 206 -> 207
            self.log_ope()
        else:
            self.error_invalid_token("<cond-exp>")

    def jump_stmnt(self):
        # <jump-stmnt>
        production = self.get_production("<jump-stmnt>")
        if production == 208: # SHIFTED 207 -> 208
            self.eat("SAIL")
            self.eat("!!")
        elif production == 209: # SHIFTED 208 -> 209
            self.eat("LAND")
            self.eat("!!")
        elif production == 210: pass # Lambda # SHIFTED 209 -> 210
        else:
            self.error_invalid_token("<jump-stmnt>")

    def look_tail(self):
        # <look-tail>
        production = self.get_production("<look-tail>")
        if production == 211: # SHIFTED 210 -> 211
            self.eat("DROPLOOK")
            self.eat("(")
            self.cond_exp()
            self.eat(")")
            self.eat("[")
            self.stmnt_tail() 
            self.jump_stmnt()
            self.eat("]")
            self.look_tail()
        elif production == 212: # SHIFTED 211 -> 212
            self.eat("DROP")
            self.eat("[")
            self.stmnt_tail()
            self.jump_stmnt()
            self.eat("]")
        elif production == 213: pass # Lambda # SHIFTED 212 -> 213
        else:
            self.error_invalid_token("<look-tail>")

    def chart_stmnt(self):
        # <chart-stmnt>
        production = self.get_production("<chart-stmnt>")
        if production == 214: # SHIFTED 213 -> 214
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
        production = self.get_production("<chart-cond>")
        if production == 215: self.const() # SHIFTED 214 -> 215
        elif production == 216: self.eat("id") # SHIFTED 215 -> 216
        else:
            self.error_invalid_token("<chart-cond>")

    def const(self):
        # <const>
        production = self.get_production("<const>")
        if production == 217: self.eat("COIN-lit") # SHIFTED 216 -> 217
        elif production == 218: self.eat("PARCH-lit") # SHIFTED 217 -> 218
        else:
            self.error_invalid_token("<const>")

    def courses(self):
        # <courses>
        production = self.get_production("<courses>")
        if production == 219: # SHIFTED 218 -> 219
            self.eat("COURSE")
            self.const()
            self.eat(":")
            self.stmnt_tail() 
            self.jump_stmnt()
        else:
            self.error_invalid_token("<courses>")

    def course_tail(self):
        # <course-tail>
        production = self.get_production("<course-tail>")
        if production == 220: # SHIFTED 219 -> 220
            # UPDATED: Rule is <course-tail> -> <courses> <course-tail>
            self.courses()
            self.course_tail() # Added recursive call
        elif production == 221: pass # Lambda # SHIFTED 220 -> 221
        else:
            self.error_invalid_token("<course-tail>")

    def adrift_case(self):
        # <adrift-case>
        production = self.get_production("<adrift-case>")
        if production == 222: # SHIFTED 221 -> 222
            self.eat("ADRIFT")
            self.eat(":")
            self.stmnt_tail() 
            self.eat("LAND")
            self.eat("!!")
        elif production == 223: pass # Lambda # SHIFTED 222 -> 223
        else:
            self.error_invalid_token("<adrift-case>")

    def hoist_stmnt(self):
        # <hoist-stmnt>
        production = self.get_production("<hoist-stmnt>")
        if production == 224: # SHIFTED 223 -> 224
            self.eat("HOIST")
            self.eat("(")
            self.init()
            self.eat("!!")
            self.cond_exp()
            self.eat("!!")
            self.inc_dec()
            self.eat(")")
            self.eat("[")
            self.stmnt_tail()
            self.jump_stmnt()
            self.eat("]")
        else:
            self.error_invalid_token("<hoist-stmnt>")

    def init(self):
        # <init>
        production = self.get_production("<init>")
        if production == 225: # SHIFTED 224 -> 225
            self.d_type()
            self.eat("id")
            self.eat("=")
            self.var_val()
            self.init1()
        elif production == 226: # SHIFTED 225 -> 226
            self.eat("id")
            self.arr_str()
            self.eat("=")
            self.var_val()
            self.init2()
        elif production == 227: pass # Lambda # SHIFTED 226 -> 227
        else:
            self.error_invalid_token("<init>")

    def init1(self):
        # <init1>
        production = self.get_production("<init1>")
        if production == 228: # SHIFTED 227 -> 228
            self.eat(",")
            self.eat("id")
            self.eat("=")
            self.var_val()
            self.init1()
        elif production == 229: pass # Lambda # SHIFTED 228 -> 229
        else:
            self.error_invalid_token("<init1>")

    def init2(self):
        # <init2>
        production = self.get_production("<init2>")
        if production == 230: # SHIFTED 229 -> 230
            self.eat(",")
            self.eat("id")
            self.arr_str()
            self.eat("=")
            self.var_val()
            self.init2()
        elif production == 231: pass # Lambda # SHIFTED 230 -> 231
        else:
            self.error_invalid_token("<init2>")
    
    def inc_dec(self):
        # <inc-dec>
        production = self.get_production("<inc-dec>")
        if production == 232: # SHIFTED 231 -> 232
            self.in_de()
            self.in_de2()
        else:
            self.error_invalid_token("<inc-dec>")

    def in_de(self):
        # <in-de>
        production = self.get_production("<in-de>")
        if production == 233: # SHIFTED 232 -> 233
            self.unary_exp()
        elif production == 234: # SHIFTED 233 -> 234
            self.eat("id")
            self.arr_str()
            self.arith_assign_op()
            self.arel_ope()
            self.arith_tail()
        else:
            self.error_invalid_token("<in-de>")

    def in_de2(self):
        # <in-de2>
        production = self.get_production("<in-de2>")
        if production == 235: # SHIFTED 234 -> 235
            self.eat(",")
            self.in_de()
        elif production == 236: pass # Lambda # SHIFTED 235 -> 236
        else:
            self.error_invalid_token("<in-de2>")

    def heave_stmnt(self):
        # <heave-stmnt>
        production = self.get_production("<heave-stmnt>")
        if production == 237: # SHIFTED 236 -> 237
            self.eat("HEAVE")
            self.eat("(")
            self.cond_exp()
            self.eat(")")
            self.eat("[")
            self.stmnt_tail() 
            self.jump_stmnt()
            self.eat("]")
        else:
            self.error_invalid_token("<heave-stmnt>")

    def haul_stmnt(self):
        # <haul-stmnt>
        production = self.get_production("<haul-stmnt>")
        if production == 238: # SHIFTED 237 -> 238
            self.eat("HAUL")
            self.eat("[")
            self.stmnt_tail()
            self.jump_stmnt()
            self.eat("]")
            self.eat("HEAVE")
            self.eat("(")
            self.cond_exp()
            self.eat(")")
            self.eat("!!")
        else:
            self.error_invalid_token("<haul-stmnt>")

    def unary_exp(self):
        # <unary-exp>
        production = self.get_production("<unary-exp>")
        if production == 239: # SHIFTED 238 -> 239
            self.unary_op() 
            self.eat("id")
        else:
            self.error_invalid_token("<unary-exp>")

    def unary_op(self):
        # <unary-op>
        production = self.get_production("<unary-op>")
        if production == 240: self.eat("+#") # SHIFTED 239 -> 240
        elif production == 241: self.eat("-#") # SHIFTED 240 -> 241
        else:
            self.error_invalid_token("<unary-op>")