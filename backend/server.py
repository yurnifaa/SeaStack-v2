import sys
import os

# 1. Setup path to find 'lexical' and 'parser' folders
# This gets the folder where server.py is located (the 'backend' folder)
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from flask import Flask, request, jsonify
from flask_cors import CORS

# 2. Corrected Imports based on your folder structure
# Folder: backend/lexical -> file: lexer.py -> class: Lexer
from lexical.lexer import Lexer
# Folder: backend/parser -> file: parser.py -> class: Parser
from parser.parser import Parser

app = Flask(__name__)
CORS(app) 

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    data = request.json
    code_string = data.get('code', '')

    # --- 1. LEXICAL ANALYSIS ---
    try:
        lexer = Lexer(code_string)
        # Assuming tokenize returns (tokens, errors)
        tokens, errors = lexer.tokenize()
    except Exception as e:
        return jsonify({
            "success": False,
            "lexical_log": f"Critical Lexer Error: {str(e)}",
            "tokens": [],
            "syntax_log": []
        })
    
    # Format tokens for UI
    ui_tokens = []
    for token in tokens:
        # Check if attributes exist, default to safety if missing
        t_type = getattr(token, 'type', 'unknown')
        t_value = getattr(token, 'value', '')
        
        if t_type == 'newline':
            ui_tokens.append({"lexeme": "newline", "token": "newline"})
        elif t_type == 'whitespace' or t_type == 'space': # Handle variations
            ui_tokens.append({"lexeme": "space", "token": "space"})
        else:
            ui_tokens.append({"lexeme": t_value, "token": t_type})

    # Prepare Lexical Logs
    if errors:
        error_list = [f"Line {e.line}: {e.error_msg} -> '{e.value}'" for e in errors]
        lexical_log = f"Lexical Errors Found:\n" + "\n".join(error_list)
        success = False
    else:
        lexical_log = f"Lexical analysis successful. {len(ui_tokens)} tokens found."
        success = True

    # --- 2. SYNTAX ANALYSIS ---
    syntax_logs = []
    
    # Only run parser if lexer succeeded
    if success:
        try:
            # We must pass the RAW tokens list to the parser, not the UI tokens
            parser = Parser(tokens)
            
            # CRITICAL: parser.parse() must RETURN logs, not just print them
            result_logs = parser.parse()
            
            if result_logs is None:
                # If parser.py prints instead of returns, catch it here
                syntax_logs = ["Parser finished (check terminal for details). Update parser.py to return strings."]
            else:
                syntax_logs = result_logs

        except Exception as e:
            syntax_logs.append(f"[CRITICAL PARSER ERROR]: {str(e)}")
            import traceback
            traceback.print_exc() # Print full error to backend terminal
            success = False

    return jsonify({
        "success": success,
        "tokens": ui_tokens,
        "lexical_log": lexical_log,
        "syntax_log": syntax_logs
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)