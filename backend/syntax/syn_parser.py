import sys
# Ensure these filenames match exactly what you created
from syntax.First_Set import FIRST
from syntax.Predict_Set import PREDICT
from syntax.Follow_Set import FOLLOW

class Parser:
    def __init__(self, tokens):
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
        for t in self.tokens:
            if t.type.startswith("id") and t.type[2:].isdigit():
                t.type = "id"
        
        # Initialize state
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.errors = []
        # Removed self.logs as we are now returning raw error objects

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
        Strictly enforces matching; otherwise raises an error.
        """
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            self.error(expected=[token_type])

    def error(self, message=None, expected=None, found=None):
    # Raises a structured error dictionary.
        # Determine Location
        if self.current_token:
            line = self.current_token.line
            col = self.current_token.col
            found_str = found if found else self.current_token.type
        else:
            line = "?"
            col = "?"
            found_str = "EOF"

        # Format Expected Tokens
        clean_expected = []
        if expected:
            clean_expected = sorted([str(t) for t in expected if t is not None])

        # If no custom message is passed, generate one intelligently
        if message is None:
            if found_str == "EOF":
                # Specific check: If we hit EOF but were expecting "AHOY" (among others)
                if "AHOY" in clean_expected:
                    message = "Unexpected End of File.\nThe program is missing the required 'AHOY' function at the end."
                else:
                    message = f"Unexpected End of File.\nExpected any: {', '.join(clean_expected)}"
            else:
                # Generic syntax error for non-EOF tokens
                message = f"Unexpected token '{found_str}'."
        
        # Create Structured Error Object
        error_data = {
            "line": line,
            "col": col,
            "found": found_str,
            "expected": clean_expected,
            "message": message if message else "Unknown Error. This is for unseened errors by the program."
        }
        
        # Stop execution by raising the dict
        raise Exception(error_data)

    def validate_token(self, non_terminal):
    # Uses FIRST_SET to check if the current token is valid for this Non-Terminal.
        if not self.current_token:
            return False
            
        allowed_tokens = FIRST.get(non_terminal, [])
        if self.current_token.type in allowed_tokens:
            return True
        return False

    def get_production(self, non_terminal):
    # Uses PREDICT_SET to return the Production Number based on current token.
        if not self.current_token:
            return None
            
        productions = PREDICT.get(non_terminal, {})
        return productions.get(self.current_token.type)



    # =========================================
    # Entry Point
    # =========================================
    def parse(self):
        try:
            if not self.tokens:
                raise Exception({
                    "line": 0, "col": 0, "found": "EMPTY", "expected": [], 
                    "message": "Empty program."
                })

            self.program()
            
            if self.current_token is not None:
                self.error(
                    message=f"Unexpected token after end of program",
                    found=self.current_token.type
                )
                
        except Exception as e:
            # Catch the dictionary raised by self.error()
            if e.args and isinstance(e.args[0], dict):
                self.errors.append(e.args[0])
            else:
                # Fallback for generic Python crashes
                self.errors.append({
                    "line": "?",
                    "col": "?",
                    "found": "CRASH",
                    "expected": [],
                    "message": str(e)
                })

        return self.errors

    # =========================================
    # Program Structure & Declarations
    # =========================================
    
    def program(self):
        # <program>
        production = self.get_production("<program>")
        if production == 1:
            self.global_dec()
            self.eat("AHOY")
            self.eat("(")
            self.eat(")")
            self.eat("[")
            self.local_dec()
            self.statements()
            self.eat("]")
        else:
            self.error(expected=list(PREDICT["<program>"].keys()))

    def global_dec(self):
        # <global-dec>
        production = self.get_production("<global-dec>")
        if production == 2:
            self.d_type()
            self.eat("id")
            self.dtype_tail()
        elif production == 3:
            self.locke_dec()
            self.global_dec()
        elif production == 4:
            self.struct_def()
        elif production == 5:
            self.nonreturn_func()
            self.sub_func()
        elif production == 6:
            pass # Lambda (Epsilon)
        else:
            self.error(expected=list(PREDICT["<global-dec>"].keys()))

    def d_type(self):
        # <d-type>
        production = self.get_production("<d-type>")
        if production == 7: self.eat("COIN")
        elif production == 8: self.eat("DIME")
        elif production == 9: self.eat("PARCH")
        elif production == 10: self.eat("SCROLL")
        elif production == 11: self.eat("BOOL")
        else:
            self.error(expected=list(PREDICT["<d-type>"].keys()))

    def dtype_tail(self):
        # <dtype-tail>
        production = self.get_production("<dtype-tail>")
        if production == 12:
            self.var_arr_dec()
            self.global_dec()
        elif production == 13:
            self.return_func()
            self.sub_func()
        else:
            self.error(expected=list(PREDICT["<dtype-tail>"].keys()))

    def var_arr_dec(self):
        # <var-arr-dec>
        production = self.get_production("<var-arr-dec>")
        if production == 14: self.variable()
        elif production == 15: self.array()
        else:
            self.error(expected=list(PREDICT["<var-arr-dec>"].keys()))

    def variable(self):
        # <variable>
        production = self.get_production("<variable>")
        if production == 16:
            self.var_init()
            self.multi_var_init()
            self.eat("!!")
        else:
            self.error(expected=list(PREDICT["<variable>"].keys()))

    def var_init(self):
        # <var-init>
        production = self.get_production("<var-init>")
        if production == 17:
            self.eat("=")
            self.var_val()
        elif production == 18:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<var-init>"].keys()))

    def multi_var_init(self):
        # <multi-var-init>
        production = self.get_production("<multi-var-init>")
        if production == 19:
            self.eat(",")
            self.eat("id")
            self.var_init()
            self.multi_var_init()
        elif production == 20:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<multi-var-init>"].keys()))

    def array(self):
        # <array>
        production = self.get_production("<array>")
        if production == 21:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.arr_tail()
            self.eat("!!")
        else:
            self.error(expected=list(PREDICT["<array>"].keys()))

    def arr_tail(self):
        # <arr-tail>
        production = self.get_production("<arr-tail>")
        if production == 22:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.arr2_tail()
        elif production == 23:
            self.eat("=")
            self.eat("[")
            self.arr_val()
            self.eat("]")
        elif production == 24:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<arr-tail>"].keys()))

    def arr2_tail(self):
        # <arr2-tail>
        production = self.get_production("<arr2-tail>")
        if production == 28:
            self.eat("=")
            self.eat("[")
            self.arr2_val()
            self.eat("]")
        elif production == 29:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<arr2-tail>"].keys()))
            
    def arr_val(self):
        # <arr-val>
        production = self.get_production("<arr-val>")
        if production == 25:
            self.var_val()
            self.arr_val_tail()
        else:
            self.error(expected=list(PREDICT["<arr-val>"].keys()))
    
    def arr_val_tail(self):
        # <arr-val-tail>
        production = self.get_production("<arr-val-tail>")
        if production == 26:
            self.eat(",")
            self.var_val()
            self.arr_val_tail()
        elif production == 27:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<arr-val-tail>"].keys()))

    def arr2_val(self):
        # <arr2-val>
        production = self.get_production("<arr2-val>")
        if production == 30:
            self.eat("[")
            self.arr_val()
            self.eat("]")
            self.arr2_val_tail()
        else:
            self.error(expected=list(PREDICT["<arr2-val>"].keys()))

    def arr2_val_tail(self):
        # <arr2-val-tail>
        production = self.get_production("<arr2-val-tail>")
        if production == 31:
            self.eat(",")
            self.arr2_val()
            self.arr2_val_tail()
        elif production == 32:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<arr2-val-tail>"].keys()))

    def locke_dec(self):
        # <locke-dec>
        production = self.get_production("<locke-dec>")
        if production == 33:
            self.eat("LOCKE")
            self.d_type()
            self.eat("id")
            self.eat("=")
            self.literals()
            self.eat("!!")
        else:
            self.error(expected=list(PREDICT["<locke-dec>"].keys()))

    def struct_def(self):
        # <struct-def>
        production = self.get_production("<struct-def>")
        if production == 34:
            self.eat("MAST")
            self.eat("id")
            self.eat("[")
            self.mem_dec()
            self.more_mem()
            self.eat("]")
            self.eat("!!")
            self.struct_def()
            self.sub_func()
        elif production == 35:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<struct-def>"].keys()))

    def mem_dec(self):
        # <mem-dec>
        production = self.get_production("<mem-dec>")
        if production == 36:
            self.d_type()
            self.eat("id")
            self.mem_dec_tail()
            self.eat("!!")
        else:
            self.error(expected=list(PREDICT["<mem-dec>"].keys()))
            
    def mem_dec_tail(self):
        # <mem-dec-tail>
        production = self.get_production("<mem-dec-tail>")
        if production == 37:
            self.eat(",")
            self.eat("id")
            self.mem_dec_tail()
        elif production == 38:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<mem-dec-tail>"].keys()))
            
    def more_mem(self):
        # <more-mem>
        production = self.get_production("<more-mem>")
        if production == 39:
            self.mem_dec()
            self.more_mem() 
        elif production == 40:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<more-mem>"].keys()))

    def var_val(self):
        # <var-val>
        production = self.get_production("<var-val>")
        if production == 41:
            self.expression()
        else:
            self.error(expected=list(PREDICT["<var-val>"].keys()))
        
    def expression(self):
        # <expression>
        production = self.get_production("<expression>")
        if production == 42:
            self.operands()
            self.exp_tail()
        else:
            self.error(expected=list(PREDICT["<expression>"].keys()))

    def operands(self):
        # <operands>
        production = self.get_production("<operands>")
        if production == 43:
            self.value()
        elif production == 44:
            self.eat("(")
            self.expression()
            self.eat(")")
        elif production == 45:
            self.not_rule()
            self.not_val()
        else:
             self.error(expected=list(PREDICT["<operands>"].keys()))

    def value(self):
        # <value>
        production = self.get_production("<value>")
        if production == 46:
            self.eat("id")
            self.id_tail()
        elif production == 47:
            self.literals()
        else:
             self.error(expected=list(PREDICT["<value>"].keys()))

    def id_tail(self):
        # <id-tail>
        production = self.get_production("<id-tail>")
        if production == 48:
            self.arr_elmt()
        elif production == 49:
            self.str_mem()
        elif production == 50:
            self.func_args()
        elif production == 51:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<id-tail>"].keys()))

    def arr_elmt(self):
        # <arr-elmt>
        production = self.get_production("<arr-elmt>")
        if production == 52:
            self.eat("{")
            self.arr_index()
            self.eat("}")
            self.arr_elmt_tail()
        else:
            self.error(expected=list(PREDICT["<arr-elmt>"].keys()))
            
    def arr_index(self):
        # <arr-index>
        production = self.get_production("<arr-index>")
        if production == 53: self.eat("COIN-lit")
        elif production == 54: self.eat("id")
        else: self.error(expected=list(PREDICT["<arr-index>"].keys()))

    def arr_elmt_tail(self):
        # <arr-elmt-tail>
        production = self.get_production("<arr-elmt-tail>")
        if production == 55:
            self.eat("{")
            self.arr_index()
            self.eat("}")
        elif production == 56:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<arr-elmt-tail>"].keys()))

    def str_mem(self):
        # <str-mem>
        production = self.get_production("<str-mem>")
        if production == 57:
            self.eat("$")
            self.eat("id")
        else:
            self.error(expected=list(PREDICT["<str-mem>"].keys()))

    def func_args(self):
        # <func-args>
        production = self.get_production("<func-args>")
        if production == 58:
            self.eat("(")
            self.args()
            self.eat(")")
        elif production == 59:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<func-args>"].keys()))

    def args(self):
        # <args>
        production = self.get_production("<args>")
        if production == 60:
            self.value()
            self.args_tail()
        elif production == 61:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<args>"].keys()))

    def args_tail(self):
        # <args-tail>
        production = self.get_production("<args-tail>")
        if production == 62:
            self.eat(",")
            self.value()
            self.args_tail()
        elif production == 63:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<args-tail>"].keys()))
            
    def literals(self):
        # <literals>
        production = self.get_production("<literals>")
        if production == 64: self.digits()
        elif production == 65: self.bool_lit()
        elif production == 66: self.eat("PARCH-lit")
        elif production == 67: 
            self.eat("SCROLL-lit")
            self.arr_elmt_tail()
        else:
            self.error(expected=list(PREDICT["<literals>"].keys()))

    def digits(self):
        # <digits>
        production = self.get_production("<digits>")
        if production == 68:
            self.neg()
            self.coin_dime()
        else:
            self.error(expected=list(PREDICT["<digits>"].keys()))

    def neg(self):
        # <neg>
        production = self.get_production("<neg>")
        if production == 69: self.eat("-")
        elif production == 70: pass # Lambda (Positive)
        else:
            self.error(expected=list(PREDICT["<neg>"].keys()))

    def coin_dime(self):
        # <coin-dime>
        production = self.get_production("<coin-dime>")
        if production == 71: self.eat("COIN-lit")
        elif production == 72: self.eat("DIME-lit")
        else:
            self.error(expected=list(PREDICT["<coin-dime>"].keys()))
        
    def bool_lit(self):
        # <bool-lit>
        production = self.get_production("<bool-lit>")
        if production == 73: self.eat("AYE")
        elif production == 74: self.eat("NAY")
        else:
            self.error(expected=list(PREDICT["<bool-lit>"].keys()))

    def exp_tail(self):
        # <exp-tail>
        production = self.get_production("<exp-tail>")
        if production == 78: self.gen_exp()
        elif production == 79: self.scroll()
        elif production == 80: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<exp-tail>"].keys()))

    def gen_exp(self):
        # <gen-exp>
        production = self.get_production("<gen-exp>")
        if production == 81:
            self.arith()
            self.rel()
            self.logeq()
        elif production == 82: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<gen-exp>"].keys()))

    def arith(self):
        # <arith>
        production = self.get_production("<arith>")
        if production == 83: self.arith_exp()
        elif production == 84: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<arith>"].keys()))

    def arith_exp(self):
        # <arith-exp>
        production = self.get_production("<arith-exp>")
        if production == 85:
            self.arith_op()
            self.gen_ope()
            self.arith()
        else:
            self.error(expected=list(PREDICT["<arith-exp>"].keys()))

    def arith_op(self):
        # <arith-op>
        production = self.get_production("<arith-op>")
        if production == 86: self.eat("+")
        elif production == 87: self.eat("-")
        elif production == 88: self.eat("*")
        elif production == 89: self.eat("/")
        elif production == 90: self.eat("%")
        elif production == 91: self.eat("^")
        else:
            self.error(expected=list(PREDICT["<arith-op>"].keys()))

    def gen_ope(self):
        # <gen-ope>
        production = self.get_production("<gen-ope>")
        if production == 92:
            self.eat("id")
            self.id_tail()
        elif production == 93:
            self.digits()
        elif production == 94:
            self.bool_rule()
        elif production == 95:
            self.eat("(")
            self.gen_ope() 
            self.gen_exp()
            self.eat(")")
        else:
            self.error(expected=list(PREDICT["<gen-ope>"].keys()))

    def bool_rule(self):
        # <bool>
        production = self.get_production("<bool>")
        if production == 96:
            self.bool_lit()
        elif production == 97:
            self.not_rule()
            self.not_val()
        else:
            self.error(expected=list(PREDICT["<bool>"].keys()))

    def not_rule(self):
        # <not>
        production = self.get_production("<not>")
        if production == 98: self.eat("!")
        elif production == 99: self.eat("!#")
        else: self.error(expected=list(PREDICT["<not>"].keys()))
        
    def not_val(self):
        # <not-val>
        production = self.get_production("<not-val>")
        if production == 100: self.eat("id")
        elif production == 101: self.bool_lit()
        elif production == 102: 
            self.eat("(")
            self.expression()
            self.eat(")")
        else: self.error(expected=list(PREDICT["<not-val>"].keys()))

    def rel(self):
        # <rel>
        production = self.get_production("<rel>")
        if production == 103:
            self.rel_op()
            self.gen_ope()
            self.arith()
        elif production == 104: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<rel>"].keys()))

    def rel_op(self):
        # <rel-op>
        production = self.get_production("<rel-op>")
        if self.current_token.type == "<":
            self.eat("<")
        elif self.current_token.type == ">":
            self.eat(">")
        elif self.current_token.type == "<=":
            self.eat("<=")
        elif self.current_token.type == ">=":
            self.eat(">=")
        else:
             self.error(expected=list(PREDICT["<rel-op>"].keys()))

    def logeq(self):
        # <logeq>
        production = self.get_production("<logeq>")
        if production == 109:
            self.logeq_op()
            self.gen_ope()
            self.gen_exp()
        elif production == 110: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<logeq>"].keys()))

    def logeq_op(self):
        # <logeq-op>
        production = self.get_production("<logeq-op>")
        if production == 111: 
            self.log_op()
        elif production == 112: 
            self.equal_op()
        else:
            self.error(expected=list(PREDICT["<logeq-op>"].keys()))
    
    def log_op(self):
        # <log-op>
        production = self.get_production("<log-op>")
        if production == 113: self.eat("||")
        elif production == 114: self.eat("&&")
        else: self.error(expected=list(PREDICT["<log-op>"].keys()))

    def equal_op(self):
        # <equal-op>
        production = self.get_production("<equal-op>")
        if production == 115: self.eat("==")
        elif production == 116: self.eat("!=")
        else: self.error(expected=list(PREDICT["<equal-op>"].keys()))

    def scroll(self):
        # <scroll>
        production = self.get_production("<scroll>")
        if production == 117:
            self.eat("&")
            self.scroll_ope()
            self.scroll()
        elif production == 118: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<scroll>"].keys()))

    def scroll_ope(self):
        # <scroll-ope>
        production = self.get_production("<scroll-ope>")
        if production == 119:
            self.eat("SCROLL-lit")
            self.arr_elmt_tail()
        elif production == 120:
            self.eat("id")
            self.id_tail()
        elif production == 121:
            self.eat("(")
            self.scroll_ope()
            self.scroll()
            self.eat(")")
        else:
            self.error(expected=list(PREDICT["<scroll-ope>"].keys()))

    def sub_func(self):
        # <sub-func>
        production = self.get_production("<sub-func>")
        if production == 122:
            self.d_type()
            self.eat("id")
            self.return_func()
        elif production == 123:
            self.nonreturn_func()
        elif production == 124:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<sub-func>"].keys()))

    def return_func(self):
        # <return-func>
        production = self.get_production("<return-func>")
        if production == 125:
            self.eat("(")
            self.func_parameters()
            self.eat(")")
            self.eat("[")
            self.local_dec()
            self.statements()
            self.eat("BACK")
            self.back_val()
            self.eat("!!")
            self.eat("]")
            self.sub_func()
        else:
            self.error(expected=list(PREDICT["<return-func>"].keys()))

    def func_parameters(self):
        # <func-parameters>
        production = self.get_production("<func-parameters>")
        if production == 126:
            self.d_type()
            self.eat("id")
            self.func_tail()
        elif production == 127: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<func-parameters>"].keys()))

    def func_tail(self):
        # <func-tail>
        production = self.get_production("<func-tail>")
        if production == 128:
            self.eat(",")
            self.d_type()
            self.eat("id")
            self.func_tail()
        elif production == 129: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<func-tail>"].keys()))

    def back_val(self):
        # <back-val>
        production = self.get_production("<back-val>")
        if production == 130: self.literals()
        elif production == 131: self.eat("id")
        elif production == 132:
            self.eat("(")
            self.expression()
            self.eat(")")
        else:
            self.error(expected=list(PREDICT["<back-val>"].keys()))

    def nonreturn_func(self):
        # <nonreturn-func>
        production = self.get_production("<nonreturn-func>")
        if production == 133:
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
            self.error(expected=list(PREDICT["<nonreturn-func>"].keys()))

    def nonreturn_back(self):
        # <nonreturn-back>
        production = self.get_production("<nonreturn-back>")
        if production == 134:
            self.eat("BACK")
            self.eat("!!")
        elif production == 135: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<nonreturn-back>"].keys()))

    def local_dec(self):
        # <local-dec>
        production = self.get_production("<local-dec>")
        if production == 136:
            self.d_type()
            self.eat("id")
            self.var_arr_dec()
            self.loc_dec_tail()
        elif production == 137:
            self.struct()
        else:
            self.error(expected=list(PREDICT["<local-dec>"].keys()))

    def loc_dec_tail(self):
        # <loc-dec-tail>
        production = self.get_production("<loc-dec-tail>")
        if production == 138:
            self.local_dec()
        elif production == 139:
            pass # Lambda 
        else:
            self.error(expected=list(PREDICT["<loc-dec-tail>"].keys()))

    def struct(self):
        # <struct>
        production = self.get_production("<struct>")
        if production == 140:
            self.struct_dec()
            self.struct()
        elif production == 141: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<struct>"].keys()))

    def struct_dec(self):
        # <struct-dec>
        production = self.get_production("<struct-dec>")
        if production == 142:
            self.eat("MAST")
            self.eat("id")
            self.eat("id")
            self.struct_dec_init()
            self.eat("!!")
        else:
            self.error(expected=list(PREDICT["<struct-dec>"].keys()))

    def struct_dec_init(self):
        # <struct-dec-init>
        production = self.get_production("<struct-dec-init>")
        if production == 143:
            self.eat(",")
            self.eat("id")
            self.struct_dec_tail()
        elif production == 144:
            self.eat("=")
            self.eat("[")
            self.arr_val()
            self.eat("]")
        elif production == 145: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<struct-dec-init>"].keys()))

    def struct_dec_tail(self):
        # <struct-dec-tail>
        production = self.get_production("<struct-dec-tail>")
        if production == 146:
            self.eat(",")
            self.eat("id")
            self.struct_dec_tail()
        elif production == 147: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<struct-dec-tail>"].keys()))

    def statements(self):
        # <statements>
        production = self.get_production("<statements>")
        if production == 148: self.assign_stmnt()
        elif production == 149: self.ask_stmnt()
        elif production == 150: self.echo_stmnt()
        elif production == 151: self.look_stmnt()
        elif production == 152: self.chart_stmnt()
        elif production == 153: self.hoist_stmnt()
        elif production == 154: self.heave_stmnt()
        elif production == 155: self.haul_stmnt()
        elif production == 156: 
            self.unary_exp()
            self.eat("!!")
        else:
            self.error(expected=list(PREDICT["<statements>"].keys()))
        
        self.stmnt_tail()

    def stmnt_tail(self):
        # <stmnt-tail>
        production = self.get_production("<stmnt-tail>")
        if production == 157:
            self.statements()
        elif production == 158:
            pass # Lambda
        else:
            self.error(expected=list(PREDICT["<stmnt-tail>"].keys()))

    def assign_stmnt(self):
        # <assign-stmnt>
        production = self.get_production("<assign-stmnt>")
        if production == 159:
            self.eat("id")
            self.assign_tail()
            self.eat("!!")
        else:
            self.error(expected=list(PREDICT["<assign-stmnt>"].keys()))

    def assign_tail(self):
        # <assign-tail>
        production = self.get_production("<assign-tail>")
        if production == 160:
            self.arr_str()
            self.assign_body()
        elif production == 161:
            self.func_args()
        else:
            self.error(expected=list(PREDICT["<assign-tail>"].keys()))

    def arr_str(self):
        # <arr-str>
        production = self.get_production("<arr-str>")
        if production == 75: self.arr_elmt()
        elif production == 76: self.str_mem()
        elif production == 77: pass # Lambda
        else:
          self.error(expected=list(PREDICT["<arr-str>"].keys()))
        
    def assign_body(self):
        # <assign-body>
        production = self.get_production("<assign-body>")
        if production == 162:
            self.eat("=")
            self.assign_val()
        elif production == 163:
            self.arith_assign_op()
            self.expression()
        else:
             self.error(expected=list(PREDICT["<assign-body>"].keys()))

    def assign_val(self):
        # <assign-val>
        production = self.get_production("<assign-val>")
        if production == 164: self.var_val()
        elif production == 165:
            self.eat("[")
            self.arr_assign()
            self.eat("]")
        else:
            self.error(expected=list(PREDICT["<assign-val>"].keys()))
            
    def arr_assign(self):
        # <arr-assign>
        production = self.get_production("<arr-assign>")
        if production == 166: self.arr_val()
        elif production == 167: self.arr2_val()
        else:
            self.error(expected=list(PREDICT["<arr-assign>"].keys()))

    def arith_assign_op(self):
        # <arith-assign-op>
        production = self.get_production("<arith-assign-op>")
        if production == 168: self.eat("+=")
        elif production == 169: self.eat("-=")
        elif production == 170: self.eat("*=")
        elif production == 171: self.eat("/=")
        elif production == 172: self.eat("%=")
        elif production == 173: self.eat("^=")
        else:
            self.error(expected=list(PREDICT["<arith-assign-op>"].keys()))

    def ask_stmnt(self):
        # <ask-stmnt>
        production = self.get_production("<ask-stmnt>")
        if production == 174:
            self.eat("ASK")
            self.eat("(")
            self.eat("SCROLL-lit")
            self.eat(",")
            self.addr()
            self.eat(")")
            self.eat("!!")
        else:
            self.error(expected=list(PREDICT["<ask-stmnt>"].keys()))
            
    def addr(self):
        # <addr>
        production = self.get_production("<addr>")
        if production == 175:
            self.eat("@")
            self.eat("id")
            self.arr_str()
            self.addr_tail()
        else:
            self.error(expected=list(PREDICT["<addr>"].keys()))
            
    def addr_tail(self):
        # <addr-tail>
        production = self.get_production("<addr-tail>")
        if production == 176:
            self.eat(",")
            self.eat("@")
            self.eat("id")
            self.arr_str()
            self.addr_tail()
        elif production == 177: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<addr-tail>"].keys()))

    def echo_stmnt(self):
        # <echo-stmnt>
        production = self.get_production("<echo-stmnt>")
        if production == 178:
            self.eat("ECHO")
            self.eat("(")
            self.eat("SCROLL-lit")
            self.echo_arg()
            self.eat(")")
            self.eat("!!")
        else:
            self.error(expected=list(PREDICT["<echo-stmnt>"].keys()))

    def echo_arg(self):
        # <echo-arg>
        production = self.get_production("<echo-arg>")
        if production == 179:
            self.eat(",")
            self.expression()
            self.echo_arg_tail()
        elif production == 180: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<echo-arg>"].keys()))
        
    def echo_arg_tail(self):
        # <echo-arg-tail>
        production = self.get_production("<echo-arg-tail>")
        if production == 181:
            self.eat(",")
            self.expression()
            self.echo_arg_tail()
        elif production == 182: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<echo-arg-tail>"].keys()))

    def look_stmnt(self):
        # <look-stmnt>
        production = self.get_production("<look-stmnt>")
        if production == 183:
            self.eat("LOOK")
            self.eat("(")
            self.cond_exp()
            self.eat(")")
            self.eat("[")
            self.statements()
            self.sail_stmt()
            self.eat("]")
            self.look_tail()
        else:
            self.error(expected=list(PREDICT["<look-stmnt>"].keys()))

    def cond_exp(self):
        # <cond-exp>
        production = self.get_production("<cond-exp>")
        if production == 184:
            self.gen_ope()
            self.gen_exp()
        else:
            self.error(expected=list(PREDICT["<cond-exp>"].keys()))

    def sail_stmt(self):
        # <sail-stmt>
        production = self.get_production("<sail-stmt>")
        if production == 185:
            self.eat("SAIL")
            self.eat("!!")
        elif production == 186: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<sail-stmt>"].keys()))

    def look_tail(self):
        # <look-tail>
        production = self.get_production("<look-tail>")
        if production == 187:
            self.eat("DROPLOOK")
            self.eat("(")
            self.cond_exp()
            self.eat(")")
            self.eat("[")
            self.statements()
            self.sail_stmt()
            self.eat("]")
            self.look_tail()
        elif production == 188:
            self.eat("DROP")
            self.eat("[")
            self.statements()
            self.sail_stmt()
            self.eat("]")
        elif production == 189: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<look-tail>"].keys()))

    def chart_stmnt(self):
        # <chart-stmnt>
        production = self.get_production("<chart-stmnt>")
        if production == 190:
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
            self.error(expected=list(PREDICT["<chart-stmnt>"].keys()))

    def chart_cond(self):
        # <chart-cond>
        production = self.get_production("<chart-cond>")
        if production == 191: self.const()
        elif production == 192: self.eat("id")
        else:
            self.error(expected=list(PREDICT["<chart-cond>"].keys()))
        
    def const(self):
        # <const>
        production = self.get_production("<const>")
        if production == 193:
            self.neg()
            self.eat("COIN-lit")
        elif production == 194:
            self.eat("PARCH-lit")
        else:
            self.error(expected=list(PREDICT["<const>"].keys()))

    def courses(self):
        # <courses>
        production = self.get_production("<courses>")
        if production == 195:
            self.eat("COURSE")
            self.const()
            self.eat(":")
            self.statements()
            self.eat("LAND")
            self.eat("!!")
        else:
            self.error(expected=list(PREDICT["<courses>"].keys()))

    def course_tail(self):
        # <course-tail>
        production = self.get_production("<course-tail>")
        if production == 196:
            self.courses()
            self.course_tail()
        elif production == 197: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<course-tail>"].keys()))

    def adrift_case(self):
        # <adrift-case>
        production = self.get_production("<adrift-case>")
        if production == 198:
            self.eat("ADRIFT")
            self.eat(":")
            self.statements()
            self.eat("LAND")
            self.eat("!!")
        elif production == 199: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<adrift-case>"].keys()))

    def hoist_stmnt(self):
        # <hoist-stmnt>
        production = self.get_production("<hoist-stmnt>")
        if production == 200:
            self.eat("HOIST")
            self.eat("(")
            self.init()
            self.eat("!!")
            self.cond_exp()
            self.eat("!!")
            self.unary_exp()
            self.eat(")")
            self.eat("[")
            self.statements()
            self.eat("]")
        else:
            self.error(expected=list(PREDICT["<hoist-stmnt>"].keys()))

    def init(self):
        # <init>
        production = self.get_production("<init>")
        if production == 201:
            self.eat("COIN")
            self.eat("id")
            self.eat("=")
            self.neg()
            self.eat("COIN-lit")
        elif production == 202:
            self.eat("id")
            self.eat("=")
            self.neg()
            self.eat("COIN-lit")
        elif production == 203: pass # Lambda
        else:
            self.error(expected=list(PREDICT["<init>"].keys()))

    def heave_stmnt(self):
        # <heave-stmnt>
        production = self.get_production("<heave-stmnt>")
        if production == 204:
            self.eat("HEAVE")
            self.eat("(")
            self.cond_exp()
            self.eat(")")
            self.eat("[")
            self.statements()
            self.eat("]")
        else:
            self.error(expected=list(PREDICT["<heave-stmnt>"].keys()))

    def haul_stmnt(self):
        # <haul-stmnt>
        production = self.get_production("<haul-stmnt>")
        if production == 205:
            self.eat("HAUL")
            self.eat("[")
            self.statements()
            self.eat("]")
            self.eat("HEAVE")
            self.eat("(")
            self.cond_exp()
            self.eat(")")
            self.eat("!!")
        else:
            self.error(expected=list(PREDICT["<haul-stmnt>"].keys()))

    def unary_exp(self):
        # <unary-exp>
        production = self.get_production("<unary-exp>")
        if production == 206:
            self.unary_op()
            self.eat("id")
        else:
            self.error(expected=list(PREDICT["<unary-exp>"].keys()))

    def unary_op(self):
        # <unary-op>
        production = self.get_production("<unary-op>")
        if production == 207: self.eat("+#")
        elif production == 208: self.eat("-#")
        else:
            self.error(expected=list(PREDICT["<unary-op>"].keys()))