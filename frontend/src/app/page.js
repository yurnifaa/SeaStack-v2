"use client";
import { useState, useEffect, useRef } from "react"; 
import SeaStackEditor from "../components/CodeEditor";

const GooeyButton = ({ onClick, children }) => {
  return (
    <button className="c-button c-button--gooey" onClick={onClick}>
      {children}
      <div className="c-button__blobs">
        <div></div>
        <div></div>
        <div></div>
      </div>
    </button>
  );
};

export default function Home() {
  const [code, setCode] = useState("");
  const [tokens, setTokens] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(true);

  // File Management State
  const [fileName, setFileName] = useState("file.sea");
  const [fileCount, setFileCount] = useState(1);
  const fileInputRef = useRef(null); 

  // Rename State
  const [isRenaming, setIsRenaming] = useState(false);
  const [tempName, setTempName] = useState("");

  const [lexicalErrors, setLexicalErrors] = useState([]);
  const [syntaxErrors, setSyntaxErrors] = useState([]);   
  const [semanticLogs, setSemanticLogs] = useState([]); 
  
  const [activeTab, setActiveTab] = useState("lexical"); 

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
      setIsDarkMode(false);
      document.body.classList.remove('dark-mode');
    } else {
      setIsDarkMode(true);
      document.body.classList.add('dark-mode');
    }
  }, []);

  const toggleTheme = (e) => {
    const checked = e.target.checked;
    setIsDarkMode(checked); 
    if (checked) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('theme', 'dark');
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('theme', 'light');
    }
  };

  // --- File Open Logic ---
  const handleFileBtnClick = () => {
    fileInputRef.current.click();
  };

  const handleFileSelection = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.sea')) {
        alert("Please select a valid .sea file.");
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        setCode(e.target.result); 
        setFileName(file.name);   
    };
    reader.readAsText(file);
    event.target.value = ''; 
  };

  // --- Save As Logic ---
  const handleSaveFile = async () => {
    if ('showSaveFilePicker' in window) {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: fileName,
          types: [{
              description: 'SeaStack Source File',
              accept: { 'text/plain': ['.sea'] },
          }],
        });
        const writable = await handle.createWritable();
        await writable.write(code);
        await writable.close();
        setFileName(handle.name);
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Save failed:', err);
          alert('Failed to save file.');
        }
      }
    } else {
      // Fallback
      const element = document.createElement("a");
      const file = new Blob([code], {type: 'text/plain'});
      element.href = URL.createObjectURL(file);
      element.download = fileName;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }
  };

  // --- Close Tab Logic ---
  const handleCloseTab = () => {
    const nextCount = fileCount + 1;
    setFileCount(nextCount);
    setFileName(`file${nextCount}.sea`);
    setCode(""); 
    setTokens([]);
    setLexicalErrors([]);
    setSyntaxErrors([]);
    setSemanticLogs([]);
  };

  // --- Rename Logic ---
  const handleTabDoubleClick = () => {
    setTempName(fileName); 
    setIsRenaming(true);   
  };

  const handleRenameSubmit = () => {
    let finalName = tempName.trim();
    if (!finalName) {
        setIsRenaming(false);
        return;
    }
    if (!finalName.endsWith(".sea")) {
        finalName += ".sea";
    }
    setFileName(finalName);
    setIsRenaming(false);
  };

  const handleRenameKeyDown = (e) => {
    if (e.key === 'Enter') handleRenameSubmit();
    if (e.key === 'Escape') setIsRenaming(false);
  };

  // ==========================================
  // --- STRUCTURED ERROR FORMATTERS ---
  // ==========================================

  const formatSyntaxError = (errObj, sourceCode) => {
    if (!errObj.line || errObj.line === "?" || errObj.line === "-") {
        return { ...errObj, isStructured: false };
    }

    const lineNum = parseInt(errObj.line, 10);
    const lines = sourceCode.split('\n');
    const actualLine = lines[lineNum - 1] ? lines[lineNum - 1].trim() : "";
    
    const errorType = errObj.error_header || "Syntax Error"; 
    const found = errObj.found || "unknown";
    
    const expected = errObj.expected && errObj.expected.length > 0 
        ? errObj.expected.join(", ") 
        : "nothing";

    return {
        line: errObj.line,
        col: errObj.col,
        headerStr: `${errorType} '${found}'`,
        sourceCode: actualLine, // Syntax errors STILL SHOW the line
        expectedStr: expected,
        isStructured: true
    };
  };

  const formatLexicalError = (errObj, sourceCode) => {
    if (!errObj.line || errObj.line === "?" || errObj.line === "-") {
        return { ...errObj, isStructured: false };
    }

    const message = errObj.message || "";
    const foundStr = errObj.found || "";
    
    const isUnknown = message.includes("Unknown Character");

    let headerStr = foundStr;
    let expectedStr = "";

    if (isUnknown) {
        headerStr = message;
        expectedStr = "";
    } else {
        headerStr = foundStr; 

        if (errObj.expected && errObj.expected.length > 0) {
            expectedStr = errObj.expected.join(", ");
        } else {
            expectedStr = "Valid Token";
        }
    }

    return {
        line: errObj.line,
        col: errObj.col,
        headerStr: headerStr,
        sourceCode: null,
        expectedStr: expectedStr, 
        isStructured: true
    };
  };

  // ==========================================
  // --- ANALYSIS LOGIC ---
  // ==========================================
  const performAnalysis = async (targetTab) => {
    setLexicalErrors([]);
    setSyntaxErrors([]);
    setTokens([]); 

    try {
      const res = await fetch('http://127.0.0.1:5000/api/analyze', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code }),
      });

      if (!res.ok) throw new Error(`Server status: ${res.status}`);
      const result = await res.json();
      
      if (result.tokens) setTokens(result.tokens);
      
      // --- HANDLE LEXICAL ERRORS ---
      if (result.lexical_errors?.length > 0) {
          const formattedLex = result.lexical_errors.map(err => formatLexicalError(err, code));
          setLexicalErrors(formattedLex);
          setActiveTab("lexical");
          return; 
      }
      
      // --- HANDLE SYNTAX ERRORS ---
      if (result.syntax_errors?.length > 0) {
          const formattedSyn = result.syntax_errors.map(err => formatSyntaxError(err, code));
          setSyntaxErrors(formattedSyn);
      }

      setActiveTab(targetTab);

    } catch (err) {
      console.error("Connection Error:", err);
      const errorObj = { line: "0", col: "0", message: "Cannot connect to Backend. Is 'server.py' running?", isStructured: false };
      setLexicalErrors([errorObj]);
      setActiveTab("lexical");
    }
  };
  
  const handleLexicalAnalysis = () => performAnalysis("lexical");
  const handleSyntaxAnalysis = () => performAnalysis("syntax");

  // ==========================================
  // --- ERROR LIST COMPONENT ---
  // ==========================================
  const ErrorList = ({ errors, typeName }) => {
    return (
        <div style={{ fontFamily: '"Fira Code", monospace', fontVariantLigatures: 'none', fontSize: '0.9rem' }}>
            <div style={{ fontWeight: 'bold', color: '#a8cbff', marginBottom: '8px' }}>
                Found &apos;{errors.length}&apos; {typeName} Error/s
            </div>
            
            {errors.map((err, i) => (
                <div key={i} style={{ display: 'flex', gap: '10px', color: '#e5e7eb', marginBottom: '12px', alignItems: 'flex-start' }}>  
                    <span style={{ minWidth: '120px', color: '#9ca3af', flexShrink: 0, paddingTop: '2px' }}>
                        Line {err.line}, Col {err.col}
                    </span>
                    <span style={{ color: '#6b7280', paddingTop: '2px' }}>|</span>
                    
                    {err.isStructured ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                            {/* Header: TYPE 'found' */}
                            <span style={{ color: '#f87171', fontWeight: 'bold' }}>
                                {err.headerStr}
                            </span>
                            
                            {/* Source Line (Render only if present - hidden for Lexical) */}
                            {err.sourceCode && (
                                <span style={{ color: '#9ca3af'}}>
                                    &apos;{err.sourceCode}&apos;
                                </span>
                            )}
                            
                            {/* Expected (Render only if string is not empty) */}
                            {err.expectedStr && (
                                <span style={{ color: '#e5e7eb'}}>
                                    Expected: &apos;{err.expectedStr}&apos;
                                </span>
                            )}
                        </div>
                    ) : (
                        <span style={{ whiteSpace: 'pre-wrap', paddingTop: '2px' }}>{err.message}</span>
                    )}
                </div>
            ))}
        </div>
    );
  };

  return (
    <div className="container">
      <header className="header">
        <div className="header-left">
          <img src="./SeaStack_Logo.png" alt="Logo" className="logo" />
          <span className="title">SeaStack</span>
          <nav className="main-nav">
            <ul>
              <li><GooeyButton onClick={handleLexicalAnalysis}>Lexical</GooeyButton></li>
              <li><GooeyButton onClick={handleSyntaxAnalysis}>Syntax</GooeyButton></li>
              <li><GooeyButton onClick={() => setActiveTab("semantic")}>Semantic</GooeyButton></li>
            </ul>
          </nav>
        </div>

        <div className="header-right">
            <input 
                type="file" 
                ref={fileInputRef}
                onChange={handleFileSelection}
                accept=".sea" 
                style={{ display: "none" }} 
            />
            <button className="btn-header" onClick={handleFileBtnClick}>File</button>
            <button className="btn-header" onClick={handleSaveFile}>Save</button>
            
            <label className="switch">
            <input type="checkbox" onChange={toggleTheme} checked={isDarkMode} />
            <span className="slider">
                <span className="circle"><span className="moon"></span></span>
            </span>
            </label>
        </div>
      </header>

      <main className="main-content">
        <div className="panel panel-left">
            <div className="panel-tab-bar">
                <div className="tab active">
                    {isRenaming ? (
                        <input
                            autoFocus
                            type="text"
                            value={tempName}
                            onChange={(e) => setTempName(e.target.value)}
                            onBlur={handleRenameSubmit}
                            onKeyDown={handleRenameKeyDown}
                            style={{
                                background: 'transparent',
                                border: 'none',
                                color: 'inherit',
                                font: 'inherit',
                                outline: 'none',
                                minWidth: '50px',
                                width: `${tempName.length + 1}ch`
                            }}
                        />
                    ) : (
                        <span onDoubleClick={handleTabDoubleClick} title="Double-click to rename">
                            {fileName}
                        </span>
                    )}
                    
                    <button className="close-tab" onClick={handleCloseTab}>×</button>
                </div>
            </div>
            <SeaStackEditor code={code} setCode={setCode} isDarkMode={isDarkMode} />
        </div>

        <div className="panel panel-right">
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th style={{ width: '50%' }}>Lexeme</th>
                  <th style={{ width: '50%' }}>Token</th>
                </tr>
              </thead>
              <tbody>
                {tokens.length === 0 ? (
                  <tr><td colSpan="2" style={{textAlign: "center", padding: "20px", color: "#888", borderBottom: 'none'}}></td></tr>
                ) : (
                  tokens.map((t, index) => (
                    <tr key={index}>
                      <td>{t.lexeme}</td>
                      <td>{t.token}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      <footer className="footer">
        <nav className="footer-nav">
          <ul>
            <li><a className={activeTab === "lexical" ? "active" : ""} onClick={() => setActiveTab("lexical")}>Lexical Logs</a></li>
            <li><a className={activeTab === "syntax" ? "active" : ""} onClick={() => setActiveTab("syntax")}>Syntax Logs</a></li>
            <li><a className={activeTab === "semantic" ? "active" : ""} onClick={() => setActiveTab("semantic")}>Semantic Logs</a></li>
          </ul>
        </nav>
        
        <div className="footer-content" style={{ padding: '10px', overflowY: 'auto' }}>
          {activeTab === "lexical" && <ErrorList errors={lexicalErrors} typeName="Lexical" />}
          {activeTab === "syntax" && <ErrorList errors={syntaxErrors} typeName="Syntax" />}
          {activeTab === "semantic" && (
             <div className="log-container">
               {semanticLogs.length === 0 && <div style={{color: '#888', fontStyle: 'italic'}}>Ready for semantic analysis...</div>}
               {semanticLogs.map((log, i) => (
                 <div key={i}>{log.message}</div>
               ))}
             </div>
          )}
        </div>
      </footer>

      <svg
        style={{ display: 'block', height: 0, width: 0, position: 'absolute' }}
        version="1.1"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <filter id="goo">
            <feGaussianBlur
              result="blur"
              stdDeviation="10"
              in="SourceGraphic"
            />
            <feColorMatrix
              result="goo"
              values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7"
              mode="matrix"
              in="blur"
            />
            <feBlend in2="goo" in="SourceGraphic" />
          </filter>
        </defs>
      </svg>
    </div>
  );
} 