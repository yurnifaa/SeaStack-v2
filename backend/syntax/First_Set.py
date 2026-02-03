# First_Set.py
# Source: SeaStack Language FIRST SETS
# lambda (epsilon) is represented as None

FIRST = {
    # 1
    "<program>": ["COIN", "DIME", "PARCH", "SCROLL", "BOOL", "LOCKE", "MAST", "ABYSS", "AHOY"],
    # 2
    "<global-dec>": ["COIN", "DIME", "PARCH", "SCROLL", "BOOL", "LOCKE", "MAST", "ABYSS", None],
    # 3
    "<var-arr-func>": ["COIN", "DIME", "PARCH", "SCROLL", "BOOL"],
    # 4
    "<coin-tail>": ["=", ",", "!!", "{", "("],
    # 5
    "<coin-dec>": ["=", ",", "!!", "{"],
    # 6
    "<coin-init>": ["=", None],
    # 7
    "<coin-mult>": [",", None],
    # 8
    "<coin-init-val>": ["id", "(", "COIN-lit"],
    # 9
    "<coin-val>": ["id", "(", "COIN-lit"],
    # 10
    "<coin-ope>": ["id", "(", "COIN-lit"],
    # 11
    "<coin-exp>": ["+", "-", "*", "/", "%", "^", None],
    # 12
    "<arith-op>": ["+", "-", "*", "/", "%", "^"],
    # 13
    "<coin-arr>": ["{"],
    # 14
    "<coin-arr-tail>": ["=", "{", None],
    # 15
    "<coin-arr1>": ["id", "(", "COIN-lit"],
    # 16
    "<coin-arr-val>": ["id", "(", "COIN-lit"],
    # 17
    "<cav-tail>": [",", None],
    # 18
    "<coin-arr2-tail>": ["=", None],
    # 19
    "<coin-arr2>": ["["],
    # 20
    "<cav2-tail>": [",", None],
    # 21
    "<coin-func>": ["("],
    # 22
    "<dime-tail>": ["=", ",", "!!", "{", "("],
    # 23
    "<dime-dec>": ["=", ",", "!!", "{"],
    # 24
    "<dime-init>": ["=", None],
    # 25
    "<dime-mult>": [",", None],
    # 26
    "<dime-init-val>": ["id", "(", "COIN-lit", "DIME-lit"],
    # 27
    "<dime-val>": ["id", "(", "COIN-lit", "DIME-lit"],
    # 28
    "<dime-ope>": ["id", "(", "COIN-lit", "DIME-lit"],
    # 29
    "<digits>": ["COIN-lit", "DIME-lit"],
    # 30
    "<dime-exp>": ["+", "-", "*", "/", "%", "^", None],
    # 31
    "<dime-arr>": ["{"],
    # 32
    "<dime-arr-tail>": ["=", "{", None],
    # 33
    "<dime-arr1>": ["id", "(", "COIN-lit", "DIME-lit"],
    # 34
    "<dime-arr-val>": ["id", "(", "COIN-lit", "DIME-lit"],
    # 35
    "<dav-tail>": [",", None],
    # 36
    "<dime-arr2-tail>": ["=", None],
    # 37
    "<dime-arr2>": ["["],
    # 38
    "<dav2-tail>": [",", None],
    # 39
    "<dime-func>": ["("],
    # 40
    "<parch-tail>": ["=", ",", "!!", "{", "("],
    # 41
    "<parch-dec>": ["=", ",", "!!", "{"],
    # 42
    "<parch-init>": ["=", None],
    # 43
    "<parch-mult>": [",", None],
    # 44
    "<parch-init-val>": ["id", "PARCH-lit"],
    # 45
    "<parch-val>": ["id", "PARCH-lit"],
    # 46
    "<parch-arr>": ["{"],
    # 47
    "<parch-arr-tail>": ["=", "{", None],
    # 48
    "<parch-arr1>": ["id", "PARCH-lit"],
    # 49
    "<parch-arr-val>": ["id", "PARCH-lit"],
    # 50
    "<pav-tail>": [",", None],
    # 51
    "<parch-arr2-tail>": ["=", None],
    # 52
    "<parch-arr2>": ["["],
    # 53
    "<pav2-tail>": [",", None],
    # 54
    "<parch-func>": ["("],
    # 55
    "<scroll-tail>": ["=", ",", "!!", "{", "("],
    # 56
    "<scroll-dec>": ["=", ",", "!!", "{"],
    # 57
    "<scroll-init>": ["=", None],
    # 58
    "<scroll-mult>": [",", None],
    # 59
    "<scroll-init-val>": ["id", "(", "SCROLL-lit"],
    # 60
    "<scroll-val>": ["id", "(", "SCROLL-lit"],
    # 61
    "<scroll-ope>": ["id", "(", "SCROLL-lit"],
    # 62
    "<scr-char>": ["{", None],
    # 63
    "<index>": ["id", "COIN-lit"],
    # 64
    "<scroll-exp>": ["&", None],
    # 65
    "<concat-op>": ["&"],
    # 66
    "<scroll-arr>": ["{"],
    # 67
    "<scroll-arr-tail>": ["=", "{", None],
    # 68
    "<scroll-arr1>": ["id", "(", "SCROLL-lit"],
    # 69
    "<sav-tail>": [",", None],
    # 70
    "<scroll-arr-val>": ["id", "(", "SCROLL-lit"],
    # 71
    "<scroll-arr2-tail>": ["=", None],
    # 72
    "<scroll-arr2>": ["["],
    # 73
    "<sav2-tail>": [",", None],
    # 74
    "<scroll-func>": ["("],
    # 75
    "<bool-tail>": ["=", ",", "!!", "{", "("],
    # 76
    "<bool-dec>": ["=", ",", "!!", "{"],
    # 77
    "<bool-init>": ["=", None],
    # 78
    "<bool-mult>": [",", None],
    # 79
    "<bool-init-val>": ["id", "(", "COIN-lit", "DIME-lit", "PARCH-lit", "SCROLL-lit", "AYE", "NAY", "!", "!#"],
    # 80
    "<bool-val>": ["id", "(", "COIN-lit", "DIME-lit", "PARCH-lit", "SCROLL-lit", "AYE", "NAY", "!", "!#"],
    # 81
    "<bool-ope>": ["id", "(", "COIN-lit", "DIME-lit", "PARCH-lit", "SCROLL-lit", "AYE", "NAY", "!", "!#"],
    # 82
    "<bool-exp2>": ["+", "-", "*", "/", "%", "^", "<", ">", "<=", ">=", "==", "!=", "&", None],
    # 83
    "<bool-arith>": ["+", "-", "*", "/", "%", "^", None],
    # 84
    "<arel-ope>": ["id", "(", "COIN-lit", "DIME-lit"],
    # 85
    "<rel>": ["<", ">", "<=", ">="],
    # 86
    "<rel-op>": ["<", ">", "<=", ">="],
    # 87
    "<rel-tail>": ["==", "!=", None],
    # 88
    "<eq-op>": ["==", "!="],
    # 89
    "<eq-ope>": ["COIN-lit", "DIME-lit", "PARCH-lit", "SCROLL-lit", "AYE", "NAY", "!", "!#"],
    # 90
    "<concat>": ["&"],
    # 91
    "<bool-scroll>": ["id", "(", "SCROLL-lit"],
    # 92
    "<bool-concat>": ["&", None],
    # 93
    "<concat-tail>": ["==", "!="],
    # 94
    "<bool-digit>": ["COIN-lit", "DIME-lit"],
    # 95
    "<rel-eq>": ["<", ">", "<=", ">=", "==", "!="],
    # 96
    "<bool-parch>": ["id", "PARCH-lit"],
    # 97
    "<scroll>": ["SCROLL-lit"],
    # 98
    "<bool>": ["AYE", "NAY", "!", "!#"],
    # 99
    "<bool-lit>": ["AYE", "NAY"],
    # 100
    "<not-op>": ["!", "!#"],
    # 101
    "<not-val>": ["id", "(", "AYE", "NAY"],
    # 102
    "<log-tail>": ["==", "!=", None],
    # 103
    "<bool-exp>": ["||", "&&", None],
    # 104
    "<log-op>": ["||", "&&"],
    # 105
    "<bool-arr>": ["{"],
    # 106
    "<bool-arr-tail>": ["=", "{", None],
    # 107
    "<bool-arr1>": ["id", "(", "COIN-lit", "DIME-lit", "PARCH-lit", "SCROLL-lit", "AYE", "NAY", "!", "!#"],
    # 108
    "<bav-tail>": [",", None],
    # 109
    "<bool-arr-val>": ["id", "(", "COIN-lit", "DIME-lit", "PARCH-lit", "SCROLL-lit", "AYE", "NAY", "!", "!#"],
    # 110
    "<bool-arr2-tail>": [",", None],
    # 111
    "<bool-arr2>": ["["],
    # 112
    "<bav2-tail>": [",", None],
    # 113
    "<bool-func>": ["("],
    # 114
    "<params>": ["COIN", "DIME", "PARCH", "SCROLL", "BOOL"],
    # 115
    "<param-mult>": [",", None],
    # 116
    "<d-type>": ["COIN", "DIME", "PARCH", "SCROLL", "BOOL"],
    # 117
    "<ret-stmts>": ["id", "ASK", "ECHO", "LOOK", "CHART", "HOIST", "HEAVE", "HAUL", "+#", "-#"],
    # 118
    "<id-tail>": ["{", "$", "("],
    # 119
    "<elmt>": ["{"],
    # 120
    "<elmt-tail>": ["{", None],
    # 121
    "<mem>": ["$"],
    # 122
    "<func>": ["("],
    # 123
    "<args>": ["id", "(", "COIN-lit", "DIME-lit", "PARCH-lit", "&", "AYE", "NAY", "!", "!#", None],
    # 124
    "<args-mult>": [",", None],
    # 125
    "<var-val>": ["id", "(", "COIN-lit", "DIME-lit", "PARCH-lit", "&", "AYE", "NAY", "!", "!#"],
    # 126
    "<value>": ["id", "(", "COIN-lit", "DIME-lit", "PARCH-lit", "&", "AYE", "NAY", "!", "!#"],
    # 127
    "<var-log>": ["||", "&&", None],
    # 128
    "<var-exp>": ["+", "-", "*", "/", "%", "^", "<", ">", "<=", ">=", "||", "&&", "==", "!=", "&", None],
    # 129
    "<expressions>": ["+", "-", "*", "/", "%", "^", "<", ">", "<=", ">=", "||", "&&", "==", "!=", "&"],
    # 130
    "<var-arith>": ["+", "-", "*", "/", "%", "^", None],
    # 131
    "<var-rel>": ["<", ">", "<=", ">=", None],
    # 132
    "<log-ope>": ["id", "(", "COIN-lit", "DIME-lit", "PARCH-lit", "SCROLL-lit", "AYE", "NAY", "!", "!#"],
    # 133
    "<var-scroll>": ["&", None],
    # 134
    "<eq-scroll>": ["==", "!="],
    # 135
    "<var-bool>": ["AYE", "NAY", "!", "!#"],
    # 136
    "<var-digit>": ["COIN-lit", "DIME-lit"],
    # 137
    "<digit-tail>": ["+", "-", "*", "/", "%", "^", "<", ">", "<=", ">=", "==", "!=", None],
    # 138
    "<eq-parch>": ["==", "!="],
    # 139
    "<var-releq>": ["<", ">", "<=", ">=", "==", "!=", None],
    # 140
    "<releq-op>": ["<", ">", "<=", ">=", "==", "!="],
    # 141
    "<var-logeq>": ["||", "&&", "==", "!=", None],
    # 142
    "<logeq-op>": ["||", "&&", "==", "!="],
    # 143
    "<const>": ["LOCKE", "COIN-lit", "PARCH-lit"],
    # 144
    "<const-init>": ["COIN", "DIME", "PARCH", "SCROLL", "BOOL"],
    # 145
    "<coin-locke>": ["id"],
    # 146
    "<coin-locke-mult>": [",", None],
    # 147
    "<dime-locke>": ["id"],
    # 148
    "<locke-digit>": ["COIN-lit", "DIME-lit"],
    # 149
    "<dime-locke-mult>": [",", None],
    # 150
    "<parch-locke>": ["id"],
    # 151
    "<parch-locke-mult>": [",", None],
    # 152
    "<scroll-locke>": ["id"],
    # 153
    "<scr-id>": ["{", None],
    # 154
    "<scroll-locke-mult>": [",", None],
    # 155
    "<bool-locke>": ["id"],
    # 156
    "<locke-bool>": ["AYE", "NAY"],
    # 157
    "<bool-locke-mult>": [",", None],
    # 158
    "<struct>": ["MAST", None],
    # 159
    "<mem-dec>": ["COIN", "DIME", "PARCH", "SCROLL", "BOOL"],
    # 160
    "<mem-mult>": [",", None],
    # 161
    "<mem-dec-tail>": ["COIN", "DIME", "PARCH", "SCROLL", "BOOL", None],
    # 162
    "<ahoy-stmnts>": ["id", "ASK", "ECHO", "LOOK", "CHART", "HOIST", "HEAVE", "HAUL", "+#", "-#"],
    # 163
    "<sub-func>": ["COIN", "DIME", "PARCH", "SCROLL", "BOOL", "ABYSS", None],
    # 164
    "<return-func>": ["COIN", "DIME", "PARCH", "SCROLL", "BOOL"],
    # 165
    "<nonreturn-func>": ["ABYSS"],
    # 166
    "<nonret-stmnts>": ["id", "ASK", "ECHO", "LOOK", "CHART", "HOIST", "HEAVE", "HAUL", "+#", "-#"],
    # 167
    "<nonret-back>": ["BACK", None],
    # 168
    "<local-dec>": ["COIN", "DIME", "PARCH", "SCROLL", "BOOL", "MAST", None],
    # 169
    "<var-arr>": ["COIN", "DIME", "PARCH", "SCROLL", "BOOL"],
    # 170
    "<coin-local>": ["=", ",", "!!", "{"],
    # 171
    "<dime-local>": ["=", ",", "!!", "{"],
    # 172
    "<parch-local>": ["=", ",", "!!", "{"],
    # 173
    "<scroll-local>": ["=", ",", "!!", "{"],
    # 174
    "<bool-local>": ["=", ",", "!!", "{"],
    # 175
    "<struct-dec>": ["MAST", None],
    # 176
    "<str-dec-init>": [",", "=", None],
    # 177
    "<str-dec-tail>": [",", None],
    # 178
    "<str-val>": ["id", "(", "COIN-lit", "DIME-lit", "PARCH-lit", "&", "AYE", "NAY", "!", "!#", "$"],
    # 179
    "<str-val-tail>": [",", None],
    # 180
    "<statements>": ["id", "ASK", "ECHO", "LOOK", "CHART", "HOIST", "HEAVE", "HAUL", "+#", "-#"],
    # 181
    "<stmnt-tail>": ["id", "ASK", "ECHO", "LOOK", "CHART", "HOIST", "HEAVE", "HAUL", "+#", "-#", None],
    # 182
    "<assign-stmnt>": ["id"],
    # 183
    "<assign-tail>": ["{", "$", "=", "+=", "-=", "*=", "/=", "%=", "^=", "("],
    # 184
    "<arr-str>": ["{", "$", None],
    # 185
    "<elmt-tail2>": ["{", None],
    # 186
    "<assignbody->": ["=", "+=", "-=", "*=", "/=", "%=", "^="],
    # 187
    "<assign-val>": ["id", "(", "COIN-lit", "DIME-lit", "PARCH-lit", "&", "AYE", "NAY", "!", "!#"],
    # 188
    "<arith-assign-op>": ["+=", "-=", "*=", "/=", "%=", "^="],
    # 189
    "<arith-ope>": ["id", "(", "COIN-lit", "DIME-lit"],
    # 190
    "<arith-tail>": ["+", "-", "*", "/", "%", "^", None],
    # 191
    "<ask-stmnt>": ["ASK"],
    # 192
    "<addr>": ["@"],
    # 193
    "<id-addr>": ["{", "$"],
    # 194
    "<addr-tail>": [",", None],
    # 195
    "<echo-stmnt>": ["ECHO"],
    # 196
    "<echo-arg>": [",", None],
    # 197
    "<echo-val>": ["id", "(", "COIN-lit", "DIME-lit", "PARCH-lit", "&", "AYE", "NAY", "!", "!#"],
    # 198
    "<look-stmnt>": ["LOOK"],
    # 199
    "<condition>": ["id", "(", "COIN-lit", "DIME-lit", "PARCH-lit", "SCROLL-lit", "AYE", "NAY", "!", "!#"],
    # 200
    "<look-body>": ["id", "ASK", "ECHO", "LOOK", "CHART", "HOIST", "HEAVE", "HAUL", "+#", "-#", "SAIL", "LAND"],
    # 201
    "<jump-stmnt>": ["SAIL", "LAND", None],
    # 202
    "<look-tail>": ["DROPLOOK", "DROP", None],
    # 203
    "<chart-stmnt>": ["CHART"],
    # 204
    "<chart-cond>": ["LOCKE", "COIN-lit", "PARCH-lit", "id"],
    # 205
    "<courses>": ["COURSE"],
    # 206
    "<course-body>": ["id", "ASK", "ECHO", "LOOK", "CHART", "HOIST", "HEAVE", "HAUL", "+#", "-#", "SAIL", "LAND"],
    # 207
    "<course-tail>": ["COURSE", None],
    # 208
    "<adrift-case>": ["ADRIFT"],
    # 209
    "<adrift-body>": ["id", "ASK", "ECHO", "LOOK", "CHART", "HOIST", "HEAVE", "HAUL", "+#", "-#"],
    # 210
    "<hoist-stmnt>": ["HOIST"],
    # 211
    "<init>": ["COIN", "id", None],
    # 212
    "<id-init>": ["{", "$"],
    # 213
    "<init1>": [",", None],
    # 214
    "<init2>": [",", None],
    # 215
    "<hoist-cond>": ["id"],
    # 216
    "<id-cond>": ["{", "$"],
    # 217
    "<hoist-ope>": ["COIN-lit", "id"],
    # 218
    "<hoist-log>": ["||", "&&", None],
    # 219
    "<inc-dec>": ["id", "+#", "-#"],
    # 220
    "<in-de>": ["id", "+#", "-#"],
    # 221
    "<in-de2>": [",", None],
    # 222
    "<heave-stmnt>": ["HEAVE"],
    # 223
    "<haul-stmnt>": ["HAUL"],
    # 224
    "<unary-exp>": ["+#", "-#"],
    # 225
    "<unary-op>": ["+#", "-#"]
}