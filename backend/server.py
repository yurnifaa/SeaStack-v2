import sys
import os

# Ensure backend can find sibling folders
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
        "lexical_errors": [], # Changed to list for structured data
        "syntax_errors": []   # Changed to list for structured data
    }

    # --- LEXICAL ANALYSIS ---
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
                col = getattr(e, 'column', '?') # Ensure your Lexer error class has a .column attribute!
                msg = getattr(e, 'error_msg', str(e))
                
                response_data['lexical_errors'].append({
                    "line": line,
                    "col": col,
                    "message": msg
                })
        
        # Mark success if no lexical errors (though we might still run syntax)
        if not lex_errors:
            response_data['success'] = True

    except Exception as e:
        response_data['lexical_errors'].append({
            "line": "-", "col": "-", "message": f"Lexer Crashed: {str(e)}"
        })
        return jsonify(response_data)

    # --- SYNTAX ANALYSIS ---
    if not response_data['lexical_errors']:
        try:
            parser = Parser(tokens)
            syntax_result = parser.parse()
            
            if syntax_result and isinstance(syntax_result, list):
                for err in syntax_result:
                    # Handle if err is a dict or an object
                    if isinstance(err, dict):
                         response_data['syntax_errors'].append(err)
                    else:
                        # Fallback for object or string
                        response_data['syntax_errors'].append({
                            "line": getattr(err, 'line', '?'),
                            "col": getattr(err, 'col', '?'),
                            "message": getattr(err, 'message', str(err))
                        })
            elif syntax_result is None:
                pass 

        except Exception as e:
            response_data['syntax_errors'].append({
                "line": "-", "col": "-", "message": f"Parser Crashed: {str(e)}"
            })
            response_data['success'] = False
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)