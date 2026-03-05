import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from backend.lexical.lexer import Lexer
from backend.syntax.syn_parser import Parser
from backend.semantic.ast_parser import ASTParser
from backend.semantic.semantic_analyzer import SemanticAnalyzer

def test_scroll_bounds():
    source_code = """SCROLL x = "hi"!!
AHOY() [
  SCROLL y = x{3}!!
  ECHO("Huh?")!!
]
"""

    print("Testing SCROLL bounds checking with quote stripping")
    print("="*70)
    print("Source:")
    print(source_code)
    print("="*70)
    print()

    # Lexer
    lexer = Lexer(source_code)
    tokens, lex_errors = lexer.tokenize()
    if lex_errors:
        print(f"❌ Lexical errors")
        return False

    # Parser
    parser = Parser(tokens)
    try:
        parser.parse()
    except Exception as e:
        print(f"❌ Parser error: {e}")
        return False

    # AST Parser
    try:
        ast_parser = ASTParser(tokens, source_code)
        ast = ast_parser.build()
    except Exception as e:
        print(f"❌ AST Parser error: {e}")
        return False

    # Semantic Analyzer
    analyzer = SemanticAnalyzer(ast, source_code)
    errors = analyzer.analyze()

    if errors:
        print(f"✅ SUCCESS! Bounds error caught:")
        found_bounds_error = False
        for err in errors:
            print(f"\n  Line {err.get('line')}, Col {err.get('col')}: {err.get('error_type')}")
            print(f"    {err.get('message')}")
            if "out of bounds" in err.get('message', '').lower():
                found_bounds_error = True

        if found_bounds_error:
            print("\n✅ Correct! Out of bounds error was detected!")
            return True
        else:
            print("\n⚠️  Error detected but not the bounds error")
            return False
    else:
        print(f"❌ FAILED: No errors detected!")
        print("   The bounds check should have caught index 3 in 'hi' (length 2)")
        return False

if __name__ == "__main__":
    success = test_scroll_bounds()
    sys.exit(0 if success else 1)
