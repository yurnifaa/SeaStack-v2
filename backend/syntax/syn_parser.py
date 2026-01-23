import sys
from syntax.First_Set import FIRST
from syntax.Predict_Set import PREDICT
from syntax.Follow_Set import FOLLOW

# IMPORT THE UPDATED ERROR HANDLER
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
    # Program Structure & Declarations
    # =========================================

    def program(self):
        # <program>
        # Prod 1
        production = self.get_production("<program>")
        if production == 1:
            self.global_dec()
            self.eat("AHOY")
            self.eat("(")
            self.eat(")")
            self.eat("[")
            
            # Local Declarations OPTIONAL
            if self.current_token and self.current_token.type in FIRST["<local-dec>"]:
                self.local_dec()
            
            self.statements()
            self.eat("]")
        else:
            expected = list(PREDICT["<program>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

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
            pass # Lambda
        else:
            expected = list(PREDICT["<global-dec>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def d_type(self):
        # <d-type>
        production = self.get_production("<d-type>")
        if production in [7, 8, 9, 10, 11]:
            if production == 7: self.eat("COIN")
            elif production == 8: self.eat("DIME")
            elif production == 9: self.eat("PARCH")
            elif production == 10: self.eat("SCROLL")
            elif production == 11: self.eat("BOOL")
        else:
            expected = list(PREDICT["<d-type>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

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
            expected = list(PREDICT["<dtype-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def var_arr_dec(self):
        # <var-arr-dec>
        production = self.get_production("<var-arr-dec>")
        if production == 14: self.variable()
        elif production == 15: self.array()
        else:
            expected = list(PREDICT["<var-arr-dec>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def variable(self):
        # <variable>
        production = self.get_production("<variable>")
        if production == 16:
            self.var_init()
            self.multi_var_init()
            self.eat("!!")
        else:
            expected = list(PREDICT["<variable>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def var_init(self):
        # <var-init>
        production = self.get_production("<var-init>")
        if production == 17:
            self.eat("=")
            self.var_val()
        elif production == 18:
            pass # Lambda
        else:
            expected = list(PREDICT["<var-init>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

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
            expected = list(PREDICT["<multi-var-init>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

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
            expected = list(PREDICT["<array>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

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
            expected = list(PREDICT["<arr-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def arr_val(self):
        # <arr-val>
        production = self.get_production("<arr-val>")
        if production == 25:
            self.var_val()
            self.arr_val_tail()
        else:
            expected = list(PREDICT["<arr-val>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

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
            expected = list(PREDICT["<arr-val-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

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
            expected = list(PREDICT["<arr2-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def arr2_val(self):
        # <arr2-val>
        production = self.get_production("<arr2-val>")
        if production == 30:
            self.eat("[")
            self.arr_val()
            self.eat("]")
            self.arr2_val_tail()
        else:
            expected = list(PREDICT["<arr2-val>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

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
            expected = list(PREDICT["<arr2-val-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

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
            expected = list(PREDICT["<locke-dec>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

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
            expected = list(PREDICT["<struct-def>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def mem_dec(self):
        # <mem-dec>
        production = self.get_production("<mem-dec>")
        if production == 36:
            self.d_type()
            self.eat("id")
            self.mem_dec_tail()
            self.eat("!!")
        else:
            expected = list(PREDICT["<mem-dec>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

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
            expected = list(PREDICT["<mem-dec-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def more_mem(self):
        # <more-mem>
        production = self.get_production("<more-mem>")
        if production == 39:
            self.mem_dec()
            self.more_mem()
        elif production == 40:
            pass # Lambda
        else:
            expected = list(PREDICT["<more-mem>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    # =========================================
    # Expressions & Values
    # =========================================

    def var_val(self):
        # <var-val>
        production = self.get_production("<var-val>")
        if production == 41:
            self.operands()
            self.exp_tail()
        else:
            expected = list(PREDICT["<var-val>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def operands(self):
        # <operands>
        production = self.get_production("<operands>")
        if production == 42:
            pass 
            self.value()
        elif production == 43:
            self.eat("(")
            self.var_val()
            self.eat(")")
        elif production == 44:
            self.not_rule()
            self.not_val()
        else:
            expected = list(PREDICT["<operands>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def value(self):
        # <value>
        production = self.get_production("<value>")
        if production == 45:
            self.eat("id")
            self.id_tail()
        elif production == 46:
            self.literals()
        else:
            expected = list(PREDICT["<value>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def id_tail(self):
        # <id-tail>
        production = self.get_production("<id-tail>")
        if production == 47:
            self.arr_elmt()
        elif production == 48:
            self.str_mem()
        elif production == 49:
            self.func_args()
        elif production == 50:
            pass # Lambda
        else:
            expected = list(PREDICT["<id-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def arr_elmt(self):
        # <arr-elmt>
        production = self.get_production("<arr-elmt>")
        if production == 51:
            self.eat("{")
            self.arr_index()
            self.eat("}")
            self.arr_elmt_tail()
        else:
            expected = list(PREDICT["<arr-elmt>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def arr_index(self):
        # <arr-index>
        production = self.get_production("<arr-index>")
        if production == 52: self.eat("COIN-lit")
        elif production == 53: self.eat("id")
        else:
            expected = list(PREDICT["<arr-index>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def arr_elmt_tail(self):
        # <arr-elmt-tail>
        production = self.get_production("<arr-elmt-tail>")
        if production == 54:
            self.eat("{")
            self.arr_index()
            self.eat("}")
        elif production == 55:
            pass # Lambda
        else:
            expected = list(PREDICT["<arr-elmt-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def str_mem(self):
        # <str-mem>
        production = self.get_production("<str-mem>")
        if production == 56:
            self.eat("$")
            self.eat("id")
        else:
            expected = list(PREDICT["<str-mem>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def func_args(self):
        # <func-args>
        production = self.get_production("<func-args>")
        if production == 57:
            self.eat("(")
            self.args()
            self.eat(")")
        elif production == 58:
            pass # Lambda
        else:
            expected = list(PREDICT["<func-args>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))
        
    def args(self):
        # <args>
        production = self.get_production("<args>")
        if production == 202:
            self.arr_val()
        elif production == 203:
            pass # Lambda
        else:
            expected = list(PREDICT["<args>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def literals(self):
        # <literals>
        production = self.get_production("<literals>")
        if production == 59: self.digits()
        elif production == 60: self.bool_lit()
        elif production == 61: self.eat("PARCH-lit")
        elif production == 62:
            self.eat("SCROLL-lit")
            self.arr_elmt_tail()
        else:
            expected = list(PREDICT["<literals>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def digits(self):
        # <digits>
        production = self.get_production("<digits>")
        if production == 63:
            self.neg()
            self.coin_dime()
        else:
            expected = list(PREDICT["<digits>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def neg(self):
        # <neg>
        production = self.get_production("<neg>")
        if production == 64: self.eat("-")
        elif production == 65: pass # Lambda
        else:
            expected = list(PREDICT["<neg>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def coin_dime(self):
        # <coin-dime>
        production = self.get_production("<coin-dime>")
        if production == 66: self.eat("COIN-lit")
        elif production == 67: self.eat("DIME-lit")
        else:
            expected = list(PREDICT["<coin-dime>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def bool_lit(self):
        # <bool-lit>
        production = self.get_production("<bool-lit>")
        if production == 68: self.eat("AYE")
        elif production == 69: self.eat("NAY")
        else:
            expected = list(PREDICT["<bool-lit>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def arr_str(self):
        # <arr-str>
        production = self.get_production("<arr-str>")
        if production == 70: self.arr_elmt()
        elif production == 71: self.str_mem()
        elif production == 72: pass # Lambda
        else:
            expected = list(PREDICT["<arr-str>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def exp_tail(self):
        # <exp-tail>
        production = self.get_production("<exp-tail>")
        if production == 73: self.gen_exp()
        elif production == 74: self.scroll()
        elif production == 75: pass # Lambda
        else:
            expected = list(PREDICT["<exp-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def gen_exp(self):
        # <gen-exp>
        production = self.get_production("<gen-exp>")
        if production == 76:
            self.arith()
            self.rel()
            self.logeq()
        elif production == 77: pass # Lambda
        else:
            expected = list(PREDICT["<gen-exp>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def arith(self):
        # <arith>
        production = self.get_production("<arith>")
        if production == 78: self.arith_exp()
        elif production == 79: pass # Lambda
        else:
            expected = list(PREDICT["<arith>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def arith_exp(self):
        # <arith-exp>
        production = self.get_production("<arith-exp>")
        if production == 80:
            self.arith_op()
            self.gen_ope()
            self.arith()
        else:
            expected = list(PREDICT["<arith-exp>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def arith_op(self):
        # <arith-op>
        production = self.get_production("<arith-op>")
        if production == 81: self.eat("+")
        elif production == 82: self.eat("-") # PDF 82 is ","? Wait. No, Page 3 says 82 is "," ??
        # RE-READING CFG SOURCE 2331:
        # 81 -> +
        # 82 -> , (Wait, that seems wrong for arith-op, maybe typo in source PDF or I misread)
        # Checking Source 2331: 
        # 81 <arith-op> -> +
        # 82 <arith-op> -> - (The PDF snippet has a comma on line 82 but "-" is expected)
        # 83 <arith-op> -> *
        # 84 <arith-op> -> /
        # 85 <arith-op> -> %
        # 86 <arith-op> -> ^
        # FIX: I will assume standard arithmetic operators based on context.
        elif production == 82: self.eat("-")
        elif production == 83: self.eat("*")
        elif production == 84: self.eat("/")
        elif production == 85: self.eat("%")
        elif production == 86: self.eat("^")
        else:
            expected = list(PREDICT["<arith-op>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def gen_ope(self):
        # <gen-ope>
        production = self.get_production("<gen-ope>")
        if production == 87:
            self.eat("id")
            self.id_tail()
        elif production == 88:
            self.digits()
        elif production == 89:
            self.bool_rule()
        elif production == 90:
            self.eat("(")
            self.gen_ope()
            self.gen_exp()
            self.eat(")")
        else:
            expected = list(PREDICT["<gen-ope>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def bool_rule(self):
        # <bool>
        production = self.get_production("<bool>")
        if production == 91: self.bool_lit()
        elif production == 92:
            self.not_rule()
            self.not_val()
        else:
            expected = list(PREDICT["<bool>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def not_rule(self):
        # <not>
        production = self.get_production("<not>")
        if production == 93: self.eat("!")
        elif production == 94: self.eat("!#")
        else:
            expected = list(PREDICT["<not>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def not_val(self):
        # <not-val>
        production = self.get_production("<not-val>")
        if production == 95:
            self.eat("id")
            self.id_tail()
        elif production == 96: self.bool_lit()
        elif production == 97:
            self.eat("(")
            self.var_val()
            self.eat(")")
        else:
            expected = list(PREDICT["<not-val>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def rel(self):
        # <rel>
        production = self.get_production("<rel>")
        if production == 98:
            self.rel_op()
            self.gen_ope()
            self.arith()
        elif production == 99: pass # Lambda
        else:
            expected = list(PREDICT["<rel>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def rel_op(self):
        # <rel-op>
        production = self.get_production("<rel-op>")
        if production == 100: self.eat("<")
        elif production == 101: self.eat(">")
        elif production == 102: self.eat("<=")
        elif production == 103: self.eat(">=")
        else:
            expected = list(PREDICT["<rel-op>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def logeq(self):
        # <logeq>
        production = self.get_production("<logeq>")
        if production == 104:
            self.logeq_op()
            self.operands() # Note CFG says <operands> here in Prod 104
            self.gen_exp()
        elif production == 105: pass # Lambda
        else:
            expected = list(PREDICT["<logeq>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def logeq_op(self):
        # <logeq-op>
        production = self.get_production("<logeq-op>")
        if production == 106: self.log_op()
        elif production == 107: self.equal_op()
        else:
            expected = list(PREDICT["<logeq-op>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def log_op(self):
        # <log-op>
        production = self.get_production("<log-op>")
        if production == 108: self.eat("||") # Source 2331 says 108 is empty space? 109 is &&. 
        # Checking table: 108 -> || (likely obscured in OCR but logically follows).
        elif production == 109: self.eat("&&")
        else:
            expected = list(PREDICT["<log-op>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def equal_op(self):
        # <equal-op>
        production = self.get_production("<equal-op>")
        if production == 110: self.eat("==")
        elif production == 111: self.eat("!=")
        else:
            expected = list(PREDICT["<equal-op>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def scroll(self):
        # <scroll>
        production = self.get_production("<scroll>")
        if production == 112:
            self.eat("&")
            self.scroll_ope()
            self.scroll()
        elif production == 113: pass # Lambda
        else:
            expected = list(PREDICT["<scroll>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def scroll_ope(self):
        # <scroll-ope>
        production = self.get_production("<scroll-ope>")
        if production == 114:
            self.eat("SCROLL-lit")
            self.arr_elmt_tail()
        elif production == 115:
            self.eat("id")
            self.id_tail()
        elif production == 116:
            self.eat("(")
            self.scroll_ope()
            self.scroll() # CFG 116: (<scroll-ope><scroll>)
            self.eat(")")
        else:
            expected = list(PREDICT["<scroll-ope>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    # =========================================
    # Functions
    # =========================================

    def sub_func(self):
        # <sub-func>
        production = self.get_production("<sub-func>")
        if production == 117:
            self.d_type()
            self.eat("id")
            self.return_func()
        elif production == 118:
            self.nonreturn_func()
            self.sub_func() # Recurse per CFG 118
        elif production == 119: pass # Lambda
        else:
            expected = list(PREDICT["<sub-func>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def return_func(self):
        # <return-func>
        production = self.get_production("<return-func>")
        if production == 120:
            self.eat("(")
            self.func_parameters()
            self.eat(")")
            self.eat("[")
            if self.current_token and self.current_token.type in FIRST["<local-dec>"]:
                self.local_dec()
            self.stmnt_tail()
            self.eat("BACK")
            self.var_val()
            self.eat("!!")
            self.eat("]")
            self.sub_func()
        else:
            expected = list(PREDICT["<return-func>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def func_parameters(self):
        # <func-parameters>
        production = self.get_production("<func-parameters>")
        if production == 121:
            self.d_type()
            self.eat("id")
            self.func_tail()
        elif production == 122: pass # Lambda
        else:
            expected = list(PREDICT["<func-parameters>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def func_tail(self):
        # <func-tail>
        production = self.get_production("<func-tail>")
        if production == 123:
            self.eat(",")
            self.d_type()
            self.eat("id")
            self.func_tail()
        elif production == 124: pass # Lambda
        else:
            expected = list(PREDICT["<func-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def nonreturn_func(self):
        # <nonreturn-func>
        production = self.get_production("<nonreturn-func>")
        if production == 125:
            self.eat("ABYSS")
            self.eat("id")
            self.eat("(")
            self.func_parameters()
            self.eat(")")
            self.eat("[")
            if self.current_token and self.current_token.type in FIRST["<local-dec>"]:
                self.local_dec()
            self.statements()
            self.nonreturn_back()
            self.eat("]")
            self.sub_func()
        else:
            expected = list(PREDICT["<nonreturn-func>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def nonreturn_back(self):
        # <nonreturn-back>
        production = self.get_production("<nonreturn-back>")
        if production == 126:
            self.eat("BACK")
            self.eat("!!")
        elif production == 127: pass # Lambda
        else:
            expected = list(PREDICT["<nonreturn-back>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def local_dec(self):
        # <local-dec>
        production = self.get_production("<local-dec>")
        if production == 128:
            self.d_type()
            self.eat("id")
            self.var_arr_dec()
            self.local_dec() # Recursion
        elif production == 129:
            self.struct()
        elif production == 130: pass # Lambda
        else:
            expected = list(PREDICT["<local-dec>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def struct(self):
        # <struct>
        production = self.get_production("<struct>")
        if production == 131:
            self.struct_dec()
            self.struct()
        elif production == 132: pass # Lambda
        else:
            expected = list(PREDICT["<struct>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def struct_dec(self):
        # <struct-dec>
        production = self.get_production("<struct-dec>")
        if production == 133:
            self.eat("MAST")
            self.eat("id")
            self.eat("id")
            self.struct_dec_init()
            self.eat("!!")
        else:
            expected = list(PREDICT["<struct-dec>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def struct_dec_init(self):
        # <struct-dec-init>
        production = self.get_production("<struct-dec-init>")
        if production == 134:
            self.eat("id")
            self.struct_dec_tail()
        elif production == 135:
            self.eat("=")
            self.eat("[")
            self.str_val()
            self.str_val_tail()
            self.eat("]")
        elif production == 136: pass # Lambda
        else:
            expected = list(PREDICT["<struct-dec-init>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def struct_dec_tail(self):
        # <struct-dec-tail>
        production = self.get_production("<struct-dec-tail>")
        if production == 137:
            self.eat(",")
            self.eat("id")
            self.struct_dec_tail()
        elif production == 138: pass # Lambda
        else:
            expected = list(PREDICT["<struct-dec-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def str_val(self):
        # <str-val>
        production = self.get_production("<str-val>")
        if production == 139:
            self.var_val()
        elif production == 140:
            self.eat("$")
            self.eat("id")
            self.eat("=")
            self.var_val()
        else:
            expected = list(PREDICT["<str-val>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def str_val_tail(self):
        # <str-val-tail>
        production = self.get_production("<str-val-tail>")
        if production == 141:
            self.str_val()
        elif production == 142: pass # Lambda
        else:
            expected = list(PREDICT["<str-val-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    # =========================================
    # Statements
    # =========================================

    def statements(self):
        # <statements>
        production = self.get_production("<statements>")
        if production == 143: self.assign_stmnt()
        elif production == 144: self.ask_stmnt()
        elif production == 145: self.echo_stmnt()
        elif production == 146: self.look_stmnt()
        elif production == 147: self.chart_stmnt()
        elif production == 148: self.hoist_stmnt()
        elif production == 149: self.heave_stmnt()
        elif production == 150: self.haul_stmnt()
        elif production == 151: 
            self.unary_exp()
            self.eat("!!")
        else:
            expected = list(PREDICT["<statements>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))
        
        self.stmnt_tail()

    def stmnt_tail(self):
        # <stmnt-tail>
        production = self.get_production("<stmnt-tail>")
        if production == 152:
            self.statements()
            self.stmnt_tail()
        elif production == 153: pass # Lambda
        else:
            expected = list(PREDICT["<stmnt-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def assign_stmnt(self):
        # <assign-stmnt>
        production = self.get_production("<assign-stmnt>")
        if production == 154:
            self.eat("id")
            self.assign_tail()
            self.eat("!!")
        else:
            expected = list(PREDICT["<assign-stmnt>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def assign_tail(self):
        # <assign-tail>
        production = self.get_production("<assign-tail>")
        if production == 155:
            self.arr_str()
            self.assign_body()
        elif production == 156:
            self.func_args()
        else:
            expected = list(PREDICT["<assign-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def assign_body(self):
        # <assign-body>
        production = self.get_production("<assign-body>")
        if production == 157:
            self.eat("=")
            self.assign_val()
        elif production == 158:
            self.arith_assign_op()
            self.var_val()
        else:
            expected = list(PREDICT["<assign-body>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def assign_val(self):
        # <assign-val>
        production = self.get_production("<assign-val>")
        if production == 159: self.var_val()
        elif production == 160:
            self.eat("[")
            self.arr_assign()
            self.eat("]")
        else:
            expected = list(PREDICT["<assign-val>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def arr_assign(self):
        # <arr-assign>
        production = self.get_production("<arr-assign>")
        if production == 161: self.arr_val()
        elif production == 162: self.arr2_val()
        else:
            expected = list(PREDICT["<arr-assign>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def arith_assign_op(self):
        # <arith-assign-op>
        production = self.get_production("<arith-assign-op>")
        if production == 163: self.eat("+=")
        elif production == 164: self.eat("-=")
        elif production == 165: self.eat("*=")
        elif production == 166: self.eat("/=")
        elif production == 167: 
            # Production 167 seems to cover both %= and ^= in the PDF or one is missing
            if self.current_token.type == "%=": self.eat("%=")
            elif self.current_token.type == "^=": self.eat("^=")
            else: self.eat("%=") # Fallback to error
        else:
            expected = list(PREDICT["<arith-assign-op>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def ask_stmnt(self):
        # <ask-stmnt>
        production = self.get_production("<ask-stmnt>")
        if production == 169:
            self.eat("ASK")
            self.eat("(")
            self.eat("SCROLL-lit")
            self.eat(",")
            self.addr()
            self.eat(")")
            self.eat("!!")
        else:
            expected = list(PREDICT["<ask-stmnt>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def addr(self):
        # <addr>
        production = self.get_production("<addr>")
        if production == 170:
            self.eat("@")
            self.eat("id")
            self.arr_str()
            self.addr_tail()
        else:
            expected = list(PREDICT["<addr>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def addr_tail(self):
        # <addr-tail>
        production = self.get_production("<addr-tail>")
        if production == 171:
            self.eat(",")
            self.eat("@")
            self.eat("id")
            self.arr_str()
            self.addr_tail()
        elif production == 172: pass # Lambda
        else:
            expected = list(PREDICT["<addr-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def echo_stmnt(self):
        # <echo-stmnt>
        production = self.get_production("<echo-stmnt>")
        if production == 173:
            self.eat("ECHO")
            self.eat("(")
            self.eat("SCROLL-lit")
            self.echo_arg()
            self.eat(")")
            self.eat("!!")
        else:
            expected = list(PREDICT["<echo-stmnt>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def echo_arg(self):
        # <echo-arg>
        production = self.get_production("<echo-arg>")
        if production == 174:
            self.eat(",")
            self.var_val()
            self.echo_arg()
        elif production == 175: pass # Lambda
        else:
            expected = list(PREDICT["<echo-arg>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def look_stmnt(self):
        # <look-stmnt>
        production = self.get_production("<look-stmnt>")
        if production == 176:
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
            expected = list(PREDICT["<look-stmnt>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def cond_exp(self):
        # <cond-exp>
        production = self.get_production("<cond-exp>")
        if production == 177:
            self.gen_ope()
            self.gen_exp()
        else:
            expected = list(PREDICT["<cond-exp>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def sail_stmt(self):
        # <sail-stmt>
        production = self.get_production("<sail-stmt>")
        if production == 178:
            self.eat("SAIL")
            self.eat("!!")
        elif production == 179: pass # Lambda
        else:
            expected = list(PREDICT["<sail-stmt>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def look_tail(self):
        # <look-tail>
        production = self.get_production("<look-tail>")
        if production == 180:
            self.eat("DROPLOOK")
            self.eat("(")
            self.cond_exp()
            self.eat(")")
            self.eat("[")
            self.statements()
            self.sail_stmt()
            self.eat("]")
            self.look_tail()
        elif production == 181:
            self.eat("DROP")
            self.eat("[")
            self.statements()
            self.sail_stmt()
            self.eat("]")
        elif production == 182: pass # Lambda
        else:
            expected = list(PREDICT["<look-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def chart_stmnt(self):
        # <chart-stmnt>
        production = self.get_production("<chart-stmnt>")
        if production == 183:
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
            expected = list(PREDICT["<chart-stmnt>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def chart_cond(self):
        # <chart-cond>
        production = self.get_production("<chart-cond>")
        if production == 184: self.const()
        elif production == 185: self.eat("id")
        else:
            expected = list(PREDICT["<chart-cond>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def const(self):
        # <const>
        production = self.get_production("<const>")
        if production == 186:
            self.neg()
            self.eat("COIN-lit")
        elif production == 187: self.eat("PARCH-lit")
        else:
            expected = list(PREDICT["<const>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def courses(self):
        # <courses>
        production = self.get_production("<courses>")
        if production == 188:
            self.eat("COURSE")
            self.const()
            self.eat(":")
            self.statements()
            self.eat("LAND")
            self.eat("!!")
        else:
            expected = list(PREDICT["<courses>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def course_tail(self):
        # <course-tail>
        production = self.get_production("<course-tail>")
        if production == 189:
            self.courses()
        elif production == 190: pass # Lambda
        else:
            expected = list(PREDICT["<course-tail>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def adrift_case(self):
        # <adrift-case>
        production = self.get_production("<adrift-case>")
        if production == 191:
            self.eat("ADRIFT")
            self.eat(":")
            self.statements()
            self.eat("LAND")
            self.eat("!!")
        elif production == 192: pass # Lambda
        else:
            expected = list(PREDICT["<adrift-case>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def hoist_stmnt(self):
        # <hoist-stmnt>
        production = self.get_production("<hoist-stmnt>")
        if production == 193:
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
            expected = list(PREDICT["<hoist-stmnt>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def init(self):
        # <init>
        production = self.get_production("<init>")
        if production == 194:
            self.eat("COIN")
            self.eat("id")
            self.eat("=")
            self.neg()
            self.eat("COIN-lit")
        elif production == 195:
            self.eat("id")
            self.eat("=")
            self.neg()
            self.eat("COIN-lit")
        elif production == 196: pass # Lambda
        else:
            expected = list(PREDICT["<init>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def heave_stmnt(self):
        # <heave-stmnt>
        production = self.get_production("<heave-stmnt>")
        if production == 197:
            self.eat("HEAVE")
            self.eat("(")
            self.cond_exp()
            self.eat(")")
            self.eat("[")
            self.statements()
            self.eat("]")
        else:
            expected = list(PREDICT["<heave-stmnt>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def haul_stmnt(self):
        # <haul-stmnt>
        production = self.get_production("<haul-stmnt>")
        if production == 198:
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
            expected = list(PREDICT["<haul-stmnt>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def unary_exp(self):
        # <unary-exp>
        production = self.get_production("<unary-exp>")
        if production == 199:
            self.unary_op()
            self.eat("id")
        else:
            expected = list(PREDICT["<unary-exp>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))

    def unary_op(self):
        # <unary-op>
        production = self.get_production("<unary-op>")
        if production == 200: self.eat("+#")
        elif production == 201: self.eat("-#")
        else:
            expected = list(PREDICT["<unary-op>"].keys())
            raise Exception(self.err_handler.get_invalid_token_error(self.current_token, expected))