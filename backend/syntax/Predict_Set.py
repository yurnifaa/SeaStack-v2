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
    # ... (Rules 12-40 omitted for brevity, focusing on Expression/Logic below) ...

    # --- EXPRESSIONS (Rules 41-80) ---
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
        # Lambda (Follow set includes operators, delimiters)
        ",": 51, "+": 51, "-": 51, "*": 51, "/": 51, "%": 51, "^": 51, 
        "<": 51, ">": 51, "<=": 51, ">=": 51, "||": 51, "&&": 51, 
        "==": 51, "!=": 51, "&": 51, "!!": 51, ")": 51, "]": 51
    },
    "<exp-tail>": {
        "+": 78, "-": 78, "*": 78, "/": 78, "%": 78, "^": 78, 
        "<": 78, ">": 78, "<=": 78, ">=": 78, "||": 78, "&&": 78, "==": 78, "!=": 78,
        "&": 79,
        # Lambda
        ",": 80, "!!": 80, "]": 80, ")": 80
    },

    # --- ARITHMETIC & LOGIC (Rules 81-121) ---
    "<gen-exp>": {
        "+": 81, "-": 81, "*": 81, "/": 81, "%": 81, "^": 81, 
        "<": 81, ">": 81, "<=": 81, ">=": 81, "||": 81, "&&": 81, "==": 81, "!=": 81,
        # Lambda
        ",": 82, "!!": 82, "]": 82, ")": 82
    },
    "<arith>": {
        "+": 83, "-": 83, "*": 83, "/": 83, "%": 83, "^": 83,
        # Lambda
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
        # Lambda
        "||": 100, "&&": 100, "==": 100, "!=": 100, ",": 100, "!!": 100, ")": 100, "]": 100
    },
    "<rel-op>": {
        "<": 101, ">": 102, "<=": 103, ">=": 104
    },
    "<logeq>": {
        "||": 105, "&&": 105, "==": 105, "!=": 105,
        # Lambda
        ",": 106, "!!": 106, "]": 106, ")": 106
    },
    "<logeq-op>": {
        "||": 107, "&&": 108, "==": 109, "!=": 109
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