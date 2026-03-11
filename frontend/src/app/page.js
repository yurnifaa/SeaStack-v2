"use client";
import { useState, useEffect, useRef } from "react";
import SeaStackEditor from "../components/CodeEditor";

const GooeyButton = ({ onClick, children, disabled, style }) => {
  return (
    <button
      className="c-button c-button--gooey"
      onClick={onClick}
      disabled={disabled}
      style={{ opacity: disabled ? 0.5 : 1, pointerEvents: disabled ? 'none' : 'auto', ...style }}
    >
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
  const [isDarkMode, setIsDarkMode] = useState(true);

  // File Management State
  const [fileName, setFileName] = useState("file.sea");
  const [fileCount, setFileCount] = useState(1);
  const fileInputRef = useRef(null);

  // Rename State
  const [isRenaming, setIsRenaming] = useState(false);
  const [tempName, setTempName] = useState("");

  // Errors — unified
  const [errors, setErrors] = useState([]);
  const [errorPhase, setErrorPhase] = useState(null);

  // Execution state
  const [isRunning, setIsRunning] = useState(false);
  const [consoleOutput, setConsoleOutput] = useState("");
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const consoleEndRef = useRef(null);

  // Interactive input state
  const [needsInput, setNeedsInput]     = useState(false);
  const [inputValue, setInputValue]     = useState("");
  const [inputDtype, setInputDtype]     = useState("SCROLL");  // expected dtype for current input
  const inputFieldRef                   = useRef(null);
  const inputBufferRef                  = useRef([]);           // queued space-delimited tokens

  // Keep a ref to the active fetch reader so Stop can abort it
  const readerRef = useRef(null);

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

  // Auto-scroll console output
  useEffect(() => {
    if (consoleEndRef.current) {
      consoleEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [consoleOutput, needsInput]);

  // Auto-focus the input field whenever it appears
  useEffect(() => {
    if (needsInput && inputFieldRef.current) {
      inputFieldRef.current.focus();
    }
  }, [needsInput]);

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
      const element = document.createElement("a");
      const file = new Blob([code], { type: 'text/plain' });
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
    setErrors([]);
    setErrorPhase(null);
    setConsoleOutput("");
    setNeedsInput(false);
    setInputValue("");
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
  // --- ERROR FORMATTERS ---
  // ==========================================

  const formatLexicalError = (errObj) => {
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
        expectedStr = `Expected: ${errObj.expected.join(", ")}`;
      } else {
        expectedStr = "Expected: Valid Token";
      }
    }

    return {
      line: errObj.line,
      col: errObj.col,
      errorType: "Lexical Error",
      headerStr: headerStr,
      sourceCode: null,
      expectedStr: expectedStr,
      isStructured: true
    };
  };

  const formatSyntaxError = (errObj, sourceCode) => {
    if (!errObj.line || errObj.line === "?" || errObj.line === "-") {
      return { ...errObj, isStructured: false };
    }

    const lineNum = parseInt(errObj.line, 10);
    const lines = sourceCode.split('\n');
    const actualLine = lines[lineNum - 1] ? lines[lineNum - 1].trim() : "";

    const found = errObj.found || "unknown";
    const expected = errObj.expected && errObj.expected.length > 0
      ? `Expected: ${errObj.expected.join(", ")}`
      : "";

    return {
      line: errObj.line,
      col: errObj.col,
      errorType: errObj.error_header || "Syntax Error",
      headerStr: `${errObj.error_header || "Syntax Error"}: '${found}'`,
      sourceCode: actualLine,
      expectedStr: expected,
      isStructured: true
    };
  };

  const formatSemanticError = (errObj, sourceCode) => {
    if (!errObj.line || errObj.line === "?" || errObj.line === "-") {
      return { ...errObj, isStructured: false };
    }

    let actualLine = errObj.actual_line || "";
    if (!actualLine && sourceCode) {
      const lineNum = parseInt(errObj.line, 10);
      const lines = sourceCode.split('\n');
      actualLine = lines[lineNum - 1] ? lines[lineNum - 1].trim() : "";
    }

    return {
      line: errObj.line,
      col: errObj.col,
      errorType: errObj.error_type || errObj.type || "Semantic Error",
      headerStr: errObj.error_type || errObj.type || "Semantic Error",
      sourceCode: actualLine || null,
      expectedStr: errObj.message || "",
      isStructured: true,
    };
  };

  // Runtime exception messages
  const simplifyRuntimeMessage = (msg) => {
    if (!msg) return "An error occurred during program execution.";
    const m = msg.toLowerCase();
    if (m.includes('coin input exceeds 16 digits')) 
      return "Overflow Error: COIN input exceeds 16 digits.";
    if (m.includes('dime input exceeds 8 digits')) 
      return "Overflow Error: DIME input exceeds 8 digits.";
    if (m.includes('division by zero') || m.includes('zerodivisionerror'))
      return "Cannot divide by zero.";
    if (m.includes('invalid literal for int') || m.includes('base 10') || (m.includes('invalid') && m.includes('int')))
      return "Invalid input: COIN was expected but the value entered cannot be converted.";
    if ((m.includes('could not convert') && m.includes('float')) || (m.includes('valueerror') && m.includes('float')))
      return "Invalid input: DIME was expected but the value entered cannot be converted.";
    if (m.includes('expected aye or nay'))
      return "Invalid input: a BOOL value was expected.";
    if (m.includes('list index out of range') || m.includes('indexerror'))
      return "Array index is out of bounds.";
    if (m.includes('keyerror'))
      return "Struct member not found. A field was accessed that does not exist in the struct.";
    if (m.includes('recursionerror') || m.includes('maximum recursion') || m.includes('stack overflow'))
      return "Stack overflow: too many nested function calls.";
    if (m.includes('valueerror'))
      return "Invalid value encountered during execution. Check the inputs and expressions in your program.";
    if (m.includes('typeerror'))
      return "A value of the wrong type was used in an operation.";
    return msg;
  };

  const formatRuntimeError = (errObj) => {
    const line = errObj.line || "-";
    // Strict check so col=0 is displayed correctly (0 is falsy in JS but valid)
    const col = (errObj.col !== undefined && errObj.col !== null && errObj.col !== "")
      ? errObj.col
      : "-";

    // Prefer actual_line from backend; fall back to looking it up from source
    let sourceCode = errObj.actual_line || null;
    if (!sourceCode && line !== "-") {
      const lineNum = parseInt(line, 10);
      if (!isNaN(lineNum) && lineNum > 0) {
        const srcLines = code.split('\n');
        const candidate = srcLines[lineNum - 1];
        if (candidate && candidate.trim()) sourceCode = candidate.trim();
      }
    }

    return {
      line,
      col,
      errorType: errObj.error_type || "Runtime Error",
      headerStr: errObj.error_type || "Runtime Error",
      sourceCode: sourceCode || null,
      expectedStr: simplifyRuntimeMessage(errObj.message),
      isStructured: true,
    };
  };

  // ==========================================
  // --- RUN LOGIC  (SSE streaming)         ---
  // ==========================================
  const handleRun = async () => {
    if (!code.trim()) {
      setErrors([{
        line: "-", col: "-",
        errorType: "Input Error",
        headerStr: "No source code",
        sourceCode: null,
        expectedStr: "Please write or load a SeaStack program before running.",
        isStructured: true
      }]);
      setErrorPhase("Input");
      return;
    }

    // Clear previous state
    setErrors([]);
    setErrorPhase(null);
    setConsoleOutput("");
    setNeedsInput(false);
    setInputValue("");
    setIsRunning(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code, session_id: sessionId }),
      });

      if (!response.ok) throw new Error(`Server status: ${response.status}`);
      if (!response.body)  throw new Error("No response body — streaming not supported.");

      const reader = response.body.getReader();
      readerRef.current = reader;
      const decoder = new TextDecoder();
      let buffer = '';

      // Read the SSE stream chunk by chunk
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // SSE frames are separated by \n\n
        const frames = buffer.split('\n\n');
        buffer = frames.pop(); // keep incomplete trailing frame

        for (const frame of frames) {
          // Each frame may contain multiple lines; we want the `data:` line
          for (const line of frame.split('\n')) {
            if (!line.startsWith('data: ')) continue;

            let event;
            try {
              event = JSON.parse(line.slice(6));
            } catch {
              continue;
            }

            if (event.type === 'output') {
              setConsoleOutput(prev => prev + event.text);

            } else if (event.type === 'input_needed') {
                setNeedsInput(true);

            } else if (event.type === 'error') {
              setErrors([formatRuntimeError(event.error)]);
              setErrorPhase("Runtime");

            } else if (event.type === 'compile_error') {
              const phase = event.phase || "Unknown";
              let formatted = [];
              if (phase === "Lexical") {
                formatted = event.errors.map(e => formatLexicalError(e));
              } else if (phase === "Syntax") {
                formatted = event.errors.map(e => formatSyntaxError(e, code));
              } else if (phase === "Semantic") {
                formatted = event.errors.map(e => formatSemanticError(e, code));
              } else {
                formatted = event.errors.map(e => ({
                  line: e.line || "-", col: e.col || "-",
                  errorType: phase + " Error",
                  headerStr: e.message || "Unknown error",
                  sourceCode: null,
                  expectedStr: e.message || "",
                  isStructured: true,
                }));
              }
              setErrors(formatted);
              setErrorPhase(phase);

            } else if (event.type === 'done') {
              setNeedsInput(false);
              setIsRunning(false);
              if (event.success) {
                setErrors([]);
                setErrorPhase(null);
              }
            }
          }
        }
      }
    } catch (err) {
      // Ignore AbortError — that's from the user clicking Stop
      if (err.name !== 'AbortError') {
        console.error("Connection Error:", err);
        setErrors([{
          line: "-", col: "-",
          errorType: "Connection Error",
          headerStr: "Cannot connect to Backend",
          sourceCode: null,
          expectedStr: "Is 'server.py' running? Start it with: python server.py",
          isStructured: true,
        }]);
        setErrorPhase("Connection");
      }
    } finally {
      readerRef.current = null;
      setIsRunning(false);
      setNeedsInput(false);
    }
  };

  // ==========================================
  // --- STOP LOGIC ---
  // ==========================================
  const handleStop = async () => {
    // Cancel the SSE reader
    if (readerRef.current) {
      try { readerRef.current.cancel(); } catch {}
    }
    // Tell the server to stop the execution thread
    try {
      await fetch('http://127.0.0.1:5000/api/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      });
    } catch (err) {
      console.error("Stop failed:", err);
    }
    setIsRunning(false);
    setNeedsInput(false);
    setInputValue("");
  };

  // ==========================================
  // --- INPUT SUBMIT LOGIC ---
  // ==========================================
const handleInputKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const value = inputValue;
      setInputValue("");
      setNeedsInput(false);
      
      // Echo the typed line securely and inline
      setConsoleOutput(prev => prev + value + '\n');

      // Send the entire line unmodified to backend
      fetch('http://127.0.0.1:5000/api/input', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, input: value }),
      }).catch(err => console.error("Input submit failed:", err));
    }
  };

  // ==========================================
  // --- ERROR LIST COMPONENT ---
  // ==========================================
  const ErrorList = ({ errors, phaseName }) => {
    if (errors.length === 0) {
      return (
        <div style={{
          fontFamily: '"Fira Code", monospace',
          fontVariantLigatures: 'none',
          fontSize: '0.85rem',
          color: '#4ade80',
          fontWeight: 'bold'
        }}>
          ✓ No errors found. Program compiled and executed successfully.
        </div>
      );
    }

    return (
      <div style={{ fontFamily: '"Fira Code", monospace', fontVariantLigatures: 'none', fontSize: '0.85rem' }}>
        {/* Line 1: Error count and type */}
        <div style={{ fontWeight: 'bold', color: '#f87171', marginBottom: '10px', fontSize: '0.9rem' }}>
          ✗ Found {errors.length} {phaseName} Error{errors.length !== 1 ? 's' : ''}
        </div>

        {errors.map((err, i) => (
          <div key={i} style={{
            marginBottom: '14px',
            paddingBottom: '10px',
            borderBottom: '1px solid rgba(255,255,255,0.08)',
          }}>
            {err.isStructured ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                {/* Line 2: Location + Error Type */}
                <div style={{ display: 'flex', gap: '10px', alignItems: 'baseline' }}>
                  <span style={{ color: '#9ca3af', minWidth: '110px', flexShrink: 0, fontSize: '0.8rem' }}>
                    Line {err.line}, Col {err.col}
                  </span>
                  <span style={{ color: '#475569', fontSize: '0.8rem' }}>│</span>
                  <span style={{ color: '#f87171', fontWeight: 'bold' }}>
                    {err.headerStr}
                  </span>
                </div>

                {/* Line 3: Source code line (if available) */}
                {err.sourceCode && (
                  <div style={{ marginLeft: '130px', color: '#94a3b8', fontStyle: 'italic', fontSize: '0.82rem' }}>
                    → {err.sourceCode}
                  </div>
                )}

                {/* Line 4: Expected / Description */}
                {err.expectedStr && (
                  <div style={{ marginLeft: '130px', color: '#cbd5e1', fontSize: '0.82rem' }}>
                    {err.expectedStr}
                  </div>
                )}
              </div>
            ) : (
              <div style={{ display: 'flex', gap: '10px', color: '#e5e7eb' }}>
                <span style={{ color: '#9ca3af', minWidth: '110px', flexShrink: 0 }}>
                  Line {err.line || '-'}, Col {err.col || '-'}
                </span>
                <span style={{ color: '#475569' }}>│</span>
                <span style={{ whiteSpace: 'pre-wrap' }}>{err.message || "Unknown error"}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  // ==========================================
  // --- CONSOLE OUTPUT COMPONENT ---
  // ==========================================
  return (
    <div className="container">
      <header className="header">
        <div className="header-left">
          <img src="./SeaStack_Logo.png" alt="Logo" className="logo" />
          <span className="title">SeaStack</span>
          <nav className="main-nav">
            <ul>
              <li>
                {isRunning ? (
                  <GooeyButton onClick={handleStop} style={{ borderColor: '#e74c3c' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor">
                        <rect width="10" height="10" rx="1" />
                      </svg>
                      Stop
                    </span>
                  </GooeyButton>
                ) : (
                  <GooeyButton onClick={handleRun}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <svg width="10" height="12" viewBox="0 0 10 12" fill="currentColor">
                        <polygon points="0,0 10,6 0,12" />
                      </svg>
                      Run
                    </span>
                  </GooeyButton>
                )}
              </li>
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
        {/* Left Panel — Code Editor */}
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

        {/* Right Panel — Output Console */}
        <div className="panel panel-right">
          {/* Right Panel — Output Console */}
        <div className="panel panel-right">
          <div className="console-panel" style={{
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            width: '100%',
          }}>
            {/* Console Header */}
            <div style={{
              backgroundColor: '#0C2B4E',
              color: '#ffffff',
              padding: '8px 15px',
              fontWeight: 'bold',
              fontSize: '0.9rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              flexShrink: 0,
            }}>
              <span style={{ fontSize: '1rem' }}>▶</span>
              Output Console
            </div>

            {/* Console Body */}
            <style>{`
              @keyframes _ss_blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
              ._ss_cursor { animation: _ss_blink 1s step-end infinite; }
            `}</style>
            <div
              style={{
                flex: 1,
                padding: '12px 15px',
                overflowY: 'auto',
                fontFamily: '"Fira Code", monospace',
                fontVariantLigatures: 'none',
                fontSize: '0.88rem',
                lineHeight: '1.6',
                wordBreak: 'break-word',
                color: isDarkMode ? '#e2e8f0' : '#1e293b',
                backgroundColor: isDarkMode ? 'rgba(17, 25, 40, 0.59)' : 'rgba(255, 255, 255, 0.45)',
                backdropFilter: 'blur(16px) saturate(180%)',
                WebkitBackdropFilter: 'blur(16px) saturate(180%)',
                cursor: needsInput ? 'text' : 'default',
                position: 'relative',
              }}
              onClick={() => needsInput && inputFieldRef.current?.focus()}
            >
              {/* Output text + inline cursor-positioned input rendered as one flow */}
              <span style={{ whiteSpace: 'pre-wrap' }}>
                {consoleOutput}
                {needsInput && (
                  <>
                    <span style={{ color: isDarkMode ? '#facc15' : '#92400e' }}>{inputValue}</span>
                    <span className="_ss_cursor" style={{ color: isDarkMode ? '#facc15' : '#92400e', userSelect: 'none' }}>▌</span>
                  </>
                )}
              </span>
              {!consoleOutput && !needsInput && (
                <span style={{ color: '#6b7280', fontStyle: 'italic' }}>
                  {isRunning ? "Waiting for output..." : "Run a program to see its output here."}
                </span>
              )}

              <input
                ref={inputFieldRef}
                type="text"
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                onKeyDown={handleInputKeyDown}
                disabled={!needsInput}
                onBlur={() => {
                  if (needsInput) setTimeout(() => inputFieldRef.current?.focus(), 10);
                }}
                autoComplete="off" autoCorrect="off" autoCapitalize="off" spellCheck={false}
                style={{ position: 'absolute', opacity: 0, width: '1px', height: '1px', border: 'none', padding: 0, margin: 0, pointerEvents: 'none' }}
              />

              <div ref={consoleEndRef} />
            </div>
          </div>
        </div>
        </div>
      </main>

      {/* Footer — Error Logs */}
      <footer className="footer">
        <nav className="footer-nav">
          <ul>
            <li>
              <a className="active">
                Error Logs
                {errors.length > 0 && (
                  <span style={{
                    marginLeft: '8px',
                    backgroundColor: '#ef4444',
                    color: '#fff',
                    borderRadius: '999px',
                    padding: '1px 7px',
                    fontSize: '0.7rem',
                    fontWeight: 'bold',
                  }}>
                    {errors.length}
                  </span>
                )}
              </a>
            </li>
          </ul>
        </nav>

        <div className="footer-content" style={{ padding: '10px', overflowY: 'auto' }}>
          {errors.length === 0 && !isRunning ? (
            <div style={{
              fontFamily: '"Fira Code", monospace',
              fontVariantLigatures: 'none',
              fontSize: '0.85rem',
              color: '#6b7280',
              fontStyle: 'italic',
            }}>
              Press Run to compile and execute your SeaStack program.
            </div>
          ) : errors.length === 0 && !errorPhase ? (
            <ErrorList errors={[]} phaseName="" />
          ) : (
            <ErrorList errors={errors} phaseName={errorPhase || "Unknown"} />
          )}
        </div>
      </footer>

      {/* SVG filter for gooey button effect */}
      <svg
        style={{ display: 'block', height: 0, width: 0, position: 'absolute' }}
        version="1.1"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <filter id="goo">
            <feGaussianBlur result="blur" stdDeviation="10" in="SourceGraphic" />
            <feColorMatrix result="goo" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" mode="matrix" in="blur" />
            <feBlend in2="goo" in="SourceGraphic" />
          </filter>
        </defs>
      </svg>
    </div>
  );
}