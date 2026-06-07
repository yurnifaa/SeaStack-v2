# 🌊 SeaStack | Programming Language and Compiler
SeaStack is a high-level programming language designed to combine structured programming principles with a thematic and engaging syntax inspired by the ocean voyager theme. It takes its foundation from the C language, adapting familiar constructs such as functions, loops, conditionals, and structures while introducing an oceanic twist to make coding both intuitive and enjoyable.

The integration of the Ocean Voyager theme enhances the language by aligning programming commands with navigational and seafaring terms. This thematic consistency creates an immersive environment that not only strengthens recall of syntax but also sparks creativity in the programming experience.

SeaStack supports a wide range of constructs, including global and local declarations, expressions, statements, arrays, structures, and user-defined functions that enable programmers to implement both simple and complex logic. These features make SeaStack suitable for learning core programming concepts, developing simple yet structured algorithms, and introducing problem-solving skills more interactively.

Overall, the SeaStack programming language makes programming accessible and enjoyable by combining solid foundations with a creative oceanic theme. It encourages learners to see coding as a voyage of discovery, emphasizing clarity, engagement, and a fun learning experience.

### 🌕 IDE - Light Mode
![Light Mode](frontend/public/GitHub_shots/Light_Mode3.png)

### 🌑 IDE - Dark Mode
![Dark Mode](frontend/public/GitHub_shots/Dark_Mode3.png)

## Language Rules
To know and learn more about the language, linked below is a detailed description of all the rules, from general to specific, as well as its transitional diagram all the way to its context free grammar and sample programs. ^ _ ^
[Click here to view the Rules of this Language](SeaStack - Rules.pdf)

## 📂 Project Structure
```plaintext
SEASTACK_PROJ/
├── backend/
│ ├── codegen/
│ │ ├── code_generator.py
│ │ ├── ir_generator.py
│ │ ├── optimizer.py
│ │ └── ir_instructions.py
│ ├── lexical/
│ │ ├── handlers/
│ │ ├── lexer_token.py
│ │ ├── lexer_errors.py
│ │ └── lexer.py
│ ├── semantic/
│ │ ├── ast_nodes.py
│ │ ├── ast_parser.py
│ │ ├── sem_error_msg.py
│ │ ├── symbol_table.py
│ │ └── semantic_analyzer.py
│ ├── syntax/
│ │ ├── generate/
│ │ ├── syn_error_msg.py
│ │ ├── Predict_Set.py
│ │ └── syn_parser.py
│ ├── run_error_msg.py
│ ├── README.md
│ └── server.py
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
│   │       ├── CodeEditor.js
│   │       └── seaStackLang.ts
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
└── README.md
 ```

## 🖥️ How to Run
Follow these steps to set up and run SeaStack locally on your computer.

### 🔑 Prerequisites
Ensure you have the following installed:
- Node.js (v18 or higher recommended)
- Python (v3.10 or higher recommended)

Navigate to the root directory and install the required Python libraries:
```plaintext 
pip install -r requirements.txt
```

**▶️ Frontend & Root Setup (Node.js)**<br>
Install dependencies for the root project (to run the scripts) and the frontend interface:
```plaintext 
# 1. Install root dependencies (for the 'concurrently' script)
npm install

# 2. Install frontend dependencies (for React/Next.js)
cd frontend
npm install
cd ..
```

**▶️ Run the Application**<br>
Start both servers with one command from the root directory:
```plaintext 
npm run dev
```

## 👥 Contributors
- ALISWAG, K. V. J.
- CAYACAP, F. A. S.
- DEL ROSARIO, J. M. A.
- MAGAAN, F. M. V.
- MULLENO, J. M. A.
