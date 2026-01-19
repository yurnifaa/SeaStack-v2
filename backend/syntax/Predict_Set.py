# Predict_Set.py
# Maps <Non-Terminal> -> { Token_Type : Production_Number }
# None represents Lambda/Epsilon (Empty production)

PREDICT = {
    # --- Program Structure ---
    "<program>": {
        "COIN": 1, "DIME": 1, "PARCH": 1, "SCROLL": 1, "BOOL": 1, "ABYSS": 1, "LOCKE": 1, "MAST": 1, "AHOY": 1
    },
    "<global-dec>": {
        "COIN": 2, "DIME": 2, "PARCH": 2, "SCROLL": 2, "BOOL": 2,
        "LOCKE": 3,
        "MAST": 4,
        "ABYSS": 5,
        "AHOY": 6  # Lambda
    },
    "<d-type>": {
        "COIN": 7, "DIME": 8, "PARCH": 9, "SCROLL": 10, "BOOL": 11
    },
    "<dtype-tail>": {
        "=": 12, ",": 12, "{": 12, "!!": 12,  # Production 12: Variable/Array
        "(": 13                             # Production 13: Function
    },
    "<var-arr-dec>": {
        "=": 14, ",": 14, "!!": 14,         # Production 14: Variable
        "{": 15                             # Production 15: Array
    },
    "<variable>": {
        "=": 16, ",": 16, "!!": 16
    },
    "<var-init>": {
        "=": 17,
        ",": 18, "!!": 18                   # Production 18: Lambda
    },
    "<multi-var-init>": {
        ",": 19,
        "!!": 20                            # Production 20: Lambda
    },
    "<array>": {
        "{": 21
    },
    "<arr-tail>": {
        "{": 22,
        "=": 23,
        "!!": 24                            # Lambda
    },
    "<arr-val>": {
        "id": 25, "-": 25, "COIN-lit": 25, "DIME-lit": 25, "SCROLL-lit": 25, 
        "PARCH-lit": 25, "AYE": 25, "NAY": 25, "(": 25, "!": 25, "!#": 25
    },
    "<arr-val-tail>": {
        ",": 26,
        "]": 27                             # Lambda
    },
    "<arr2-tail>": {
        "=": 28,
        "!!": 29                            # Lambda
    },
    "<arr2-val>": {
        "[": 30
    },
    "<arr2-val-tail>": {
        ",": 31,
        "]": 32                             # Lambda
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
        "!!": 38                            # Lambda
    },
    "<more-mem>": {
        "COIN": 39, "DIME": 39, "PARCH": 39, "SCROLL": 39, "BOOL": 39,
        "]": 40                             # Lambda
    },
    
    # --- EXPRESSIONS ---
    "<var-val>": {
        "(": 41, "id": 41, "-": 41, "COIN-lit": 41, "DIME-lit": 41, 
        "PARCH-lit": 41, "SCROLL-lit": 41, "AYE": 41, "NAY": 41, "!": 41, "!#": 41
    },
    "<expression>": {
        "(": 42, "id": 42, "-": 42, "COIN-lit": 42, "DIME-lit": 42, 
        "PARCH-lit": 42, "SCROLL-lit": 42, "AYE": 42, "NAY": 42, "!": 42, "!#": 42
    },
    "<operands>": {
        "id": 43, "-": 43, "COIN-lit": 43, "DIME-lit": 43, "PARCH-lit": 43, "SCROLL-lit": 43, "AYE": 43, "NAY": 43,
        "(": 44,
        "!": 45, "!#": 45
    },
    "<value>": {
        "id": 46,
        "-": 47, "COIN-lit": 47, "DIME-lit": 47, "PARCH-lit": 47, "SCROLL-lit": 47, "AYE": 47, "NAY": 47
    },
    "<id-tail>": {
        "{": 48,
        "$": 49,
        "(": 50,
        ",": 51, "+": 51, "-": 51, "*": 51, "/": 51, "%": 51, "^": 51, 
        "<": 51, ">": 51, "<=": 51, ">=": 51, "||": 51, "&&": 51, 
        "==": 51, "!=": 51, "&": 51, "!!": 51, ")": 51, "]": 51
    },
    "<arr-elmt>": {
        "{": 52
    },
    "<arr-index>": {
        "COIN-lit": 53,
        "id": 54
    },
    "<arr-elmt-tail>": {
        "{": 55,
        ",": 56, "+": 56, "-": 56, "*": 56, "/": 56, "%": 56, "^": 56, 
        "<": 56, ">": 56, "<=": 56, ">=": 56, "||": 56, "&&": 56, 
        "==": 56, "!=": 56, "&": 56, "!!": 56, ")": 56, "]": 56,
        "=": 56, "+=": 56, "-=": 56, "*=": 56, "/=": 56, "%=": 56, "^=": 56 # Lambda
    },
    "<str-mem>": {
        "$": 57
    },
    "<func-args>": {
        "(": 58,
        ",": 59, "+": 59, "-": 59, "*": 59, "/": 59, "%": 59, "^": 59, 
        "<": 59, ">": 59, "<=": 59, ">=": 59, "||": 59, "&&": 59, 
        "==": 59, "!=": 59, "&": 59, "!!": 59, ")": 59, "]": 59 # Lambda
    },
    "<args>": {
        "id": 60, "-": 60, "COIN-lit": 60, "DIME-lit": 60, "PARCH-lit": 60, "SCROLL-lit": 60, "AYE": 60, "NAY": 60,
        ")": 61 # Lambda
    },
    "<args-tail>": {
        ",": 62,
        ")": 63 # Lambda
    },
    "<exp-tail>": {
        "+": 78, "-": 78, "*": 78, "/": 78, "%": 78, "^": 78, 
        "<": 78, ">": 78, "<=": 78, ">=": 78, "||": 78, "&&": 78, "==": 78, "!=": 78,
        "&": 79,
        ",": 80, "!!": 80, "]": 80, ")": 80
    },

    # --- ARITHMETIC & LOGIC ---
    "<gen-exp>": {
        "+": 81, "-": 81, "*": 81, "/": 81, "%": 81, "^": 81, 
        "<": 81, ">": 81, "<=": 81, ">=": 81, "||": 81, "&&": 81, "==": 81, "!=": 81,
        ",": 82, "!!": 82, "]": 82, ")": 82
    },
    "<arith>": {
        "+": 83, "-": 83, "*": 83, "/": 83, "%": 83, "^": 83,
        "<": 84, ">": 84, "<=": 84, ">=": 84, "||": 84, "&&": 84, 
        "==": 84, "!=": 84, ",": 84, "!!": 84, ")": 84, "]": 84
    },
    "<arith-exp>": {
        "+": 85, "-": 85, "*": 85, "/": 85, "%": 85, "^": 85
    },
    "<arith-op>": {
        "+": 86, "-": 87, "*": 88, "/": 89, "%": 90, "^": 91
    },
    "<gen-ope>": {
        "id": 92,
        "-": 93, "COIN-lit": 93, "DIME-lit": 93, "PARCH-lit": 93, "SCROLL-lit": 93,
        "AYE": 94, "NAY": 94, "!": 94, "!#": 94,
        "(": 95
    },
    "<bool>": {
        "AYE": 96, "NAY": 96,
        "!": 97, "!#": 97
    },
    "<not>": {
        "!": 98, "!#": 99
    },
    "<not-val>": {
        "id": 100, "AYE": 101, "NAY": 101, "(": 102
    },
    "<rel>": {
        "<": 103, ">": 103, "<=": 103, ">=": 103,
        "||": 104, "&&": 104, "==": 104, "!=": 104, ",": 104, "!!": 104, ")": 104, "]": 104 # Lambda
    },
    "<rel-op>": {
        "<": 107, ">": 106, # 105 is skipped in PDF numbering or implicit
        "<=": 107, ">=": 108
    },
    "<logeq>": {
        "||": 109, "&&": 109, "==": 109, "!=": 109,
        ",": 110, "!!": 110, "]": 110, ")": 110
    },
    "<logeq-op>": {
        "||": 111, "&&": 111,
        "==": 112, "!=": 112
    },
    "<log-op>": {
        "||": 113, "&&": 114
    },
    "<equal-op>": {
        "==": 115, "!=": 116
    },
    "<literals>": {
        "COIN-lit": 64, "DIME-lit": 64, "-": 64, 
        "AYE": 65, "NAY": 65,
        "PARCH-lit": 66,
        "SCROLL-lit": 67
    },
    "<digits>": {
        "COIN-lit": 68, "DIME-lit": 68, "-": 68 
    },
    "<neg>": {
        "-": 69,
        "COIN-lit": 70, "DIME-lit": 70 # Lambda
    },
    "<coin-dime>": {
        "COIN-lit": 71,
        "DIME-lit": 72
    },
    "<bool-lit>": {
        "AYE": 73,
        "NAY": 74
    },
    "<arr-str>": {
        "{": 75,
        "$": 76,
        ",": 77, "+": 77, "-": 77, "*": 77, "/": 77, "%": 77, "^": 77, 
        "<": 77, ">": 77, "<=": 77, ">=": 77, "||": 77, "&&": 77, 
        "==": 77, "!=": 77, "&": 77, "!!": 77, ")": 77, "]": 77, "=":77,
        "+=": 77, "-=": 77, "*=": 77, "/=": 77, "%=": 77, "^=": 77 # Lambda
    },

    # --- SCROLL & FUNCTIONS ---
    "<scroll>": {
        "&": 117,
        ",": 118, "!!": 118, "]": 118, ")": 118 # Lambda
    },
    "<scroll-ope>": {
        "SCROLL-lit": 119, "id": 120, "(": 121
    },
    "<sub-func>": {
        "COIN": 122, "DIME": 122, "PARCH": 122, "SCROLL": 122, "BOOL": 122,
        "ABYSS": 123,
        "AHOY": 124, "MAST": 124 # Lambda
    },
    "<return-func>": {
        "(": 125
    },
    "<func-parameters>": {
        "COIN": 126, "DIME": 126, "PARCH": 126, "SCROLL": 126, "BOOL": 126,
        ")": 127 # Lambda
    },
    "<func-tail>": {
        ",": 128,
        ")": 129 # Lambda
    },
    "<back-val>": {
        "COIN-lit": 130, "DIME-lit": 130, "PARCH-lit": 130, "SCROLL-lit": 130, "AYE": 130, "NAY": 130, "-": 130,
        "id": 131,
        "(": 132
    },
    "<nonreturn-func>": {
        "ABYSS": 133
    },
    "<nonreturn-back>": {
        "BACK": 134,
        "]": 135 # Lambda
    },

    # --- LOCAL DECLARATIONS ---
    "<local-dec>": {
        "COIN": 136, "DIME": 136, "PARCH": 136, "SCROLL": 136, "BOOL": 136,
        "MAST": 137
    },
    "<loc-dec-tail>": {
        # Recurse
        "COIN": 138, "DIME": 138, "PARCH": 138, "SCROLL": 138, "BOOL": 138, "MAST": 138,
        # Lambda (Start of statements)
        "id": 139, "ASK": 139, "ECHO": 139, "LOOK": 139, "CHART": 139, 
        "HOIST": 139, "HEAVE": 139, "HAUL": 139, "+#": 139, "-#": 139,
        "SAIL": 139, "BACK": 139, "]": 139, "LAND": 139
    },
    "<struct>": {
        "MAST": 140,
        # Lambda
        "id": 141, "ASK": 141, "ECHO": 141, "LOOK": 141, "CHART": 141, 
        "HOIST": 141, "HEAVE": 141, "HAUL": 141, "+#": 141, "-#": 141,
        "SAIL": 141, "BACK": 141, "]": 141, "LAND": 141
    },
    "<struct-dec>": {
        "MAST": 142
    },
    "<struct-dec-init>": {
        ",": 143,
        "=": 144,
        "!!": 145 # Lambda
    },
    "<struct-dec-tail>": {
        ",": 146,
        "!!": 147 # Lambda
    },

    # --- STATEMENTS ---
    "<statements>": {
        "id": 148,
        "ASK": 149,
        "ECHO": 150,
        "LOOK": 151,
        "CHART": 152,
        "HOIST": 153,
        "HEAVE": 154,
        "HAUL": 155,
        "+#": 156, "-#": 156,
        "]": 139,
        "LAND": 139
    },
    "<stmnt-tail>": {
        "id": 157, "ASK": 157, "ECHO": 157, "LOOK": 157, "CHART": 157, 
        "HOIST": 157, "HEAVE": 157, "HAUL": 157, "+#": 157, "-#": 157,
        # Lambda
        "BACK": 158, "]": 158, "LAND": 158
    },
    "<assign-stmnt>": { "id": 159 },
    "<assign-tail>": { 
        "{": 160, "$": 160, "=": 160, "(": 161,
        "+=": 160, "-=": 160, "*=": 160, "/=": 160, "%=": 160, "^=": 160
    },
    "<assign-body>": { "=": 162, "+=": 163, "-=": 163, "*=": 163, "/=": 163, "%=": 163, "^=": 163 },
    "<assign-val>": {
        "(": 164, "id": 164, "-": 164, "COIN-lit": 164, "DIME-lit": 164, "PARCH-lit": 164, "SCROLL-lit": 164, "AYE": 164, "NAY": 164, "!": 164, "!#": 164,
        "[": 165
    },
    "<arr-assign>": {
        "(": 166, "id": 166, "-": 166, "COIN-lit": 166, "DIME-lit": 166, "PARCH-lit": 166, "SCROLL-lit": 166, "AYE": 166, "NAY": 166, "!": 166, "!#": 166,
        "[": 167
    },
    "<arith-assign-op>": {
        "+=": 168, "-=": 169, "*=": 170, "/=": 171, "%=": 172, "^=": 173
    },
    "<ask-stmnt>": { "ASK": 174 },
    "<addr>": { "@": 175 },
    "<addr-tail>": { ",": 176, ")": 177 },
    "<echo-stmnt>": { "ECHO": 178 },
    "<echo-arg>": { 
        ",": 179, "(": 179, "id": 179, "-": 179, "COIN-lit": 179, "DIME-lit": 179, "PARCH-lit": 179, "SCROLL-lit": 179, "AYE": 179, "NAY": 179, "!": 179, "!#": 179,
        ")": 180 
    },
    "<echo-arg-tail>": { ",": 181, ")": 182 },
    "<look-stmnt>": { "LOOK": 183 },
    "<cond-exp>": {
         "id": 184, "-": 184, "COIN-lit": 184, "DIME-lit": 184, "AYE": 184, "NAY": 184, "!": 184, "!#": 184, "(": 184
    },
    "<sail-stmt>": { "SAIL": 185, "]": 186 },
    "<look-tail>": { "DROPLOOK": 187, "DROP": 188, "id": 189, "ASK": 189, "ECHO": 189, "LOOK": 189, "CHART": 189, "HOIST": 189, "HEAVE": 189, "HAUL": 189, "+#": 189, "-#": 189, "BACK": 189, "]": 189, "LAND": 189 },
    "<chart-stmnt>": { "CHART": 190 },
    "<chart-cond>": {
        "-": 191, "COIN-lit": 191, "PARCH-lit": 191, "id": 192
    },
    "<const>": {
        "-": 193, "COIN-lit": 193, "PARCH-lit": 194
    },
    "<courses>": { "COURSE": 195 },
    "<course-tail>": { "COURSE": 196, "ADRIFT": 197, "]": 197 },
    "<adrift-case>": { "ADRIFT": 198, "]": 199 },
    "<hoist-stmnt>": { "HOIST": 200 },
    "<init>": { "COIN": 201, "id": 202, "!!": 203 },
    "<heave-stmnt>": { "HEAVE": 204 },
    "<haul-stmnt>": { "HAUL": 205 },
    "<unary-exp>": { "+#": 206, "-#": 206 },
    "<unary-op>": { "+#": 207, "-#": 208 }
}