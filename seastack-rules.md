**Table of Contents**

[**Overview of the Programming Language	2**](#overview-of-the-programming-language)

[**I. STRUCTURE OVERVIEW	3**](#structure-overview)

[**II. GENERAL RULES	4**](#general-rules)

[**III. SPECIFIC RULES	11**](#specific-rules)

[DECLARATIONS	11](#declarations)

[DATA TYPES AND LITERALS	12](#data-types-and-literals)

[IDENTIFIERS	18](#identifiers)

[VARIABLES	19](#variables)

[CONSTANTS	21](#constants)

[ARRAYS	22](#arrays)

[STRUCTURES	25](#structures)

[OPERATORS	30](#operators)

[OPERATOR PRECEDENCE	34](#operator-precedence)

[EXPRESSIONS	35](#expressions)

[STATEMENTS	40](#statements)

[FUNCTIONS	59](#functions)

[COMMENTS	66](#comments)

[**IV. REGULAR DEFINITION	67**](#regular-definition)

[**V. REGULAR EXPRESSION	69**](#regular-expression)

[**VI. TRANSITION DIAGRAM	73**](#transition-diagram)

[RESERVED WORDS	73](#reserved-words)

[RESERVED SYMBOLS	76](#reserved-symbols)

[IDENTIFIERS	80](#identifiers-1)

[COIN LITERALS	82](#coin-literals)

[DIME LITERALS	84](#dime-literals)

[PARCH AND SCROLL LITERALS	85](#parch-and-scroll-literals)

[COMMENTS	85](#comments-1)

[**VII. CONTEXT FREE GRAMMAR	86**](#context-free-grammar)

[**VIII. FIRST SET	102**](#first-set)

[**IX. FOLLOW SET	111**](#follow-set)

[**X. PREDICT SET	119**](#predict-set)

[**XI. TEST SCRIPTS	151**](#test-scripts)

# **Overview of the Programming Language** {#overview-of-the-programming-language}

SeaStack is a high-level programming language designed to combine structured programming principles with a thematic and engaging syntax inspired by the ocean voyager theme. It takes its foundation from the C language, adapting familiar constructs such as functions, loops, conditionals, and structures while introducing an oceanic twist to make coding both intuitive and enjoyable.

The integration of the Ocean Voyager theme enhances the language by aligning programming commands with navigational and seafaring terms. This thematic consistency creates an immersive environment that not only strengthens recall of syntax but also sparks creativity in the programming experience.

SeaStack supports a wide range of constructs, including global and local declarations, expressions, statements, arrays, structures, and user-defined functions that enable programmers to implement both simple and complex logic. These features make SeaStack suitable for learning core programming concepts, developing simple yet structured algorithms, and introducing problem-solving skills more interactively.

Overall, the SeaStack programming language makes programming accessible and enjoyable by combining solid foundations with a creative oceanic theme. It encourages learners to see coding as a voyage of discovery, emphasizing clarity, engagement, and a fun learning experience.

1. # **STRUCTURE OVERVIEW** {#structure-overview}

| \<global\_declaration/s\> | λ LOCKE \<DATA\_TYPE\> \<id\> \= \<value\>\!\!          \~ Global Constant | λ \<DATA\_TYPE\> \<id\>\!\!                                         \~ Global Variable | λ \<DATA\_TYPE\> \<id\>{\<size\>}\!\!                           \~ Global Array | λ  MAST \<id\> \[                                                        \~ Structure Definition | λ      \<member declaration/s\> \]\!\!   \<DATA\_TYPE\> \<id\>(\<parameter/s\>) \[           \~ Returning Function | λ     \<local\_declaration/s\> | λ     \<statement/s\> | λ                 BACK \<return\_value\>\!\!                              \]    ABYSS \<id\>(\<parameter/s\>) \[                         \~ Non-returning Function | λ    \<local\_declaration/s\> | λ    \<statement/s\>     BACK\!\!  | λ \]    \~\~ muti-line  comment \~\~  AHOY() \[                                                              \~ Main Program    \<local\_declaration/s\> | λ    \<DATA\_TYPE\> \<id\>\!\!                                      \~ Local Variable | λ    \<DATA\_TYPE\> \<id\>{\<size\>}\!\!                        \~ Local Array | λ     MAST \<id\> \<variable/s\> \!\!                            \~ Structure Declaration | λ      \<statement/s\>  \] |
| :---- |

2. # **GENERAL RULES** {#general-rules}

     
1. SeaStack supports variables, constants, arrays, structures, expressions, statements, subfunctions, comments, and a single AHOY function. It also supports global and local declarations.  
2. Global declarations include variables, constants, arrays, and structure and function definition. These are located at the start of the program and can be accessed or modified anywhere within the program.   
3. Local declarations include variables, arrays, and structure variables, and it overrides global declarations of the same name and type. These are declared at the start of any function body and can only be accessed or modified within the function in which they are declared.  
4. SeaStack uses two exclamation marks (**\!\!**) as a statement terminator.  
5. The body of functions, structures, conditional statements and looping statements, as well as the initial values of an array and structure variable, must be enclosed within a pair of square brackets ( **\[ \]** ).  
6. SeaStack recognizes the following reserved words as data types: COIN, DIME, PARCH, SCROLL, and BOOL.  
7. COIN is any whole number. It must contain at least one (**1**) digit and may contain up to sixteen (**16**) digits only. Leading zeros are not allowed.  
8. DIME is any number with a decimal component. The integer part must contain at least one (**1**) digit and may contain up to sixteen (**16**) digits only. The decimal part may contain up to eight (**8**) digits. Leading zeroes, and trailing zeroes exceeding 8 digits, are not allowed.  
9. PARCH is any single ASCII character, except newline and single quotation mark, or a single escape sequence, enclosed in a pair of single quotation marks (**' '**).  
10. SCROLL is any sequence of ASCII characters, except newline and double quotation marks, enclosed in a pair of double quotation marks (**" "**).  
11. BOOL can be either AYE (**true**) or NAY (**false**) only.  
12. Identifiers are used to name variables, constants, arrays, structures, structure member or variable, and subfunctions. It must only start with a lowercase letter, and can be followed by a sequence of lowercase letters, digits, and underscores only. Identifiers should have a length of at least one (**1**) and at most twenty (**20**) valid characters.  
13. Variables are values that can be accessed and modified in the program. It is declared with the data type, then the identifier, and the statement terminator.  
14. Constants are fixed values that can be accessed but cannot be modified in the program. It must be initialized at the time of declaration, beginning with the reserved word LOCKE, then the data type, identifier, assignment operator (**\=**), the assigned value, and the statement terminator.  
15. Arrays are collections of elements that share the same data type. An array declaration begins with the data type, then the identifier, a fixed size enclosed in curly braces ( **{ }** ), and the statement terminator. Arrays in SeaStack can be either one-dimensional or two-dimensional only.  
16. Structures are groups of several related variables of different data types. It is defined after the declaration of any global constant, variable, or array, and before any function. It starts with the reserved word MAST, followed by the identifier, then the member declaration enclosed in square brackets, and ends with the statement terminator.  
17. A structure variable can only be declared inside the AHOY function. It must start with the reserved word MAST, followed by the structure member identifier, then the variable identifier, and end with the statement terminator.  
18. SeaStack supports arithmetic, assignment, unary, relational, logical, and concatenation operators. Operators follow the given operator precedence rule.  
19. Operators must not appear consecutively without any operand in between.   
20. SeaStack supports arithmetic, relational, logical, unary, and SCROLL expressions.  
21. Arithmetic expressions perform mathematical calculations on operands of type COIN or DIME only with arithmetic operators (**\+**, **\-**, **\***, **/**, **%**, **^**).   
22. Relational expressions compare exactly two operands of type COIN or DIME only with less than (**\<**), greater than (**\>**), less than or equal (**\<=**), or greater than or equal (**\>=**) operators. Relational expressions using the operators equal to (**\==**) or not equal to (**\!=**) can compare two operands of any compatible data type.  
23. Logical expressions compare operands of type BOOL only with logical operators (**\!**, **\!\#**, **||, &&**).   
24. Unary expressions perform increment or decrement on operands of type COIN only with unary operators (**\+\#**, **\-\#**) as prefix.  
25. SCROLL expressions combine operands of type SCROLL with the concatenation operator (**&**).  
26. SeaStack supports input, output, assignment, conditional, looping, and jump statements.  
27. Input statements use the reserved word ASK to get user input, while output statements use the reserved word ECHO to display output.  
28. Assignment statements assign a value to the left-hand operand with the assignment operators (**\=**, **\+=**, **\-=**, **\*=**, **/=**, **%=, ^=**).   
29. Conditional statements execute when a certain condition is met. LOOK, DROP, DROPLOOK, and CHART are reserved words used for conditional statements. The body of conditional statements must be enclosed within square brackets.  
30. Looping statements execute repeatedly based on a given condition. HOIST, HEAVE, and HAUL-HEAVE are reserved words used for looping statements. The body of looping statements must be enclosed within square brackets.  
31. Jump statements immediately execute a block of code in another part of the program. LAND, SAIL, and BACK are reserved words used for jump statements.   
32. The AHOY function serves as the main function, found at the end of the program. It must not have a return type, not include any parameter, and not have any BACK statement. It cannot be called by any function.  
33. Subfunctions must be defined after the declaration of any global constant, variable, array, or structure definition, and before the AHOY function. It can either be a returning or nonreturning function. It must begin with a return type, followed by a unique identifier, then a pair of parentheses ( **( )** ) with an optional parameter list inside, and the body enclosed within square brackets ( **\[ \]** ).   
34. Returning functions must have a single BACK statement located at the end of the body. Statements, excluding the single BACK statement, are optional.  
35. Nonreturning functions and the AHOY function must have at least one statement, excluding jump statements.  
36. A returning function can only have a return type of COIN, DIME, PARCH, SCROLL, or BOOL and must end with a single BACK statement that returns a value matching the declared return type.  
37. A nonreturning function must only have a return type of ABYSS and must not return any value. It can end with a single BACK statement without a return value.  
38. Comments are ignored during execution. A single-line comment starts with a tilde symbol (**\~**) followed by a sequence of characters, and ends with a newline.  
39. A multi-line comment starts with a tilde and open parenthesis ( **\~(** ), and is enclosed with a closing parenthesis followed by a tilde ( **)\~**  ). A multi-line comment that is not enclosed is invalid.

**RESERVED WORDS** 

| Reserved Words | C Equivalent | Definition |
| :---: | :---: | ----- |
| **ABYSS** | void | Indicates that it will not return a value. |
| **ADRIFT** | default | Runs if no COURSE matches in a CHART statement. |
| **AHOY** | main | The starting or entry point of the program. |
| **ASK** | scanf | Reads input from the standard input stream. |
| **AYE** | true | Represents the value true. |
| **BACK** | return | Exits a function and optionally passes a value. |
| **BOOL** | bool | Used to store Boolean values, AYE (true) or NAY (false). |
| **CHART** | switch | Executes a block of code based on the value of an expression. |
| **COIN** | int  | Represents whole numbers. |
| **COURSE** | case | Defines a branch inside a CHART statement. |
| **DIME** | double | Represents numbers with a decimal part. |
| **DROP** | else | Executes a block of code if the previous LOOK is false. |
| **DROPLOOK** | else if | Tests multiple conditions after an initial LOOK. |

| Reserved Words | C Equivalent | Definition |
| :---: | :---: | ----- |
| **ECHO** | printf | Prints output to the standard output stream. |
| **HAUL-HEAVE** | do-while | Creates a loop that executes once and loops while the condition is true. |
| **HEAVE** | while | Creates a loop that runs as long as a condition is true. |
| **HOIST**  | for | Creates a loop that runs a fixed number of times. |
| **LAND** | break | Used to exit from a loop or CHART statement. |
| **LOCKE** | const | Defines an initial value that cannot be modified. |
| **LOOK** | if | Executes a block of code if the condition is true. |
| **MAST** | struct | Defines a collection of variables of different data types. |
| **NAY** | false | Represents the value false. |
| **PARCH** | char | Represents a single character. |
| **SAIL** | continue | Skips the loop and jumps to the next iteration. |
| **SCROLL** | string | Represents a sequence of characters. |

**RESERVED SYMBOLS**

| Operators |  |
| :---: | :---: |
| Arithmetic Operators | **\+** ,  **\-** , **\*** , **/** , **%, ^** |
| Assignment Operators | **\=** , **\+=** , **\-=** , **\*=** , **/=** , **%=, ^=** |
| Unary Operators | **\+\#** , **\-\#** |
| Relational Operators | **\<** , **\>** , **\<=** , **\>=** ,  **\==** , **\!=** |
| Logical Operators | **\!** , **\!\#** , **||** , **&&**  |
| Concatenation Operator | **&** |

| Other Symbols |  |
| :---: | ----- |
| **RESERVED SYMBOLS** | **DEFINITION** |
| **@** | Used as a prefix to reference a variable. |
| **$** | Used to access the member of a structure variable. |
| **,** | Used to separate values. |
| **:** | Used to indicate the start of a COURSE’s body. |
| **{** | Used to enclose the size or index of an array or the character of a SCROLL. |
| **}** |  |
| **(** | Used to enclose parameters, arguments, grouped expressions, or conditions. |
| **)** |  |
| **\[** | Used to enclose a block of statements, initial values of an array, and member declaration or member initialization of a structure. |
| **\]** |  |

| Other Symbols |  |
| :---: | ----- |
| **RESERVED SYMBOLS** | **DEFINITION** |
| **'** | Used to enclose a PARCH literal. |
| **"** | Used to enclose a SCROLL literal. |
| **\~** | Used to start a single-line comment. |
| **\~(** | Used to start a multi-line comment. |
| **)\~** | Used to end a multi-line comment. |
| **\!\!** | Used as a statement terminator. |

3. # **SPECIFIC RULES** {#specific-rules}

## **DECLARATIONS** {#declarations}

Establish the characteristics of variables, constants, arrays, or structures before they are used. SeaStack allows global and local declarations.

1. **Global declarations** \- Located at the start of the program and can be accessed or modified anywhere within the program. Global declarations include the following:  
1. Declaration or initialization of variables, arrays, or initialization of constants. Constants can only be declared globally. Local constant declarations are invalid.  
2. Definition of structures  
3. Definition of subfunctions  
     
2. **Local declarations** \- Located at the start of any function body and can only be accessed or modified within the function they are declared in. If a local and global declaration share the same identifier, the local declaration will override the global declaration. Local declarations include the following:  
1. Declaration or initialization of variables or arrays  
2. Declaration or initialization of structure variables

## 

## **DATA TYPES AND LITERALS** {#data-types-and-literals}

	Data types specify which type of value a variable can hold and the type of operations that can be performed on it. The reserved words COIN, DIME, PARCH, SCROLL, and BOOL are used as data types, while ABYSS is used as a return type for functions that do not return a value.

1. **COIN** \- A whole number without a decimal component within a specified range.  
   **Rules for COIN**  
1. A COIN literal represents whole numbers. The inclusion of any character other than digits or the dash sign (**\-**) is not permitted.  
2. A COIN accepts a maximum of sixteen (**16**) digits. The accepted range is from \-9999999999999999 to 9999999999999999\.  
3. Leading zeros are not allowed unless the value is zero, in which case one zero remains.  
4. Positive COIN literals are unsigned and represented without a prefix.  
5. Negative COIN literals must be denoted by a dash sign (**\-**) placed immediately before the first digit. Any whitespace between the dash sign and the digit is prohibited. 

**Examples**

| VALID | INVALID |
| :---: | :---: |
| 20 | 20**.5** |
| 1000000000000000 | 1**,**000**,**000**,**000**,**000**,**000 |
| 1234567890123456 | 1234567890123456**7** |
| 2000000000001  | **00**2000000000000000 |
| 67 | **\+**67 |
| \-20 | **\-** 20 |
| \-34 | 3**a**4 |

2. **DIME** \- A number with a decimal component within a specified range.  
   **Rules for DIME**  
1. A DIME literal represents numbers with a decimal part. The inclusion of any character other than digits, the decimal point (**.**), or the dash sign (**\-**) is not permitted.  
2. A DIME accepts a maximum of sixteen (**16**) digits for the integer part and a maximum of eight (**8**) digits for the decimal part. The accepted range is from \-9999999999999999.99999999 to 9999999999999999.99999999.  
3. If the value has no integer part, a single leading zero is required before the decimal point. If no decimal part is provided, a decimal point followed by a single zero (**.0**) is automatically added to the value.  
4. Leading zeros are not allowed unless they are the single leading zero required before the decimal point, or the value is zero. Any digit after the eighth digit in the decimal part is invalid.  
5. Positive DIME literals are unsigned and represented without a prefix.  
6. Negative DIME literals must be denoted by a dash sign (**\-**) placed immediately before the first digit. 

   **Examples**

| VALID | INVALID |
| :---: | :---: |
| 0.12345678 | **00**0.12345678 |
| 1.12345678 | 1.12345678**001** |
| 1234567890123456.12345678 | 1234567890123456**10**.12345678 |
| 12.5 | 12.5**a** |
| 0.123 | **.**123 |
| 20 → 20.0 | 20**.** |
| \-3.5 | **\- 3.5** |
| 12.0 | 12.0**000** |

   

   

3. **PARCH** \- A single character enclosed in single quotation marks (**' '**).  
   **Rules for PARCH**  
1. PARCH represents a single ASCII character, except a newline, backslash, or single quotation mark, or a single escape sequence, enclosed in single quotation marks.  
2. Using any symbol other than a pair of single quotation marks, or the lack thereof, is invalid to enclose a PARCH.  
3. Any value enclosed in single quotation marks that exceeds or subceeds a single character or escape sequence is invalid.   
4. PARCH recognizes only five escape sequences. These are valid only inside the pair of single quotation marks. Any instance of a backslash that is not followed by any valid escape sequence character is invalid.  
1. **\\s** : Single quote                        d.  **\\0** : Null  
2. **\\n** : Newline 			e.   **\\\\** : Backslash  
3.  **\\t** : Horizontal tab

	**Examples**

| VALID | INVALID |
| :---: | :---: |
| 'A' | **"**A**"** |
| '+' | '**\++**' |
| ' ' | **''** |
| '\\n' | '**\\m**' |
| '\\s' | '**'**' |
| '\\\\' | '\\\\**\\**' |

4. **SCROLL** \- A sequence of characters enclosed in double quotation marks (**" "**).  
   **Rules for SCROLL**  
1. SCROLL represents an ordered sequence of ASCII characters, except a newline, backslash, or double quotation mark, enclosed in double quotation marks.  
2. Using any symbol other than a pair of double quotation marks, or the lack thereof, is invalid to enclose a SCROLL.  
3. It must consist of at least one (**1**) valid ASCII character enclosed in double quotation marks.  
4. Each character of a SCROLL is treated as a single-character SCROLL literal, and can be accessed using an index.  
5. SCROLL recognizes only five escape sequences. These are valid only inside the pair of double quotation marks. Any instance of a backslash that is not followed by any valid escape sequence character is invalid.  
1. **\\d** : Double quote               d.   **\\0** : Null  
2. **\\n** : Newline 		       e.   **\\\\** : Backslash  
3. **\\t** : Horizontal tab

**Examples**

| VALID | INVALID |
| :---: | :---: |
| "Hello" | **'**Hello**'** |
| " " | **""** |
| "\\d" | "**"**" |
| "CFarers\\n" | "CFarers\\n**\\s**" |
| "CFarers\\n, AHOY\!" | "CFarers**\\s**, AHOY\!" |
| "She said, \\dHello World\\d" | "She said, \\dHello World"**\\d** |
| "Line 1\\nLine2" | **"Line 1Line2"** |

**Rules for Accessing SCROLL**

1. Individual characters in a SCROLL are accessed using an index operator. It must start with a literal or variable of type SCROLL, followed by the index enclosed in curly braces (**{ }**).   
2. The index indicates the position of the character in the SCROLL and starts at zero (**0**). The index must be a literal or variable of type COIN only and must not be empty or exceed the length of the SCROLL. 

**Syntax**

| \<SCROLL-lit\>{\<index\>} |
| :---: |
| \<id\>{\<index\>} |

**Examples**

| VALID | INVALID |
| :---: | :---: |
| word{1} | **word** |
| "Hello"{0} | "Hello"**{}** |
| message{i} | message{**i+1**} |
| "Hello"{1} | "Hello"{**1.5**} |
| name{index} | name{**index()**} |
| word{x} | word**\[2\]** |

5. **BOOL** \- BOOL represents either of two values: AYE (true) or NAY (false).  
   **Rules for BOOL**  
1. BOOL is restricted to only two values: AYE or NAY; otherwise, it is invalid.

	**Examples**

| VALID | INVALID |
| :---: | :---: |
| AYE | TRUE, True |
| NAY | FALSE, False |
| AYE | 1 |
| NAY | 0 |
| AYE | aye |

6. **ABYSS** \- Represents the absence of a value.  
   **Rules for ABYSS**  
1. ABYSS is used as a return type for a nonreturning function to signify that the function will not return any value to the calling function.  
2. It cannot be used to declare or call variables, constants, arrays, or structures.  
3. The keyword ABYSS, as well as any function defined with it, cannot be used as operands or values inside any expression or assignment statement.

**Examples**

| VALID | INVALID |
| :---: | :---: |
| ABYSS function() \[ ECHO("Hello")\!\! \] | ABYSS **function()\!\!** |
| ABYSS run() \[ ECHO("Go")\!\! \] | ABYSS **count \= 0**\!\! |
|  | **LOCKE** ABYSS val \= 0\!\! |
|  | ABYSS **arr{5}**\!\! |
|  | **MAST** item \[ ABYSS id\!\! \]\!\! |

## **IDENTIFIERS** {#identifiers}

Identifiers are designated names given to identify a variable, constant, array, structure, structure member or variable, or subfunction.   
**Rules in Naming Identifiers**

1. An identifier must begin with a lowercase letter only. Subsequent characters may consist of a combination of lowercase letters, digits, and underscores only. The use of uppercase letters and any other special character is strictly prohibited.  
2. It must consist of at least one (**1**) lowercase letter and at most twenty (**20**) valid characters.  
3. An identifier must be unique within its defined scope. Variables, arrays, constants, structures, structure members, structure variables, and subfunctions within the same scope, must each have a unique identifier. Declaring or defining with an identical identifier is invalid.  
4. SeaStack allows identifier shadowing. A local identifier may share the same name as a global identifier. In such cases, the local declaration will take precedence and override within its local scope.  
5. Reserved words are strictly not allowed to be used as identifiers.

**Examples**

| VALID | INVALID |
| :---: | :---: |
| number | **N**umber |
| age | **\_**age |
| person1 | p**ERSON**1 |
| middle\_name | middle\_name**$** |
| this\_is\_a\_twentychar | this\_is\_a\_twentyfour**char** |
| coin | **COIN** |
| COIN age\!\!DIME gwa\!\! | COIN **age**\!\!DIME **age**\!\! |
| COIN x\!\!AHOY() \[ DIME x\!\!\] | AHOY() \[COIN **x**\!\!  **COIN x**\!\!\] |

## **VARIABLES** {#variables}

Variables are user-defined containers for storing values.

**Rules in Declaring a Variable**

1. Declaring a variable must begin with the data type, followed by the identifier, and end with the statement terminator (**\!\!**).  
2. Multiple declarations of variables with the same data type are allowed and are separated with a comma (**,**).  
3. Multiple variables with different data types cannot be declared at once.  
4. Declared variables are undefined and cannot be used in the program until it is assigned a value.

   

	**Syntax**

| \<dtype\> \<id\>\!\! |
| :---: |
| \<dtype\> \<id1\>, \<id2\>, …, \<idN\>\!\! |

	**Examples**

| VALID | INVALID |
| :---: | :---: |
| COIN age\!\! | COIN age |
| DIME pi\!\! | **pi** DIME\!\! |
| SCROLL greet, welcome\!\! | SCROLL greet **welcome**\!\! |
| PARCH letter, digit\!\! | PARCH letter, **COIN** digit\!\! |
| BOOL flag\!\! | BOOL flag, **AYE**\!\! |
| BOOL power, level, flag\!\! | BOOL power **&&** flag\!\! |

**Rules in Initializing a Variable**

1. Initializing a variable must begin with the data type, followed by the identifier, the assignment operator (**\=**), then the assigned value, and end with the statement terminator (**\!\!**).  
2. The initial value assigned to a variable must be of the same data type as the variable. It can be a literal, variable, constant, array element, structure member, function return value, or expression.  
3. Initialization and declaration of multiple variables with the same data type is allowed and is separated with a comma (**,**). Multiple variables with different data types cannot be initialized at once.

	  
**Syntax**

| \<dtype\> \<id\> \= \<value\>\!\! |
| :---: |
| \<dtype\> \<id1\> \= \<value\>, …, \<idN\> \= \<value\>\!\! |
| \<dtype\> \<id1\> \= \<value\>, \<id2\>, …, \<idN\> \= \<value\>\!\! |

	  
	**Examples**

| VALID | INVALID |
| :---: | :---: |
| COIN age \= 9\!\! | COIN age \= **'9'** \!\! |
| PARCH letter \= x\!\! | PARCH letter \= x |
| DIME sec \= add(x,y), min \= (2.2\*3.3)\!\! | COIN sec \= 1, **DIME** min \= 2.2\!\! |
| SCROLL name \= students{3}\!\! | SCROLL name \= **1\*2+3**\!\! |
| BOOL flag \= AYE, on \= menu$first\!\! | BOOL flag \= AYE, on \= **9**\!\! |
| BOOL flag \= AYE, choice, on \= NAY\!\! | BOOL flag \= AYE, choice, on **\=** \!\! |

## 

## **CONSTANTS** {#constants}

Constants are fixed values. It must be given an initial value at the time of declaration, and this value must not be reassigned or modified after initialization.

**Rules in Declaring and Initializing Constants**

1. A constant must be initialized at the time of declaration; otherwise, it is invalid. It must begin with the reserved word LOCKE, followed by the data type, the identifier, the assignment operator (**\=**), the assigned value, and end with the statement terminator (**\!\!**).  
2. The value to be assigned to a constant must only be a literal matching the declared data type.   
3. Any attempt to reassign a new value to a constant is invalid.  
4. Initialization of multiple constants with the same data type is allowed and is separated with a comma (**,**). Multiple constants with different data types cannot be initialized at once.

   

	**Syntax**

| LOCKE \<dtype\> \<id\> \= \<value\>\!\! |
| :---: |
| LOCKE \<dtype\> \<id1\> \= \<value\>, …, \<idN\> \= \<value\>\!\! |

**Examples**

| VALID | INVALID |
| :---: | :---: |
| LOCKE DIME pi \= 3.14\!\! | LOCKE DIME pi**\!\!** |
| LOCKE SCROLL name \= "Juan"\!\! | LOCKE SCROLL name \= **123**\!\! |
| LOCKE BOOL flag \= AYE\!\! | LOCKE BOOL flag \= **10 \> x**\!\! |
| LOCKE SCROLL language \= "English", programming\_language \= "SeaStack"\!\! | LOCKE SCROLL name \= "Jose", nickname \= **names()**\!\! |
| LOCKE COIN max\_score \= 100\!\! | LOCKE COIN max\_score \= 100\!\! **max\_score \= 150\!\!** |

## 

## **ARRAYS** {#arrays}

A fixed-size collection of elements of the same data type.   
**Rules for Arrays**

1. The size of an array must be specified upon declaration with a COIN literal only. The size must be at least one (**1**).  
2. The elements of an array can be a literal, variable, constant, array element, structure member, function return value, or expression, which evaluates to the declared data type of the array.  
3. The number of elements assigned to an array must not exceed the declared size. If fewer elements are provided than the declared size, the remaining indices without a value will be assigned a value of null.

1. **One-dimensional Array \-** A one-dimensional array is a collection of elements of the same data type in a single row or list of values.

**Rules for One-dimensional Array**

1. A one-dimensional array declaration begins with the data type, followed by the identifier, the size enclosed in curly braces (**{ }**), and the statement terminator (**\!\!**). Only one array can be declared or initialized at once.  
2. It can be initialized with the assignment operator (**\=**), followed by square brackets (**\[ \]**) enclosing the array elements which are separated by commas (**,**), and end with the statement terminator (**\!\!**). 

	**Syntax**

| \<dtype\> \<id\>{\<size\>}\!\!  |
| :---: |
| \<dtype\> \<id\>{\<size\>} \= \[\<value1\>, …, \<valueN\>\]\!\! |

	**Examples**

| VALID | INVALID |
| :---: | :---: |
| COIN numbers{2}\!\! | COIN numbers**{}**\!\! |
| DIME average{3}\!\! | DIME arr1{5}**, arr2{5}**\!\! |
| PARCH letters{3} \= \['A', 'B', 'C'\]\!\! | PARCH letters{3} \= \['A', 'B', 'C', **'D'**\]\!\! |
| BOOL flag{2} \= \[3\<5, status(a, c)\]\!\! | BOOL flag{2} \= \[AYE, **1**\]\!\! |

2. **Two-dimensional Array \-** A two-dimensional array is an array where each element is another array.

**Rules for Two-dimensional Array**

1. A two-dimensional array declaration begins with the data type, followed by the identifier, then the size of the row and the column, each enclosed in curly braces (**{ }**), and ends with the statement terminator (**\!\!**). Only one array can be declared or initialized at once.  
2. It can be initialized using the assignment operator (**\=**), with square brackets enclosing the elements (**\[ \]**), and each element being another set of array elements, with each set enclosed in square brackets (**\[ \]**).

**Syntax**

| \<dtype\> \<id\>{\<rows\>}{\<columns\>}\!\! |
| :---: |
| \<dtype\> \<id\>{\<rows\>}{\<columns\>} \= \[\[\<r1c1\>, ..., \<r1cN\>\], …,  \[\<rNc1\>, ..., \<rNcN\>\]\]\!\! |

**Examples**

| VALID | INVALID |
| :---: | :---: |
| DIME grades{2}{2}\!\! | DIME grades{2}**{}**\!\! |
| PARCH letters{1}{2}\!\!  | PARCH letters{1}{**x**}\!\! |
| COIN table{1}{2} \= \[\[1, add(x,y)\]\]\!\! | COIN table{1}{2} \= \[\[1, 3**\>**5\]\]\!\! |
| COIN table{2}{3} \= \[\[1, 1, 1\],\[2, 2, 2\]\]\!\! | COIN table{2}{1} \= \[\[1\], \[2\], **\[3\]**\]\!\! |
| COIN table{1}{3} \= \[\[1, 2+3, 3\]\]\!\! | COIN table{**1, 3**} \= \[1, 2, 3\]\!\! |

	

**Rules for Accessing Array Elements**

1. Array elements are stored consecutively in an index starting from zero (**0**).  
2. Accessing an array element starts with the array identifier, followed by the array index enclosed in curly braces. The index must be a literal or variable of type COIN only and must not be empty or less than zero.  
3. Accessing array elements can be used to modify or assign a value to the specified index.

   

**Syntax**

| \<id\>{\<index\>} |
| :---: |
| \<id\>{\<index\>}{\<index\>} |

**Examples**

| VALID | INVALID |
| :---: | :---: |
| grade{3} | grade**{}** |
| nums{1}{2} | nums**\[1\]\[2\]** |
| numbers{2} | numbers{**2.5**} |
| nums{x} | nums{**get\_num()**} |
| table{i}{j} | table{**i, j**} |
| average{i} | average{**COIN**} |

## 

## **STRUCTURES** {#structures}

A collection of several related variables of possibly different types. The items in a structure are called members, and they can be of any valid data type.

**Rules for Defining Structures**

1. Defining a structure begins with the reserved word **MAST**, followed by a unique identifier, then the member declarations enclosed within the square brackets (**\[ \]**), and ends with the statement terminator (**\!\!**). It is defined after the declaration of any global constant, variable, or array, and before any function.  
2. Declaring a member starts with the data type, followed by the identifier, and ends with the statement terminator (**\!\!**). There must be at least one member declaration in a structure definition.  
3. Multiple members of the same data type can be declared at once by separating each member with a comma (**,**). Multiple members of different data types cannot be declared at once.

   

	**Syntax**

| MAST \<id\> \[      \<dtype\> \<id\>\!\! \]\!\! |
| :---- |
| MAST \<id\> \[      \<dtype\> \<id1\>, \<id2\>, …, \<idN\>\!\! \]\!\! |
| MAST \<id\> \[      \<dtype1\> \<id1\>\!\!      …      \<dtypeN\> \<idN\>\!\! \]\!\! |

**Examples**

| VALID | INVALID |
| ----- | ----- |
| MAST person \[ SCROLL name\!\! \]\!\! | **person** \[ SCROLL name\!\! \]\!\! |
| MAST person \[ COIN age\!\!\]\!\!  | MAST person \[ **\]\!\!**  |
| MAST person \[ COIN age, year\!\!\]\!\!  | MAST person \[ COIN age, **DIME** year\!\!  \]\!\! |
| MAST item \[DIME price\!\!\]\!\! | MAST item \[**DIME price**\]\!\! |
| MAST student \[ COIN age\!\! DIME gwa\!\!\]\!\!  | MAST student \[ COIN age\!\! DIME gwa\!\!**\]** |

**Rules for Declaring Structure Variables**

1. Declaring a structure variable must begin with the reserved word MAST, followed by the structure member identifier, then the structure variable identifier, and the statement terminator (**\!\!**). It can only be declared inside the AHOY function.  
2. Multiple structure variables can be declared at once by separating each variable with a comma (**,**).

**Syntax**

| MAST \<struct\_id\> \<var\_id\>\!\! |
| :---: |
| MAST \<struct\_id\> \<var\_id1\>, \<var\_id2\>, …, \<var\_idN\>\!\! |

**Example**

| VALID | INVALID |
| :---: | :---: |
| MAST book  book1\!\! | MAST book book1, **MAST employee**\!\! |
| MAST employee e1, e2, e3\!\! | MAST employee e**(1+3)**\!\! |
| MAST student s1, s2, s3\!\! | MAST **S**tudent s1\!\! |
| MAST book novel\!\! | MAST **SCROLL** book novell\!\! |
| MAST car c1, c2\!\! | MAST car **c1 c2**\!\! |

**Rules for Initializing Structure Variables**

1. Initializing a structure variable must begin with the reserved word MAST, followed by the structure identifier, the structure variable identifier, the assignment operator (**\=**), then the assigned values enclosed in square brackets (**\[ \]**), and end with the statement terminator (**\!\!**).  
2. Only one structure variable can be initialized at once.  
3. The value assigned to the members of a structure variable can be a literal, variable, constant, array element, structure member, function return value, or expression, which evaluates to the declared data type of the member.  
4. Values are assigned sequentially to the members in the order of their declaration in the structure definition. This sequence is maintained until the initialization block ends or a member operator is encountered.  
5. To initialize a specific member, start with the member operator (**$**), followed by the member identifier, then the assignment operator, and the assigned value. The succeeding value will be assigned to the next member, unless specified otherwise with another member operator.  
6. A member can only be left uninitialized if all succeeding members are also uninitialized, unless a member operator is used to skip the order. Uninitialized members will be assigned a value of null.  
7. Providing a number of initial values that exceeds the number of defined members is invalid.

**Syntax**

| MAST \<struct\_id\> \<var\_id\> \= \[\<value\>\]\!\! |
| :---: |
| MAST \<struct\_id\> \<var\_id\> \= \[\<value1\>, …, \<valueN\>\]\!\! |
| MAST \<struct\_id\> \<var\_id\> \= \[$\<mem\_id\> \= \<value\>\]\!\! |
| MAST \<struct\_id\> \<var\_id\> \= \[$\<mem\_id1\> \= \<value1\>, …, $\<mem\_idN\> \= \<valueN\>\]\!\! |

**Examples**

| VALID | INVALID |
| ----- | ----- |
| MAST vehicle truck \= \["Foton", "12-wheeler"\]\!\! | **vehicle** truck \= \["Foton", "12-wheeler"\]\!\! |
| MAST blk3 s1 \= \["Liza", 19, 1.00\]\!\! | MAST blk3 s1 \= \["Liza"\], **s2 \= \["Ann"\]**\!\! |
| MAST movies movie1 \= \[$title \= "Fantastic Mr. Fox"\]\!\! | MAST movies movie1 \= \[**title** \= "Fantastic Mr. Fox"\]\!\! |
| MAST books book1 \= \[$title \= "Gone Girl", "Mystery", $price \= 499.99\]\!\! | MAST books book1 \= \[$title \= "Gone Girl", "Mystery", **COIN x\!\!**\]\!\! |
| MAST animal insect \= \["spider", "8 legs"\]\!\! | MAST animal **reptile, mammal,** insect \= \["spider", "8 legs"\]\!\! |
|  | MAST animal insect \= **{**"spider", "8 legs"**}**\!\! |

**Rules for Accessing Members**

1. To access a member, it must start with the structure variable identifier, followed by the member operator (**$**), and then the member identifier.  
2. Accessing members can be used to modify or assign a value to the specific member.

**Syntax**

| \<var\_id\>$\<mem\_id\> |
| :---: |

**Example**

| VALID | INVALID |
| :---: | :---: |
| student1$name | student1**.**name |
| employee1$salary | employee1**$** |
| student1$age | student1$**MAST** |
| employee1$role | employee1()**$**role |
| student1$age \= 20\!\! | **MAST**$age \= 20\!\! |

## **OPERATORS** {#operators}

Operators are symbols that provide instructions on how to perform arithmetic, relational, and logical calculations, concatenate SCROLL values, or perform other special operations. SeaStack supports arithmetic, assignment, unary, relational, logical, and other operators.

**Rules for Operators**

1. Seastack operators follow a standard operator precedence table.  
2. Operators must not be used consecutively without any operand in between, unless the second operator is the unary minus (**\-**), logical not (**\!**), or logical double not (**\!\#**).  
3. A dash sign (**\-**) that is immediately followed by a digit, without any whitespace in between, is always considered as a negative digit. Otherwise, it is treated as a subtraction or unary minus operator.  
4. Arithmetic operators follow the PEMDAS order, where operations inside parentheses are evaluated first, followed by exponents, then multiplication, division, or modulo, and finally, addition or subtraction.   
5. Logical operators are evaluated using short-circuit rules, meaning that in logical AND, if the first operand evaluates to false, the second operand is not evaluated, and in logical OR, if the first operand evaluates to true, the second operand is not evaluated.   
6. The modulo operation with negative values preserves the sign of the dividend or left operand.

1. **Arithmetic Operators \-** Used to perform basic mathematical operations.

| OPERATOR | DEFINITION |
| :---: | ----- |
| **\+** | Adds operands. |
| **\-** | Subtracts operands. |
| **\*** | Multiplies operands. |
| **/** | Divides operands. |
| **%** | Gets the remainder from dividing operands. |
| **^** | Exponentiates an operand. |

   

2. **Assignment Operators \-** Used to assign values or update existing values.

| OPERATOR | DEFINITION |
| :---: | ----- |
| **\=** | Assignment operator. Assigns the value of the right-operand to the left-operand. |
| **\+=** | Add and Assign operator. It adds the right operand to the left operand and assigns the result to the left operand. |
| **\-=** | Subtract and Assign operator. It subtracts the right operand from the left operand and assigns the result to the left operand. |
| **\*=** | Multiply and Assign operator. It multiplies the left operand by the right operand and assigns the result to the left operand. |
| **/=** | Divide and Assign operator. It divides the left operand by the right operand and assigns the result to the left operand. |
| **%=** | Modulo and Assign operator. It divides the left operand by the right operand and assigns the remainder to the left operand. |
|  **^=** | Exponent and Assign operator. Raises the left operand to the power of the right operand and assigns the result to the left operand. |

3. **Unary Operators** \- Used to perform an operation on a single operand.

| OPERATOR | DEFINITION |
| :---: | ----- |
| **\+\#** | Used to increment an operand. |
| **\-\#** | Used to decrement an operand. |
| **\-** | Used to negate an operand. |

   

   

4. **Relational Operators** \- Used to compare two values and returns a BOOL value.

| OPERATOR | DEFINITION |
| :---: | ----- |
| **\<** | Returns AYE if the left operand is less than the right operand. Otherwise, returns NAY. |
| **\>** | Returns AYE if the left operand is greater than the right operand. Otherwise, returns NAY. |
| **\>=** | Returns AYE  if the left operand is greater than or equal to the right. Otherwise, returns NAY. |
| **\<=** | Returns AYE if the left operand is less than or equal to the right. Otherwise, returns NAY. |
| **\==** | Returns AYE if the left operand is equal to the right operand.  Otherwise, it returns NAY. |
| **\!=** | Returns AYE if the left operand is not equal to the right operand.  Otherwise, returns NAY. |

   

5. **Logical Operators** \- Used to combine or negate bool expressions.

| Logical Operators |  |
| :---: | ----- |
| **RESERVED SYMBOLS** | **DEFINITION** |
| **&&** | Logical AND. Returns AYE if both operands evaluate to true. Otherwise, it returns NAY. |
| || | Logical OR. Returns AYE if at least one operand evaluates to true. Otherwise, it returns NAY.  |
| **\!** | Logical NOT. Returns AYE if the operand evaluates to false, and NAY if it evaluates to true. |
| **\!\#** | Logical DOUBLE NOT. Returns AYE if the operand evaluates to true, and NAY if it evaluates to false. |

   

   

   

6. **Other Operators** \- Used to perform a specific function.

| OPERATOR | DEFINITION |
| :---: | ----- |
| **&** | Concatenation operator. Used to concatenate values of type SCROLL. |
| **@** | Address operator. Used to access the address of an operand. |
| **$** | Member operator. Used to access a member of a structure. |
| **{}** | Index operator. Used to access an element of an array or a character of a SCROLL literal. |
| **()** | Call operator. Used as a placeholder of arguments to be passed to a function call. |

## 

## **OPERATOR PRECEDENCE** {#operator-precedence}

| Precedence | Operator | Operation | Associativity |
| :---: | :---: | :---: | :---: |
| 1 | ( ) | Function Call, Grouping | Left to Right |
|  | { } | Index Accessing |  |
|  | $ | Member Accessing |  |
| 2 | \+\#, \-\# | Increment, Decrement | Right to Left |
|  | \!, \!\# | Logical Not, Logical Double Not |  |
|  | \- | Unary Minus |  |
| 3 | ^ | Exponent | Right to Left |
| 4 | \*, /, % | Multiply, Divide, Modulo | Left to Right |
| 5 | \+, \-, & | Add, Subtract, Concatenation |  |
| 6 | \<, \> | Less than, Greater than |  |
|  | \<=, \>= | Less than or Equal, Greater than or Equal |  |
| 7 | \==, \!= | Equality, Inequality |  |
| 8 | && | Logical And |  |
| 9 | || | Logical Or |  |
| 10 | \= | Assignment |  |
|  | \+=, \-=, \*=, /=, %=, ^= | Compound Assignment |  |

## **EXPRESSIONS** {#expressions}

Expressions combine operands with operators to produce a single value.

1. **Arithmetic Expressions** \- It performs mathematical calculations.

**Rules for Arithmetic Expressions**

1. An arithmetic expression must begin with an operand, followed by an arithmetic operator, and end with an operand.  
2. An arithmetic expression must contain at least one arithmetic operator and two operands of type COIN or DIME.  
3. Operands may be literals, variables, constants, array elements, structure members, function return values,  or grouped expressions that evaluate to a COIN or DIME only.  
4. A dash sign (**\-**) preceding a digit, without any whitespace in between, is always considered as a negative digit. If the dash sign is not preceding a digit without any intervening whitespace, and is preceded by an operand, it is treated as a subtraction operator. Otherwise, it is treated as a unary minus operator.  
5. A unary minus operator is used to negate a variable, constant, array element, structure member, function return value, or grouped arithmetic expression.

**Syntax**

| \<operand\> \<arith\_op\> \<operand\> |
| :---: |
| \<operand1\> \<arith\_op\> \<operand2\> … \<arith\_op\> \<operandN\>  |

	  
	**Examples**

| VALID | INVALID |
| :---: | :---: |
| 2 \* (x \+ 3\) | 5 **\+\*** 2            |
| 5- 3 | 5**\-3** |
| items{5} \* 10 | items{5} \+ **"USD"** |
| (x \* y \+ z) / (x \- y)  | (x \* y \+ z) / **( )** |
|  \- x \+ 5.0 |  **\*** x \+ 5.0 |

2. **Relational Expressions** \- It performs comparison of two operands.

**Rules for Relational Expressions**

1. A relational expression must begin with an operand, followed by a relational operator, and end with an operand.   
2. A relational expression must contain exactly one relational operator and two operands.  
3. For less than (**\<**), greater than (**\>**), less than or equal (**\<=**), or greater than or equal (**\>=**) operators, the operands must only be literals, variables, constants, array elements, structure members, function return values, arithmetic expressions, or grouped expressions that evaluate to a COIN or DIME only.   
4. For equal to (**\==**) and not equal to (**\!=**) operators, the operands must only be literals, variables, constants, array elements, structure members, function return values, or grouped expressions. The operands must have the same data type, except for COIN and DIME values; otherwise, it is invalid. COIN and DIME values can be compared with each other using these operators.

   

**Syntax**  

| \<operand\> \<rel\_op\> \<operand\> |
| :---: |

	**Examples**

| VALID | INVALID |
| :---: | :---: |
| (a \+ b) \>= (a \* b) | **\>=** (a \+ b) (a \* b) |
| 5 \< 20 | 5 \< 10 **\< 20** |
| 4 \<= (val \* 2\) | username \> **"admin"**                     |
| 1 \== 1.5 | "Hello" \== **AYE** |
| val \>= flag | val **\>\>** flag |

3. **Logical Expressions** \- It performs comparison of BOOL operands.  
     
   **Rules for Logical Expressions**  
1. For the logical not (**\!**) and logical double not (**\!\#**) operators, it must start with exactly one operator followed by a single operand.  
2. For the logical or (**||**) and  logical and (**&&**) operators, it must start with an operand, followed by the logical operator, and end with an operand.  
3. A logical expression must contain at least one logical operator, and its operands must only be literals, variables, constants, array elements, structure members, function return values, relational expressions, or grouped expressions that evaluate to a BOOL.

   

**Syntax**

| \<operand\> \<log\_op\> \<operand\> |
| :---: |
| \<operand1\> \<log\_op\> \<operand2\> … \<log\_op\> \<operandN\>  |
| \!\<operand\> |
| \!\#\<operand\> |

**Examples**

| VALID | INVALID |
| :---: | :---: |
| num1 \> 0 && num2 \< 10 | **&&** (num1 \> 0\)                      |
| \!NAY | AYE**\!**NAY                              |
| count \> 5 || count \< 100 | (count \> 5**) (**count \< 100\)         |
| 3 \+ 5 \> 6 && 4 \== 3 | 3 \+ 5 \> 6 && **4** |
| x \> 5 && y \< 10 \!\! 3 \== 6 | (x \> 5\) **&&&** |
| a && b || c && d | a && **b c** && d |

4. **Unary Expressions** \- It performs increment or decrement.  
     
   **Rules for Unary Expressions**  
1. A unary expression must start with the unary operator followed by a single operand.  Any whitespace between the operator and the operand is invalid.  
2. The operand must be a variable, array element, or structure member of type COIN only.  
3. A unary expression may appear either as part of a condition in a HOIST statement or as a standalone statement ending with the statement terminator (**\!\!**).  

   

**Syntax**

| \<unary\_op\>\<operand\> |
| :---: |

	**Examples**

| VALID | INVALID |
| :---: | :---: |
| \-\#x | \-\# x              |
| \+\#count | **\++**count         |
| \-\#value | value**\-\#**         |
| \+\#age{3} | \+\#**(5+3)** |
| \-\#flag$count | \+\#**9** |

5. **SCROLL Expressions** \- A combination of SCROLL values combined with the concatenation operator.

**Rules for SCROLL Expressions**

1. A SCROLL expression must begin with an operand, followed by the concatenation operator (**&**), and end with an operand.  
2. Operands can be literals, variables, constants, array elements, structure members, function return values,  grouped SCROLL expressions, or SCROLL expressions of type SCROLL.  
3. SCROLL expressions are evaluated from left to right and return a single SCROLL value formed by appending the operands in order without altering any character.

**Syntax**

| \<operand\> & \<operand\> |
| :---: |
| \<operand1\> & \<operand2\> … & \<operandN\>  |

**Examples**

| VALID | INVALID |
| :---: | :---: |
| "Hi" & "There" | "Hi" "There"                |
| "Name: "\&name1&" "\&name2 | "Name: " & name1 name2 |
| ("Good" & "Morning") & "Boss" | "Good & "Morning" & "Boss" |
| ("Sea" & "Stack") & " " & "Year" & " " & "2026" | ("Sea" & "Stack") &**&&** "Year" &**””**& "2026" |
| "Hello" & "There" | "Hello" **\+** "There" |
| greeting & " Boss" | greeting & **\!\!** |

## **STATEMENTS** {#statements}

Statements are instructions that the computer executes. SeaStack supports input, output, assignment, conditional, looping, and jump statements. 

1. **Input Statements \-** Used to obtain user input.

**Rules for Input Statements**

1. It must start with the reserved word ASK, followed by the argument list enclosed in parentheses, and end with the statement terminator (**\!\!**).  
2. The first argument consists of the format specifier/s only enclosed in double quotation marks, followed by a comma, then the second argument which is the addressing of target variable, array element, or structure member.  
3. Format specifiers must begin with a percentage symbol (**%**), followed by the first character of the data type (**%C:** COIN,  **%D:** DIME,  **%P:** PARCH, **%S:** SCROLL,  **%B:** BOOL). It must strictly match the data type, quantity, and order of the targets in the second argument, and must not be separated by any comma.   
4. Addressing the target variable, array element, or structure member starts with the address symbol (**@**) followed by the identifier. Multiple target variables must be separated with a comma.

**Syntax**

| ASK("\<format\_specifier\>", @\<id\>)\!\! |
| :---: |
| ASK("\<format\_specifier1\>...\<format\_specifierN\>", @\<id1\>, ..., @idN)\!\! |

**Examples**

| VALID | INVALID |
| :---: | :---: |
| ASK("%C", @score)\!\! | ASK("%C", **score**)\!\! |
| ASK("%D%C", @gwa, @score)\!\! | ASK("%C%D", **@cost**)\!\! |
| ASK("%C%D%D", @age, @weight, @height)\!\! | ASK("**%s**", @name)\!\! |
| ASK("%C%C", @score, @total)\!\! | ASK("**%C, %C**", @score, @total)\!\! |
| ASK("%D", @gwa)\!\! | ASK("%D" @gwa)\!\! |
| ASK("%C", @player$hp)\!\! | ASK("%C", @player**.**hp)\!\! |

2. **Output Statements \-** Used to display an output.

**Rules for Output Statements**

1. It must start with the reserved word ECHO, followed by the argument list enclosed in parentheses, and end with the statement terminator (**\!\!**).  
2. The first argument is the text to be displayed and must be a SCROLL literal. It can be combined with format specifier/s which must be placed within the SCROLL literal.  
3. A format specifier is used as a placeholder of a value to be displayed. If the first argument does not have any format specifier, it must not have a second argument.  
4. The value/s in  the second argument can be a literal, variable, constant, array element, structure member, function return value, or expression.  The value/s must strictly match the data type, quantity, and order of the format specifier/s in the SCROLL literal. Multiple values must be separated with commas.

**Syntax**

| ECHO("\<SCROLL-lit\>")\!\! |
| :---: |
| ECHO("\<SCROLL-lit\>", \<value\>)\!\! |

**Examples**

| VALID | INVALID |
| :---: | :---: |
| ECHO("Enter your age: ")\!\! | ECHO(**Enter your age**)\!\! |
| ECHO("Your score: %C", score)\!\! | ECHO("Your score: **%C**")\!\! |
| ECHO("Hello\\nWorld")\!\! | ECHO("Hello" **& greet**)\!\! |
| ECHO("Your name: %S”, name)\!\! | ECHO("Your name: name", **%S**)\!\! |
| ECHO("%C+%C \= %C", a, b, sum)\!\! | **ECHO("%C+%C \= %C", a, b, sum)** |

3. **Assignment Statements \-** Used to assign a value to the operand.   
   

**Rules for Assignment Statements**

1. It must start with an operand, then the assignment operator, the value to be assigned, and end with the statement terminator (**\!\!**). The operand must only be a declared variable, array element, or structure member.  
2. For the standard assignment operator (=), the operand can be any data type, and the value to be assigned must be a literal, variable, constant, array element, structure member, function return value, expression, or grouped expression of the same data type as the operand.  
3. For the compound assignment operators (**\+=, \-=, \*=, /=, %=, ^=**), the operand must be of type COIN or DIME. The value to be assigned must be a literal, variable, constant, array element, structure member, function return value, or arithmetic expression that evaluate to a COIN or DIME.

**Syntax**

| \<operand\> \<assignment\_op\> \<value\>\!\! |
| :---: |

**Examples**

| VALID | INVALID |
| :---: | :---: |
| num1 \= 10\*2\!\! | num1 \= 10 |
| flag \= AYE && 3 \> (5+4)\!\! | **9** \= num2\!\! |
| username \= "captain\_01"\!\! | **username()** \= "hi"\!\! |
| total \*= 9\!\! | **total \* 9** \= 5\!\! |
| height \*= 3+5/(4-6)\!\! | height \*= **"tall"**\!\! |

4. **Conditional Statements** \- Used to execute different blocks of code based on a given condition. The reserved words LOOK, DROP, DROPLOOK, and CHART are used for conditional statements.  
     
   **a. LOOK** \- Executes the following block of statements if the given condition is true; otherwise, the block of statements is ignored.  
   **Rules in LOOK Statements**  
1. It must start with the reserved word LOOK, then a condition enclosed in parentheses (**( )**), then the body enclosed in square brackets (**\[ \]**).   
2. The condition must be a literal, variable, constant, array element, structure member, function return value, relational expression, or grouped expression that evaluates to a BOOL data type. It must not be empty.     
3. The body supports all statements, except BACK statements, and can be empty. LAND and SAIL statements are optional and the body can only have either one located at the end.  
   **Syntax**

| LOOK (\<condition\>) \[    \<statement/s\>  \] |
| :---- |
| LOOK (\<condition\>) \[\] |

**Examples**

| VALID | INVALID |
| ----- | ----- |
| LOOK (b \> 5\) \[    ECHO("b equals 5")\!\! \] | LOOK (**COIN b \= 5**) \[    ECHO("Invalid condition")\!\! \] |
| LOOK (AYE) \[    ECHO("Always true")\!\!    SAIL\!\! \] | LOOK (AYE) \[    **SAIL\!\!**    ECHO("Always true")\!\! \] |
| LOOK (3+5\>6 || 4 \< 5\) \[  \] | LOOK (**x \= 10**) \[  \] |
| LOOK (is\_valid \== AYE) \[  ECHO("Granted")\!\! \] | LOOK **()** \[  ECHO("Empty")\!\! \] |
| LOOK (score \>= 90\) \[  ECHO("Excellent")\!\! \] | **LOOK** \[ ECHO("True")\!\! \] |

**b. DROP \-** Executes the block of statements under DROP only if the preceding LOOK or DROPLOOK conditions does not evaluate to true.

**Rules in DROP Statements**

1. A DROP statement must have an initial LOOK statement and can be preceded by a DROPLOOK statement.  
2. The reserved word DROP must be followed by the body enclosed in square brackets (**\[ \]**).  
3. The body supports all statements, except BACK statements, and can be empty. LAND and SAIL statements are optional and the body can only have either one located at the end.

**Syntax**

| LOOK (\<condition\>) \[    \<statement/s\> \] DROP \[     \<statement/s\> \] |
| :---- |
| LOOK (\<condition\>) \[ \] DROP \[  \] |

**Examples**

| VALID | INVALID |
| ----- | ----- |
| LOOK (is\_rainy) \[  \] DROP \[  \] | LOOK (x \> 5\) \[    ECHO("x is greater")\!\! \] DROP **(x\<5)** \[ |
| LOOK (age \>= 18\) \[    ECHO("You are old.\\n")\!\! \] DROP \[    ECHO("You are not old.\\n")\!\! \] | LOOK (age \>= 18\) \[ \] DROP \[    **SAIL\!\!    LAND\!\!** \] |
| LOOK (flag) \[ \] DROP \[    ECHO("ON.")\!\! \] | LOOK (is\_safe) \[  \] DROP \[     **BACK \!\!**  \] |
| LOOK (flag) \[DROP \[  ECHO("ON.")\!\!\] | **DROP** \[ ECHO("ON.")\!\!\] |
| LOOK (is\_rainy) \[\] DROP \[\] | LOOK (is\_rainy) \[\] DROP**ECHO**("No Brackets")\!\! |

**c. DROPLOOK** \- Evaluates the conditions from top to bottom. If the condition does not evaluate to true, it proceeds to check the next condition. Once a condition is evaluated to be true, it executes the corresponding block of statements and skips the rest of the conditions.

**Rules in DROPLOOK Statements**

1. A DROPLOOK statement must have an initial LOOK statement and can be preceded by another DROPLOOK statement. It can be followed by another DROPLOOK statement or an optional final DROP statement.  
2. The reserved word DROPLOOK must be followed by a condition enclosed in parentheses (**( )**), then the body enclosed in square brackets (**\[ \]**).   
3. The condition must be a literal, variable, constant, array element, structure member, function return value, relational expression, or grouped expression that evaluates to a BOOL data type. It must not be empty.  
4. The body supports all statements, except BACK statements, and can be empty. LAND and SAIL statements are optional and the body can only have either one located at the end.

**Syntax**

| LOOK (\<condition1\>) \[    \<statement/s\> \] DROPLOOK (\<condition2\>) \[     \<statement/s\> \] … DROPLOOK (\<conditionN\>) \[    \<statement/s\> \] |
| :---- |
| LOOK (\<condition1\>) \[    \<statement/s\> \] … DROPLOOK (\<conditionN\>) \[    \<statement/s\> \] DROP \[    \<statement/s\> \]  |
| LOOK (\<condition1\>) \[ \] DROPLOOK (\<condition2\>) \[  \] DROP \[ \]  |

**Examples**

| VALID | INVALID |
| ----- | ----- |
| LOOK (score \>= 90\) \[      ECHO("Excellent.")\!\! \] DROPLOOK (score \>= 75\) \[      ECHO("Passed.")\!\! \] DROP \[      ECHO("Failed.")\!\! \] | **DROPLOOK** (score \>= 75\) \[    ECHO("Missing LOOK")\!\! \] DROP \[    ECHO("Failed.")\!\! \]  |
| LOOK (temp \> 37.5) \[    ECHO("Very hot")\!\! \] DROPLOOK (temp \> 30.5) \[    ECHO("Hot")\!\! \] DROPLOOK (temp \> 20.5) \[    ECHO("Warm")\!\! \] | LOOK **( )** \[    ECHO("No Condition")\!\! \] DROPLOOK **( )** \[    ECHO("No Condition")\!\! \] DROPLOOK **( )** \[    ECHO("No Condition")\!\! \] |
| LOOK (grade \== 'A') \[    ECHO("Outstanding")\!\! \] DROPLOOK (grade \== 'B') \[    ECHO("Good")\!\!    LAND\!\! \] | LOOK (grade \== 'A') \[    ECHO("Outstanding")\!\! \] DROPLOOK (grade \== 'B') \[    ECHO("Good")\!\!    **BACK\!\!** \] |
| LOOK (condition{0}) \[    ECHO("True")\!\! \] DROPLOOK (condition) \[    ECHO("False")\!\! \] DROP \[ \] | LOOK (**3+6**) \[    ECHO("Not Boolean")\!\! \] DROPLOOK **()** \[    ECHO("No Condition")\!\! \] DROP \[ \] |
| LOOK (temp \> 100\) \[    ECHO("Boiling")\!\!  \] DROPLOOK (temp \> 0 && temp \<= 100\) \[     ECHO("Liquid")\!\!  \] | LOOK (temp \> 100\) \[    ECHO("Boiling")\!\!  \] DROPLOOK **(COIN x)** \[    ECHO("Wrong Cndtn")\!\!  \] |

**d. Chart Statements** \- Executes different parts of the code based on the value of a single variable.

**Rules in CHART Statements**

1. It must start with the keyword CHART, followed by a condition enclosed in parentheses (**( )**), and end with the body enclosed in square brackets (**\[ \]**).   
2. The condition of a CHART statement must be a literal or variable of type COIN, PARCH, or SCROLL only and must not be empty.  
3. The body of a CHART statement must consist of at least one COURSE body and can end with a single optional ADRIFT body.  
4. Each COURSE body must start with the keyword COURSE, followed by a unique label, then a colon symbol (**:**), followed by the statements to be executed. The label must be a COIN, PARCH, or SCROLL literal. Accessing a SCROLL character is allowed given that the index is a COIN literal that is within the length of the SCROLL.  
5. The body supports all statements, except BACK statements, and can be empty. LAND and SAIL statements are optional and the body can only have either one located at the end.  
6. The optional ADRIFT body must start with the keyword ADRIFT, followed by a colon (**:**), then the statements to be executed. It supports all statements, except BACK and SAIL statements, and must have a LAND statement at the end.

**Syntax**

| CHART (\<condition\>) \[  COURSE label:    \<statement/s\> \] |
| :---- |
| CHART (\<condition\>) \[  COURSE label1:    \<statement/s\> … COURSE labelN:    \<statement/s\> ADRIFT:    \<statement/s\> LAND\!\! \] |
| CHART (\<condition\>) \[  COURSE label: \] |

**Examples**

| VALID | INVALID |
| ----- | ----- |
| CHART (day) \[ COURSE 1:      ECHO("Monday\\n")\!\!     LAND\!\! \] | CHART (**night, day**) \[ COURSE 1:      ECHO("Invalid Condition")\!\!     LAND\!\! \] |
| CHART (display) \[ COURSE 1:    ECHO("Hello")\!\! \] | CHART (letter) \[ COURSE **a**:    ECHO("Variable as label")\!\!    LAND\!\! |
| CHART (menu) \[ COURSE 1:    ECHO("File Menu")\!\!    SAIL\!\! \] | CHART (menu) \[ **ADRIFT**:    ECHO("No COURSE body")\!\!    LAND\!\! \] |
| CHART (letter) \[ COURSE 'A':    ECHO("Excellent")\!\!    LAND\!\! ADRIFT:    ECHO("Below Average")\!\!    LAND\!\! \] | CHART (digit) \[ COURSE 3:    ECHO("Variable as label")\!\!    LAND\!\! ADRIFT:    ECHO("Variable as label")\!\!    **SAIL\!\!** \] |
| CHART (grade) \[ COURSE 'A':    ECHO("Pass")\!\!    LAND\!\! ADRIFT:     LAND\!\! \] | CHART (grade) \[ COURSE 'A':    ECHO("Pass")\!\!    LAND\!\! ADRIFT:     **BACK\!** \] |

5. **Looping Statements \-** A looping statement executes a block of statements repeatedly until a given condition is satisfied. The reserved words HOIST, HEAVE, and HAUL-HEAVE are used for looping statements.  
     
   **a. HOIST** \- Iterates over a specific range of numbers.

**Rules in HOIST Statement**

1. It must always begin with a reserved word HOIST, followed by the condition enclosed in parentheses (**( )**), and end with the body enclosed in square brackets (**\[ \]**). The HOIST condition has three arguments: initialization, condition, and update.   
2. The initialization argument defines the starting state of the loop. The value assigned in the initialization must be a literal, variable, constant, array element, structure member, function return value, or arithmetic expression evaluating to type COIN only. It can be any of the three ways:  
1. Initialization of a COIN variable starting with the reserved word COIN, followed by the identifier, the assignment operator (**\=**), the value, and the statement terminator (**\!\!**). Multiple initialization is allowed and must be separated with commas.  
2. Assignment of a COIN value starting with the operand (variable, array element, or structure member), followed by the assignment operator, the value, and the statement terminator. Multiple assignments are allowed and must be separated with commas.  
3. A lone statement terminator.  
3. The condition is checked before each iteration. If the condition evaluates to NAY (false), the loop terminates; otherwise, the loop continues. The condition must be a relational expression wherein the operands can only be literals, variables, constants, array elements, structure members, function return values, or arithmetic expressions of type COIN or DIME, and it must not be empty. Multiple relational expressions are allowed and must strictly be separated with logical operators.  
4. The update argument runs after each iteration before re-evaluating the condition. It supports increment or decrement through a unary expression or assignment of values using a compound assignment operator. Multiple updates are allowed and must be separated with commas.  
5. The body supports all statements, except BACK statements, and can be empty. LAND and SAIL statements are optional and the body can only have either one located at the end.

**Syntax**

| HOIST (\<initialization\>\!\! \<condition\>\!\! \<update\>) \[    \<statement/s\> \] |
| ----- |
| HOIST (\<initialization\>\!\! \<condition\>\!\! \<update\>) \[ \] |
| **Initialization** |
| \<dtype\> \<id\> \= \<value\> |
| \<id\> \= \<value\> |
| λ |
| **Condition** |
| \<operand\>\<rel\_op\>\<operand\> |
| \<rel\_exp\>\<log\_op\>\<rel\_exp\> |
| **Update** |
| \<unary\_op\>\<id\> |
| \<id\> \<compound\_assign\_op\> \<value\> |

**Examples**

| VALID | INVALID |
| ----- | ----- |
| HOIST (COIN i \= 0\!\! i \< 5\!\! \+\#i) \[  \] | HOIST (**COIN i \= 0 i \< 5  i++**) \[  \] |
| HOIST (i{4} \= 0\!\! i{4}\<5\!\! \+\#i{4}) \[     ECHO("i \= %C, j \= %C\\n", i, j)\!\! \] | HOIST (**COIN i \= 0\!\! i--**) \[     ECHO("No condition”)\!\! \] |
| HOIST (\!\! x \> 0\!\! x+=1) \[    ECHO("Countdown: %C\\n", x)\!\! \] | HOIST**( )** \[ ECHO("empty condition")\!\! \] |
| HOIST (COIN i \= 0, j \= 10\!\! i \< j\!\! \+\#i, \-\#j) \[  \] | HOIST (COIN i \= 0, x \= **"start"**\!\! i \< j\!\! \+\#i, \-\#j) \[  \] |
| HOIST (COIN i \= 0\!\! i \< 10\!\! \+\#i) \[     \] | HOIST (COIN i \= 0\!\! i \< 10\!\! \+\#i) \[    **BACK\!\!** \] |
| HOIST (COIN i \= 0, j \= 10\!\! i \< 10\!\! \+\#i, \+\#j) \[    ECHO("i is %C, j is %C\\n", i, j)\!\! \] | HOIST (COIN i \= 0, j \= 10\!\! i \< 10\!\! **\+\#i+\#j**) \[    ECHO("i is %C, j is %C\\n", i, j)\!\! \] |
| HOIST (COIN i \= 0 \!\! i \< 10 && signal \== 1 \!\! \+\#i) \[     ECHO("The signal is %C", signal)\!\!        \] |     HOIST (COIN i \= 0\!\! i \< 10\!\! \+\#i) \[         **BACK\!\!**      \] |
|  HOIST (COIN i \= 1 \!\! i \+ 1 \< 10 && flag \== 1 \!\! \+\#i) \[         ECHO("Iteration: %C\\n", i)\!\!     \] | HOIST (COIN i \= 0, i **\<** 10, \+\#i) \[    \]  |

**b. HEAVE** \-  Executes the block of statements repeatedly while the given condition evaluates to true.  
**Rules in HEAVE Statements**

1. It must always begin with the reserved word HEAVE, followed by the condition enclosed in parentheses (**( )**), then the body enclosed in square brackets (**\[ \]**).   
2. The condition must be a literal, variable, constant, array element, structure member, function return value, relational expression, or grouped expression that evaluates to a BOOL data type. It must not be empty.  
3. The body supports all statements, except BACK statements, and can be empty. LAND and SAIL statements are optional and the body can only have either one located at the end.

**Syntax**

| HEAVE (\<condition\>) \[    \<statement/s\> \] |
| :---- |
| HEAVE (\<condition\>) \[ \] |

**Examples** 

| VALID | INVALID |
| ----- | ----- |
| HEAVE (i \< 5\) \[    ECHO("i \= %C\\n", i)\!\!    \+\#i\!\! \] | HEAVE (i \< 5)\!\! \[ i**\++**\!\! \] |
| HEAVE (choice \!= 3\) \[    ECHO("Enter 3 to exit: ")\!\!    ASK("%C", @choice)\!\!  \] | HEAVE **choice \!=3** \[     ECHO("Enter 3 to exit: ")\!\!    ASK("%C", @choice) \] |
| HEAVE (count \> 0\) \[    ECHO("Count: %C\\n", count)\!\!    \-\#count\!\! \] | HEAVE **()** \[    ECHO("Empty condition")\!\! \] |
| HEAVE (player$hp \> 0\) \[  \] | HEAVE **(100)** \[  \] |
| HEAVE (fuel \> 0\) \[    ECHO("Flying...")\!\!    fuel \-= 10 \!\!    SAIL \!\! \] | HEAVE (fuel \> 0\) \[    ECHO("Flying...")\!\!    fuel \-= 10 \!\!   **BACK\!\!** \] |

**c. HAUL-HEAVE** \- Executes the block of statements at least once, then executes it repeatedly as long as the condition is AYE (**true**), and terminates once the condition evaluates to NAY (**false**).

**Rules in HAUL-HEAVE Statements**

1. The HAUL-HEAVE statement begins with the HAUL keyword, followed by the HAUL body enclosed in square brackets (**\[ \]**).  
2. The HAUL body must be followed by the HEAVE keyword, a condition enclosed in parentheses (**( )**), and end with the statement terminator (**\!\!**).  
3. The condition must be a literal, variable, constant, array element, structure member, function return value, relational expression, or grouped expression that evaluates to a BOOL data type. It must not be empty.  
4. The body supports all statements, except BACK statements, and can be empty. LAND and SAIL statements are optional and the body can only have either one located at the end.

**Syntax**

| HAUL \[    \<statement/s\> \] HEAVE (\<condition\>)\!\! |
| :---- |
| HAUL \[ \] HEAVE (\<condition\>)\!\! |

**Examples** 

| VALID | INVALID |
| ----- | ----- |
| HAUL \[    ECHO("i \= %C\\n", i)\!\!     \+\#i\!\!  \] HEAVE (i \< 5)\!\! | HAUL \[    ECHO("No condition")\!\!  \] **HEAVE\!\!** |
| HAUL \[  \+\#x\!\!  \] HEAVE (x \< 10)\!\! | HAUL \[  \+\#x\!\!  \] HEAVE **(x \+ 10\)**\!\! |
| HAUL \[    ECHO("Processing...")\!\!    SAIL \!\! \] HEAVE (AYE)\!\! | HAUL \[    **BACK \!\!** \] HEAVE (AYE)\!\! |
| HAUL \[ECHO("Processing...")\!\!\] HEAVE (tries \< 4)\!\! | HAUL \[ECHO("Processing...")\!\!\] HEAVE **\[**tries \< 4**\]**\!\! |
| HAUL \[ECHO("Processing...")\!\!\] HEAVE (is\_waiting)\!\! | HAUL \[ECHO("Processing...")\!\!\] HEAVE (is\_waiting) |

6. **Jump Statements \-** A jump statement immediately jumps to execute a block of code in another part of the program.  
   **a. LAND Statement \-** It uses the reserved word LAND to immediately exit or terminate a conditional or looping statement.

**Rules for LAND Statements**

1. The LAND statement must begin with the reserved word LAND and end with the statement terminator (**\!\!**).  
2. It is required to end an ADRIFT body. For other conditional and looping statements, it is optional and can only be placed at the end of the body. Otherwise, it is considered invalid.

**Syntax**

| LAND\!\! |
| :---: |

**Examples**

| VALID | INVALID |
| ----- | ----- |
| LAND\!\! | LAND**(1\<3)**\!\! |
|  | L**and**\!\! |
| AHOY()\[     LOOK(3\>5) \[     LAND\!\!     \] \] | AHOY() \[     **LAND\!\!**      \] |
| AHOY() \[          CHART (day) \[             COURSE 1:                  ECHO("Monday")\!\!                  LAND\!\!              ADRIFT:                  ECHO("Noramal Day")\!\!                  LAND\!\!      \] \] | AHOY()\[     LOOK(3\>5) \[     \]    **LAND\!\!**     \] |
|  | AHOY() \[      LOOK (3 \> 5\) \[     LAND\!\!      **ECHO**("Land must be last")\!\!     \] \] |

**b. SAIL Statement \-** It uses the reserved word SAIL to skip the rest of the current iteration and continue to the next iteration.  
**Rules for SAIL Statements**

1. The SAIL statement must begin with the reserved word SAIL and end with the statement terminator (**\!\!**).  
2. It must not be used in an ADRIFT body. For other conditional and looping statements, it is optional and can only be placed at the end of the body. Otherwise, it is considered invalid.  
   **Syntax**

| SAIL\!\! |
| :---: |

**Examples**

| VALID | INVALID |
| ----- | ----- |
| SAIL\!\! | SAIL **id**\!\! |
|  | S**ail**\!\! |
| AHOY()\[     LOOK(3\>5) \[     SAIL\!\!     \]        \] | AHOY()\[     LOOK(3\>5) \[     \]     **SAIL\!\!**     \] |
| LOOK(x \> y) \[     ECHO("Correct placement")\!\!     SAIL\!\! \] | AHOY() \[     LOOK(3 \> 5\) \[         SAIL\!\!           **ECHO(**"Sail must be last")\!\!      \] \] |
| AHOY() \[     CHART(anchor) \[         COURSE 1:         ADRIFT:             ECHO("This is valid.")\!\!             LAND\!\!     \] \] | AHOY() \[     CHART(anchor) \[         COURSE 1:         ADRIFT:             **SAIL\!\!**                 LAND\!\!     \] \] |

**c. BACK Statement  \-** It uses the reserved word BACK to terminate the execution of a function. It may be used to return a value to the calling function.  
**Rules for BACK Statements**

1. A BACK statement must begin with the reserved word BACK, followed by an optional return value, and end with the statement terminator (**\!\!**).  
2. For returning functions:  
   1. A BACK statement is mandatory at the end of the body.  
   2. The keyword BACK must be followed by the return value. It must be a literal, variable, constant, array element, structure member, function return value, or expression of type COIN, DIME, BOOL, PARCH, or SCROLL only, and end with a statement terminator (**\!\!**).  
   3. The data type of the returned value must match the function's declared return type.  
3. For non-returning functions:  
1. A BACK statement is optional.  
2. The keyword BACK must be followed by the statement terminator (**\!\!**). Indicating a return value is invalid.  
4. For AHOY function:  
   1. There must be no BACK statement.

**Syntax**

| BACK \<value\>\!\! |
| :---: |
| BACK\!\!  |

**Examples**

| VALID | INVALID |
| :---: | ----- |
| BACK a\!\! | BACK **ECHO("Invalid")**\!\! |
| BACK\!\! | B**ack**\!\! |
| BACK\!\! | AHOY()\[    **BACK\!\!** \] |
| COIN add() \[BACK a \+ b\!\!\] | COIN add() \[BACK **ECHO("No")\!\!**\] |
| ABYSS display() \[ECHO("Hi")\!\!BACK\!\!\] | ABYSS display() \[ECHO("Hi")\!\!BACK **10**\!\!\] |

## 

## **FUNCTIONS** {#functions}

A function is a self-contained block of code designed to perform a specific task or related set of tasks. Functions may or may not return values depending on their intended purpose. The types of functions in SeaStack are the main function, returning functions, and non-returning functions, each serving distinct roles in program execution.

1. **AHOY Function** \- The main function uses the reserved word AHOY and is required in every program. This function coordinates the flow of instructions by calling other functions and managing the program’s control structure.  
   

**Rules for AHOY Function**

1. A valid SeaStack program must have exactly one AHOY function. It must be located at the bottom of the program.  
2. It starts with the reserved word AHOY followed by a pair of parentheses (**()**), and ends with the body enclosed in square brackets (**\[ \]**).  
3. The AHOY function cannot accept arguments, hence the parentheses must be left empty.  
4. The body must have at least one statement, excluding jump statements, and must not have any BACK statement. Local declarations are optional and located at the top of the body, before any statement.

	**Syntax**

| AHOY() \[     \<statement/s\>  \] |
| :---- |
| AHOY() \[     \<local\_declaration/s\>    \<statement/s\>  \] |

**Examples**

| VALID | INVALID |
| ----- | ----- |
| AHOY() \[  COIN age \= 18\!\! ECHO("Age: %C", age)\!\!  \]  | **COIN** AHOY() \[     COIN x \= 10\!\!     BACK x\!\! \] |
| AHOY() \[     COIN x \= 10\!\!     ECHO("X: %C\\n", x)\!\! \] |  AHOY**(x)** \[     COIN x \= 10\!\!     ECHO("X: %C\\n", x)\!\! \]  |
| AHOY() \[     COIN x \= 5, y \= 10, z \= x \+ y\!\!     ECHO("Sum: %C", z)\!\! \] | **AHOY {**     COIN x \= 5, y \= 10, z \= x \+ y\!\!     ECHO("Sum: %C", z)\!\! **}** |
| AHOY() \[     COIN x \= 10\!\!     COIN y \= 20\!\!     COIN sum \= x \+ y\!\!     ECHO("Sum: %C", sum)\!\! \]  |  AHOY**(1, 3\)** \[    ECHO("Hello, World")\!\! \]  |
|  | AHOY() \[    ECHO("Hello, World")\!\! \] **COIN add(COIN x, COIN y) \[ \<statement/s\>\!\! \]**  |
|  | AHOY() \[    ECHO("Hello, World")\!\!    **BACK 0\!\!** \] |

2. **Returning Function** \- This performs a specific computation and returns a value.

**Rules for Returning Function**

1. A returning function must be defined before the AHOY function and after all the global declarations. Any function definition inside a returning function is invalid.  
2. It must start with the return type, followed by a unique identifier, then the parameter list enclosed in parentheses (**( )**), and end with the body enclosed in square brackets (**\[ \]**).  
3. The return type can only be COIN, DIME, PARCH, SCROLL, or BOOL.  
4. The parameter list consists of parameter/s. A parameter starts with the data type followed by the identifier. Multiple parameters are allowed and must be separated with commas. The parameter list is optional and can be left empty if not needed.  
5. The body must contain a mandatory BACK statement as its final statement to return a value. All other statements are optional. Local declarations are optional and located at the top of the body, before any statement.

**Syntax**

| \<dtype\> \<id\> (\<parameter/s\>) \[     BACK \<value\>\!\! \] |
| :---- |
| \<dtype\> \<id\> (\<parameter/s\>) \[     \<statement/s\>     BACK \<value\>\!\! \] |
| \<dtype\> \<id\> (\<parameter/s\>) \[     \<local declaration/s\>     \<statement/s\>     BACK \<value\>\!\! \] |

**Examples**

| VALID | INVALID |
| ----- | ----- |
| COIN add(COIN a, COIN b) \[     BACK a+b\!\! \] | **ABYSS** addtwo(COIN a, COIN b) \[ BACK a \+ b\!\! \]  |
| COIN get\_ten() \[     COIN value \= 10\!\!     BACK value\!\! \] | PARCH get\_char() \[ BACK **123**\!\! \] |
| COIN get\_max() \[     COIN max \= 100\!\!     BACK 100\!\! \]  | COIN sum() **COIN x, COIN y** \[ BACK x \+ y\!\! \]  |
|  | COIN sum(**COIN x COIN y**)\[ BACK x \+ y\!\! \]  |
| PARCH get\_char(SCROLL text) \[     PARCH first \= 'X'\!\!     BACK first\!\! \]  | **BOOL** get\_text() \[     SCROLL text \= "test"\!\!  \] |
| SCROLL get\_name() \[     SCROLL name \= "SeaStack"\!\!     BACK name\!\! \] | **SCROLL** get\_number() \[     COIN num \= 42\!\!     **BACK 42**\!\!  \] |
| SCROLL concat\_strings(SCROLL first, SCROLL last) \[     SCROLL full \= first & " " & last\!\!     BACK full\!\! \] | **PARCH** get\_word() \[     SCROLL word \= "hello"\!\!     BACK **3+5**\!\! \] |

3. **Non-returning Function** \- This operates but does not return a value to the caller. 

**Rules for Non-returning Function**

1. A non-returning function must be defined before the AHOY function and after all the global declarations. Any function definition inside a non-returning function is invalid.  
2. It must start with the reserved word ABYSS as its return type, indicating it does not return a value. It is followed by a unique identifier, then the parameter list enclosed in parentheses (**( )**), and ends with the body enclosed in square brackets (**\[ \]**).  
3. The parameter list consists of parameter/s. A parameter starts with the data type followed by the identifier. Multiple parameters are allowed and must be separated with commas. The parameter list is optional and can be left empty if not needed.  
4. The body must have at least one statement, excluding jump statements. It can end with an optional BACK statement without a return value. Local declarations are optional and located at the top of the body, before any statement.

**Syntax**

| ABYSS \<id\> (\<parameter/s\>) \[     \<statement/s\> \] |
| :---- |
| ABYSS \<id\> (\<parameter/s\>) \[     \<statement/s\>     BACK\!\! \] |
| ABYSS  \<id\> (\<parameter/s\>) \[     \<local declaration/s\>     \<statement/s\>     BACK\!\! \] |

**Examples**

| VALID | INVALID |
| ----- | ----- |
| ABYSS greet() \[     SCROLL msg \= "Hello World"\!\!     ECHO("%S", msg)\!\! \] | ABYSS display() \[     ECHO("Hello")\!\!     BACK **10**\!\! \] |
| ABYSS display() \[ ECHO("SeaStack")\!\! \] | ABYSS **display** \[ ECHO("SeaStack”)\!\! \]  |
| ABYSS display\_sum(COIN a, COIN b) \[     COIN sum \= a \+ b\!\!     ECHO("Sum: %C", sum)\!\! \] | ABYSS add\_numbers(**COIN a  COIN b**) \[ COIN sum \= a \+ b\!\! ECHO("The sum is: %C, sum)\!\! \]  |
| ABYSS add\_three(COIN x, COIN y, COIN z) \[ COIN sum \= x \+ y \+ z\!\! ECHO("The sum is: %C”, sum)\!\! BACK\!\! \] | ABYSS result() **\[ \]**  |
| ABYSS display\_diff(COIN x, COIN y) \[     COIN diff\!\!     diff \= x \- y\!\!     ECHO("The difference is: %C", diff)\!\!     BACK\!\! \] | ABYSS display\_diff(COIN x, COIN y) \[     COIN diff\!\!     diff \= x \- y     ECHO("The difference is: %C", diff)\!\!     BACK **diff**\!\! \] |

	

**Rules for Function Calling**

1. A function is called by indicating its identifier followed by a pair of parentheses enclosing the arguments, separated by commas, and ending with the statement terminator (**\!\!**).  
2. The number and types of arguments in a function call must exactly match the function’s parameter list and any exceeding or subceeding argument is invalid.  The argument can be literals, variables, constants, array elements, structure members, function return values, or expressions.  
3. A subfunction can be called inside the AHOY function or another subfunction and must be defined before calling. The AHOY function cannot be called by any function.

	**Syntax**

| \<id\>()\!\! |
| :---: |
| \<id\>(\<argument1\>,\<argument2\>, …, \<argumentN\>)\!\! |

**Examples**

| VALID | INVALID |
| :---: | :---: |
| hello()\!\! | hello\!\! |
| add\_numbers(5, 10)\!\! | add\_numbers(**5 10**)\!\! |
| greet\_name('A', 20)\!\! | greet\_name**{**'A', 20**}** |
| increment(num)\!\! | increment(num**\!\!** |
| multiply(5, 3)\!\! | **AHOY**()\!\! |

## **COMMENTS** {#comments}

A comment is an annotation in the source code that helps with understanding the code but is ignored by the system during execution.

**Rules for Comments**

1. A single-line comment must start with a single tilde symbol (**\~**) and terminates with a newline.  
2. A multi-line comment must start with a tilde followed by an open parenthesis **\~(**. Any following character will be read as a comment until enclosed with a close parenthesis and tilde **)\~**. Unclosed multi-line comments are invalid.  
3. Any character following a tilde symbol **\~** that is not immediately succeeded by an open parenthesis **(** is treated as a single-line comment.  
4. Comments placed inside a SCROLL literal are considered as a part of the literal and not a comment. Comments in between COIN, DIME, PARCH, or BOOL literals are invalid.

	  
**Syntax**

| \~\<single-line-comment\> |
| :---: |
| \~(\<multi-line comment/s\>)\~ |

**Examples**

| VALID | INVALID |
| :---: | :---: |
| \~This is a single line | **\~** |
| \~(This is a multi-line comment It spans multiple lines)\~ | **/\*** Invalid Symbol **\*/**   |
| COIN a \= 10\!\! \~This comment is valid | COIN b \= 15 \~Statement not properly terminated |
| COIN sum \= 5 \+ 10\!\!  \~ valid comment  | COIN sum \= 5 **\~ comment** \+ 10\!\! |

4. # **REGULAR DEFINITION** {#regular-definition}

| Name | Definition |
| :---: | :---: |
| lowlet | {a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z} |
| uplet | {A, B, C, D, E, H, L, M, N, P, S} |
| digit | {0, 1, 2, 3, 4, 5, 6, 7, 8, 9} |
| nonzero | {1, 2, 3, 4, 5, 6, 7, 8, 9} |
| alphanumeric | {lowlet, digit} |
| ASCII | {all printable characters} |
| whitespace | {  , \\t, \\n } |
| arith\_op | {+, \-, \*, /, %, ^} |
| gen\_op | {arith\_op, \<, \>, \=, \!, &, |} |
| comment | {\~} |
| id\_delim | {whitespace, gen\_op, (, ), \], {, }, $, ,} |
| gen\_op\_delim | {whitespace, alphanumeric, \-, (} |
| log\_op\_delim | {gen\_op\_delim, A, N, ', "} |
| minus\_delim | {whitespace, lowlet, (} |
| not\_delim | {lowlet, A, N, (} |
| concat\_delim | {whitespace, lowlet, (, "} |
| assign\_delim | {log\_op\_delim, \[, \!} |
| back\_delim | {whitespace, (, \!} |
| digit\_delim | {whitespace, gen\_op, ), \], }, :, ,} |
| bool\_delim | {whitespace, ), \], &, |, \!, \=, ,} |
| parch\_delim | {bool\_delim, :} |
| scr\_delim | {parch\_delim, { } |
| comma\_delim | {assign\_delim, @} |
| colon\_delim | {whitespace, lowlet, A, C, E, H, L, \+, \-} |
| terminator\_delim | {colon\_delim, B, D, M, P, S, \] } |
| closecb\_delim | {whitespace, gen\_op, ), \], {, &, :, ,} |
| closep\_delim | {whitespace, gen\_op, ), \[, \], ,} |
| openp\_delim | {log\_op\_delim, B, C, D, P, S, ), \!} |
| closesb\_delim | {whitespace, lowlet, uplet, \], \!, \+, \-, ,} |
| opensb\_delim | {closesb\_delim, digit, \[, ', "} |
| c\_parch | {ASCII} \- { ' | \\n | \\} |
| c\_scr | {ASCII} \- { " | \\n | \\} |
| es\_parch | {s, n, t, 0, \\} |
| es\_scr | {d, n, t, 0, \\} |
| multi\_comment | {ASCII} \- {)} |

5. # **REGULAR EXPRESSION** {#regular-expression}

| RESERVED WORDS |  |  |
| :---: | :---: | :---: |
| **Reserved Word** | **Regular Expression** | **Token** |
| ABYSS | (A)(B)(Y)(S)(S) | **ABYSS** |
| ADRIFT | (A)(D)(R)(I)(F)(T) | **ADRIFT** |
| AHOY | (A)(H)(O)(Y) | **AHOY** |
| ASK | (A)(S)(K) | **ASK** |
| AYE | (A)(Y)(E) | **AYE** |
| BACK | (B)(A)(C)(K) | **BACK** |
| BOOL | (B)(O)(O)(L) | **BOOL** |
| CHART | (C)(H)(A)(R)(T) | **CHART** |
| COIN | (C)(O)(I)(N) | **COIN** |
| COURSE | (C)(O)(U)(R)(S)(E) | **COURSE** |
| DIME | (D)(I)(M)(E) | **DIME** |
| DROP | (D)(R)(O)(P) | **DROP** |
| DROPLOOK | (D)(R)(O)(P)(L)(O)(O)(K) | **DROPLOOK** |
| ECHO | (E)(C)(H)(O) | **ECHO** |
| HAUL | (H)(A)(U)(L) | **HAUL** |
| HEAVE | (H)(E)(A)(V)(E) | **HEAVE** |
| HOIST | (H)(O)(I)(S)(T) | **HOIST** |
| LAND | (L)(A)(N)(D) | **LAND** |
| LOCKE | (L)(O)(C)(K)(E) | **LOCKE** |
| **Reserved Word** | **Regular Expression** | **Token** |
| LOOK | (L)(O)(O)(K) | **LOOK** |
| MAST | (M)(A)(S)(T) | **MAST** |
| NAY | (N)(A)(Y) | **NAY** |
| PARCH | (P)(A)(R)(C)(H) | **PARCH** |
| SAIL | (S)(A)(I)(L) | **SAIL** |
| SCROLL | (S)(C)(R)(O)(L)(L) | **SCROLL** |

| RESERVED SYMBOLS |  |  |
| :---: | :---: | :---: |
| **Reserved Symbol** | **Regular Expression** | **Token** |
| \+ | (+) | **\+** |
| \+\# | (+)(\#) | **\+\#** |
| \+= | (+)(=) | **\+=** |
| \- | (-) | **\-** |
| \-\# | (-)(\#) | **\-\#** |
| \-= | (-)(=) | **\-=** |
| \* | (\*) | **\*** |
| \*= | (\*)(=) | **\*=** |
| / | (/) | **/** |
| /= | (/)(=) | **/=** |
| % | (%) | **%** |
| %= | (%)(=) | **%=** |
| **Reserved Symbol** | **Regular Expression** | **Token** |
| ^ | (^) | **^** |
| ^= | (^)(=) | **^=** |
| \= | (=) | **\=** |
| \== | (=)(=) | **\==** |
| \! | (\!) | **\!** |
| \!\! | (\!)(\!) | **\!\!** |
| \!\# | (\!)(\#) | **\!\#** |
| \!= | (\!)(=) | **\!=** |
| \< | (\<) | **\<** |
| \<= | (\<)(=) | **\<=** |
| \> | (\>) | **\>** |
| \>= | (\>)(=) | **\>=** |
| & | (&) | **&** |
| && | (&)(&) | **&&** |
| || | (|)(|) | **||** |
| : | (:) | **:** |
| @ | (@) | **@** |
| $ | ($) | **$** |
| , | (,) | **,** |
| { | ({) | **{** |
| } | (}) | **}** |
| ( | (() | **(** |
| **Reserved Symbol** | **Regular Expression** | **Token** |
| ) | ()) | **)** |
| \[ | (\[) | **\[** |
| \] | (\]) | **\]** |

| LITERALS |  |  |
| :---: | :---: | :---: |
| **Literal** | **Regular Expression** | **Token** |
| Identifier | (lowlet)(alphanumeric \+ \_ \+ λ)19 | id |
| COIN | ( \- \+  λ)(digit)(digit \+ λ)15 | COIN-lit |
| DIME | ( \- \+  λ)(digit)(digit \+ λ)15(.)(digit)(digit \+ λ)7 | DIME-lit |
| PARCH | (')((c\_parch)|(\\)(es\_parch))(') | PARCH-lit |
| SCROLL | (")((c\_scr)|(\\)(es\_scr))\+(") | SCROLL-lit |
| Single-line Comment | (\~)(ASCII)\*(\\n) | single-comment |
| Multi-line Comment | (\~()(multi\_comment)\*()\~) | multi-comment |

6. # **TRANSITION DIAGRAM** {#transition-diagram}

   ## **RESERVED WORDS** {#reserved-words}

![][image1]  
![][image2]  
![][image3]

## **RESERVED SYMBOLS** {#reserved-symbols}

![][image4]

![][image5]

![][image6]  
![][image7]

## **IDENTIFIERS** {#identifiers-1}

![][image8]

![][image9]

## 

## 

## **COIN LITERALS** {#coin-literals}

![][image10]  
![][image11]

## **DIME LITERALS** {#dime-literals}

![][image12]

## **PARCH AND SCROLL LITERALS** {#parch-and-scroll-literals}

![][image13]

## **COMMENTS** {#comments-1}

**![][image14]** 

7. # **CONTEXT FREE GRAMMAR** {#context-free-grammar}

![][image15]

![][image16]

![][image17]

![][image18]

![][image19]

![][image20]

![][image21]

![][image22]

![][image23]

![][image24]

![][image25]

![][image26]

![][image27]

![][image28]

![][image29]

![][image30] 

![][image31]

![][image32]

# 

8. # **FIRST SET** {#first-set}

![][image33]  
![][image34]

![][image35]

![][image36]

![][image37]

![][image38]

![][image39]

![][image40]

9. # **FOLLOW SET** {#follow-set}

![][image41]

![][image42]

![][image43]

![][image44]

![][image45]

![][image46]

![][image47]

![][image48]

![][image49]

![][image50]

# 

10. # **PREDICT SET** {#predict-set}

![][image51]

![][image52]

![][image53]

![][image54]

![][image55]

![][image56]

![][image57]

![][image58]

![][image59]

![][image60]

![][image61]

![][image62]

![][image63]

![][image64]

![][image65]

![][image66]

![][image67]

![][image68]

![][image69]

![][image70]

![][image71]

![][image72]

![][image73]

![][image74]

![][image75]

![][image76]  
![][image77]

![][image78]  
![][image79]  
![][image80]  
![][image81]

![][image82]  
![][image83]  
![][image84]

11. # **TEST SCRIPTS** {#test-scripts}

    ## **LEXICAL ANALYSIS**

![][image85]

![][image86]

![][image87]

![][image88]

![][image89]![][image90]  
  ![][image91]  
![][image92]

![][image93]

![][image94]

![][image95]

![][image96]  
![][image97]  
![][image98]

![][image99]

![][image100]

![][image101]

![][image102]

![][image103]

![][image104]

![][image105]

![][image106]

![][image107]

| Test Case/Test Scenario | Expected Output | Actual Output | Test Result |
| ----- | ----- | ----- | ----- |
| **Variable Declaration/Initialization** |  |  |  |
| AHOY() \[     COIN x \= 5, y \= 10, z \= x \+ y\!\!     ECHO("Sum: %C", z)\!\! \] | No Syntax Error | No Syntax Error |  ✔ |
| AHOY() \[     DIME pi \= 3.14159, radius \= 2.5, area \= pi \* (radius ^ 2)\!\!     ECHO("Area: %D", area)\!\! \] | No Syntax Error | No Syntax Error |  ✔  |
| COIN add(COIN a, COIN b) \[     COIN sum \= a \+ b\!\!     BACK sum\!\! \] AHOY() \[     COIN num1 \= 15, num2 \= 25, total \= add(num1, num2)\!\!     ECHO("Total: %C", total)\!\! \]  | No Syntax Error | No Syntax Error |  ✔  |
| AHOY() \[     SCROLL first \= "Hello", second \= "World", greeting \= first & " " & second\!\!     ECHO("%S", greeting)\!\! \] | No Syntax Error | No Syntax Error |  ✔  |
| AHOY() \[     BOOL flag1 \= AYE, flag2 \= NAY, result \= flag1 && \!flag2\!\!     ECHO("Result: %B", result)\!\! \] | No Syntax Error | No Syntax Error |  ✔  |
| AHOY() \[     PARCH initial \= 'A', next \= 'B'\!\!     DIME value1 \= 10.5, value2 \= 20.7, avg \= (value1 \+ value2) / 2.0\!\!     ECHO("Average: %D", avg)\!\! \] | No Syntax Error | No Syntax Error |  ✔  |
| AHOY() \[     increment()\!\!     COIN local\_copy \= global\_counter\!\!     SCROLL status \= "Counter updated"\!\!     ECHO("%S: %C", status, local\_copy)\!\! \]  | With Syntax Error | Unexpected token: 'COIN' 'COIN local\_copy \= global\_counter\!\!' Expected: 'id, ASK, ECHO, LOOK, CHART, HOIST, HEAVE, HAUL, \+\#, \-\#, \]' |  ✔  |
| AHOY() \[     PARCH initial \= 'A', next \= 'B'\!\!     DIME value1 \= 10.5, value2 \= 20.7, avg \= (value1 \+ value2) / 2.0\!\!     ECHO("Average: %D", avg)\!\! \] | No Syntax Error | No Syntax Error |  ✔  |
| AHOY() \[     COIN x \= 5, DIME y \= 10.5\!\!       ECHO("Invalid")\!\! \] | With Syntax Error | Misplaced Token: 'DIME' 'COIN x \= 5, DIME y \= 10.5\!\!' Expected: 'id'  |  ✔ |
| AHOY() \[     COIN grade \= 100 \!\!     DIME ml \= 12.5 \!\! PARCH letter \= 'a'\!\!     SCROLL name \= "Black Pearl" \!\!     BOOL is\_true \= AYE \!\!     ECHO("%S", name)\!\! \] | No Syntax Error | No Syntax Error |  ✔  |
| AHOY() \[     COIN area{5} \!\!     DIME area2{2} \= \[14.5, 121.0\]\!\!     ECHO("%D", area2)\!\! \] | No Syntax Error | No Syntax Error |  ✔  |
| AHOY() \[     COIN area \= 20\!\!     PARCH letter \= "A"\!\!     DIME height \= \-12.4\!\!     ECHO("%P", letter)\!\! \] | With Syntax Error | Unexpected token: 'SCROLL-lit' 'PARCH letter \= "A"\!\!' Expected: 'id, PARCH-lit' |  ✔ |
| AHOY() \[     COIN age \= 25, DIME weight \= 68.5\!\!     ECHO("Data: %C, %D\\n", age, weight)\!\! \]  | With Syntax Error | Misplaced Token: 'DIME' 'COIN age \= 25, DIME weight \= 68.5\!\!' Expected: 'id' |  ✔ |
| **Constant Declaration/Initialization** |  |  |  |
| LOCKE COIN max\_students \= 50\!\! AHOY() \[     COIN double\_max \= max\_students \* 2\!\!     ECHO("Double: %C\\n", double\_max)\!\! \] | No Syntax Error | No Syntax Error |  ✔  |
| LOCKE DIME pi \= 3.14159265\!\! AHOY() \[     DIME area \= pi \* 5.0 \* 5.0\!\!     ECHO("Area: %D\\n", area)\!\! \] | No Syntax Error | No Syntax Error |  ✔  |
| LOCKE SCROLL university \= "University of the Philippines"\!\! AHOY() \[ SCROLL msg \= university & " is great"\!\! ECHO("%S\\n", msg)\!\! \] | No Syntax Error | No Syntax Error |  ✔  |
| LOCKE BOOL debug\_mode \= AYE\!\! AHOY() \[ BOOL status \= debug\_mode\!\! ECHO("Debug: %B\\n", status)\!\! \] | No Syntax Error | No Syntax Error |  ✔  |
| LOCKE PARCH grade\_a \= 'A'\!\! AHOY() \[     PARCH my\_grade \= grade\_a\!\!     ECHO("Grade: %P\\n", my\_grade)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| LOCKE DIME rate \= 0.05 \+ 0.02\!\! AHOY() \[     ECHO("Invalid\\n")\!\! \] | With Syntax Error | Misplaced Token '+' 'LOCKE DIME rate \= 0.05 \+ 0.02\!\!' Expected any: '\!\!' |  ✔ |
| limit \= 500\!\! AHOY() \[     ECHO("Invalid\\n")\!\! \] | With Syntax Error | Invalid Token 'id' 'limit \= 500\!\!' Expected any: 'COIN, DIME, PARCH, SCROLL, BOOL, ABYSS, LOCKE, MAST, AHOY' |  ✔ |
| LOCKE PARCH delimiter \= ';', separator \= ','\!\! AHOY() \[     ECHO("Invalid\\n")\!\! \] | With Syntax Error | Misplaced Token ',' 'LOCKE PARCH delimiter \= ';', separator \= ','\!\!' Expected any: '\!\!' |  ✔ |
| LOCKE DIME tax\_rate \= 0.15\!\! LOCKE COIN default\_quantity \= 1\!\! AHOY() \[     COIN price \= 100\!\!     DIME total \= price \* (1.0 \+ tax\_rate) \* default\_quantity\!\!     ECHO("Total: %D", total)\!\! \] |  No Syntax Error  |  No Syntax Error |  ✔  |
| LOCKE COIN max\_score \= 100\!\! AHOY() \[     ECHO("Maximum score: %C", max\_score)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| LOCKE SCROLL name \= 123\!\!    AHOY() \[     ECHO("name: %S", name)\!\! \] | With Syntax Error | Misplaced Token: 'COIN-lit' 'LOCKE SCROLL name \= 123\!\!' Expected: 'SCROLL-lit'  |  ✔ |
| LOCKE BOOL valid\_status \= AYE && AYE\!\! AHOY() \[     ECHO("Status: %B\\n", valid\_status)\!\! \] | With Syntax Error | Unexpected token: '&&' 'LOCKE BOOL valid\_status \= AYE && AYE\!\!' Expected: ',, \!\!'  |  ✔ |
| LOCKE BOOL is\_passing \= 75 \>= 60\!\! AHOY() \[     BOOL check \= is\_passing\!\!     ECHO("Pass: %B\\n", check)\!\! \] | With Syntax Error | Unexpected token: 'COIN-lit' 'LOCKE BOOL is\_passing \= 75 \>= 60\!\!' Expected: 'AYE, NAY' |  ✔ |
| LOCKE PARCH grade \= 'B'\!\! AHOY() \[     PARCH my\_grade \= grade\!\!     ECHO("Grade: %P\\n", my\_grade)\!\! \]  |  No Syntax Error |  No Syntax Error |  ✔  |
| Array Declaration/Initialization |  |  |  |
| AHOY() \[     COIN numbers{5} \= \[10, 20, 30, 40, 50\]\!\!     COIN sum \= numbers{0} \+ numbers{4}\!\!     ECHO("Sum: %C", sum)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     DIME values{3} \= \[1.5, 2.7, 3.9\]\!\!     DIME avg \= (values{0} \+ values{1} \+ values{2}) / 3.0\!\!     ECHO("Average: %D", avg)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     PARCH letters{5} \= \['A', 'B', 'C', 'D', 'E'\]\!\!     PARCH first \= letters{0}\!\!     PARCH mid \= letters{2}\!\!     ECHO("First: %P, Mid: %P", first, mid)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     COIN grid{3}{3} \= \[\[1, 2, 3\], \[4, 5, 6\], \[7, 8, 9\]\]\!\!     COIN diagonal \= grid{0}{0} \+ grid{1}{1} \+ grid{2}{2}\!\!     ECHO("Diagonal sum: %C", diagonal)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     COIN matrix{2, 3} \= \[\[1, 2, 3\], \[4, 5, 6\]\]\!\!     ECHO("Invalid\\n")\!\! \] | With Syntax Error | Misplaced Token: ',' 'COIN matrix{2, 3} \= \[\[1, 2, 3\], \[4, 5, 6\]\]\!\!' Expected: '}'  |  ✔ |
| AHOY() \[     DIME grid{3}{3} \= \[\[1.1, 2.2, 3.3\], \[4.4, 5.5, 6.6\], \[7.7, 8.8, 9.9\]\]\!\!     DIME sum \= grid{0}{0} \+ grid{1}{1} \+ grid{2}{2}\!\!     ECHO("Diagonal sum: %D", sum)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     DIME grid{3}{3} \= \[\[1.1, 2.2, 3.3\], \[4.4, 5.5, 6.6\], \[7.7, 8.8, 9.9\]\]\!\!     DIME sum \= grid{0}{0} \+ grid{1}{1} \+ grid{2}{2}\!\!     ECHO("Diagonal sum: %D", sum)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     COIN scores{5}\!\!     scores{0} \= 85\!\!     scores{1} \= 90\!\!     scores{2} \= 78\!\!     scores{3} \= 92\!\!     scores{4} \= 88\!\!     ECHO("Score 3: %C", scores{3})\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ COIN mixed\_array{5} \= \[     10,     calculate\_coin(),     3.14,     get\_value() \+ 5,     15 \]\!\! | With Syntax Error |   Unexpected token: 'DIME-lit' '3.14,' Expected: 'id, (, COIN-lit' |  ✔ |
| **MAST Defining/Acessing** |  |  |  |
| MAST animal \[    SCROLL species\!\!     SCROLL description\!\! \]\!\! AHOY() \[     MAST animal insect \= \["spider", "8 legs"\]\!\! \] | With Syntax Error | Unexpected token: '\]' '\]' Expected: 'MAST, id, ASK, ECHO, LOOK, CHART, HOIST, HEAVE, HAUL, \+\#, \-\#'  |  ✔ |
| MAST employee \[     SCROLL name\!\!     COIN id, age\!\! \]\!\! AHOY() \[     MAST employee e1, e2, e3\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| MAST pirate \[     SCROLL name\!\!     COIN c\!\!     BOOL hook\!\! \]\!\! AHOY() \[     MAST pirate p1\!\!     p1$name \= "Bie"\!\!     p1$c \= 100\!\!     p1$hook \= NAY\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| MAST box \[     COIN weight\!\! \]\!\! AHOY() \[     MAST box b1\!\!     b1$weight \= 50\!\!     ECHO ("%C, b1$weight")\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| MAST add \[     DIME grade\!\! \]\!\! AHOY() \[     MAST add g1\!\!     g1$grade \= 2.5\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| MAST product \[     SCROLL name\!\!     DIME price\!\!     COIN quantity\!\! \] AHOY() \[     MAST product item1 \= \["Laptop", 899.99, 5\]\!\!     ECHO("Product: %S\\n", item1$name)\!\! \] | With Syntax Error | Misplaced Token: 'AHOY' 'AHOY() \[' Expected: '\!\!'  |  ✔ |
| MAST vehicle \[     SCROLL brand\!\!     SCROLL model\!\!     COIN year\!\! \]\!\! AHOY() \[     MAST vehicle car1 \= ("Toyota", "Camry", 2023)\!\!     ECHO("Brand: %S\\n", car1$brand)\!\! \]  | With Syntax Error | Unexpected token: '\]' '\]\!\!' Expected: 'COIN, DIME, PARCH, SCROLL, BOOL'  |  ✔ |
| **Arithmetic Expressions** |  |  |  |
| AHOY() \[     DIME values{3} \= \[2.5, 3.5, 4.5\]\!\!     DIME avg \= (values{0} \+ values{1} \+ values{2}) / 3.0\!\!     ECHO("Average: %D\\n", avg)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     DIME matrix{2}{2} \= \[\[1.5, 2.5\], \[3.5, 4.5\]\]\!\!     DIME sum \= (matrix{0}{0} \+ matrix{1}{1}) \* (matrix{0}{1} \+ matrix{1}{0})\!\!     ECHO("Sum: %D", sum)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     DIME y \= 5.5\!\!     DIME wrong \= (y \+ )\!\!     ECHO("Invalid\\n")\!\! \] | With Syntax Error | Unexpected token: ')' 'DIME wrong \= (y \+ )\!\!' Expected: 'id, (, DIME-lit, COIN-lit'  |  ✔  |
| AHOY() \[     COIN value\!\!     value \= \* 20\!\!     ECHO("Value: %C\\n", value)\!\! \] | With Syntax Error | Unexpected token: '\*' 'value \= \* 20\!\!' Expected: 'id, (, COIN-lit, DIME-lit, PARCH-lit, SCROLL-lit, AYE, NAY, \!, \!\#' |  ✔  |
| AHOY() \[     DIME x \= 10.5, y \= 3.2, z \= 2.0\!\!     DIME complex \= (x \* y \+ z) / (x \- y) \+ (y ^ z)\!\!     ECHO("Complex: %D", complex)\!\! \] AHOY() \[     COIN a \= 5, b \= 10\!\!     COIN calc \= a \++ b\!\!     ECHO("Invalid\\n")\!\! \] |  No Syntax Error With Syntax Error  |  No Syntax Error Invalid character '+' Expected: '\#, (, \-, \=, alphanumeric, whitespace'  |  ✔  ✔  |
| **Relational Expressions** |  |  |  |
| AHOY() \[ COIN x \= 5, y \= 10\!\! BOOL result \= x \< y\!\! ECHO("Result: %B\\n", result)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ DIME a \= 3.5, b \= 2.1\!\! BOOL check \= (a \+ b) \>= (a \* b)\!\! ECHO("Check: %B\\n", check)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ SCROLL name1 \= "Alice", name2 \= "Bob"\!\! BOOL same \= (name1 \== name2)\!\! BOOL different \= (name1 \!= name2)\!\! ECHO("Same: %B, Different: %B", same, different)\!\! \]  |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     BOOL flag1 \= AYE, flag2 \= NAY\!\!     BOOL comp1 \= (flag1 \== AYE)\!\!     BOOL comp2 \= (flag2 \!= AYE)\!\!     BOOL result \= comp1 && comp2\!\!     ECHO("Result: %B", result)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ PARCH grade1 \= 'A', grade2 \= 'B'\!\! BOOL is\_higher \= (grade1 \== grade2)\!\! BOOL not\_equal \= (grade1 \!= grade2)\!\! ECHO("Higher: %B, Not equal: %B", is\_higher, not\_equal)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ BOOL flag \= AYE\!\! COIN num \= 5\!\! BOOL wrong \= flag \< num\!\! ECHO("Invalid\\n")\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ PARCH ch \= 'A'\!\! BOOL bad \= ch \> 'Z'\!\! ECHO("Invalid\\n")\!\! \] | With Syntax Error  | Unexpected token: 'PARCH-lit' 'BOOL bad \= ch \> 'Z'\!\!' Expected: 'id, (, COIN-lit, DIME-lit'  |  ✔  |
| AHOY() \[     COIN score \= 85\!\!     BOOL passed \= score \>= \!\!     ECHO("Passed: %B\\n", passed)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     BOOL flag \= AYE\!\!     COIN num \= 5\!\!     BOOL wrong \= flag \< num\!\!     ECHO("Invalid\\n")\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| **Logical Expressions** |  |  |  |
| AHOY() \[     DIME gpa \= 3.5\!\!     COIN age \= 20\!\!     BOOL eligible \= ((gpa \>= 3.0) && (age \>= 18)) || ((gpa \>= 3.5) && (age \>= 17))\!\!     ECHO("Eligible: %B", eligible)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     BOOL a \= AYE\!\!     BOOL result \= \!\#a && \!NAY || AYE && \!\#NAY\!\!     ECHO("Result: %B", result)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     COIN score \= 85, attendance \= 90\!\!     BOOL pass \= (score \>= 60 && attendance \>= 75\) || (score \>= 90 || attendance \== 100)\!\!     ECHO("Pass: %B", pass)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     SCROLL name \= "Admin"\!\!     COIN level \= 5\!\!     BOOL access \= (name \== "Admin" && level \>= 3\) || (name \!= "Guest" && level \> 0)\!\!     ECHO("Access: %B", access)\!\! \]  |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     BOOL matrix{2}{2} \= \[\[AYE, NAY\], \[NAY, AYE\]\]\!\!     BOOL check \= (matrix{0}{0} && \!matrix{0}{1}) || (matrix{1}{1} && \!matrix{1}{0})\!\!     ECHO("Check: %B", check)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     BOOL status \= NAY\!\!     BOOL nested \= \!((status && AYE) || (NAY && status))\!\!     ECHO("Nested: %B\\n", nested)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     SCROLL name \= "Test"\!\!     BOOL wrong \= name \> "Admin"\!\!     ECHO("Invalid\\n")\!\! \] | With Syntax Error  | Unexpected token: 'SCROLL-lit' 'BOOL wrong \= name \> "Admin"\!\!' Expected: 'COIN-lit, DIME-lit, \-' |  ✔  |
| AHOY() \[     BOOL a \= AYE\!\!     BOOL result \= a && \!\!     ECHO("Result: %B\\n", result)\!\! \] | With Syntax Error  |  Unexpected token: '\!\!' 'BOOL result \= a && \!\!' Expected: 'id, (, AYE, NAY, \!, \!\#, COIN-lit, DIME-lit, PARCH-lit, SCROLL-lit' |  ✔  |
| AHOY() \[     BOOL x \= AYE, y \= NAY\!\!     BOOL result \= x && || y     ECHO("Result: %B\\n", result)\!\! \] | With Syntax Error  | Unexpected token: '||' 'BOOL result \= x && || y' Expected: 'id, (, AYE, NAY, \!, \!\#, COIN-lit, DIME-lit, PARCH-lit, SCROLL-lit' |  ✔  |
| **Unary Expressions** |  |  |  |
| AHOY() \[     COIN counter \= 0\!\!     HOIST (COIN i \= 0\!\! i \< 5\!\! \+\#i) \[         \+\#counter\!\!         ECHO("Counter: %C", counter)\!\!     \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     COIN nums{5} \= \[10, 20, 30, 40, 50\]\!\!     COIN index \= 0\!\!     HEAVE (index \< 5\) \[         ECHO("Num: %C", nums{index})\!\!         \+\#index\!\!     \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ COIN countdown \= 10\!\! HAUL \[ ECHO("T-minus: %C", countdown)\!\! \-\#countdown\!\! \] HEAVE (countdown \>= 0)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     COIN x \= 50\!\!     LOOK (x \> 25\) \[         \+\#x\!\!         LOOK (x \> 40\) \[             \-\#x\!\!             \-\#x\!\!         \]     \]     ECHO("Final x: %C", x)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     COIN attempts \= 0, max\_attempts \= 3\!\!     HEAVE (attempts \< max\_attempts) \[         \+\#attempts\!\!         LOOK (attempts \== 2\) \[             ECHO("Warning: Last attempt")\!\!         \]     \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     COIN loop\_var \= 1\!\!     HOIST (loop\_var\!\! loop\_var \<= 5\!\! \+\#loop\_var) \[         ECHO("Loop: %C\\n", loop\_var)\!\!     \] \] | With Syntax Error  | Misplaced Token: '\!\!' 'HOIST (loop\_var\!\! loop\_var \<= 5\!\! \+\#loop\_var) \[' Expected: '='  | ✔  |
| AHOY() \[     COIN tries \= 0, max\_tries \= 3\!\!     HAUL \[         \+\#tries\!\!         ECHO("Attempt: %C\\n", tries)\!\!     \] HEAVE (tries \< max\_tries)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| **SCROLL Expressions** |  |  |  |
| AHOY() \[ SCROLL first \= "Hello", middle \= " beautiful ", last \= "world"\!\! SCROLL full \= first & middle & last & "\!"\!\! ECHO("%S", full)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ SCROLL names{3} \= \["Alice", "Bob", "Charlie"\]\!\! SCROLL combined \= names{0} & ", " & names{1} & ", and " & names{2}\!\! ECHO("%S", combined)\!\! \] |  No Syntax Error  |  No Syntax Error |  ✔  |
| AHOY() \[ SCROLL name \= "Smith"\!\! SCROLL full \= get\_title() & " " & name\!\! ECHO("%S", full)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ SCROLL matrix{2}{2} \= \[\["A", "B"\], \["C", "D"\]\]\!\! SCROLL diagonal \= matrix{0}{0} & "-" & matrix{1}{1}\!\! SCROLL anti \= matrix{0}{1} & "-" & matrix{1}{0}\!\! SCROLL both \= diagonal & " and " & anti\!\! ECHO("%S", both)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     SCROLL word \= "SeaStack"\!\!     SCROLL first \= word{0} & word{1} & word{2}\!\!     SCROLL last \= word{5} & word{6} & word{7}\!\!     SCROLL combined \= first & "-" & last\!\!     ECHO("%S", combined)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     SCROLL parts{4} \= \["The", "quick", "brown", "fox"\]\!\!     SCROLL sentence \= parts{0} & " " & parts{1} & " " & parts{2} & " " & parts{3} & "."\!\!     ECHO("%S", sentence)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     SCROLL result \= "Hello" & 123\!\!      ECHO("Invalid")\!\! \] | With Syntax Error  |  Unexpected token: 'COIN-lit' 'SCROLL result \= "Hello" & 123\!\!' Expected: 'SCROLL-lit, id, ('  |  ✔ |
| AHOY() \[     SCROLL result \= "Hello" & 123\!\!      ECHO("Invalid")\!\! \] | With Syntax Error  |  Unexpected token: 'COIN-lit' 'SCROLL result \= "Hello" & 123\!\!' Expected: 'SCROLL-lit, id, ('  |  ✔  |
| **Input Statements** |  |  |  |
| AHOY() \[     COIN num\!\!     ASK("%C", @num)\!\! \]  |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     COIN score1, score2\!\!     ASK("%C%C", @score1, @score2)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ COIN score1, score2\!\! DIME gwa\!\! ASK("%C%C%D%P", @score1, @score2, @gwa)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ COIN count\!\! DIME gwa\!\! ASK("%D%C", @count, @gwa)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ COIN a, b\!\! ASK("%C", @a, @b)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ SCROLL first, middle, last\!\! ASK("%S%S%S", @first, @middle, @last)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ COIN score, count\!\! ASK("%C%C", @score, @count)\!\! \] |  No Syntax Error |  No Syntax Error  |  ✔  |
| AHOY() \[     DIME gwa\!\!     ASK("%D", @@gwa)\!\! \] |  With Syntax Error  |  Invalid character '@' Expected any: 'lowercase letter'  |  ✔  |
| AHOY() \[     DIME gwa, COIN score\!\!     ASK("%D%C", @gwa, @score)\!\! \] | With Syntax Error  |  Misplaced Token: 'COIN' 'DIME gwa, COIN score\!\!' Expected: 'id' |  ✔  |
| AHOY() \[     COIN age\!\!     ASK("%C", @age)     ECHO("Age: %C\\n", age)\!\! \] | With Syntax Error  |  Misplaced Token: 'ECHO' 'ECHO("Age: %C\\n", age)\!\!' Expected: '\!\!' |  ✔  |
| AHOY() \[     COIN score, final, midterms\!\!     ASK("%C%C%C", @score, @final, @midterms)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
|  AHOY() \[     COIN num\!\!     ASK("%C, %C" @num)\!\! \]  | With Syntax Error  | Unexpected token: '\!\!' 'COIN num\!\!' Expected: '=, ,, {' |  ✔  |
| **Output Statements** |  |  |  |
| AHOY() \[     COIN score \= 100\!\!     ECHO("Your score is displayed here: ", score)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     COIN score \= 95\!\!     ECHO("Your score: %C")\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     PARCH initial \= 'B'\!\!     PARCH grade \= 'A'\!\!     ECHO("Student Initial: %P", initial)\!\!     ECHO("Final Grade: %P", 'A')\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     SCROLL greeting \= "Hi"\!\!     ECHO("Hello") \] | With Syntax Error  | Missplaced Token '\]' '\]' Expected any: '\!\!'  |  ✔ |
| AHOY() \[     COIN score \= 50\!\!     ECHO("Score: %C", score)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     SCROLL msg \= "SeaStack"\!\!     ECHO "Hello"\!\!     ASK ("HI")\!\! \] | With Syntax Error  | Misplaced Token: 'SCROLL-lit' 'ECHO "Hello"\!\!' Expected: '('  |  ✔ |
| **Assignment Statements** |  |  |  |
| AHOY() \[   PARCH grade\!\!   grade \= 'A'\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[   COIN x, y, sum\!\!   x \= 10\!\!   y \= 20\!\!   sum \= x \+ y\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| MAST student \[     SCROLL name\!\! \]\!\! AHOY() \[     SCROLL name\!\!     MAST student student1 \= \["Luffy"\]\!\!     name \= student1$name\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     100 \= 200\!\!     ECHO("Invalid\\n")\!\! \] | With Syntax Error  | Unexpected token: 'COIN-lit' '100 \= 200\!\!' Expected: 'COIN, DIME, PARCH, SCROLL, BOOL, MAST, id, ASK, ECHO, LOOK, CHART, HOIST, HEAVE, HAUL, \+\#, \-\#' |  ✔ |
| AHOY() \[     DIME wallet, item\_price\!\!     COIN quantity\!\!     BOOL afford\!\!         wallet \= 1000.00\!\!     item\_price \= 299.50\!\!     quantity \= 3\!\!          wallet \-= item\_price \* quantity\!\!     afford \= wallet \> 0.00\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| **Conditional Statements** |  |  |  |
| AHOY() \[     BOOL system\_online \= AYE\!\!     LOOK (system\_online \== AYE) \[         ECHO("All systems GO\!\!")\!\!     \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     DROPLOOK (AYE) \[         ECHO("Error: Missing LOOK")\!\!     \] \] | With Syntax Error  | Unexpected token: 'DROPLOOK' 'DROPLOOK (AYE) \[' Expected: 'COIN, DIME, PARCH, SCROLL, BOOL, MAST, id, ASK, ECHO, LOOK, CHART, HOIST, HEAVE, HAUL, \+\#, \-\#'  |  ✔  |
| AHOY() \[     COIN current\_followers \= 990000\!\!          LOOK (current\_followers \>= 1000000\) \[         ECHO("1 Million reached\!\!")\!\!     \] DROPLOOK (current\_followers \>= 900000\) \[         ECHO("Almost at 1 Million\!\!")\!\!     \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     BOOL goal\_reached \= AYE\!\!     LOOK (goal\_reached \== AYE) \[         ECHO("Milestone achieved\! YAY\!")\!\!     \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     LOOK (AYE) \[         LAND\!\!      \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     LOOK (AYE) \[ ECHO("OK")\!\! \]     DROP (NAY) \[ ECHO("Error")\!\! \] \] | With Syntax Error  | Misplaced Token: '(' 'DROP (NAY) \[ ECHO("Error")\!\! \]' Expected: '\['  |  ✔  |
| AHOY() \[     COIN score \= 85\!\!     LOOK (score \>= 90\) \[         ECHO("Grade: A")\!\!     \] DROPLOOK (score \>= 80\) \[         ECHO("Grade: B")\!\!     \] DROPLOOK (score \>= 70\) \[         ECHO("Grade: C")\!\!     \] DROP \[         ECHO("Grade: F")\!\!     \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     LOOK () \[         ECHO("Empty condition\\n")\!\!     \] \] | With Syntax Error  | Unexpected token: ')' 'LOOK () \[' Expected: '-, id, (, COIN-lit, DIME-lit, PARCH-lit, SCROLL-lit, AYE, NAY, \!, \!\#'  |  ✔  |
| AHOY() \[     COIN hp\!\! BOOL poisoned, cure\!\!     hp \= 15\!\! poisoned \= AYE\!\! cure \= NAY\!\!     LOOK ((hp \< 20 || poisoned) && \!cure) \[         ECHO("Danger: Critical Status\!\!")\!\!     \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| **Chart Statements** |  |  |  |
| AHOY() \[     COIN grade\_score \= 5\!\!     CHART (grade\_score) \[     COURSE 5:         ECHO("Excellent\!")\!\!         LAND\!\!     COURSE 4:         ECHO("Good\!")\!\!         LAND\!\!     ADRIFT:         ECHO("Unknown Grade")\!\!         LAND\!\!    \] \] | No Syntax Error | No Syntax Error |  ✔ |
| CHART (x) \[     ADRIFT:         ECHO("Lost at sea")\!\!         LAND\!\!     COURSE (x \> 10):          ECHO("High Velocity")\!\! \] | With Syntax Error | Invalid character ')' Expected any: '), ,, \[, \], operator, whitespace' | ✔ |
| AHOY() \[     COIN menu \= 1\!\!     CHART (menu) \[         COURSE 1:             ECHO("File Menu")\!\!             LAND\!\!         COURSE 2:             ECHO("Edit Menu")\!\!             LAND\!\!         COURSE 3:             ECHO("View Menu")\!\!             LAND\!\!         ADRIFT:             ECHO("Exit")\!\!             LAND\!\!     \] \] |  No Syntax Error |  No Syntax Error |  ✔ |
| AHOY() \[     CHART (menu) \[         ADRIFT:             ECHO("No COURSE body")\!\!             LAND\!\!         ADRIFT:             ECHO("Edit Menu")     \] \] | With Syntax Error | Unexpected token: 'ADRIFT' 'ADRIFT:' Expected: 'COURSE' | ✔ |
| CHART (y) \[     ADRIFT:         ECHO("This is in the wrong spot\!\!")\!\!         LAND\!\!     COURSE 1:         ECHO("Valid course")\!\!         LAND\!\! \] | With Syntax Error | Unexpected Beginning Token: 'CHART' 'CHART (y) \[' Expected: 'COIN, DIME, PARCH, SCROLL, BOOL, ABYSS, LOCKE, MAST, AHOY' | ✔ |
| AHOY()\[ COIN signal\_level \= 1\!\! CHART (signal\_level) \[     COURSE 1:         ECHO("Low Signal Detected")\!\!         LAND\!\!     COURSE 2:         ECHO("Medium Signal Detected")\!\!         LAND\!\!     ADRIFT:         ECHO("No Signal Found")\!\!         LAND\!\!   \] \] | No Syntax Error | No Syntax Error | ✔ |
| AHOY() \[     COIN result \= 0\!\!      CHART (operation) \[         COURSE 1:             result \= num1 \+ num2\!\!             ECHO("Sum: %C", result)\!\!             LAND\!\!         COURSE 2:             result \= num1 \- num2\!\!             ECHO("Difference: %C", result)\!\!             LAND\!\!         COURSE 3:             result \= num1 \* num2\!\!             ECHO("Product: %C", result)\!\!             LAND\!\!         ADRIFT:             ECHO("Invalid operation\!")\!\!             LAND\!\!     \] \] |  No Syntax Error |  No Syntax Error |  ✔ |
| AHOY() \[     COIN rank\!\!     rank \= 2\!\!     CHART (rank) \[         COURSE 1:             ECHO("You are the Captain\!\!")\!\!         LAND\!\!         COURSE 2:             ECHO("You are the First Mate\!\!")\!\!         LAND\!\!         ADRIFT:             ECHO("You are a Deckhand\!\!")\!\!         LAND\!\!     \] \] | No Syntax Error | No Syntax Error | ✔ |
| AHOY() \[     COIN level\!\!     level \= 2\!\!     CHART (level) \[         COURSE 1:             ECHO("Primary Building\!\!")\!\!         LAND\!\!         COURSE 2:             ECHO("Secondary Building\!\!")\!\!         LAND\!\!         ADRIFT:             ECHO("Admin Building\!\!")\!\!         LAND\!\!     \] \] | No Syntax Error | No Syntax Error | ✔ |
| AHOY() \[     COIN target\!\!     COIN input\!\!     target \= 10\!\!     input \= 10\!\!     CHART (input) \[         COURSE target:             ECHO("Target Hit\!\!")\!\!         LAND\!\!     \] | With Syntax Error | Invalid character 'target' Expected: '\!, $, %, &, (, ), \*, \+, ,, \-, /, \<, \=, \>, \], ^, whitespace, {, |, }' | ✔ |
| AHOY() \[ COIN floor\!\! floor \= 1\!\! CHART floor \[ COURSE 1: ECHO("Lobby\!\!")\!\! LAND\!\! \]  \] |  With Syntax Error |  Misplaced Token: 'id' 'CHART floor \[' Expected: '(' | ✔ |
| AHOY() \[ COIN choice\!\! choice \= 1\!\! CHART (choice) \[ COURSE 1: ECHO("Choice 1\!\!")\!\! LAND\!\! ECHO("Error\!\!")\!\! \] \] | With Syntax Error | Unexpected token: 'ECHO' 'ECHO("Error\!\!")\!\!' Expected: 'COURSE, ADRIFT, \]' | ✔ |
| AHOY() \[ CHART () \[ COURSE 1: ECHO("Invalid\\n")\!\! LAND\!\! \] \] | With Syntax Error |  Unexpected token: ')' 'CHART () \[' Expected: 'id, COIN-lit, PARCH-lit, SCROLL-lit' | ✔ |
| AHOY() \[ COIN choice \= 1\!\! CHART (choice) \[ ADRIFT: ECHO("Default\\n")\!\! LAND\!\! \] \] | With Syntax Error | Unexpected token: 'ADRIFT' 'ADRIFT:' Expected: 'COURSE' | ✔ |
| AHOY() \[ COIN menu \= 2\!\! CHART (menu) \[ COURSE 1 ECHO("Missing colon\\n")\!\! LAND\!\! \] \] | With Syntax Error | Misplaced Token: 'ECHO' 'ECHO("Missing colon\\n")\!\!' Expected: ':' | ✔ |
| **Looping Statements** |  |  |  |
|  AHOY() \[ HOIST (COIN i \= 0\!\! i \< 10\!\! \+\#i) \[ ECHO("Count: %C\\n", i)\!\! \] \]  |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ HOIST (COIN x \= 10\!\! x \> 0\!\! \-\#x) \[ ECHO("Countdown: %C\\n", x)\!\! \]  |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ COIN numbers{5} \= \[10, 20, 30, 40, 50\]\!\! HOIST (COIN i \= 0\!\! i \< 5\!\! \+\#i) \[ ECHO("Element %C: %C\\n", i, numbers{i})\!\! \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ HOIST (COIN i \= 0\!\! i \< 10\!\! \+\#i) \[ ECHO("Count: %C\\n", i)\!\! \] \] |  No Syntax Error |  No Syntax Error |     ✔  |
| AHOY() \[     HOIST (COIN i \= 0\!\! i \< 5\!\! \+\#i) \[         ECHO("%C", i)\!\!     \]     ECHO("%C", )\!\!  \]  | With Syntax Error | Unexpected token: 'id' 'HOIST (COIN i \= 0\!\! i \< 5\!\! \+\#i) \[' Expected: 'COIN-lit, DIME-lit, \-'  |          ✔ |
| AHOY() \[ COIN choice \= 0\!\! HEAVE (choice \!= 3\) \[ ECHO("Menu:\\n")\!\! ECHO("1. Option 1\\n")\!\! ECHO("2. Option 2\\n")\!\! ECHO("3. Exit\\n")\!\! ECHO("Enter choice: ")\!\! ASK("%C", @choice)\!\! \] \] |  No Syntax Error |     No Syntax Error |  ✔  |
| AHOY() \[ COIN fuel\!\! fuel \= 3\!\! HEAVE (fuel \> 0\) \[ ECHO("Sailing... Fuel left: %C\\n", fuel)\!\! fuel \-= 1\!\! LOOK (fuel \== 0\) \[ ECHO("Empty tank\! Anchoring now.\\n")\!\! \] \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ HOIST (COIN i \= 0\!\! i \< 5\!\! \+\#i) \[ ECHO("Count: %C", i)\!\! \] \] |  No Syntax Error |  No Syntax Error |      ✔  |
| AHOY() \[ BOOL is\_waiting\!\! is\_waiting \= AYE\!\! HEAVE (is\_waiting \== AYE) \[ \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ COIN target\!\! target \= 5\!\! HOIST (COIN i \= 1\!\! i \<= target\!\! \+\#i) \[ ECHO("Day: %C\\n", i)\!\! \] \] | No Syntax Error | No Syntax Error |      ✔  |
| **Jump Statements** |  |  |  |
| AHOY() \[ COIN target \= 50\!\! BOOL found \= NAY\!\! HOIST (COIN i \= 0\!\! i \< 100\!\! \+\#i) \[ LOOK (i \== target) \[ ECHO("Found target: %C\\n", i)\!\! found \= AYE\!\! SAIL\!\! \] ECHO("Checking: %C\\n", i)\!\! \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ HOIST (COIN i \= 0\!\! i \< 5\!\! \+\#i) \[ LOOK (i \== 2\) \[ ECHO("Skipping")\!\! SAIL\!\! \] \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ COIN treasure\_pos\!\! treasure\_pos \= 3\!\! HOIST (COIN i \= 1\!\! i \<= 10\!\! \+\#i) \[ LOOK (i \== treasure\_pos) \[ ECHO("Treasure found at %C\!\!", i)\!\! LAND\!\! \] \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[ COIN target\!\! target \= 7\!\! HOIST (COIN i \= 1\!\! i \<= 10\!\! \+\#i) \[ LOOK (i \== target) \[ ECHO("Target Found: %C\\n", i)\!\! LAND\!\! \] \] \] |  No Syntax Error |  No Syntax Error |      ✔  |
| AHOY() \[ COIN x\!\! x \= 0\!\! HEAVE (AYE) \[ x \+= 1\!\! LOOK (x \== 5\) \[ ECHO("Found five\!\!")\!\! LAND\!\! \] \] \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     COIN option \= 9\!\!     CHART (option) \[         COURSE 1:             ECHO("One\\n")\!\!             LAND\!\!         ADRIFT:             ECHO("Default\\n")\!\!             SAIL\!\!             LAND\!\!     \] \] | With Syntax Error | Unexpected token: 'SAIL' 'SAIL\!\!' Expected: 'id, ASK, ECHO, LOOK, CHART, HOIST, HEAVE, HAUL, \+\#, \-\#, LAND' |  ✔ |
| **AHOY Function** |  |  |  |
| MAST person \[ SCROLL name\!\! COIN age\!\! DIME salary\!\! \]\!\! AHOY() \[ MAST person emp \= \["John Doe", 30, 50000.50\]\!\! emp$salary \*= 1.10\!\! ECHO("Employee: %S, New Salary: %D\\n", emp$name, emp$salary)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| AHOY() \[     COIN age \= 0, score \= 0\!\!     BOOL has\_permit \= NAY\!\!     ECHO("Enter age: ")\!\!     ASK("%C", @age)\!\!     ECHO("Enter score: ")\!\!     ASK("%C", @score)\!\!     ECHO("Has permit? (AYE/NAY): ")\!\!     ASK("%B", @has\_permit)\!\!     LOOK ((age \>= 18\) && ((score \>= 75\) || (has\_permit))) \[         ECHO("Eligible\\n")\!\!     \] DROPLOOK ((age \>= 16\) && (score \>= 85)) \[         ECHO("Conditionally eligible\\n")\!\!     \] DROP \[         ECHO("Not eligible\\n")\!\!     \] \] |  No Syntax Error |  No Syntax Error  |  ✔    |
| AHOY() \[     COIN x \= 10\!\!     ECHO("X: %C\\n", x)\!\! \] | No Syntax Error | No Syntax Error |   ✔  |
| AHOY() \[     COIN x \= 10\!\!          COIN helper() \[         COIN y \= 20\!\!         BACK y\!\!     \]          ECHO("%C\\n", x)\!\! \]   |  No Syntax Error |  No Syntax Error |  ✔  |
| **Returning Function** |  |  |  |
| AHOY() \[     COIN add\_one(COIN n) \[         COIN x \= n \+ 1\!\!          BACK x\!\!     \]     COIN result \= 0\!\!     result \= add\_one(5)\!\! \] | With Syntax Error | Unexpected token: '(' 'COIN add\_one(COIN n) \[' Expected: '=, ,, \!\!, {' | ✔ |
| BOOL is\_passed(COIN score) \[     BOOL AYE\!\!     status \= score \> 74\!\!     BACK status\!\! \] | With Syntax Error | Misplaced Token: 'AYE' 'BOOL AYE\!\!' Expected: 'id' | ✔ |
| BOOL is\_passed(COIN score) \[     BOOL status\!\!                status \= score \> 74\!\!        BACK status\!\!            \] AHOY() \[     COIN my\_score\!\!     my\_score \= 85\!\!     ECHO("Passed: %B", is\_passed(my\_score))\!\! \] | No Syntax Error | No Syntax Error | ✔ |
| COIN check\_fuel(COIN liters) \[     ECHO("fuel levels: %B, low")\!\!     BOOL low\!\!     low \= liters \< 10\!\!     BACK low\!\! \] | With Syntax Error | Unexpected token: 'BOOL' 'BOOL low\!\!' Expected: 'id, ASK, ECHO, LOOK, CHART, HOIST, HEAVE, HAUL, \+\#, \-\#, BACK, \], LAND, SAIL' | ✔ |
| add() \[   COIN sum \= a \+ b\!\!   BACK sum\!\! \] | With Syntax Error | Unexpected Beginning Token: 'id' 'add() \[' Expected: 'COIN, DIME, PARCH, SCROLL, BOOL, ABYSS, LOCKE, MAST, AHOY' | ✔ |
| COIN add(COIN a COIN b) \[ \] | With Syntax Error |  Unexpected token: 'COIN' 'COIN add(COIN a COIN b) \[' Expected: ',, )' | ✔ |
| ABYSS addtwo(COIN a, COIN b) \[   BACK a \+ b\!\! \]  | With Syntax Error |  Unexpected token: 'BACK' 'BACK a \+ b\!\!' Expected: 'id, ASK, ECHO, LOOK, CHART, HOIST, HEAVE, HAUL, \+\#, \-\#' | ✔ |
| COIN add(COIN a COIN b) \[     COIN sum \= a \+ b\!\!     BACK sum\!\! \] | With Syntax Error | Unexpected token: 'COIN' 'COIN add(COIN a COIN b) \[' Expected: ',, )' | ✔ |
| COIN get\_ten() \[     COIN value\!\!     value \= 10\!\!     BACK value\!\! AHOY() \[     COIN local\_sum\!\!     local\_sum \= get\_ten()\!\!     ECHO("The sum is: %C", local\_sum)\!\! \] | With Syntax Error | Misplaced Token: 'AHOY' 'AHOY() \[' Expected: '\]' | ✔ |
| COIN get\_ten() \[     COIN value \= 10\!\!     BACK value\!\! \] AHOY() \[     COIN local\_sum\!\!     local\_sum \= get\_ten()\!\!     ECHO("The sum is: %C", local\_sum)\!\! \] | No Syntax Error | No Syntax Error | ✔ |
| COIN add(COIN a, COIN b) \[     COIN sum \= a \+ b\!\!     BACK sum\!\! \] AHOY() \[   COIN a, b\!\!   add(5,6)\!\!   ECHO("The sum is: %C", sum)\!\! \] | With Syntax Error | Unexpected token: 'BACK' 'BACK sum\!\!' Expected: 'COIN, DIME, PARCH, SCROLL, BOOL, MAST, id, ASK, ECHO, LOOK, CHART, HOIST, HEAVE, HAUL, \+\#, \-\#' | ✔ |
| PARCH get\_first\_char(SCROLL text) \[     PARCH first \= 'X'\!\!     BACK first\!\! \] AHOY() \[     COIN local\_sum\!\!     local\_sum \= get\_ten()\!\!     ECHO("The sum is: %C", local\_sum)\!\! \] | With Syntax Error | Unexpected token: 'BACK' 'BACK first\!\!' Expected: 'COIN, DIME, PARCH, SCROLL, BOOL, MAST, id, ASK, ECHO, LOOK, CHART, HOIST, HEAVE, HAUL, \+\#, \-\#' | ✔ |
| COIN add(COIN a, COIN b) \[     COIN sum\!\!     sum \= a \+ b\!\!     BACK sum\!\! \] AHOY() \[   COIN a, b\!\!   add(5,6)\!\!   ECHO("The sum is: %C", sum)\!\! \] | No Syntax Error | No Syntax Error | ✔ |
| **Non- returning Function** |  |  |  |
| AHOY() \[     ABYSS display \[         ECHO("SeaStack")\!\!     \] \]  | With Syntax Error | Unexpected token: 'ABYSS' 'ABYSS display \[' Expected: 'COIN, DIME, PARCH, SCROLL, BOOL, MAST, id, ASK, ECHO, LOOK, CHART, HOIST, HEAVE, HAUL, \+\#, \-\#' | ✔ |
| AHOY() \[     ABYSS result() \[     \] \]  | With Syntax Error | Unexpected token: 'ABYSS' 'ABYSS result() \[' Expected: 'COIN, DIME, PARCH, SCROLL, BOOL, MAST, id, ASK, ECHO, LOOK, CHART, HOIST, HEAVE, HAUL, \+\#, \-\#' | ✔ |
| ABYSS display() \[ ECHO("SeaStack")\!\! \] AHOY() \[ display()\!\! \] | No Syntax Error | No Syntax Error |     ✔  |
| ABYSS add\_numbers(COIN a, COIN b) \[ COIN sum\!\! sum \= a \+ b\!\! ECHO("The sum is: %C", sum)\!\! BACK\!\! \] AHOY() \[ COIN x \= 5\!\! add\_numbers(x, 10)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| **Function Call** |  |  |  |
| AHOY() \[     COIN result\!\!     SCROLL ship\!\!     log(get\_name())\!\! \] | No Syntax Error | No Syntax Error |     ✔ |
| ABYSS log(SCROLL message) \[     ECHO("LOG: %S", message)\!\! \] AHOY() \[     COIN result\!\!     SCROLL ship\!\!     log("Voyage Started")\!\! \] |  No Syntax Error |  No Syntax Error |     ✔  |
| COIN add(COIN a, COIN b) \[     COIN sum\!\!     sum \= a \+ b\!\!     BACK sum\!\! \] AHOY() \[     COIN result\!\!     SCROLL ship\!\!     result \= add(10, 20)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| COIN add(COIN a, COIN b) \[     COIN sum\!\!     sum \= a \+ b\!\!     BACK sum\!\! \] AHOY() \[     COIN result\!\!     SCROLL ship\!\!     result \= add(10, 20)\!\! \] |  No Syntax Error |  No Syntax Error |  ✔  |
| COIN add(COIN a, COIN b) \[     COIN sum\!\!     sum \= a \+ b\!\!     BACK sum\!\! \] AHOY() \[     COIN result\!\!     SCROLL ship\!\!          result \= add(10, 20\) \] | With Syntax Error  | Misplaced Token: '\]' '\]' Expected: '\!\!' |  ✔  |

**Semantic Test Scripts**  
![][image108]

![][image109]

**![][image110]**  
**![][image111]**  
**![][image112]**  
**![][image113]**  
**![][image114]**

**Runtime Test Scripts**  
**![][image115]**

**![][image116]**

**![][image117]**

**![][image118]**

**![][image119]**

**![][image120]**

**![][image121]**

**![][image122]**

**![][image123]**

**![][image124]**

**![][image125]**

**![][image126]**