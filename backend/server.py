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
                
                response_data['lexical_errors'].append({
                    "line": line,
                    "col": col,
                    "message": msg
                })
        
        if not lex_errors:
            response_data['success'] = True

    except Exception as e:
        response_data['lexical_errors'].append({
            "line": "-", "col": "-", "message": f"Lexer Crashed: {str(e)}"
        })
        return jsonify(response_data)

    # =================================
    #    --- SYNTAX ANALYSIS ---
    # =================================
    if not response_data['lexical_errors']:
        try:
            # Pass the tokens list from the lexer to the parser
            parser = Parser(tokens)
            
            # Now returns a list of raw error DICTIONARIES, not strings
            syntax_errors = parser.parse() 
            
            if syntax_errors:
                response_data['syntax_errors'].extend(syntax_errors)
                response_data['success'] = False
            else:
                # If list is empty, it means success (no errors returned)
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
    # Run the server on port 5000
    app.run(debug=True, port=5000)