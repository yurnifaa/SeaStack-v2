# SeaStack Language Cheat Sheet (LLM Reference)
# AVOID ADDING COMMENTS IN THE PROGRAM. JUST PURE CODE

## Core Rules
- Statement terminator: `!!` (not `;`)
- Blocks enclosed in `[ ]` (not `{ }`)
- Identifiers: start with lowercase letter, only lowercase/digits/underscores, max 20 chars
- Local declarations must be at the TOP of any function body, before any statements
- `AHOY()` is the main function — always at the bottom, no return type, no parameters, no BACK

## Program Structure
```
[global constants]        LOCKE <dtype> <id> = <value>!!
[global variables]        <dtype> <id>!!
[global arrays]           <dtype> <id>{size}!!
[struct definitions]      MAST <id> [ <members> ]!!
[subfunctions]            <dtype> <id>(<params>) [ ... BACK value!! ]
AHOY() [
    [local declarations]
    <statements>
]
```

## Data Types
| Type   | C equiv | Description                        | Example literal    |
|--------|---------|------------------------------------|--------------------|
| COIN   | int     | Whole number, max 16 digits        | `42`, `-7`         |
| DIME   | double  | Decimal, max 16 int + 8 dec digits | `3.14`, `-0.5`     |
| PARCH  | char    | Single char in single quotes       | `'A'`, `'\n'`      |
| SCROLL | string  | String in double quotes            | `"Hello"`          |
| BOOL   | bool    | AYE (true) or NAY (false)          | `AYE`, `NAY`       |
| ABYSS  | void    | Non-returning function return type | —                  |

PARCH escape sequences: `\s`=single quote, `\n`=newline, `\t`=tab, `\0`=null, `\\`=backslash
SCROLL escape sequences: `\d`=double quote, `\n`=newline, `\t`=tab, `\0`=null, `\\`=backslash

## Declarations
```
COIN x!!                          # declare variable
COIN x = 5!!                      # initialize variable
COIN a = 1, b = 2!!               # multiple same-type vars
LOCKE COIN MAX = 100!!            # constant (global only, literal value only)
COIN arr{5}!!                     # 1D array
COIN arr{5} = [1, 2, 3, 4, 5]!!  # 1D array initialized
COIN grid{2}{3}!!                 # 2D array
MAST person [ SCROLL name!! COIN age!! ]!!   # struct definition
MAST person p1!!                  # struct variable (AHOY only)
MAST person p1 = ["Ana", 20]!!   # struct variable initialized
```
- Array index starts at 0. Access: `arr{i}`, `grid{i}{j}`
- Struct member access: `p1$name`

## Operators
| Category     | Operators                          |
|--------------|------------------------------------|
| Arithmetic   | `+` `-` `*` `/` `%` `^`           |
| Assignment   | `=` `+=` `-=` `*=` `/=` `%=` `^=` |
| Unary (prefix, COIN only) | `+#` (increment) `-#` (decrement) |
| Relational   | `<` `>` `<=` `>=` `==` `!=`       |
| Logical      | `&&` `\|\|` `!` `!#` (double-not) |
| Concatenation| `&` (SCROLL only)                  |
| Address      | `@` (used in ASK)                  |
| Member       | `$` (struct member)                |

Precedence (high→low): `(){}$` → `+# -# ! !# -` → `^` → `* / %` → `+ - &` → `< > <= >=` → `== !=` → `&&` → `\|\|` → `= += ...`

## Statements

### Input / Output
```
ASK("%C", @x)!!                      # read COIN into x
ASK("%C%D%S", @a, @b, @c)!!         # read multiple
ECHO("Hello\n")!!                    # print string
ECHO("Val: %C", x)!!                 # print with format specifier
ECHO("Name: %S, Age: %C", n, a)!!   # multiple values
```
Format specifiers: `%C`=COIN, `%D`=DIME, `%P`=PARCH, `%S`=SCROLL, `%B`=BOOL

### Conditional
```
LOOK (condition) [ statements ]
LOOK (x > 0) [ ECHO("pos\n")!! ] DROP [ ECHO("non-pos\n")!! ]
LOOK (x > 90) [ ... ] DROPLOOK (x > 75) [ ... ] DROP [ ... ]

CHART (variable) [
    COURSE 1: ECHO("one")!! LAND!!
    COURSE 2: ECHO("two")!! LAND!!
    ADRIFT:   ECHO("other")!! LAND!!
]
```
- CHART condition must be COIN, PARCH, or SCROLL literal/variable
- COURSE labels must be literals (not variables)
- ADRIFT requires LAND!! at end; SAIL!! is invalid in ADRIFT

### Loops
```
HOIST (COIN i = 0!! i < 10!! +#i) [ ECHO("%C\n", i)!! ]
HEAVE (x > 0) [ -#x!! ]
HAUL [ ECHO("once+\n")!! ] HEAVE (condition)!!
```
- `LAND!!` = break, `SAIL!!` = continue (optional, end of body only)
- No `BACK!!` inside loops or conditionals

### Jump
```
LAND!!    # break from loop or CHART
SAIL!!    # continue to next loop iteration
BACK x!!  # return value from returning function
BACK!!    # return from non-returning function
```

## Functions
```
# Returning function
COIN add(COIN a, COIN b) [
    COIN sum = a + b!!
    BACK sum!!
]

# Non-returning function
ABYSS greet(SCROLL name) [
    ECHO("Hello %S\n", name)!!
]

# Main function
AHOY() [
    COIN result = add(3, 4)!!
    greet("World")!!
    ECHO("Result: %C\n", result)!!
]
```
- Functions defined before AHOY, after global declarations
- Parameters separated by commas: `COIN a, DIME b`
- AHOY cannot be called; cannot have parameters or BACK

## Comments
```
~ single line comment
~( multi-line
   comment )~
```

## Complete Example
```
~ Reverse digit program
COIN reverse_digits(COIN n) [
    COIN rev = 0!!
    COIN rem!!
    HEAVE (n != 0) [
        rem = n % 10!!
        rev = rev * 10 + rem!!
        n /= 10!!
    ]
    BACK rev!!
]

AHOY() [
    COIN num!!
    ECHO("Enter a number: ")!!
    ASK("%C", @num)!!
    ECHO("Reversed: %C\n", reverse_digits(num))!!
]
```
