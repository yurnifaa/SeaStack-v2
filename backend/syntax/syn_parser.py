import sys
# Ensure these filenames match exactly what you created
from syntax.First_Set import FIRST
from syntax.Predict_Set import PREDICT
from syntax.Follow_Set import FOLLOW

class Parser:
    def __init__(self, tokens):
        # 1. Define tokens to ignore
        ignored_types = [
            "whitespace", 
            "newline", 
            "single-comment", 
            "multi-comment"
    ]
        
        # 2. Filter out junk tokens
        self.tokens = [t for t in tokens if t.type not in ignored_types]
        
        # 3. NORMALIZE IDENTIFIERS
        for t in self.tokens:
            if t.type.startswith("id") and t.type[2:].isdigit():
                t.type = "id"
        
        # 4. Initialize state
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.errors = []
        self.logs = []

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
            """
            if token_type not in ["newline", "whitespace", "single-line comment"]:
                self.skip_whitespace_and_comments()

            if self.current_token and self.current_token.type == token_type:
                self.advance()
            else:
                found = self.current_token.type if self.current_token else 'EOF'
                self.error(f"Expected {token_type}, but found {found}")

    def error(self, message):
        """Records a syntax error and stops parsing."""
        if self.current_token:
            err_msg = f"Syntax Error at Line {self.current_token.line}, Col {self.current_token.col}: {message}"
        else:
            err_msg = "Syntax Error: Unexpected End of File"
        
        print(err_msg)
        self.errors.append(err_msg)
        raise Exception(err_msg)

    def validate_token(self, non_terminal):
        """
        Uses FIRST_SET to check if the current token is valid for this Non-Terminal.
        """
        if not self.current_token:
            return False
            
        allowed_tokens = FIRST.get(non_terminal, [])
        if self.current_token.type in allowed_tokens:
            return True
        return False

    def get_production(self, non_terminal):
        """
        Uses PREDICT_SET to return the Production Number based on current token.
        """
        if not self.current_token:
            return None
            
        productions = PREDICT.get(non_terminal, {})
        return productions.get(self.current_token.type)

    def skip_whitespace_and_comments(self):
        while self.current_token and self.current_token.type in ["newline", "whitespace", "single-line comment", "multi-line comment"]:
            self.advance()

    # =========================================
    # Entry Point
    # =========================================
    def parse(self):
        print("Starting Parsing...")
        self.logs.append("Starting Parsing...")

        try:
            self.program()
            if self.current_token is not None:
                self.error(f"Unexpected token after end of program: {self.current_token.type}")
            else:
                msg = "Parsing Completed Successfully! No Syntax Errors."
                print(msg)
                self.logs.append(msg)
        except Exception as e:
            self.logs.append(str(e))

        return self.logs

    # =========================================
    # Program Structure & Declarations
    # =========================================

    def program(self):
        # Production 1
        if not self.validate_token("<program>"):
            self.error(f"Invalid start of program. Expected one of {FIRST['<program>']}")

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
            self.error("Invalid Production for <program>")

    def global_dec(self):
        # Productions 2-6
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
            pass # Allow lambda if in follow set

    def d_type(self):
        # Productions 7-11
        production = self.get_production("<d-type>")
        if production == 7: self.eat("COIN")
        elif production == 8: self.eat("DIME")
        elif production == 9: self.eat("PARCH")
        elif production == 10: self.eat("SCROLL")
        elif production == 11: self.eat("BOOL")
        else: self.error("Expected Data Type")

    def dtype_tail(self):
        # Productions 12-13
        production = self.get_production("<dtype-tail>")
        if production == 12:
            self.var_arr_dec()
            self.global_dec()
        elif production == 13:
            self.return_func()
            self.sub_func()
        else:
            self.error("Invalid declaration tail")

    def var_arr_dec(self):
        # Productions 14-15
        production = self.get_production("<var-arr-dec>")
        if production == 14: self.variable()
        elif production == 15: self.array()
        else: self.error("Expected variable or array declaration")

    def variable(self):
        # Production 16
        production = self.get_production("<variable>")
        if production == 16:
            self.var_init()
            self.multi_var_init()
            self.eat("!!")

    def var_init(self):
        # Productions 17-18
        production = self.get_production("<var-init>")
        if production == 17:
            self.eat("=")
            self.var_val()
        elif production == 18:
            pass # Lambda

    def multi_var_init(self):
        # Productions 19-20
        production = self.get_production("<multi-var-init>")
        if production == 19:
            self.eat(",")
            self.eat("id")
            self.var_init()
            self.multi_var_init()
        elif production == 20:
            pass # Lambda

    def array(self):
        # Production 21
        production = self.get_production("<array>")
        if production == 21:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.arr_tail()
            self.eat("!!")

    def arr_tail(self):
        # Productions 22-24
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

    def arr2_tail(self):
        # Productions 28-29
        production = self.get_production("<arr2-tail>")
        if production == 28:
            self.eat("=")
            self.eat("[")
            self.arr2_val()
            self.eat("]")
        elif production == 29:
            pass # Lambda
            
    def arr_val(self):
        # Production 25
        production = self.get_production("<arr-val>")
        if production == 25:
            self.var_val()
            self.arr_val_tail()
    
    def arr_val_tail(self):
        # Productions 26-27
        production = self.get_production("<arr-val-tail>")
        if production == 26:
            self.eat(",")
            self.var_val()
            self.arr_val_tail()
        elif production == 27:
            pass

    def arr2_val(self):
        # Production 30
        production = self.get_production("<arr2-val>")
        if production == 30:
            self.eat("[")
            self.arr_val()
            self.eat("]")
            self.arr2_val_tail()

    def arr2_val_tail(self):
        # Productions 31-32
        production = self.get_production("<arr2-val-tail>")
        if production == 31:
            self.eat(",")
            self.arr2_val()
            self.arr2_val_tail()
        elif production == 32:
            pass

    def locke_dec(self):
        # Production 33
        production = self.get_production("<locke-dec>")
        if production == 33:
            self.eat("LOCKE")
            self.d_type()
            self.eat("id")
            self.eat("=")
            self.literals()
            self.eat("!!")

    def struct_def(self):
        # Productions 34-35
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

    def mem_dec(self):
        # Production 36
        production = self.get_production("<mem-dec>")
        if production == 36:
            self.d_type()
            self.eat("id")
            self.mem_dec_tail()
            self.eat("!!")
            
    def mem_dec_tail(self):
        # Productions 37-38
        production = self.get_production("<mem-dec-tail>")
        if production == 37:
            self.eat(",")
            self.eat("id")
            self.mem_dec_tail()
        elif production == 38:
            pass
            
    def more_mem(self):
        # Productions 39-40
        production = self.get_production("<more-mem>")
        if production == 39:
            self.mem_dec()
        elif production == 40:
            pass

    # =========================================
    # Expressions (Productions 41 - 121)
    # =========================================

    def var_val(self):
        # Production 41
        production = self.get_production("<var-val>")
        if production == 41:
            self.expression()

    def expression(self):
        # Production 42
        production = self.get_production("<expression>")
        if production == 42:
            self.operands()
            self.exp_tail()

    def operands(self):
        # Productions 43-45
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

    def value(self):
        # Productions 46-47
        production = self.get_production("<value>")
        if production == 46:
            self.eat("id")
            self.id_tail()
        elif production == 47:
            self.literals()

    def id_tail(self):
        # Productions 48-51
        production = self.get_production("<id-tail>")
        if production == 48:
            self.arr_elmt()
        elif production == 49:
            self.str_mem()
        elif production == 50:
            self.func_args()
        elif production == 51:
            pass # Lambda

    def arr_elmt(self):
        # Production 52
        production = self.get_production("<arr-elmt>")
        if production == 52:
            self.eat("{")
            self.arr_index()
            self.eat("}")
            self.arr_elmt_tail()
            
    def arr_index(self):
        # Productions 53-54
        production = self.get_production("<arr-index>")
        if production == 53: self.eat("COIN-lit")
        elif production == 54: self.eat("id")

    def arr_elmt_tail(self):
        # Productions 55-56
        production = self.get_production("<arr-elmt-tail>")
        if production == 55:
            self.eat("{")
            self.arr_index()
            self.eat("}")
        elif production == 56:
            pass

    def str_mem(self):
        # Production 57
        production = self.get_production("<str-mem>")
        if production == 57:
            self.eat("$")
            self.eat("id")

    def func_args(self):
        # Productions 58-59
        production = self.get_production("<func-args>")
        if production == 58:
            self.eat("(")
            self.args()
            self.eat(")")
        elif production == 59:
            pass

    def args(self):
        # Productions 60-61
        production = self.get_production("<args>")
        if production == 60:
            self.value()
            self.args_tail()
        elif production == 61:
            pass

    def args_tail(self):
        # Productions 62-63
        production = self.get_production("<args-tail>")
        if production == 62:
            self.eat(",")
            self.value()
        elif production == 63:
            pass
            
    def literals(self):
        # Productions 64-67
        production = self.get_production("<literals>")
        if production == 64: self.digits()
        elif production == 65: self.bool_lit()
        elif production == 66: self.eat("PARCH-lit")
        elif production == 67: 
            self.eat("SCROLL-lit")
            self.arr_elmt_tail()

    def digits(self):
        # Productions 68-69
        production = self.get_production("<digits>")
        if production == 68 or production == 69:
            self.neg()
            self.coin_dime()

    def neg(self):
        # Productions 69-70
        production = self.get_production("<neg>")
        if production == 69: self.eat("-")
        elif production == 70: pass

    def coin_dime(self):
        # Productions 71-72
        production = self.get_production("<coin-dime>")
        if production == 71: self.eat("COIN-lit")
        elif production == 72: self.eat("DIME-lit")
        
    def bool_lit(self):
        # Productions 73-74
        production = self.get_production("<bool-lit>")
        if production == 73: self.eat("AYE")
        elif production == 74: self.eat("NAY")

    def exp_tail(self):
        # Productions 78-80
        production = self.get_production("<exp-tail>")
        if production == 78: self.gen_exp()
        elif production == 79: self.scroll()
        elif production == 80: pass

    def gen_exp(self):
        # Productions 81-82
        production = self.get_production("<gen-exp>")
        if production == 81:
            self.arith()
            self.rel()
            self.logeq()
        elif production == 82: pass

    def arith(self):
        # Productions 83-84
        production = self.get_production("<arith>")
        if production == 83: self.arith_exp()
        elif production == 84: pass

    def arith_exp(self):
        # Production 85
        production = self.get_production("<arith-exp>")
        if production == 85:
            self.arith_op()
            self.gen_ope()
            self.arith()

    def arith_op(self):
        # Productions 86-91
        production = self.get_production("<arith-op>")
        if production == 86: self.eat("+")
        elif production == 87: self.eat("-")
        elif production == 88: self.eat("*")
        elif production == 89: self.eat("/")
        elif production == 90: self.eat("%")
        elif production == 91: self.eat("^")

    def gen_ope(self):
        # Productions 92-95
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

    def bool_rule(self):
        # Production 45 equivalent for predict check
        production = self.get_production("<bool>")
        # Note: <bool> was not in your original map, ensure it is added if used.
        # Assuming you meant checking literals logic or specific boolean production
        if production == 45: 
             # Logic logic ...
             pass
        else:
             # Logic ...
             self.bool_lit()

    def not_rule(self):
        # Production 46
        # No get_production check was here originally, just token check
        if self.current_token.type == "!": self.eat("!")
        elif self.current_token.type == "!#": self.eat("!#")
        
    def not_val(self):
        # Production 47
        if self.current_token.type == "id": self.eat("id")
        elif self.current_token.type == "AYE": self.eat("AYE")
        elif self.current_token.type == "NAY": self.eat("NAY")
        elif self.current_token.type == "(": 
            self.eat("(")
            self.expression()
            self.eat(")")

    def rel(self):
        # Productions 99-100
        production = self.get_production("<rel>")
        if production == 99:
            self.rel_op()
            self.gen_ope()
            self.arith()
        elif production == 100: pass

    def rel_op(self):
        # Productions 101-104
        production = self.get_production("<rel-op>")
        if production == 101: self.eat("<")
        elif production == 102: self.eat(">")
        elif production == 103: self.eat("<=")
        elif production == 104: self.eat(">=")

    def logeq(self):
        # Productions 105-106
        production = self.get_production("<logeq>")
        if production == 105:
            self.logeq_op()
            self.gen_ope()
            self.gen_exp()
        elif production == 106: pass

    def logeq_op(self):
        # Productions 107-109
        production = self.get_production("<logeq-op>")
        if production == 107: self.eat("||")
        elif production == 108: self.eat("&&")
        elif production == 109: 
            if self.current_token.type == "==": self.eat("==")
            elif self.current_token.type == "!=": self.eat("!=")

    def scroll(self):
        # Productions 117-118
        production = self.get_production("<scroll>")
        if production == 117:
            self.eat("&")
            self.scroll_ope()
            self.scroll()
        elif production == 118: pass

    def scroll_ope(self):
        # Productions 119-121
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

    # =========================================
    # Functions (Sub, Return, Non-Return)
    # =========================================

    def sub_func(self):
        # Productions 122-124
        production = self.get_production("<sub-func>")
        if production == 122:
            self.d_type()
            self.eat("id")
            self.return_func()
        elif production == 123:
            self.nonreturn_func()
        elif production == 124:
            pass

    def return_func(self):
        # Production 125
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

    def func_parameters(self):
        # Productions 126-127
        production = self.get_production("<func-parameters>")
        if production == 126:
            self.d_type()
            self.eat("id")
            self.func_tail()
        elif production == 127: pass

    def func_tail(self):
        # Productions 128-129
        production = self.get_production("<func-tail>")
        if production == 128:
            self.eat(",")
            self.d_type()
            self.eat("id")
            self.func_tail()
        elif production == 129: pass

    def back_val(self):
        # Productions 130-132
        production = self.get_production("<back-val>")
        if production == 130: self.literals()
        elif production == 131: self.eat("id")
        elif production == 132:
            self.eat("(")
            self.expression()
            self.eat(")")

    def nonreturn_func(self):
        # Production 133
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

    def nonreturn_back(self):
        # Productions 134-135
        production = self.get_production("<nonreturn-back>")
        if production == 134:
            self.eat("BACK")
            self.eat("!!")
        elif production == 135: pass

    # =========================================
    # Local Declarations (Rules 136-139)
    # =========================================

    def local_dec(self):
        # Productions 136-137
        production = self.get_production("<local-dec>")
        if production == 136:
            self.d_type()
            self.eat("id")
            self.var_arr_dec()
            self.loc_dec_tail()
        elif production == 137:
            self.struct()
            
    def loc_dec_tail(self):
        # Productions 138-139
        production = self.get_production("<loc-dec-tail>")
        if production == 138:
            self.local_dec()
        elif production == 139:
            pass # Lambda

    def struct(self):
        # Productions 140-141
        production = self.get_production("<struct>")
        if production == 140:
            self.struct_dec()
            self.struct()
        elif production == 141: pass

    def struct_dec(self):
        # Production 142
        production = self.get_production("<struct-dec>")
        if production == 142:
            self.eat("MAST")
            self.eat("id")
            self.eat("id")
            self.struct_dec_init()
            self.eat("!!")

    def struct_dec_init(self):
        # Productions 143-145
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
        elif production == 145: pass

    def struct_dec_tail(self):
        # Productions 146-147
        production = self.get_production("<struct-dec-tail>")
        if production == 146:
            self.eat(",")
            self.eat("id")
            self.struct_dec_tail()
        elif production == 147: pass

    # =========================================
    # Statements (Productions 148 - 156)
    # =========================================

    def statements(self):
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
        
        self.stmnt_tail()

    def stmnt_tail(self):
        production = self.get_production("<stmnt-tail>")
        if production == 157:
            self.statements()
        elif production == 158:
            pass # Lambda

    def assign_stmnt(self):
        # Production 159
        production = self.get_production("<assign-stmnt>")
        if production == 159:
            self.eat("id")
            self.assign_tail()
            self.eat("!!")

    def assign_tail(self):
        # Productions 160-161
        production = self.get_production("<assign-tail>")
        if production == 160:
            self.arr_str()
            self.assign_body()
        elif production == 161:
            self.func_args()

    def arr_str(self):
        # Productions 75-77 (Using for assignment logic)
        production = self.get_production("<arr-str>")
        if production == 75: self.arr_elmt()
        elif production == 76: self.str_mem()
        elif production == 77: pass
        
    def assign_body(self):
        # Productions 162-163
        production = self.get_production("<assign-body>")
        if production == 162:
            self.eat("=")
            self.assign_val()
        elif production == 163:
            self.arith_assign_op()
            self.expression()

    def assign_val(self):
        # Productions 164-165
        production = self.get_production("<assign-val>")
        if production == 164: self.var_val()
        elif production == 165:
            self.eat("[")
            self.arr_assign()
            self.eat("]")
            
    def arr_assign(self):
        # Productions 166-167
        production = self.get_production("<arr-assign>")
        if production == 166: self.arr_val()
        elif production == 167: self.arr2_val()

    def arith_assign_op(self):
        # Productions 168-173
        production = self.get_production("<arith-assign-op>")
        if production == 168: self.eat("+=")
        elif production == 169: self.eat("-=")
        elif production == 170: self.eat("*=")
        elif production == 171: self.eat("/=")
        elif production == 172: self.eat("%=")
        elif production == 173: self.eat("^=")

    def ask_stmnt(self):
        # Production 174
        production = self.get_production("<ask-stmnt>")
        if production == 174:
            self.eat("ASK")
            self.eat("(")
            self.eat("SCROLL-lit")
            self.eat(",")
            self.addr()
            self.eat(")")
            self.eat("!!")
            
    def addr(self):
        # Production 175
        production = self.get_production("<addr>")
        if production == 175:
            self.eat("@")
            self.eat("id")
            self.arr_str()
            self.addr_tail()
            
    def addr_tail(self):
        # Productions 176-177
        production = self.get_production("<addr-tail>")
        if production == 176:
            self.eat(",")
            self.eat("@")
            self.eat("id")
            self.arr_str()
            self.addr_tail()
        elif production == 177: pass

    def echo_stmnt(self):
        # Production 178
        production = self.get_production("<echo-stmnt>")
        if production == 178:
            self.eat("ECHO")
            self.eat("(")
            self.eat("SCROLL-lit")
            self.echo_arg()
            self.eat(")")
            self.eat("!!")

    def echo_arg(self):
        # Productions 179-180
        production = self.get_production("<echo-arg>")
        if production == 179:
            self.eat(",")
            self.expression()
            self.echo_arg_tail()
        elif production == 180: pass
        
    def echo_arg_tail(self):
        # Productions 181-182
        production = self.get_production("<echo-arg-tail>")
        if production == 181:
            self.eat(",")
            self.expression()
            self.echo_arg_tail()
        elif production == 182: pass

    def look_stmnt(self):
        # Production 183
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

    def cond_exp(self):
        # Production 184
        production = self.get_production("<cond-exp>")
        if production == 184:
            self.gen_ope()
            self.gen_exp()

    def sail_stmt(self):
        # Productions 185-186
        production = self.get_production("<sail-stmt>")
        if production == 185:
            self.eat("SAIL")
            self.eat("!!")
        elif production == 186: pass

    def look_tail(self):
        # Productions 187-189
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
        elif production == 189: pass

    def chart_stmnt(self):
        # Production 190
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

    def chart_cond(self):
        # Productions 191-192
        production = self.get_production("<chart-cond>")
        if production == 191: self.const()
        elif production == 192: self.eat("id")
        
    def const(self):
        # Productions 193-194
        production = self.get_production("<const>")
        if production == 193:
            self.neg()
            self.eat("COIN-lit")
        elif production == 194:
            self.eat("PARCH-lit")

    def courses(self):
        # Production 195
        production = self.get_production("<courses>")
        if production == 195:
            self.eat("COURSE")
            self.const()
            self.eat(":")
            self.statements()
            self.eat("LAND")
            self.eat("!!")

    def course_tail(self):
        # Productions 196-197
        production = self.get_production("<course-tail>")
        if production == 196:
            self.courses()
            self.course_tail()
        elif production == 197: pass

    def adrift_case(self):
        # Productions 198-199
        production = self.get_production("<adrift-case>")
        if production == 198:
            self.eat("ADRIFT")
            self.eat(":")
            self.statements()
            self.eat("LAND")
            self.eat("!!")
        elif production == 199: pass

    def hoist_stmnt(self):
        # Production 200
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

    def init(self):
        # Productions 201-203
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
        elif production == 203: pass

    def heave_stmnt(self):
        # Production 204
        production = self.get_production("<heave-stmnt>")
        if production == 204:
            self.eat("HEAVE")
            self.eat("(")
            self.cond_exp()
            self.eat(")")
            self.eat("[")
            self.statements()
            self.eat("]")

    def haul_stmnt(self):
        # Production 205
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

    def unary_exp(self):
        # Production 206
        production = self.get_production("<unary-exp>")
        if production == 206:
            self.unary_op()
            self.eat("id")

    def unary_op(self):
        # Productions 207-208
        production = self.get_production("<unary-op>")
        if production == 207: self.eat("+#")
        elif production == 208: self.eat("-#")