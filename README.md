# 🌊 SeaStack Compiler
A C-inspired programming language with an oceanic twist — built from scratch for automata theory and formal languages.

SeaStack is a high-level programming language designed to combine structured programming principles with a thematic and engaging syntax inspired by the Ocean Voyager theme. It takes its foundation from the C language, adapting familiar constructs such as functions, loops, conditionals, and data type. 

This built as part of an academic project in automata theory and formal languages, SeaStack includes its own lexer, parser, and GUI-based IDE.

## 📖 IDE Screenshots
### Light Mode
![Light Mode](frontend/public/GitHub_shots/Light_Mode2.png)

### Dark Mode
![Dark Mode](frontend/public/GitHub_shots/Dark_Mode2.png)

## Language Rules (to be added in the future)

## 📂 Project Structure
```plaintext
SEASTACK_PROJ/
├── backend/
│   ├── lexical/
│   │   ├── handlers/
│   │   ├── lexer_token.py
│   │   └── lexer.py
│   ├── syntax/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── First_Set.py
│   │   ├── Follow_Set.py
│   │   ├── Predict_Set.py
│   │   └── syn_parser.py
│   ├── README.md
│   └── server.py
├── frontend/
│   ├── .next/
│   ├── node_modules/
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── favicon.ico
│   │   │   ├── globals.css
│   │   │   ├── layout.js
│   │   │   └── page.js
│   │   └── components/
│   │       └── CodeEditor.js
│   ├── .gitignore
│   ├── eslint.config.mjs
│   ├── jsconfig.json
│   ├── next.config.mjs
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.mjs
│   └── README.md
├── node_modules/
├── package-lock.json
├── package.json
├── README.md
├── sample.sea
└── test_compiler.py
 ```

## How to Run
Install Dependencies:
```plaintext 
This project requires eel: 
pip install eel
```

Run the Application:
```plaintext 
Execute the main app.py file:
python app.py
```
This will start the local server and open the desktop application window.

## 👥 Contributors
- ALISWAG, K. V. J.
- ALTEZA, J. R. D.
- CAYACAP, F. A. S.
- DEL ROSARIO, J. M. A.
- MAGAAN, F. M. V.
- MULLENO, J. M. A.
