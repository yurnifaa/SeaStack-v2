# backend/server.py
from flask import Flask, request, jsonify
from flask_cors import CORS

from lexer import Lexer, Token
from parser.parser import Parser

app = Flask(__name__)
CORS(app) 

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    data = request.json
    code_string = data.get('code', '')

    # 1. LEXICAL ANALYSIS
    try:
        lexer = Lexer(code_string)
        tokens, errors = lexer.tokenize()
    except Exception as e:
        return jsonify({
            "success": False,
            "lexical_log": f"Critical Lexer Error: {str(e)}",
            "tokens": [],
            "syntax_log": []
        })
    
    ui_tokens = []
    for token in tokens:
        if token.type == 'newline':
            ui_tokens.append({"lexeme": "newline", "token": "newline"})
        elif token.type == 'space':
            ui_tokens.append({"lexeme": "space", "token": "space"})
        else:
            ui_tokens.append({"lexeme": token.value, "token": token.type})

    # Prepare Lexical Logs
    if errors:
        error_list = [f"Line {e.line}, Col {e.col} | {e.error_msg}: '{e.value}'" for e in errors]
        lexical_log = f"Lexical Errors Found:\n" + "\n".join(error_list)
        success = False
    else:
        lexical_log = f"Lexical analysis successful. {len(ui_tokens)} tokens found."
        success = True

    # 2. SYNTAX ANALYSIS
    syntax_logs = []
    if success:
        try:
            parser = Parser(tokens)
            result_logs = parser.parse()
            
            # --- SAFETY NET START ---
            # If parser returns None (the current bug), we force a log message
            if result_logs is None:
                syntax_logs = ["[WARNING]: Parser finished but returned no logs. (Did you forget 'return self.logs'?)"]
            else:
                syntax_logs = result_logs
            # --- SAFETY NET END ---

        except Exception as e:
            syntax_logs.append(f"[CRITICAL ERROR]: Parser crashed. {str(e)}")
            success = False

    return jsonify({
        "success": success,
        "tokens": ui_tokens,
        "lexical_log": lexical_log,
        "syntax_log": syntax_logs # This will now NEVER be null
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)