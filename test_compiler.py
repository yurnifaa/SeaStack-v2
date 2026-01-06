import sys
import os

# 1. Add the current directory (SEASTACK_PROJ) to Python's path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 2. Now we can import the modules safely
try:
    from backend.lexical.lexer import Lexer
    from backend.syntax.syn_parser import Parser

except ImportError as e:
    print("\nCRITICAL IMPORT ERROR:")
    print(f"Could not import backend modules. Details: {e}")
    print("Make sure you are running this script from the 'SEASTACK_PROJ' folder.")
    print(f"Current Path: {sys.path[0]}\n")
    sys.exit(1)

def run_test(filename):
    print(f"--- Compiling {filename} ---")
    
    # Read Source Code
    try:
        with open(filename, 'r') as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return

    # --- STEP 1: LEXER ---
    print("\n[Step 1] Running Lexer...")
    lexer = Lexer(source_code)
    # Tokenize returns (tokens, errors)
    tokens, errors = lexer.tokenize()

    if errors:
        print(f"Lexical Errors Found ({len(errors)}):")
        for err in errors:
            # Adjust this based on your Token class structure
            print(f"  Line {err.line}: {err.error_msg} -> {err.value}")
        print("Aborting Compilation.")
        return

    print(f"Lexer Success! {len(tokens)} tokens generated.")

    # DEBUG: Print the first 5 tokens to check their types
    print("--- FIRST 5 TOKENS ---")
    for t in tokens[:5]:
        print(f"Type: '{t.type}' | Value: '{t.value}'")
    print("----------------------")
    
    # --- STEP 2: PARSER ---
    print("\n[Step 2] Running Parser...")
    try:
        parser = Parser(tokens)
        parser.parse()
    except Exception as e:
        print(f"\nCompiler Crash during Parsing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Creates a dummy file if it doesn't exist for quick testing
    test_file = "sample.sea"
    if not os.path.exists(test_file):
        with open(test_file, "w") as f:
            f.write("AHOY() [ COIN x = 10!! ]")
            
    run_test(test_file)