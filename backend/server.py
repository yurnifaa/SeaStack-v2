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
               
                found_str = msg
                expected_list = ["Valid Token"] # Default fallback

                if "Expected" in msg:
                    parts = msg.split("Expected")
                    
                    # Error Description (Before 'Expected')
                    raw_found = parts[0].strip(" .:,")
                    if raw_found:
                        found_str = raw_found
                        # If specific value exists, append it for clarity (e.g. "Invalid character '!'")
                        if "Invalid Character" in found_str and val:
                             found_str = f"Invalid character '{val}'"
                    else:
                        found_str = "Invalid Token"

                    # PART 2: The "Expected" List (After 'Expected')
                    if len(parts) > 1:
                        raw_expected = parts[1].strip(" .:,")
                        if raw_expected:
                            # Pass the full string provided by the handler
                            expected_list = [raw_expected]
                
                # Fallback for messages without "Expected" keyword
                else:
                    if val:
                        found_str = f"{msg} '{val}, '"

                response_data['lexical_errors'].append({
                    "line": line,
                    "col": col,
                    "found": found_str,
                    "expected": expected_list,
                    "message": msg 
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