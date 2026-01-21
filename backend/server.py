import sys
import os

# Add the parent directory to sys.path to allow imports from sibling folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS

# --- IMPORTS ---
try:
    from backend.lexical.lexer import Lexer
    from backend.syntax.syn_parser import Parser 
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
        
        # Format Valid Tokens for UI Table
        formatted_tokens = []
        for t in tokens:
            t_type = getattr(t, 'type', str(t))
            t_value = getattr(t, 'value', '')
            formatted_tokens.append({"token": t_type, "lexeme": t_value})
        
        response_data['tokens'] = formatted_tokens

        # Process Lexical Errors (WITH SMART PARSING)
        clean_lex_errors = []
        for err in lex_errors:
            if isinstance(err, dict):
                clean_lex_errors.append(err)
            else:
                err_msg = getattr(err, 'error_msg', str(err))
                
                expected_list = getattr(err, 'expected', [])
                
                if not expected_list:
                    if "Expected" in err_msg:
                        try:
                            part_after = err_msg.split("Expected")[1]
                            part_after = part_after.lstrip(" :")
                            extracted_items = [item.strip() for item in part_after.split(',')]
                            expected_list = extracted_items
                        except:
                            expected_list = ["Valid Token"] # Fail safe
                    else:
                        expected_list = ["Valid Token"]

                clean_lex_errors.append({
                    "line": getattr(err, 'line', '?'),
                    "col": getattr(err, 'col', '?'),
                    "found": f"Invalid character '{getattr(err, 'value', '?')}'",
                    "expected": expected_list,  # Use our smart list
                    "message": err_msg
                })
        
        response_data['lexical_errors'] = clean_lex_errors
        
        if not clean_lex_errors:
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
            parser = Parser(tokens, code_string) 
            syntax_errors = parser.parse() 
            
            if syntax_errors:
                response_data['syntax_errors'].extend(syntax_errors)
                response_data['success'] = False
            else:
                pass 

        except Exception as e:
            response_data['syntax_errors'].append({
                "type": "Server Error",
                "line": "?", "col": "?", 
                "found": "CRASH", "expected": [],
                "message": f"Parser Crashed: {str(e)}"
            })
            response_data['success'] = False
    
    return jsonify(response_data)

    # =================================
    #    --- SYNTAX ANALYSIS ---
    # =================================
    # Only run Syntax Analysis if Lexical Analysis passed
    if not response_data['lexical_errors']:
        try:
            # FIX: Use 'code_string' here, not 'code'
            parser = Parser(tokens, code_string) 
            
            syntax_errors = parser.parse() 
            
            if syntax_errors:
                response_data['syntax_errors'].extend(syntax_errors)
                response_data['success'] = False
            else:
                pass # Success remains True

        except Exception as e:
            response_data['syntax_errors'].append({
                "type": "Server Error",
                "line": "?", 
                "col": "?", 
                "found": "CRASH",
                "expected": [],
                "message": f"Parser Crashed: {str(e)}"
            })
            response_data['success'] = False
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)