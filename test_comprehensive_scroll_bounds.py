import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from backend.lexical.lexer import Lexer
from backend.syntax.syn_parser import Parser
from backend.semantic.ast_parser import ASTParser
from backend.semantic.semantic_analyzer import SemanticAnalyzer

def analyze(code):
    lexer = Lexer(code)
    tokens, _ = lexer.tokenize()
    parser = Parser(tokens)
    parser.parse()
    ast_parser = ASTParser(tokens, code)
    ast = ast_parser.build()
    analyzer = SemanticAnalyzer(ast, code)
    errors = analyzer.analyze()
    return errors

test_cases = [
    # (name, code, should_have_error, error_contains)
    ("Valid index 0",
     'SCROLL x = "hi"!!\nAHOY() [ SCROLL y = x{0}!! ]',
     False,
     None),

    ("Valid index 1 (last)",
     'SCROLL x = "hi"!!\nAHOY() [ SCROLL y = x{1}!! ]',
     False,
     None),

    ("Out of bounds index 2",
     'SCROLL x = "hi"!!\nAHOY() [ SCROLL y = x{2}!! ]',
     True,
     "out of bounds"),

    ("Out of bounds index 3 (user example)",
     'SCROLL x = "hi"!!\nAHOY() [ SCROLL y = x{3}!! ]',
     True,
     "out of bounds"),

    ("Negative index",
     'SCROLL x = "hello"!!\nAHOY() [ SCROLL y = x{-1}!! ]',
     True,
     "out of bounds"),

    ("Single char - valid",
     'SCROLL x = "a"!!\nAHOY() [ SCROLL y = x{0}!! ]',
     False,
     None),

    ("Single char - out of bounds",
     'SCROLL x = "a"!!\nAHOY() [ SCROLL y = x{1}!! ]',
     True,
     "out of bounds"),

    ("Longer string - valid",
     'SCROLL x = "hello"!!\nAHOY() [ SCROLL y = x{4}!! ]',
     False,
     None),

    ("Longer string - out of bounds",
     'SCROLL x = "hello"!!\nAHOY() [ SCROLL y = x{5}!! ]',
     True,
     "out of bounds"),
]

print("="*70)
print("SCROLL BOUNDS CHECKING - COMPREHENSIVE TEST SUITE")
print("="*70)

passed = 0
failed = 0

for test_name, code, should_error, error_str in test_cases:
    errors = analyze(code)
    has_error = len(errors) > 0
    has_expected_error = any(error_str.lower() in err.get('message', '').lower() for err in errors) if error_str else not has_error

    test_passed = (should_error and has_expected_error) or (not should_error and not has_error)

    status = "✅ PASS" if test_passed else "❌ FAIL"
    print(f"\n{status}: {test_name}")

    if not test_passed:
        print(f"  Expected: {'error' if should_error else 'no error'}")
        print(f"  Got: {len(errors)} error(s)")
        if errors and error_str:
            for err in errors:
                print(f"    {err.get('message')}")
        failed += 1
    else:
        passed += 1

print(f"\n{'='*70}")
print(f"Results: {passed}/{passed+failed} tests passed")
print(f"{'='*70}")

success = failed == 0
if success:
    print("\n✅ All tests passed! SCROLL bounds checking works correctly!")
else:
    print(f"\n❌ {failed} test(s) failed")

sys.exit(0 if success else 1)
