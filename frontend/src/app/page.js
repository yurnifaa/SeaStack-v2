"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import { Waves } from "lucide-react";
import SeaStackEditor from "../components/CodeEditor";
import { simplifyRuntimeMessage } from "../utils/runtimeErrorMsg";

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

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';

export default function Home() {
  const [isDarkMode, setIsDarkMode] = useState(true);

  // Multi-tab State
  const [tabs, setTabs] = useState([{ id: 1, fileName: 'file.sea', code: '' }]);
  const [activeTabId, setActiveTabId] = useState(1);
  const [tabIdCounter, setTabIdCounter] = useState(2);
  const [renamingTabId, setRenamingTabId] = useState(null);
  const [tempName, setTempName] = useState('');
  const [dragTabId, setDragTabId] = useState(null);
  const fileInputRef = useRef(null);

  // Derived from active tab
  const activeTab = tabs.find(t => t.id === activeTabId) ?? tabs[0];
  const code = activeTab?.code ?? '';
  const fileName = activeTab?.fileName ?? 'file.sea';
  const setCode = useCallback((val) => {
    setTabs(prev => prev.map(t => t.id === activeTabId ? { ...t, code: val } : t));
  }, [activeTabId]);

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

  // Resize handle state
  const mainContentRef = useRef(null);
  const [leftWidth, setLeftWidth] = useState(60);

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
      const content = e.target.result;
      if (!activeTab?.code.trim()) {
        setTabs(prev => prev.map(t => t.id === activeTabId ? { ...t, fileName: file.name, code: content } : t));
      } else {
        const newId = tabIdCounter;
        setTabIdCounter(prev => prev + 1);
        setTabs(prev => [...prev, { id: newId, fileName: file.name, code: content }]);
        setActiveTabId(newId);
      }
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
          types: [{ description: 'SeaStack Source File', accept: { 'text/plain': ['.sea'] } }],
        });
        const writable = await handle.createWritable();
        await writable.write(code);
        await writable.close();
        setTabs(prev => prev.map(t => t.id === activeTabId ? { ...t, fileName: handle.name } : t));
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
  const handleCloseTab = (id) => {
    if (tabs.length === 1) {
      setTabs([{ id: tabs[0].id, fileName: 'file.sea', code: '' }]);
      setErrors([]);
      setErrorPhase(null);
      setConsoleOutput('');
      setNeedsInput(false);
      setInputValue('');
      return;
    }
    const idx = tabs.findIndex(t => t.id === id);
    const newTabs = tabs.filter(t => t.id !== id);
    setTabs(newTabs);
    if (activeTabId === id) {
      setActiveTabId(newTabs[Math.max(0, idx - 1)].id);
    }
  };

  // --- New Tab Logic ---
  const handleNewTab = () => {
    const newId = tabIdCounter;
    setTabIdCounter(prev => prev + 1);
    setTabs(prev => [...prev, { id: newId, fileName: `file${newId}.sea`, code: '' }]);
    setActiveTabId(newId);
  };

  // --- Rename Logic ---
  const handleTabDoubleClick = (id) => {
    setTempName(tabs.find(t => t.id === id)?.fileName ?? '');
    setRenamingTabId(id);
  };

  const handleRenameSubmit = () => {
    let finalName = tempName.trim();
    if (!finalName) { setRenamingTabId(null); return; }
    if (!finalName.endsWith('.sea')) finalName += '.sea';
    setTabs(prev => prev.map(t => t.id === renamingTabId ? { ...t, fileName: finalName } : t));
    setRenamingTabId(null);
  };

  const handleRenameKeyDown = (e) => {
    if (e.key === 'Enter') handleRenameSubmit();
    if (e.key === 'Escape') setRenamingTabId(null);
  };

  // --- Tab Drag Logic ---
  const handleTabDragStart = (e, id) => {
    setDragTabId(id);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleTabDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleTabDrop = (e, targetId) => {
    e.preventDefault();
    if (dragTabId === null || dragTabId === targetId) return;
    setTabs(prev => {
      const from = prev.findIndex(t => t.id === dragTabId);
      const to = prev.findIndex(t => t.id === targetId);
      const next = [...prev];
      const [moved] = next.splice(from, 1);
      next.splice(to, 0, moved);
      return next;
    });
    setDragTabId(null);
  };

  const handleTabDragEnd = () => setDragTabId(null);

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
    const rawLine = lines[lineNum - 1] || "";
    const leadingSpaces = rawLine.length - rawLine.trimStart().length;
    const actualLine = rawLine.trim();

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
      leadingSpaces,
      expectedStr: expected,
      isStructured: true
    };
  };

  const formatSemanticError = (errObj) => {
    // Backend (sem_error_msg.py) guarantees all fields are populated.
    // Guard only against the internal-error case where line is '?'.
    if (errObj.line === '?') return { ...errObj, isStructured: false };
    const rawLine = errObj.actual_line || "";
    const leadingSpaces = rawLine.length - rawLine.trimStart().length;
    return {
      line:         errObj.line,
      col:          errObj.col,
      errorType:    errObj.error_type,
      headerStr:    errObj.error_type,
      sourceCode:   rawLine.trim() || null,
      leadingSpaces,
      expectedStr:  errObj.message,
      isStructured: true,
    };
  };

  const formatRuntimeError = (errObj) => {
    const line = errObj.line || "-";
    // Strict check so col=0 is displayed correctly (0 is falsy in JS but valid)
    const col = (errObj.col !== undefined && errObj.col !== null && errObj.col !== "")
      ? errObj.col
      : "-";

    // Prefer actual_line from backend; fall back to looking it up from source
    let sourceCode = null;
    let leadingSpaces = 0;
    if (errObj.actual_line) {
      const rawLine = errObj.actual_line;
      leadingSpaces = rawLine.length - rawLine.trimStart().length;
      sourceCode = rawLine.trim();
    } else if (line !== "-") {
      const lineNum = parseInt(line, 10);
      if (!isNaN(lineNum) && lineNum > 0) {
        const srcLines = code.split('\n');
        const candidate = srcLines[lineNum - 1];
        if (candidate && candidate.trim()) {
          leadingSpaces = candidate.length - candidate.trimStart().length;
          sourceCode = candidate.trim();
        }
      }
    }

    return {
      line,
      col,
      errorType: errObj.error_type || "Runtime Error",
      headerStr: errObj.error_type || "Runtime Error",
      sourceCode: sourceCode || null,
      leadingSpaces,
      expectedStr: simplifyRuntimeMessage(errObj.message),
      isStructured: true,
    };
  };

  // ==========================================
  // --- RUN LOGIC  (SSE streaming)         ---
  // ==========================================
  const handleRun = async () => {
    console.log("Attempting to connect to:", API_URL);
    // Clear previous state
    setErrors([]);
    setErrorPhase(null);
    setConsoleOutput("");
    setNeedsInput(false);
    setInputValue("");
    setIsRunning(true);

    try {
      const response = await fetch(`${API_URL}/api/run`, {
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
                formatted = event.errors.map(e => formatSemanticError(e));
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
      await fetch(`${API_URL}/api/stop`, {
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
  // --- RESIZE HANDLE LOGIC ---
  // ==========================================
  const handleResizeMouseDown = (e) => {
    e.preventDefault();
    const onMouseMove = (moveEvent) => {
      const container = mainContentRef.current;
      if (!container) return;
      const rect = container.getBoundingClientRect();
      const newPct = ((moveEvent.clientX - rect.left) / rect.width) * 100;
      setLeftWidth(Math.min(Math.max(newPct, 25), 75));
    };
    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
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
      fetch(`${API_URL}/api/input`, {
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

                {/* Line 3: Source code line + column caret */}
                {err.sourceCode && (
                  <>
                    <div style={{ marginLeft: '130px', color: '#94a3b8', fontStyle: 'italic', fontSize: '0.82rem', whiteSpace: 'pre' }}>
                      {'→ '}{err.sourceCode}
                    </div>
                    {err.col !== "-" && err.col !== undefined && !isNaN(Number(err.col)) && (
                      <div style={{ marginLeft: '130px', color: '#94a3b8', fontSize: '0.82rem', whiteSpace: 'pre' }}>
                        {'  ' + ' '.repeat(Math.max(0, Number(err.col) - 1 - (err.leadingSpaces || 0))) + '^'}
                      </div>
                    )}
                  </>
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
                  <GooeyButton onClick={handleRun} disabled={!code.trim()}>
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

      <main className="main-content" ref={mainContentRef}>
        {/* Left Panel — Code Editor + Error Logs */}
        <div className="panel-left" style={{ width: `${leftWidth}%` }}>
          <div className="editor-card">
          <div className="panel-tab-bar">
            {tabs.map(tab => (
              <div
                key={tab.id}
                className={`tab${tab.id === activeTabId ? ' active' : ''}${dragTabId === tab.id ? ' dragging' : ''}`}
                draggable
                onDragStart={(e) => handleTabDragStart(e, tab.id)}
                onDragOver={handleTabDragOver}
                onDrop={(e) => handleTabDrop(e, tab.id)}
                onDragEnd={handleTabDragEnd}
                onClick={() => { if (renamingTabId !== tab.id) setActiveTabId(tab.id); }}
              >
                <Waves size={13} className="tab-icon" />
                {renamingTabId === tab.id ? (
                  <input
                    autoFocus
                    type="text"
                    value={tempName}
                    onChange={(e) => setTempName(e.target.value)}
                    onBlur={handleRenameSubmit}
                    onKeyDown={handleRenameKeyDown}
                    onClick={(e) => e.stopPropagation()}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: 'inherit',
                      font: 'inherit',
                      outline: 'none',
                      minWidth: '50px',
                      width: `${Math.max(tempName.length + 1, 8)}ch`,
                    }}
                  />
                ) : (
                  <span
                    className="tab-name"
                    onDoubleClick={(e) => { e.stopPropagation(); handleTabDoubleClick(tab.id); }}
                    title="Double-click to rename"
                  >
                    {tab.fileName}
                  </span>
                )}
                <button
                  className="close-tab"
                  onClick={(e) => { e.stopPropagation(); handleCloseTab(tab.id); }}
                  title="Close tab"
                >×</button>
              </div>
            ))}
            <button className="new-tab-btn" onClick={handleNewTab} title="New tab">+</button>
          </div>
          <SeaStackEditor code={code} setCode={setCode} isDarkMode={isDarkMode} />
          </div>{/* end editor-card */}

          {/* Error Panel */}
          <div className="error-panel">
            <nav className="error-panel-nav">
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
            <div className="error-panel-content">
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
          </div>
        </div>

        {/* Draggable Resize Handle */}
        <div className="resize-handle" onMouseDown={handleResizeMouseDown} />

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
                overflowX: 'auto',
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
      </main>

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