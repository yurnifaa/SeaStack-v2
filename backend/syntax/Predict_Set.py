# Predict_Set.py
# Maps <Non-Terminal> -> { Token_Type : Production_Number }
# Based on UPDATED - PREDICT SET.pdf and CFG

PREDICT = {
    "<program>": {
        "COIN": 1, "DIME": 1, "PARCH": 1, "SCROLL": 1, "BOOL": 1, "LOCKE": 1, "MAST": 1, "ABYSS": 1, "AHOY": 1
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
        "id": 25, "COIN-lit": 25, "DIME-lit": 25, "PARCH-lit": 25, "SCROLL-lit": 25, 
        "AYE": 25, "NAY": 25, "(": 25, "!": 25, "!#": 25
    },
    "<arr-val-tail>": {
        ",": 26,
        "]": 27, ")": 27 # Lambda
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
    "<locke-init>": {
        "COIN": 34, "DIME": 35, "PARCH": 36, "SCROLL": 37, "BOOL": 38
    },
    "<scr-id>": {
        "{": 39,
        "!!": 40 # Lambda
    },
    "<struct-def>": {
        "MAST": 41,
        "COIN": 42, "DIME": 42, "PARCH": 42, "SCROLL": 42, "BOOL": 42, "ABYSS": 42, "AHOY": 42 # Lambda
    },
    "<mem-dec>": {
        "COIN": 43, "DIME": 43, "PARCH": 43, "SCROLL": 43, "BOOL": 43
    },
    "<mem-dec-tail>": {
        ",": 44,
        "!!": 45 # Lambda
    },
    "<more-mem>": {
        "COIN": 46, "DIME": 46, "PARCH": 46, "SCROLL": 46, "BOOL": 46,
        "]": 47 # Lambda
    },
    "<var-val>": {
        "id": 48, "(": 48, "!": 50, "!#": 50, # Prod 50 is not/not-val/log-eq
        "COIN-lit": 49, "DIME-lit": 49, "PARCH-lit": 49, "SCROLL-lit": 49, "AYE": 49, "NAY": 49
    },
    "<operands>": {
        "id": 51,
        "(": 52
    },
    "<id-tail>": {
        "{": 53,
        "$": 54,
        "(": 55,
        ",": 56, "+": 56, "-": 56, "*": 56, "/": 56, "%": 56, "^": 56, 
        "<": 56, ">": 56, "<=": 56, ">=": 56, "||": 56, "&&": 56, 
        "==": 56, "!=": 56, "&": 56, "!!": 56, "]": 56, ")": 56 # Lambda
    },
    "<arr-elmt>": {
        "{": 57
    },
    "<arr-index>": {
        "id": 58,
        "COIN-lit": 59
    },
    "<arr-elmt-tail>": {
        "{": 60,
        ",": 61, "+": 61, "-": 61, "*": 61, "/": 61, "%": 61, "^": 61, 
        "<": 61, ">": 61, "<=": 61, ">=": 61, "||": 61, "&&": 61, 
        "==": 61, "!=": 61, "&": 61, "!!": 61, "]": 61, ")": 61,
        "=": 61, "+=": 61, "-=": 61, "*=": 61, "/=": 61, "%=": 61, "^=": 61 # Lambda (Including assign ops)
    },
    "<str-mem>": {
        "$": 62
    },
    "<func-args>": {
        "(": 63
    },
    "<args>": {
        "id": 64, "COIN-lit": 64, "DIME-lit": 64, "PARCH-lit": 64, 
        "SCROLL-lit": 64, "AYE": 64, "NAY": 64, "(": 64, "!": 64, "!#": 64,
        ")": 65 # Lambda
    },
    "<literals>": {
        "COIN-lit": 66, "DIME-lit": 66,
        "AYE": 67, "NAY": 67,
        "PARCH-lit": 69, 
        "SCROLL-lit": 68 
    },
    "<digits>": {
        "COIN-lit": 70,
        "DIME-lit": 71
    },
    "<bool-lit>": {
        "AYE": 72,
        "NAY": 73
    },
    "<scroll>": {
        "SCROLL-lit": 74
    },
    "<exp-tail>": {
        "+": 75, "-": 75, "*": 75, "/": 75, "%": 75, "^": 75,
        "<": 76, ">": 76, "<=": 76, ">=": 76,
        "||": 77, "&&": 77,
        "==": 78, "!=": 78,
        "&": 79,
        ",": 80, "!!": 80, ")": 80, "]": 80 # Lambda
    },
    "<digit-tail>": {
        "+": 81, "-": 81, "*": 81, "/": 81, "%": 81, "^": 81,
        "<": 82, ">": 82, "<=": 82, ">=": 82,
        "==": 83, "!=": 83,
        ",": 84, "!!": 84, ")": 84, "]": 84 # Lambda
    },
    "<arith-exp>": {
        "+": 85, "-": 85, "*": 85, "/": 85, "%": 85, "^": 85
    },
    "<arith>": {
        "+": 86, "-": 86, "*": 86, "/": 86, "%": 86, "^": 86
    },
    "<arith-tail>": {
        "+": 87, "-": 87, "*": 87, "/": 87, "%": 87, "^": 87,
        "<": 88, ">": 88, "<=": 88, ">=": 88, "||": 88, "&&": 88, 
        "==": 88, "!=": 88, ",": 88, "!!": 88, "]": 88, ")": 88 # Lambda
    },
    "<arith-op>": {
        "+": 89, "-": 90, "*": 91, "/": 92, "%": 93, "^": 94
    },
    "<arel-ope>": {
        "id": 95,
        "COIN-lit": 96, "DIME-lit": 96,
        "(": 97
    },
    "<rel-exp>": {
        "<": 98, ">": 98, "<=": 98, ">=": 98
    },
    "<rel>": {
        "<": 99, ">": 99, "<=": 99, ">=": 99
    },
    "<rel-op>": {
        "<": 100, ">": 101, "<=": 102, ">=": 103
    },
    "<rel-eq>": {
        "<": 104, ">": 104, "<=": 104, ">=": 104, "==": 104, "!=": 104,
        ",": 105, "!!": 105, ")": 105, "]": 105 # Lambda
    },
    "<rel-eq-exp>": {
        "<": 106, ">": 106, "<=": 106, ">=": 106,
        "==": 107, "!=": 107
    },
    "<eq-arith>": {
        "==": 108, "!=": 108
    },
    "<eq-op>": {
        "==": 109, "!=": 110
    },
    "<log-eq>": {
        "||": 111, "&&": 111,
        "==": 112, "!=": 112,
        ",": 113, "!!": 113, ")": 113, "]": 113 # Lambda
    },
    "<log-exp>": {
        "||": 114, "&&": 114,
        ",": 115, "!!": 115, ")": 115, "]": 115 # Lambda
    },
    "<log-op>": {
        "||": 116, "&&": 117
    },
    "<log-ope>": {
        "id": 118, "COIN-lit": 119, "DIME-lit": 119, "(": 118, "PARCH-lit": 120, "SCROLL-lit": 121,
        "AYE": 122, "NAY": 122,
        "!": 123, "!#": 123 # UPDATED: New Production 123
    },
    "<eq-exp>": {
        "==": 124, "!=": 124 # SHIFTED 123 -> 124
    },
    "<not>": {
        "!": 125, "!#": 126 # SHIFTED 124,125 -> 125,126
    },
    "<not-val>": {
        "id": 127, # SHIFTED 126 -> 127
        "AYE": 128, "NAY": 128, # SHIFTED 127 -> 128
        "(": 129 # SHIFTED 128 -> 129
    },
    "<scroll-tail>": {
        "&": 130, # SHIFTED 129 -> 130
        "==": 131, "!=": 131, # SHIFTED 130 -> 131
        ",": 132, "!!": 132, ")": 132, "]": 132 # Lambda # SHIFTED 131 -> 132
    },
    "<scroll-exp>": {
        "&": 133 # SHIFTED 132 -> 133
    },
    "<concat>": {
        "&": 134 # SHIFTED 133 -> 134
    },
    "<concat-tail>": {
        "&": 135, # SHIFTED 134 -> 135
        "==": 136, "!=": 136, "||": 136, "&&": 136, ",": 136, "!!": 136, ")": 136, "]": 136 # Lambda # SHIFTED 135 -> 136
    },
    "<scroll-ope>": {
        "SCROLL-lit": 137, # SHIFTED 136 -> 137
        "id": 138, # SHIFTED 137 -> 138
        "(": 139 # SHIFTED 138 -> 139
    },
    "<eq-scroll>": {
        "==": 140, "!=": 140, # SHIFTED 139 -> 140
        ",": 141, "!!": 141, ")": 141, "]": 141 # Lambda # SHIFTED 140 -> 141
    },
    "<eq-parch>": {
        "==": 142, "!=": 142, # SHIFTED 141 -> 142
        ",": 143, "!!": 143, ")": 143, "]": 143 # Lambda # SHIFTED 142 -> 143
    },
    "<sub-func>": {
        "COIN": 144, "DIME": 144, "PARCH": 144, "SCROLL": 144, "BOOL": 144, # SHIFTED 143 -> 144
        "ABYSS": 145, # SHIFTED 144 -> 145
        "AHOY": 146 # Lambda # SHIFTED 145 -> 146
    },
    "<return-func>": {
        "(": 147 # SHIFTED 146 -> 147
    },
    "<func-params>": {
        "COIN": 148, "DIME": 148, "PARCH": 148, "SCROLL": 148, "BOOL": 148, # SHIFTED 147 -> 148
        ")": 149 # Lambda # SHIFTED 148 -> 149
    },
    "<func-tail>": {
        ",": 150, # SHIFTED 149 -> 150
        ")": 151 # Lambda # SHIFTED 150 -> 151
    },
    "<nonreturn-func>": {
        "ABYSS": 152 # SHIFTED 151 -> 152
    },
    "<nonreturn-back>": {
        "BACK": 153, # SHIFTED 152 -> 153
        "]": 154 # Lambda # SHIFTED 153 -> 154
    },
    "<local-dec>": {
        "COIN": 155, "DIME": 155, "PARCH": 155, "SCROLL": 155, "BOOL": 155, # SHIFTED 154 -> 155
        "MAST": 156, # SHIFTED 155 -> 156
        "BACK": 157, "id": 157, "ASK": 157, "ECHO": 157, "LOOK": 157, "CHART": 157, "HOIST": 157, "HEAVE": 157, "HAUL": 157, "+#": 157, "-#": 157, "]": 157 # Lambda # SHIFTED 156 -> 157
    },
    "<struct>": {
        "MAST": 158, # SHIFTED 157 -> 158
        "BACK": 159, "id": 159, "ASK": 159, "ECHO": 159, "LOOK": 159, "CHART": 159, "HOIST": 159, "HEAVE": 159, "HAUL": 159, "+#": 159, "-#": 159, "]": 159 # Lambda # SHIFTED 158 -> 159
    },
    "<str-dec>": {
        "MAST": 160 # SHIFTED 159 -> 160
    },
    "<str-dec-init>": {
        "id": 161, # SHIFTED 160 -> 161
        ",": 161, # Fix preserved
        "=": 162, # SHIFTED 161 -> 162
        "!!": 163 # Lambda # SHIFTED 162 -> 163
    },
    "<str-dec-tail>": {
        ",": 164, # SHIFTED 163 -> 164
        "!!": 165 # Lambda # SHIFTED 164 -> 165
    },
    "<str-val>": {
        "id": 166, "COIN-lit": 166, "DIME-lit": 166, "PARCH-lit": 166, "SCROLL-lit": 166, "AYE": 166, "NAY": 166, "(": 166, "!": 166, "!#": 166, # SHIFTED 165 -> 166
        "$": 167 # SHIFTED 166 -> 167
    },
    "<str-val-tail>": {
        ",": 168, # SHIFTED 167 -> 168
        "]": 169 # Lambda # SHIFTED 168 -> 169
    },
    "<statements>": {
        "id": 170, # SHIFTED 169 -> 170
        "ASK": 171, # SHIFTED 170 -> 171
        "ECHO": 172, # SHIFTED 171 -> 172
        "LOOK": 173, # SHIFTED 172 -> 173
        "CHART": 174, # SHIFTED 173 -> 174
        "HOIST": 175, # SHIFTED 174 -> 175
        "HEAVE": 176, # SHIFTED 175 -> 176
        "HAUL": 177, # SHIFTED 176 -> 177
        "+#": 178, "-#": 178 # SHIFTED 177 -> 178
    },
    "<stmnt-tail>": {
        "id": 179, "ASK": 179, "ECHO": 179, "LOOK": 179, "CHART": 179, "HOIST": 179, "HEAVE": 179, "HAUL": 179, "+#": 179, "-#": 179, # SHIFTED 178 -> 179
        "]": 180, "BACK": 180 # Lambda # SHIFTED 179 -> 180
    },
    "<assign-stmnt>": {
        "id": 181 # SHIFTED 180 -> 181
    },
    "<assign-tail>": {
        "{": 182, "$": 182, "=": 182, "+=": 182, "-=": 182, "*=": 182, "/=": 182, "%=": 182, "^=": 182, # SHIFTED 181 -> 182
        "(": 183 # SHIFTED 182 -> 183
    },
    "<arr-str>": {
        "{": 184, # SHIFTED 183 -> 184
        "$": 185, # SHIFTED 184 -> 185
        "=": 186, "+=": 186, "-=": 186, "*=": 186, "/=": 186, "%=": 186, "^=": 186, ",": 186, ")": 186, "!!": 186 # Lambda # SHIFTED 185 -> 186
    },
    "<assign-body>": {
        "=": 187, # SHIFTED 186 -> 187
        "+=": 188, "-=": 188, "*=": 188, "/=": 188, "%=": 188, "^=": 188 # SHIFTED 187 -> 188
    },
    "<assign-val>": {
        "id": 189, "COIN-lit": 189, "DIME-lit": 189, "PARCH-lit": 189, "SCROLL-lit": 189, "AYE": 189, "NAY": 189, "(": 189, "!": 189, "!#": 189, # SHIFTED 188 -> 189
        "[": 190 # SHIFTED 189 -> 190
    },
    "<arr-assign>": {
        "id": 191, "COIN-lit": 191, "DIME-lit": 191, "PARCH-lit": 191, "SCROLL-lit": 191, "AYE": 191, "NAY": 191, "(": 191, "!": 191, "!#": 191, # SHIFTED 190 -> 191
        "[": 192 # SHIFTED 191 -> 192
    },
    "<arith-assign-op>": {
        "+=": 193, "-=": 194, "*=": 195, "/=": 196, "%=": 197, "^=": 198 # SHIFTED 192-197 -> 193-198
    },
    "<ask-stmnt>": {
        "ASK": 199 # SHIFTED 198 -> 199
    },
    "<addr>": {
        "@": 200 # SHIFTED 199 -> 200
    },
    "<addr-tail>": {
        ",": 201, # SHIFTED 200 -> 201
        ")": 202 # Lambda # SHIFTED 201 -> 202
    },
    "<echo-stmnt>": {
        "ECHO": 203 # SHIFTED 202 -> 203
    },
    "<echo-arg>": {
        ",": 204, # SHIFTED 203 -> 204
        ")": 205 # Lambda # SHIFTED 204 -> 205
    },
    "<look-stmnt>": {
        "LOOK": 206 # SHIFTED 205 -> 206
    },
    "<cond-exp>": {
        "id": 207, "COIN-lit": 207, "DIME-lit": 207, "PARCH-lit": 207, "SCROLL-lit": 207, "AYE": 207, "NAY": 207, "(": 207, "!": 207, "!#": 207 # SHIFTED 206 -> 207
    },
    "<jump-stmnt>": {
        "SAIL": 208, # SHIFTED 207 -> 208
        "LAND": 209, # SHIFTED 208 -> 209
        "]": 210, "COURSE": 210, "ADRIFT": 210 # Lambda # SHIFTED 209 -> 210
    },
    "<look-tail>": {
        "DROPLOOK": 211, # SHIFTED 210 -> 211
        "DROP": 212, # SHIFTED 211 -> 212
        "id": 213, "ASK": 213, "ECHO": 213, "LOOK": 213, "CHART": 213, "HOIST": 213, "HEAVE": 213, "HAUL": 213, "+#": 213, "-#": 213, "]": 213, "BACK": 213 # Lambda # SHIFTED 212 -> 213
    },
    "<chart-stmnt>": {
        "CHART": 214 # SHIFTED 213 -> 214
    },
    "<chart-cond>": {
        "COIN-lit": 215, "PARCH-lit": 215, # SHIFTED 214 -> 215
        "id": 216 # SHIFTED 215 -> 216
    },
    "<const>": {
        "COIN-lit": 217, # SHIFTED 216 -> 217
        "PARCH-lit": 218 # SHIFTED 217 -> 218
    },
    "<courses>": {
        "COURSE": 219 # SHIFTED 218 -> 219
    },
    "<course-tail>": {
        "COURSE": 220, # SHIFTED 219 -> 220
        "ADRIFT": 221, "]": 221 # Lambda # SHIFTED 220 -> 221
    },
    "<adrift-case>": {
        "ADRIFT": 222, # SHIFTED 221 -> 222
        "]": 223 # Lambda # SHIFTED 222 -> 223
    },
    "<hoist-stmnt>": {
        "HOIST": 224 # SHIFTED 223 -> 224
    },
    "<init>": {
        "COIN": 225, "DIME": 225, "PARCH": 225, "SCROLL": 225, "BOOL": 225, # SHIFTED 224 -> 225
        "id": 226, # SHIFTED 225 -> 226
        "!!": 227 # Lambda # SHIFTED 226 -> 227
    },
    "<init1>": {
        ",": 228, # SHIFTED 227 -> 228
        "!!": 229 # Lambda # SHIFTED 228 -> 229
    },
    "<init2>": {
        ",": 230, # SHIFTED 229 -> 230
        "!!": 231 # Lambda # SHIFTED 230 -> 231
    },
    "<inc-dec>": {
        "+#": 232, "-#": 232, "id": 232 # SHIFTED 231 -> 232
    },
    "<in-de>": {
        "+#": 233, "-#": 233, # SHIFTED 232 -> 233
        "id": 234 # SHIFTED 233 -> 234
    },
    "<in-de2>": {
        ",": 235, # SHIFTED 234 -> 235
        ")": 236 # Lambda # SHIFTED 235 -> 236
    },
    "<heave-stmnt>": {
        "HEAVE": 237 # SHIFTED 236 -> 237
    },
    "<haul-stmnt>": {
        "HAUL": 238 # SHIFTED 237 -> 238
    },
    "<unary-exp>": {
        "+#": 239, "-#": 239 # SHIFTED 238 -> 239
    },
    "<unary-op>": {
        "+#": 240, # SHIFTED 239 -> 240
        "-#": 241 # SHIFTED 240 -> 241
    }
}