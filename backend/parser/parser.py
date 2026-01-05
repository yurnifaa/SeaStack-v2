import sys
# Ensure these filenames match exactly what you created
from backend.parser.First_Set import FIRST
from backend.parser.Predict_Set import PREDICT
from backend.parser.Follow_Set import FOLLOW

class Parser:
    def __init__(self, tokens):
        # 1. Define tokens to ignore
        # These must match the strings your Lexer generates EXACTLY.
        ignored_types = [
            "whitespace", 
            "newline", 
            "single-comment", 
            "multi-comment"
    ]
        
        # 2. Filter out junk tokens
        self.tokens = [t for t in tokens if t.type not in ignored_types]
        
        # 3. NORMALIZE IDENTIFIERS (The Fix)
        # The Lexer produces 'id1', 'id2'. The Parser tables expect 'id'.
        # We rewrite the type to 'id' so the grammar rules match.
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
            Otherwise, records an error.
            """
            # 1. Skip junk (newlines/comments) before checking, UNLESS we are specifically looking for them
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
        Returns True if valid, False otherwise.
        """
        if not self.current_token:
            return False
            
        allowed_tokens = FIRST.get(non_terminal, [])
        if self.current_token.type in allowed_tokens:
            return True
        return False

    def get_production(self, non_terminal):
        """
        Uses PREDICT_SET to return the Rule Number based on current token.
        """
        if not self.current_token:
            return None
            
        rules = PREDICT.get(non_terminal, {})
        return rules.get(self.current_token.type)

    def skip_whitespace_and_comments(self):
        """Skips over newline and comment tokens to find the next code token."""
        while self.current_token and self.current_token.type in ["newline", "whitespace", "single-line comment", "multi-line comment"]:
            self.advance()

    # =========================================
    # Entry Point
    # =========================================
    def parse(self):
        print("Starting Parsing...")
        self.logs.append("Starting Parsing...") # <--- ADD LOG

        try:
            self.program()
            if self.current_token is not None:
                self.error(f"Unexpected token after end of program: {self.current_token.type}")
            else:
                msg = "Parsing Completed Successfully! No Syntax Errors."
                print(msg)
                self.logs.append(msg) # <--- ADD LOG
        except Exception as e:
            # Catch the error we raised in self.error() so the server doesn't crash
            self.logs.append(str(e))

        return self.logs # <--- CRITICAL: RETURN THE LOGS

    # =========================================
    # Program Structure & Declarations
    # =========================================

    def program(self):
        # Rule 1
        if not self.validate_token("<program>"):
            self.error(f"Invalid start of program. Expected one of {FIRST['<program>']}")

        rule = self.get_production("<program>")
        if rule == 1:
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
        # Rules 2-6
        rule = self.get_production("<global-dec>")
        if rule == 2:
            self.d_type()
            self.eat("id")
            self.dtype_tail()
        elif rule == 3:
            self.locke_dec()
            self.global_dec()
        elif rule == 4:
            self.struct_def()
        elif rule == 5:
            self.nonreturn_func()
            self.sub_func()
        elif rule == 6:
            pass # Lambda
        else:
            pass # Allow lambda if in follow set

    def d_type(self):
        # Rules 7-11
        rule = self.get_production("<d-type>")
        if rule == 7: self.eat("COIN")
        elif rule == 8: self.eat("DIME")
        elif rule == 9: self.eat("PARCH")
        elif rule == 10: self.eat("SCROLL")
        elif rule == 11: self.eat("BOOL")
        else: self.error("Expected Data Type")

    def dtype_tail(self):
        # Rules 12-13
        rule = self.get_production("<dtype-tail>")
        if rule == 12:
            self.var_arr_dec()
            self.global_dec()
        elif rule == 13:
            self.return_func()
            self.sub_func()
        else:
            self.error("Invalid declaration tail")

    def var_arr_dec(self):
        # Rules 14-15
        rule = self.get_production("<var-arr-dec>")
        if rule == 14: self.variable()
        elif rule == 15: self.array()
        else: self.error("Expected variable or array declaration")

    def variable(self):
        # Rule 16
        rule = self.get_production("<variable>")
        if rule == 16:
            self.var_init()
            self.multi_var_init()
            self.eat("!!")

    def var_init(self):
        # Rule 17-18
        rule = self.get_production("<var-init>")
        if rule == 17:
            self.eat("=")
            self.var_val()
        elif rule == 18:
            pass # Lambda

    def multi_var_init(self):
        # Rule 19-20
        rule = self.get_production("<multi-var-init>")
        if rule == 19:
            self.eat(",")
            self.eat("id")
            self.var_init()
            self.multi_var_init()
        elif rule == 20:
            pass # Lambda

    def array(self):
        # Rule 21
        rule = self.get_production("<array>")
        if rule == 21:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.arr_tail()
            self.eat("!!")

    def arr_tail(self):
        # Rules 22-24
        rule = self.get_production("<arr-tail>")
        if rule == 22:
            self.eat("{")
            self.eat("COIN-lit")
            self.eat("}")
            self.arr2_tail()
        elif rule == 23:
            self.eat("=")
            self.eat("[")
            self.arr_val()
            self.eat("]")
        elif rule == 24:
            pass # Lambda

    def arr2_tail(self):
        # Rules 28-29
        rule = self.get_production("<arr2-tail>")
        if rule == 28:
            self.eat("=")
            self.eat("[")
            self.arr2_val()
            self.eat("]")
        elif rule == 29:
            pass # Lambda
            
    def arr_val(self):
        # Rule 25
        rule = self.get_production("<arr-val>")
        if rule == 25:
            self.var_val()
            self.arr_val_tail()
    
    def arr_val_tail(self):
        # Rule 26-27
        rule = self.get_production("<arr-val-tail>")
        if rule == 26:
            self.eat(",")
            self.var_val()
            self.arr_val_tail()
        elif rule == 27:
            pass

    def arr2_val(self):
        # Rule 30
        rule = self.get_production("<arr2-val>")
        if rule == 30:
            self.eat("[")
            self.arr_val()
            self.eat("]")
            self.arr2_val_tail()

    def arr2_val_tail(self):
        # Rule 31-32
        rule = self.get_production("<arr2-val-tail>")
        if rule == 31:
            self.eat(",")
            self.arr2_val()
            self.arr2_val_tail()
        elif rule == 32:
            pass

    def locke_dec(self):
        # Rule 33
        rule = self.get_production("<locke-dec>")
        if rule == 33:
            self.eat("LOCKE")
            self.d_type()
            self.eat("id")
            self.eat("=")
            self.literals()
            self.eat("!!")

    def struct_def(self):
        # Rule 34-35
        rule = self.get_production("<struct-def>")
        if rule == 34:
            self.eat("MAST")
            self.eat("id")
            self.eat("[")
            self.mem_dec()
            self.more_mem()
            self.eat("]")
            self.eat("!!")
            self.struct_def()
            self.sub_func()
        elif rule == 35:
            pass # Lambda

    def mem_dec(self):
        # Rule 36
        rule = self.get_production("<mem-dec>")
        if rule == 36:
            self.d_type()
            self.eat("id")
            self.mem_dec_tail()
            self.eat("!!")
            
    def mem_dec_tail(self):
        # Rule 37-38
        rule = self.get_production("<mem-dec-tail>")
        if rule == 37:
            self.eat(",")
            self.eat("id")
            self.mem_dec_tail()
        elif rule == 38:
            pass
            
    def more_mem(self):
        # Rule 39-40
        rule = self.get_production("<more-mem>")
        if rule == 39:
            self.mem_dec()
        elif rule == 40:
            pass

    # =========================================
    # Expressions (Rules 41 - 121)
    # =========================================

    def var_val(self):
        # Rule 41
        rule = self.get_production("<var-val>")
        if rule == 41:
            self.expression()

    def expression(self):
        # Rule 42
        rule = self.get_production("<expression>")
        if rule == 42:
            self.operands()
            self.exp_tail()

    def operands(self):
        # Rules 43-45
        rule = self.get_production("<operands>")
        if rule == 43:
            self.value()
        elif rule == 44:
            self.eat("(")
            self.expression()
            self.eat(")")
        elif rule == 45:
            self.not_rule()
            self.not_val()

    def value(self):
        # Rules 46-47
        rule = self.get_production("<value>")
        if rule == 46:
            self.eat("id")
            self.id_tail()
        elif rule == 47:
            self.literals()

    def id_tail(self):
        # Rules 48-51
        rule = self.get_production("<id-tail>")
        if rule == 48:
            self.arr_elmt()
        elif rule == 49:
            self.str_mem()
        elif rule == 50:
            self.func_args()
        elif rule == 51:
            pass # Lambda

    def arr_elmt(self):
        # Rule 52
        rule = self.get_production("<arr-elmt>")
        if rule == 52:
            self.eat("{")
            self.arr_index()
            self.eat("}")
            self.arr_elmt_tail()
            
    def arr_index(self):
        # Rule 53-54
        rule = self.get_production("<arr-index>")
        if rule == 53: self.eat("COIN-lit")
        elif rule == 54: self.eat("id")

    def arr_elmt_tail(self):
        # Rule 55-56
        rule = self.get_production("<arr-elmt-tail>")
        if rule == 55:
            self.eat("{")
            self.arr_index()
            self.eat("}")
        elif rule == 56:
            pass

    def str_mem(self):
        # Rule 57
        rule = self.get_production("<str-mem>")
        if rule == 57:
            self.eat("$")
            self.eat("id")

    def func_args(self):
        # Rule 58-59
        rule = self.get_production("<func-args>")
        if rule == 58:
            self.eat("(")
            self.args()
            self.eat(")")
        elif rule == 59:
            pass

    def args(self):
        # Rule 60-61
        rule = self.get_production("<args>")
        if rule == 60:
            self.value()
            self.args_tail()
        elif rule == 61:
            pass

    def args_tail(self):
        # Rule 62-63
        rule = self.get_production("<args-tail>")
        if rule == 62:
            self.eat(",")
            self.value()
        elif rule == 63:
            pass
            
    def literals(self):
        # Rules 64-67
        rule = self.get_production("<literals>")
        if rule == 64: self.digits()
        elif rule == 65: self.bool_lit()
        elif rule == 66: self.eat("PARCH-lit")
        elif rule == 67: 
            self.eat("SCROLL-lit")
            self.arr_elmt_tail()

    def digits(self):
        # Rules 68-69
        rule = self.get_production("<digits>")
        if rule == 68 or rule == 69:
            self.neg()
            self.coin_dime()

    def neg(self):
        # Rule 69-70
        rule = self.get_production("<neg>")
        if rule == 69: self.eat("-")
        elif rule == 70: pass

    def coin_dime(self):
        # Rule 71-72
        rule = self.get_production("<coin-dime>")
        if rule == 71: self.eat("COIN-lit")
        elif rule == 72: self.eat("DIME-lit")
        
    def bool_lit(self):
        # Rule 73-74
        rule = self.get_production("<bool-lit>")
        if rule == 73: self.eat("AYE")
        elif rule == 74: self.eat("NAY")

    def exp_tail(self):
        # Rules 78-80
        rule = self.get_production("<exp-tail>")
        if rule == 78: self.gen_exp()
        elif rule == 79: self.scroll()
        elif rule == 80: pass

    def gen_exp(self):
        # Rules 81-82
        rule = self.get_production("<gen-exp>")
        if rule == 81:
            self.arith()
            self.rel()
            self.logeq()
        elif rule == 82: pass

    def arith(self):
        # Rules 83-84
        rule = self.get_production("<arith>")
        if rule == 83: self.arith_exp()
        elif rule == 84: pass

    def arith_exp(self):
        # Rule 85
        rule = self.get_production("<arith-exp>")
        if rule == 85:
            self.arith_op()
            self.gen_ope()
            self.arith()

    def arith_op(self):
        # Rules 86-91
        rule = self.get_production("<arith-op>")
        if rule == 86: self.eat("+")
        elif rule == 87: self.eat("-")
        elif rule == 88: self.eat("*")
        elif rule == 89: self.eat("/")
        elif rule == 90: self.eat("%")
        elif rule == 91: self.eat("^")

    def gen_ope(self):
        # Rules 92-95
        rule = self.get_production("<gen-ope>")
        if rule == 92:
            self.eat("id")
            self.id_tail()
        elif rule == 93:
            self.digits()
        elif rule == 94:
            self.bool_rule()
        elif rule == 95:
            self.eat("(")
            self.gen_ope() 
            self.gen_exp()
            self.eat(")")

    def bool_rule(self):
        # Rule 45 equivalent for predict check
        rule = self.get_production("<bool>")
        if rule == 45:
            if self.current_token.type in ["!", "!#"]:
                self.not_rule()
                self.not_val()
            else:
                self.bool_lit()

    def not_rule(self):
        # Rule 46
        rule = self.get_production("<not>")
        if self.current_token.type == "!": self.eat("!")
        elif self.current_token.type == "!#": self.eat("!#")
        
    def not_val(self):
        # Rule 47
        rule = self.get_production("<not-val>")
        if self.current_token.type == "id": self.eat("id")
        elif self.current_token.type == "AYE": self.eat("AYE")
        elif self.current_token.type == "NAY": self.eat("NAY")
        elif self.current_token.type == "(": 
            self.eat("(")
            self.expression()
            self.eat(")")

    def rel(self):
        # Rule 99-100
        rule = self.get_production("<rel>")
        if rule == 99:
            self.rel_op()
            self.gen_ope()
            self.arith()
        elif rule == 100: pass

    def rel_op(self):
        # Rules 101-104
        rule = self.get_production("<rel-op>")
        if rule == 101: self.eat("<")
        elif rule == 102: self.eat(">")
        elif rule == 103: self.eat("<=")
        elif rule == 104: self.eat(">=")

    def logeq(self):
        # Rules 105-106
        rule = self.get_production("<logeq>")
        if rule == 105:
            self.logeq_op()
            self.gen_ope()
            self.gen_exp()
        elif rule == 106: pass

    def logeq_op(self):
        # Rules 107-109
        rule = self.get_production("<logeq-op>")
        if rule == 107: self.eat("||")
        elif rule == 108: self.eat("&&")
        elif rule == 109: 
            if self.current_token.type == "==": self.eat("==")
            elif self.current_token.type == "!=": self.eat("!=")

    def scroll(self):
        # Rule 117-118
        rule = self.get_production("<scroll>")
        if rule == 117:
            self.eat("&")
            self.scroll_ope()
            self.scroll()
        elif rule == 118: pass

    def scroll_ope(self):
        # Rule 119-121
        rule = self.get_production("<scroll-ope>")
        if rule == 119:
            self.eat("SCROLL-lit")
            self.arr_elmt_tail()
        elif rule == 120:
            self.eat("id")
            self.id_tail()
        elif rule == 121:
            self.eat("(")
            self.scroll_ope()
            self.scroll()
            self.eat(")")

    # =========================================
    # Functions (Sub, Return, Non-Return)
    # =========================================

    def sub_func(self):
        # Rules 122-124
        rule = self.get_production("<sub-func>")
        if rule == 122:
            self.d_type()
            self.eat("id")
            self.return_func()
        elif rule == 123:
            self.nonreturn_func()
        elif rule == 124:
            pass

    def return_func(self):
        # Rule 125
        rule = self.get_production("<return-func>")
        if rule == 125:
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
        # Rules 126-127
        rule = self.get_production("<func-parameters>")
        if rule == 126:
            self.d_type()
            self.eat("id")
            self.func_tail()
        elif rule == 127: pass

    def func_tail(self):
        # Rules 128-129
        rule = self.get_production("<func-tail>")
        if rule == 128:
            self.eat(",")
            self.d_type()
            self.eat("id")
            self.func_tail()
        elif rule == 129: pass

    def back_val(self):
        # Rules 130-132
        rule = self.get_production("<back-val>")
        if rule == 130: self.literals()
        elif rule == 131: self.eat("id")
        elif rule == 132:
            self.eat("(")
            self.expression()
            self.eat(")")

    def nonreturn_func(self):
        # Rule 133
        rule = self.get_production("<nonreturn-func>")
        if rule == 133:
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
        # Rules 134-135
        rule = self.get_production("<nonreturn-back>")
        if rule == 134:
            self.eat("BACK")
            self.eat("!!")
        elif rule == 135: pass

    def local_dec(self):
        # Rules 136-137
        rule = self.get_production("<local-dec>")
        if rule == 136:
            self.d_type()
            self.eat("id")
            self.var_arr_dec()
            self.local_dec()
        elif rule == 137:
            self.struct()
            
    def struct(self):
        # Rule 140-141
        rule = self.get_production("<struct>")
        if rule == 140:
            self.struct_dec()
            self.struct()
        elif rule == 141: pass

    def struct_dec(self):
        # Rule 142
        rule = self.get_production("<struct-dec>")
        if rule == 142:
            self.eat("MAST")
            self.eat("id")
            self.eat("id")
            self.struct_dec_init()
            self.eat("!!")

    def struct_dec_init(self):
        # Rule 143-145
        rule = self.get_production("<struct-dec-init>")
        if rule == 143:
            self.eat(",")
            self.eat("id")
            self.struct_dec_tail()
        elif rule == 144:
            self.eat("=")
            self.eat("[")
            self.arr_val()
            self.eat("]")
        elif rule == 145: pass

    def struct_dec_tail(self):
        # Rule 146-147
        rule = self.get_production("<struct-dec-tail>")
        if rule == 146:
            self.eat(",")
            self.eat("id")
            self.struct_dec_tail()
        elif rule == 147: pass

    # =========================================
    # Statements (Rules 148 - 156)
    # =========================================

    def statements(self):
        rule = self.get_production("<statements>")
        if rule == 148: self.assign_stmnt()
        elif rule == 149: self.ask_stmnt()
        elif rule == 150: self.echo_stmnt()
        elif rule == 151: self.look_stmnt()
        elif rule == 152: self.chart_stmnt()
        elif rule == 153: self.hoist_stmnt()
        elif rule == 154: self.heave_stmnt()
        elif rule == 155: self.haul_stmnt()
        elif rule == 156: 
            self.unary_exp()
            self.eat("!!")
        
        self.stmnt_tail()

    def stmnt_tail(self):
        rule = self.get_production("<stmnt-tail>")
        if rule == 157:
            self.statements()
        elif rule == 158:
            pass # Lambda

    def assign_stmnt(self):
        # Rule 159
        rule = self.get_production("<assign-stmnt>")
        if rule == 159:
            self.eat("id")
            self.assign_tail()
            self.eat("!!")

    def assign_tail(self):
        # Rule 160-161
        rule = self.get_production("<assign-tail>")
        if rule == 160:
            self.arr_str()
            self.assign_body()
        elif rule == 161:
            self.func_args()

    def arr_str(self):
        # Rule 75-77 (Using for assignment logic)
        rule = self.get_production("<arr-str>")
        if rule == 75: self.arr_elmt()
        elif rule == 76: self.str_mem()
        elif rule == 77: pass
        
    def assign_body(self):
        # Rule 162-163
        rule = self.get_production("<assign-body>")
        if rule == 162:
            self.eat("=")
            self.assign_val()
        elif rule == 163:
            self.arith_assign_op()
            self.expression()

    def assign_val(self):
        # Rule 164-165
        rule = self.get_production("<assign-val>")
        if rule == 164: self.var_val()
        elif rule == 165:
            self.eat("[")
            self.arr_assign()
            self.eat("]")
            
    def arr_assign(self):
        # Rule 166-167
        rule = self.get_production("<arr-assign>")
        if rule == 166: self.arr_val()
        elif rule == 167: self.arr2_val()

    def arith_assign_op(self):
        # Rules 168-173
        rule = self.get_production("<arith-assign-op>")
        if rule == 168: self.eat("+=")
        elif rule == 169: self.eat("-=")
        elif rule == 170: self.eat("*=")
        elif rule == 171: self.eat("/=")
        elif rule == 172: self.eat("%=")
        elif rule == 173: self.eat("^=")

    def ask_stmnt(self):
        # Rule 174
        rule = self.get_production("<ask-stmnt>")
        if rule == 174:
            self.eat("ASK")
            self.eat("(")
            self.eat("SCROLL-lit")
            self.eat(",")
            self.addr()
            self.eat(")")
            self.eat("!!")
            
    def addr(self):
        # Rule 175
        rule = self.get_production("<addr>")
        if rule == 175:
            self.eat("@")
            self.eat("id")
            self.arr_str()
            self.addr_tail()
            
    def addr_tail(self):
        # Rule 176-177
        rule = self.get_production("<addr-tail>")
        if rule == 176:
            self.eat(",")
            self.eat("@")
            self.eat("id")
            self.arr_str()
            self.addr_tail()
        elif rule == 177: pass

    def echo_stmnt(self):
        # Rule 178
        rule = self.get_production("<echo-stmnt>")
        if rule == 178:
            self.eat("ECHO")
            self.eat("(")
            self.eat("SCROLL-lit")
            self.echo_arg()
            self.eat(")")
            self.eat("!!")

    def echo_arg(self):
        # Rule 179-180
        rule = self.get_production("<echo-arg>")
        if rule == 179:
            self.eat(",")
            self.expression()
            self.echo_arg_tail()
        elif rule == 180: pass
        
    def echo_arg_tail(self):
        # Rule 181-182
        rule = self.get_production("<echo-arg-tail>")
        if rule == 181:
            self.eat(",")
            self.expression()
            self.echo_arg_tail()
        elif rule == 182: pass

    def look_stmnt(self):
        # Rule 183
        rule = self.get_production("<look-stmnt>")
        if rule == 183:
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
        # Rule 184
        rule = self.get_production("<cond-exp>")
        if rule == 184:
            self.gen_ope()
            self.gen_exp()

    def sail_stmt(self):
        # Rule 185-186
        rule = self.get_production("<sail-stmt>")
        if rule == 185:
            self.eat("SAIL")
            self.eat("!!")
        elif rule == 186: pass

    def look_tail(self):
        # Rule 187-189
        rule = self.get_production("<look-tail>")
        if rule == 187:
            self.eat("DROPLOOK")
            self.eat("(")
            self.cond_exp()
            self.eat(")")
            self.eat("[")
            self.statements()
            self.sail_stmt()
            self.eat("]")
            self.look_tail()
        elif rule == 188:
            self.eat("DROP")
            self.eat("[")
            self.statements()
            self.sail_stmt()
            self.eat("]")
        elif rule == 189: pass

    def chart_stmnt(self):
        # Rule 190
        rule = self.get_production("<chart-stmnt>")
        if rule == 190:
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
        # Rules 191-192
        rule = self.get_production("<chart-cond>")
        if rule == 191: self.const()
        elif rule == 192: self.eat("id")
        
    def const(self):
        # Rule 193-194
        rule = self.get_production("<const>")
        if rule == 193:
            self.neg()
            self.eat("COIN-lit")
        elif rule == 194:
            self.eat("PARCH-lit")

    def courses(self):
        # Rule 195
        rule = self.get_production("<courses>")
        if rule == 195:
            self.eat("COURSE")
            self.const()
            self.eat(":")
            self.statements()
            self.eat("LAND")
            self.eat("!!")

    def course_tail(self):
        # Rule 196-197
        rule = self.get_production("<course-tail>")
        if rule == 196:
            self.courses()
            self.course_tail()
        elif rule == 197: pass

    def adrift_case(self):
        # Rule 198-199
        rule = self.get_production("<adrift-case>")
        if rule == 198:
            self.eat("ADRIFT")
            self.eat(":")
            self.statements()
            self.eat("LAND")
            self.eat("!!")
        elif rule == 199: pass

    def hoist_stmnt(self):
        # Rule 200
        rule = self.get_production("<hoist-stmnt>")
        if rule == 200:
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
        # Rules 201-203
        rule = self.get_production("<init>")
        if rule == 201:
            self.eat("COIN")
            self.eat("id")
            self.eat("=")
            self.neg()
            self.eat("COIN-lit")
        elif rule == 202:
            self.eat("id")
            self.eat("=")
            self.neg()
            self.eat("COIN-lit")
        elif rule == 203: pass

    def heave_stmnt(self):
        # Rule 204
        rule = self.get_production("<heave-stmnt>")
        if rule == 204:
            self.eat("HEAVE")
            self.eat("(")
            self.cond_exp()
            self.eat(")")
            self.eat("[")
            self.statements()
            self.eat("]")

    def haul_stmnt(self):
        # Rule 205
        rule = self.get_production("<haul-stmnt>")
        if rule == 205:
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
        # Rule 206
        rule = self.get_production("<unary-exp>")
        if rule == 206:
            self.unary_op()
            self.eat("id")

    def unary_op(self):
        # Rules 207-208
        rule = self.get_production("<unary-op>")
        if rule == 207: self.eat("+#")
        elif rule == 208: self.eat("-#")