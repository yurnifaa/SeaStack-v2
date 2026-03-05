import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from backend.lexical.lexer import Lexer
from backend.syntax.syn_parser import Parser
from backend.semantic.ast_parser import ASTParser
from backend.semantic.semantic_analyzer import SemanticAnalyzer

source_code = """SCROLL x = "hi"!!
AHOY() [
  SCROLL y = x{3}!!
  ECHO("Huh?")!!
]
"""

print("Debugging SCROLL bounds checking")
print("="*60)
print(source_code)
print("="*60)

# Lexer
lexer = Lexer(source_code)
tokens, lex_errors = lexer.tokenize()

# Parser
parser = Parser(tokens)
try:
    parser.parse()
except Exception as e:
    print(f"Parser error: {e}")
    sys.exit(1)

# AST Parser
try:
    ast_parser = ASTParser(tokens, source_code)
    ast = ast_parser.build()
except Exception as e:
    print(f"AST Parser error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("AST structure:")
print(f"Global decls: {ast.global_decls}")
for decl in ast.global_decls:
    print(f"  {type(decl).__name__}: {decl}")
    if hasattr(decl, 'name'):
        print(f"    name: {decl.name}")
    if hasattr(decl, 'init_value'):
        print(f"    init_value: {decl.init_value}")

# Semantic Analyzer
print("\nRunning semantic analysis...")
analyzer = SemanticAnalyzer(ast, source_code)

# Check the symbol table before analysis
print(f"\nSymbol table before analysis:")
print(analyzer.sym.dump())

# Run analysis
errors = analyzer.analyze()

# Check the symbol table after analysis
print(f"\nSymbol table after analysis:")
print(analyzer.sym.dump())

# Check specifically the 'x' symbol
print("\nLooking for 'x' symbol in global scope:")
x_sym = analyzer.sym.lookup_global_scope('x')
if x_sym:
    print(f"  Found: {x_sym}")
    print(f"  dtype: {x_sym.dtype}")
    print(f"  kind: {x_sym.kind}")
    print(f"  init_expr: {x_sym.init_expr}")
    if x_sym.init_expr:
        print(f"  init_expr type: {type(x_sym.init_expr).__name__}")
        print(f"  init_expr value: {x_sym.init_expr.value if hasattr(x_sym.init_expr, 'value') else 'N/A'}")
else:
    print("  Not found!")

print(f"\nSemantic errors: {len(errors)}")
if errors:
    for err in errors:
        print(f"  Line {err.get('line')}: {err.get('error_type')}")
        print(f"    {err.get('message')}")
else:
    print("  No errors found")
