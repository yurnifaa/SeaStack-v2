import sys
import os

# Add the parent directory to sys.path to allow imports from sibling folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS

# --- IMPORTS ---
try:
    from lexical.lexer import Lexer
    from syntax.syn_parser import Parser 
except ImportError as e:
    print(f"\n[ERROR] Import Failed! Details: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    data = request.json
    code_string = data.get('code', '')

    response_data = {
        "success": False,
        "tokens": [],
        "lexical_errors": [],
        "syntax_errors": []
    }

    # =================================
    #    --- LEXICAL ANALYSIS ---
    # =================================
    tokens = [] 
    try:
        lexer = Lexer(code_string)
        tokens, lex_errors = lexer.tokenize()
        
        # 1. Format Valid Tokens for UI Table
        formatted_tokens = []
        for t in tokens:
            t_type = getattr(t, 'type', str(t))
            t_value = getattr(t, 'value', '')
            formatted_tokens.append({"token": t_type, "lexeme": t_value})
        
        response_data['tokens'] = formatted_tokens

        # 2. Process Lexical Errors (With Crash Prevention)
        # This loop ensures that even if a 'Token' object sneaks in, 
        # it gets converted to a Dictionary so JSON doesn't crash.
        clean_lex_errors = []
        for err in lex_errors:
            if isinstance(err, dict):
                clean_lex_errors.append(err)
            else:
                # Fallback: Convert stray Token objects to Dicts
                clean_lex_errors.append({
                    "line": getattr(err, 'line', '?'),
                    "col": getattr(err, 'col', '?'),
                    "found": f"Invalid character '{getattr(err, 'value', '?')}'",
                    "expected": ["Valid Token"],
                    "message": getattr(err, 'error_msg', str(err))
                })
        
        response_data['lexical_errors'] = clean_lex_errors
        
        # Mark success if no errors found
        if not clean_lex_errors:
            response_data['success'] = True

    except Exception as e:
        # Catch generic crashes in Lexer
        response_data['lexical_errors'].append({
            "line": "-", "col": "-", 
            "found": "CRASH", "expected": [],
            "message": f"Lexer Crashed: {str(e)}"
        })
        return jsonify(response_data)

    # =================================
    #    --- SYNTAX ANALYSIS ---
    # =================================
    # Only run Syntax Analysis if Lexical Analysis passed
    if not response_data['lexical_errors']:
        try:
            # Pass the tokens list from the lexer to the parser
            parser = Parser(tokens)
            
            # Now returns a list of raw error DICTIONARIES from ErrorHandler
            syntax_errors = parser.parse() 
            
            if syntax_errors:
                response_data['syntax_errors'].extend(syntax_errors)
                response_data['success'] = False
            else:
                # Success remains True from Lexical step
                pass

        except Exception as e:
            response_data['syntax_errors'].append({
                "line": "-", 
                "col": "-", 
                "found": "CRASH",
                "expected": [],
                "message": f"Parser Crashed: {str(e)}"
            })
            response_data['success'] = False
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)