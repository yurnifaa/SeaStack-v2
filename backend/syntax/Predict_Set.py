# Predict_Set.py
# Maps <Non-Terminal> -> { Token_Type : Production_Rule_Number }
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
        "=": 12, ",": 12, "{": 12, "!!": 12,  # Rule 12: Variable/Array
        "(": 13                             # Rule 13: Function
    },
    "<var-arr-dec>": {
        "=": 14, ",": 14, "!!": 14,         # Rule 14: Variable
        "{": 15                             # Rule 15: Array
    },
    "<variable>": {
        "=": 16, ",": 16, "!!": 16
    },
    "<var-init>": {
        "=": 17,
        ",": 18, "!!": 18                   # Rule 18: Lambda
    },
    "<multi-var-init>": {
        ",": 19,
        "!!": 20                            # Rule 20: Lambda
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
    
    # --- EXPRESSIONS (Rules 41-80) ---
    "<var-val>": {
        # Rule 41: This was the missing bridge causing the error
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
    "<exp-tail>": {
        "+": 78, "-": 78, "*": 78, "/": 78, "%": 78, "^": 78, 
        "<": 78, ">": 78, "<=": 78, ">=": 78, "||": 78, "&&": 78, "==": 78, "!=": 78,
        "&": 79,
        ",": 80, "!!": 80, "]": 80, ")": 80
    },

    # --- ARITHMETIC & LOGIC (Rules 81-121) ---
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
        "-": 93, "COIN-lit": 93, "DIME-lit": 93,
        "AYE": 94, "NAY": 94, "!": 94, "!#": 94,
        "(": 95
    },
    "<rel>": {
        "<": 99, ">": 99, "<=": 99, ">=": 99,
        "||": 100, "&&": 100, "==": 100, "!=": 100, ",": 100, "!!": 100, ")": 100, "]": 100
    },
    "<rel-op>": {
        "<": 101, ">": 102, "<=": 103, ">=": 104
    },
    "<logeq>": {
        "||": 105, "&&": 105, "==": 105, "!=": 105,
        ",": 106, "!!": 106, "]": 106, ")": 106
    },
    "<logeq-op>": {
        "||": 107, "&&": 108, "==": 109, "!=": 109
    },
    "<literals>": {
        # From First Set of Literals
        "COIN-lit": 64, "DIME-lit": 64, "-": 64, # digits
        "AYE": 65, "NAY": 65,                    # bool
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

    # --- SCROLL & FUNCTIONS (Rules 117-135) ---
    "<scroll>": {
        "&": 117,
        # Lambda
        ",": 118, "!!": 118, "]": 118, ")": 118
    },
    "<scroll-ope>": {
        "SCROLL-lit": 119, "id": 120, "(": 121
    },
    "<sub-func>": {
        "COIN": 122, "DIME": 122, "PARCH": 122, "SCROLL": 122, "BOOL": 122,
        "ABYSS": 123,
        # Lambda
        "AHOY": 124, "MAST": 124
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

    # --- LOCAL DECLARATIONS (Rules 136-147) ---
    "<local-dec>": {
        # This is the specific rule that fixes your error!
        "COIN": 136, "DIME": 136, "PARCH": 136, "SCROLL": 136, "BOOL": 136,
        "MAST": 137,
        # Lambda (Start of statements)
        "id": 138, "ASK": 138, "ECHO": 138, "LOOK": 138, "CHART": 138, 
        "HOIST": 138, "HEAVE": 138, "HAUL": 138, "+#": 138, "-#": 138,
        "SAIL": 138, "BACK": 138, "]": 138, "LAND": 138
    },
    "<struct>": {
        "MAST": 140,
        # Lambda
        "id": 141, "ASK": 141, "ECHO": 141, "LOOK": 141, "CHART": 141, 
        "HOIST": 141, "HEAVE": 141, "HAUL": 141, "+#": 141, "-#": 141,
        "SAIL": 141, "BACK": 141, "]": 141
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

    # --- STATEMENTS (Rules 148-156) ---
    "<statements>": {
        "id": 148,
        "ASK": 149,
        "ECHO": 150,
        "LOOK": 151,
        "CHART": 152,
        "HOIST": 153,
        "HEAVE": 154,
        "HAUL": 155,
        "+#": 156, "-#": 156
    },
    "<stmnt-tail>": {
        "id": 157, "ASK": 157, "ECHO": 157, "LOOK": 157, "CHART": 157, 
        "HOIST": 157, "HEAVE": 157, "HAUL": 157, "+#": 157, "-#": 157,
        # Lambda
        "BACK": 158, "]": 158, "LAND": 158
    }
}