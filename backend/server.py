# backend/server.py
from flask import Flask, request, jsonify
from flask_cors import CORS

# IMPORT YOUR EXISTING LEXER UNTOUCHED
from lexer import Lexer, Token 

app = Flask(__name__)
CORS(app) # Allow Next.js (Port 3000) to talk to Flask

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    data = request.json
    code_string = data.get('code', '')

    # --- LOGIC COPIED FROM YOUR ide_interface.py ---
    lexer = Lexer(code_string)
    tokens, errors = lexer.tokenize()
    
    ui_tokens = []
    for token in tokens:
        if token.type == 'newline':
            ui_tokens.append({"lexeme": "newline", "token": "newline"})
        elif token.type == 'space':
            ui_tokens.append({"lexeme": "space", "token": "space"})
        else:
            ui_tokens.append({"lexeme": token.value, "token": token.type})

    if errors:
        PREFIX_WIDTH = 16
        # Slight tweak: returning errors as a list is often easier for React to render than a giant string
        error_list = [f"Line {e.line}, Col {e.col} | {e.error_msg}: '{e.value}'" for e in errors]
        error_msg = "\n".join(error_list)
        log_msg = f"Lexical analysis completed with {len(errors)} error(s)."
        success = False
    else:
        error_msg = ""
        log_msg = f"Lexical analysis successful. {len(ui_tokens)} tokens found."
        success = True
    # -----------------------------------------------

    return jsonify({
        "success": success,
        "tokens": ui_tokens,
        "error": error_msg,
        "log": log_msg
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)