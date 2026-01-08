"use client";
import { useState, useEffect, useRef } from "react"; 
import SeaStackEditor from "../components/CodeEditor";

export default function Home() {
  const [code, setCode] = useState("");
  const [tokens, setTokens] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(false);

  // --- File Management State ---
  const [fileName, setFileName] = useState("file.sea");
  const [fileCount, setFileCount] = useState(1);
  const fileInputRef = useRef(null); 

  // --- NEW: Rename State ---
  const [isRenaming, setIsRenaming] = useState(false);
  const [tempName, setTempName] = useState("");

  const [lexicalErrors, setLexicalErrors] = useState([]);
  const [syntaxErrors, setSyntaxErrors] = useState([]);   
  const [semanticLogs, setSemanticLogs] = useState([]); 
  
  const [activeTab, setActiveTab] = useState("lexical"); 

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    const isDark = document.body.classList.contains('dark-mode') || savedTheme === 'dark';

    if (isDark) {
      setIsDarkMode(true);
      document.body.classList.add('dark-mode'); 
    }
  }, []);

  const toggleTheme = (e) => {
    const checked = e.target.checked;
    setIsDarkMode(checked); 
    if (checked) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  };

  // --- 1. File Open Logic ---
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

  // --- 2. Save As Logic ---
  const handleSaveFile = async () => {
    if ('showSaveFilePicker' in window) {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: fileName, // Uses the current (possibly renamed) tab name
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

  // --- 3. Close Tab Logic ---
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

  // --- NEW: 4. Rename Logic (Double Click) ---
  const handleTabDoubleClick = () => {
    setTempName(fileName); // Load current name into input
    setIsRenaming(true);   // Show input
  };

  const handleRenameSubmit = () => {
    let finalName = tempName.trim();
    
    // If empty, revert to old name
    if (!finalName) {
        setIsRenaming(false);
        return;
    }

    // Force .sea extension
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
      if (result.lexical_errors?.length > 0) setLexicalErrors(result.lexical_errors);
      if (result.syntax_errors?.length > 0) setSyntaxErrors(result.syntax_errors);

      setActiveTab(targetTab);

    } catch (err) {
      console.error("Connection Error:", err);
      const errorObj = { line: "0", col: "0", message: "Cannot connect to Backend. Is 'server.py' running?" };
      if (targetTab === "lexical") setLexicalErrors([errorObj]);
      else setSyntaxErrors([errorObj]);
    }
  };
  
  const handleLexicalAnalysis = () => performAnalysis("lexical");
  const handleSyntaxAnalysis = () => performAnalysis("syntax");

  const ErrorList = ({ errors, typeName }) => {
    if (errors.length === 0) {
        return <div style={{color: '#4ade80', fontStyle: 'italic', padding: '10px'}}>No {typeName} Errors found.</div>;
    }
    return (
        <div style={{ fontFamily: '"Fira Code", monospace', fontSize: '0.9rem' }}>
            <div style={{ fontWeight: 'bold', color: '#f87171', marginBottom: '8px' }}>
                Found &apos;{errors.length}&apos; {typeName} Error&apos;s
            </div>
            
            {errors.map((err, i) => (
                <div key={i} style={{ display: 'flex', gap: '10px', color: '#e5e7eb', marginBottom: '4px' }}>
                    <span style={{ minWidth: '120px', color: '#9ca3af' }}>
                        Line {err.line}, Col {err.col}
                    </span>
                    <span style={{ color: '#6b7280' }}>|</span>
                    <span>{err.message}</span>
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
              <li><button onClick={handleLexicalAnalysis}>Lexical</button></li>
              <li><button onClick={handleSyntaxAnalysis}>Syntax</button></li>
              <li><button>Semantic</button></li>
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
                    {/* --- NEW: Conditional Rendering for Rename --- */}
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
                                width: `${tempName.length + 1}ch` // Auto-width hack
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
          
          {activeTab === "lexical" && (
            <ErrorList errors={lexicalErrors} typeName="Lexical" />
          )}

          {activeTab === "syntax" && (
             <ErrorList errors={syntaxErrors} typeName="Syntax" />
          )}

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
    </div>
  );
}