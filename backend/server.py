import sys
import os
import re

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
        
        # Format tokens for UI
        formatted_tokens = []
        for t in tokens:
            t_type = getattr(t, 'type', str(t))
            t_value = getattr(t, 'value', '')
            formatted_tokens.append({"token": t_type, "lexeme": t_value})
        
        response_data['tokens'] = formatted_tokens

        # Process Lexical Errors
        if lex_errors:
            for e in lex_errors:
                line = getattr(e, 'line', '?')
                col = getattr(e, 'col', getattr(e, 'column', '?')) 
                msg = getattr(e, 'error_msg', str(e))
                val = getattr(e, 'value', '')

                # --- STRUCTURED ERROR PARSING ---
                # Default fallback
                found_str = msg
                expected_list = ["Valid Token"]

                # 1. Handle SCROLL (String) Literals
                if "SCROLL literal" in msg:
                    found_str = "Invalid SCROLL literal"
                    expected_list = ['"'] # Double quote
                
                # 2. Handle PARCH (Char) Literals
                elif "PARCH literal" in msg:
                    found_str = "Invalid PARCH literal"
                    expected_list = ["'"] # Single quote

                # 3. Handle Invalid Characters
                elif "Invalid Character" in msg:
                    # If we have the value, show it
                    if val:
                        found_str = f"Invalid character '{val}'"
                    else:
                        found_str = "Invalid character"
                    expected_list = ["Valid Token"]

                # 4. Handle Identifier Delimiters
                elif "Invalid Indentifier" in msg or "Invalid Identifier" in msg:
                    found_str = "Invalid Identifier"
                    expected_list = ["Delimiter (Space, Operator, etc.)"]

                response_data['lexical_errors'].append({
                    "line": line,
                    "col": col,
                    "found": found_str,
                    "expected": expected_list,
                    "message": msg # Keep original for debugging/fallback
                })
        
        if not lex_errors:
            response_data['success'] = True

    except Exception as e:
        response_data['lexical_errors'].append({
            "line": "-", "col": "-", 
            "found": "CRASH", "expected": [],
            "message": f"Lexer Crashed: {str(e)}"
        })
        return jsonify(response_data)

    # =================================
    #    --- SYNTAX ANALYSIS ---
    # =================================
    if not response_data['lexical_errors']:
        try:
            # Pass the tokens list from the lexer to the parser
            parser = Parser(tokens)
            
            # Now returns a list of raw error DICTIONARIES
            syntax_errors = parser.parse() 
            
            if syntax_errors:
                response_data['syntax_errors'].extend(syntax_errors)
                response_data['success'] = False
            else:
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