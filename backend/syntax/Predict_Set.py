# Predict_Set.py
# Maps <Non-Terminal> -> { Token_Type : Production_Number }
# Based on UPDATED - CFG.pdf and UPDATED - PREDICT SET.pdf

PREDICT = {
    "<program>": {
        "COIN": 1, "DIME": 1, "PARCH": 1, "SCROLL": 1, "BOOL": 1, "ABYSS": 1, "LOCKE": 1, "MAST": 1, "AHOY": 1
    },
    "<global-dec>": {
        "COIN": 2, "DIME": 2, "PARCH": 2, "SCROLL": 2, "BOOL": 2,
        "LOCKE": 3,
        "MAST": 4,
        "ABYSS": 5,
        "AHOY": 6 # Lambda
    },
    "<d-type>": {
        "COIN": 7, "DIME": 8, "PARCH": 9, "SCROLL": 10, "BOOL": 11
    },
    "<dtype-tail>": {
        "=": 12, ",": 12, "{": 12, "!!": 12, 
        "(": 13
    },
    "<var-arr-dec>": {
        "=": 14, ",": 14, "!!": 14,
        "{": 15
    },
    "<variable>": {
        "=": 16, ",": 16, "!!": 16
    },
    "<var-init>": {
        "=": 17,
        ",": 18, "!!": 18 # Lambda
    },
    "<multi-var-init>": {
        ",": 19,
        "!!": 20 # Lambda
    },
    "<array>": {
        "{": 21
    },
    "<arr-tail>": {
        "{": 22,
        "=": 23,
        "!!": 24 # Lambda
    },
    "<arr-val>": {
        "id": 25, "-": 25, "COIN-lit": 25, "DIME-lit": 25, "SCROLL-lit": 25, 
        "PARCH-lit": 25, "AYE": 25, "NAY": 25, "(": 25, "!": 25, "!#": 25
    },
    "<arr-val-tail>": {
        ",": 26,
        "]": 27 # Lambda
    },
    "<arr2-tail>": {
        "=": 28,
        "!!": 29 # Lambda
    },
    "<arr2-val>": {
        "[": 30
    },
    "<arr2-val-tail>": {
        ",": 31,
        "]": 32 # Lambda
    },
    "<locke-dec>": {
        "LOCKE": 33
    },
    "<struct-def>": {
        "MAST": 34,
        "COIN": 35, "DIME": 35, "PARCH": 35, "SCROLL": 35, "BOOL": 35, "ABYSS": 35, "AHOY": 35 # Lambda
    },
    "<mem-dec>": {
        "COIN": 36, "DIME": 36, "PARCH": 36, "SCROLL": 36, "BOOL": 36
    },
    "<mem-dec-tail>": {
        ",": 37,
        "!!": 38 # Lambda
    },
    "<more-mem>": {
        "COIN": 39, "DIME": 39, "PARCH": 39, "SCROLL": 39, "BOOL": 39,
        "]": 40 # Lambda
    },
    
    # --- EXPRESSIONS & VALUES ---
    "<var-val>": {
        "(": 41, "id": 41, "-": 41, "COIN-lit": 41, "DIME-lit": 41, 
        "PARCH-lit": 41, "SCROLL-lit": 41, "AYE": 41, "NAY": 41, "!": 41, "!#": 41
    },
    "<operands>": {
        "id": 42, "-": 42, "COIN-lit": 42, "DIME-lit": 42, "PARCH-lit": 42, "SCROLL-lit": 42, "AYE": 42, "NAY": 42,
        "(": 43,
        "!": 44, "!#": 44
    },
    "<value>": {
        "id": 45,
        "-": 46, "COIN-lit": 46, "DIME-lit": 46, "PARCH-lit": 46, "SCROLL-lit": 46, "AYE": 46, "NAY": 46
    },
    "<id-tail>": {
        "{": 47,
        "$": 48,
        "(": 49,
        ",": 50, "+": 50, "-": 50, "*": 50, "/": 50, "%": 50, "^": 50, 
        "<": 50, ">": 50, "<=": 50, ">=": 50, "||": 50, "&&": 50, 
        "==": 50, "!=": 50, "&": 50, "!!": 50, ")": 50, "]": 50, "}": 50 # Lambda
    },
    "<arr-elmt>": {
        "{": 51
    },
    "<arr-index>": {
        "COIN-lit": 52,
        "id": 53
    },
    "<arr-elmt-tail>": {
        "{": 54,
        "=": 55, "+=": 55, "-=": 55, "*=": 55, "/=": 55, "%=": 55, "^=": 55,
        ",": 55, "+": 55, "-": 55, "*": 55, "/": 55, "%": 55, "^": 55, 
        "<": 55, ">": 55, "<=": 55, ">=": 55, "||": 55, "&&": 55, 
        "==": 55, "!=": 55, "&": 55, "!!": 55, ")": 55, "]": 55, "}": 55 # Lambda
    },
    "<str-mem>": {
        "$": 56
    },
    "<func-args>": {
        "(": 57,
        ",": 58, "+": 58, "-": 58, "*": 58, "/": 58, "%": 58, "^": 58, 
        "<": 58, ">": 58, "<=": 58, ">=": 58, "||": 58, "&&": 58, 
        "==": 58, "!=": 58, "&": 58, "!!": 58, ")": 58, "]": 58 # Lambda
    },
    "<literals>": {
        "COIN-lit": 59, "DIME-lit": 59, "-": 59, 
        "AYE": 60, "NAY": 60,
        "PARCH-lit": 61,
        "SCROLL-lit": 62
    },
    "<digits>": {
        "COIN-lit": 63, "DIME-lit": 63, "-": 64
    },
    "<neg>": {
        "-": 64,
        "COIN-lit": 65, "DIME-lit": 65 # Lambda
    },
    "<coin-dime>": {
        "COIN-lit": 66,
        "DIME-lit": 67
    },
    "<bool-lit>": {
        "AYE": 68,
        "NAY": 69
    },
    "<arr-str>": {
        "{": 70,
        "$": 71,
        ",": 72, "=": 72, "+=": 72, "-=": 72, "*=": 72, "/=": 72, "%=": 72, "^=": 72 # Lambda
    },
    "<exp-tail>": {
        "+": 73, "-": 73, "*": 73, "/": 73, "%": 73, "^": 73, 
        "<": 73, ">": 73, "<=": 73, ">=": 73, "||": 73, "&&": 73, "==": 73, "!=": 73,
        "&": 74,
        ",": 75, "!!": 75, "]": 75, ")": 75
    },
    "<gen-exp>": {
        "+": 76, "-": 76, "*": 76, "/": 76, "%": 76, "^": 76, 
        "<": 76, ">": 76, "<=": 76, ">=": 76, "||": 76, "&&": 76, "==": 76, "!=": 76,
        ",": 77, "!!": 77, "]": 77, ")": 77 # Lambda
    },
    "<arith>": {
        "+": 78, "-": 78, "*": 78, "/": 78, "%": 78, "^": 78,
        "<": 79, ">": 79, "<=": 79, ">=": 79, "||": 79, "&&": 79, 
        "==": 79, "!=": 79, ",": 79, "!!": 79, ")": 79, "]": 79 # Lambda
    },
    "<arith-exp>": {
        "+": 80, "-": 80, "*": 80, "/": 80, "%": 80, "^": 80
    },
    "<arith-op>": {
        "+": 81, ",": 82, "*": 83, "/": 84, "%": 85, "^": 86
    },
    "<gen-ope>": {
        "id": 87,
        "-": 88, "COIN-lit": 88, "DIME-lit": 88,
        "AYE": 89, "NAY": 89, "!": 89, "!#": 89,
        "(": 90
    },
    "<bool>": {
        "AYE": 91, "NAY": 91,
        "!": 92, "!#": 92
    },
    "<not>": {
        "!": 93, "!#": 94
    },
    "<not-val>": {
        "id": 95, "AYE": 96, "NAY": 96, 
        "(": 97
    },
    "<rel>": {
        "<": 98, ">": 98, "<=": 98, ">=": 98,
        "||": 99, "&&": 99, "==": 99, "!=": 99, ",": 99, "!!": 99, ")": 99, "]": 99 # Lambda
    },
    "<rel-op>": {
        "<": 100, ">": 101, "<=": 102, ">=": 103
    },
    "<logeq>": {
        "||": 104, "&&": 104, "==": 104, "!=": 104,
        ",": 105, "!!": 105, "]": 105, ")": 105 # Lambda
    },
    "<logeq-op>": {
        "||": 106, "&&": 106,
        "==": 107, "!=": 107
    },
    "<log-op>": {
        "||": 108, "&&": 109
    },
    "<equal-op>": {
        "==": 110, "!=": 111
    },
    "<scroll>": {
        "&": 112,
        ",": 113, "!!": 113, "]": 113, ")": 113 # Lambda
    },
    "<scroll-ope>": {
        "SCROLL-lit": 114, "id": 115, "(": 116
    },
    
    # --- FUNCTIONS ---
    "<sub-func>": {
        "COIN": 117, "DIME": 117, "PARCH": 117, "SCROLL": 117, "BOOL": 117,
        "ABYSS": 118,
        "AHOY": 119, "MAST": 119 # Lambda
    },
    "<return-func>": {
        "(": 120
    },
    "<func-parameters>": {
        "COIN": 121, "DIME": 121, "PARCH": 121, "SCROLL": 121, "BOOL": 121,
        ")": 122 # Lambda
    },
    "<func-tail>": {
        ",": 123,
        ")": 124 # Lambda
    },
    "<nonreturn-back>": {
        "BACK": 126,
        "]": 127 # Lambda
    },
    "<local-dec>": {
        "COIN": 128, "DIME": 128, "PARCH": 128, "SCROLL": 128, "BOOL": 128,
        "MAST": 129,
        # Lambda
        "id": 130, "ASK": 130, "ECHO": 130, "LOOK": 130, "CHART": 130, 
        "HOIST": 130, "HEAVE": 130, "HAUL": 130, "+#": 130, "-#": 130
    },
    "<struct>": {
        "MAST": 131,
        # Lambda
        "id": 132, "ASK": 132, "ECHO": 132, "LOOK": 132, "CHART": 132, 
        "HOIST": 132, "HEAVE": 132, "HAUL": 132, "+#": 132, "-#": 132
    },
    "<struct-dec>": {
        "MAST": 133
    },
    "<struct-dec-init>": {
        "id": 134,
        "=": 135,
        "!!": 136 # Lambda
    },
    "<struct-dec-tail>": {
        ",": 137,
        "!!": 138 # Lambda
    },
    "<str-val>": {
        "id": 139, "-": 139, "COIN-lit": 139, "DIME-lit": 139, "PARCH-lit": 139, 
        "SCROLL-lit": 139, "AYE": 139, "NAY": 139, "!": 139, "!#": 139, "(": 139,
        "$": 140
    },
    "<str-val-tail>": {
        "id": 141, "$": 141, # Recurse
        "]": 142, "!!": 142 # Lambda
    },
    
    # --- STATEMENTS ---
    "<statements>": {
        "id": 143,
        "ASK": 144,
        "ECHO": 145,
        "LOOK": 146,
        "CHART": 147,
        "HOIST": 148,
        "HEAVE": 149,
        "HAUL": 150,
        "+#": 151, "-#": 151
    },
    "<stmnt-tail>": {
        "id": 152, "ASK": 152, "ECHO": 152, "LOOK": 152, "CHART": 152, 
        "HOIST": 152, "HEAVE": 152, "HAUL": 152, "+#": 152, "-#": 152,
        # Lambda
        "BACK": 153, "]": 153, "LAND": 153, "SAIL": 153
    },
    "<assign-stmnt>": { "id": 154 },
    "<assign-tail>": { 
        "{": 155, "$": 155, "=": 155, "+=": 155, "-=": 155, "*=": 155, "/=": 155, "%=": 155, "^=": 155,
        "(": 156
    },
    "<assign-body>": { "=": 157, "+=": 158, "-=": 158, "*=": 158, "/=": 158, "%=": 158, "^=": 158 },
    "<assign-val>": {
        "(": 159, "id": 159, "-": 159, "COIN-lit": 159, "DIME-lit": 159, "PARCH-lit": 159, "SCROLL-lit": 159, "AYE": 159, "NAY": 159, "!": 159, "!#": 159,
        "[": 160
    },
    "<arr-assign>": {
        "(": 161, "id": 161, "-": 161, "COIN-lit": 161, "DIME-lit": 161, "PARCH-lit": 161, "SCROLL-lit": 161, "AYE": 161, "NAY": 161, "!": 161, "!#": 161,
        "[": 162
    },
    "<arith-assign-op>": {
        "+=": 163, "-=": 164, "*=": 165, "/=": 166, "%=": 167, "^=": 167, 
        # Typo in PDF? 167 appears twice for %, ^. 
    },
    "<ask-stmnt>": { "ASK": 169 },
    "<addr>": { "@": 170 },
    "<addr-tail>": { ",": 171, ")": 172 },
    "<echo-stmnt>": { "ECHO": 173 },
    "<echo-arg>": { 
        ",": 174,
        ")": 175 
    },
    "<look-stmnt>": { "LOOK": 176 },
    "<cond-exp>": {
         "id": 177, "-": 177, "COIN-lit": 177, "DIME-lit": 177, "AYE": 177, "NAY": 177, "!": 177, "!#": 177, "(": 177
    },
    "<sail-stmt>": { "SAIL": 178, "]": 179 },
    "<look-tail>": { "DROPLOOK": 180, "DROP": 181, 
        "id": 182, "ASK": 182, "ECHO": 182, "LOOK": 182, "CHART": 182, "HOIST": 182, "HEAVE": 182, "HAUL": 182, "+#": 182, "-#": 182, "BACK": 182, "]": 182, "LAND": 182
    },
    "<chart-stmnt>": { "CHART": 183 },
    "<chart-cond>": {
        "-": 184, "COIN-lit": 184, "PARCH-lit": 184, "id": 185
    },
    "<const>": {
        "-": 186, "COIN-lit": 186, "PARCH-lit": 187
    },
    "<courses>": { "COURSE": 188 },
    "<course-tail>": { "COURSE": 189, "ADRIFT": 190, "]": 190 },
    "<adrift-case>": { "ADRIFT": 191, "]": 192 },
    "<hoist-stmnt>": { "HOIST": 193 },
    "<init>": { "COIN": 194, "id": 195, "!!": 196 },
    "<heave-stmnt>": { "HEAVE": 197 },
    "<haul-stmnt>": { "HAUL": 198 },
    "<unary-exp>": { "+#": 199, "-#": 199 },
    "<unary-op>": { "+#": 200, "-#": 201 }
}