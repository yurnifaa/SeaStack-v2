"use client";
import { useState, useEffect } from "react"; 
import SeaStackEditor from "../components/CodeEditor";

export default function Home() {
  const [code, setCode] = useState("");
  const [tokens, setTokens] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(false);

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

      if (result.lexical_errors && result.lexical_errors.length > 0) {
          setLexicalErrors(result.lexical_errors);
      }

      if (result.syntax_errors && result.syntax_errors.length > 0) {
          setSyntaxErrors(result.syntax_errors);
      }

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
            <input type="file" id="file-input" accept=".sea" style={{ display: "none" }} />
            <button className="btn-header">File</button>
            <button className="btn-header">Save</button>
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
                    <span>file.sea</span>
                    <button className="close-tab">×</button>
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