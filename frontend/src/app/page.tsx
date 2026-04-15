"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import Image from "next/image";
import { Fish, Play, Square, FolderOpen, Download, SquareTerminal } from "lucide-react";
import SeaStackEditor from "../components/CodeEditor";
import { simplifyRuntimeMessage } from "../utils/runtimeErrorMsg";
import type { Tab, FormattedError, RawError } from "../types";

interface GooeyButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  disabled?: boolean;
  style?: React.CSSProperties;
}

const GooeyButton = ({ onClick, children, disabled, style }: GooeyButtonProps) => {
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
  const [tabs, setTabs] = useState<Tab[]>([{ id: 1, fileName: 'file.sea', code: '' }]);
  const [activeTabId, setActiveTabId] = useState(1);
  const [tabIdCounter, setTabIdCounter] = useState(2);
  const [renamingTabId, setRenamingTabId] = useState<number | null>(null);
  const [tempName, setTempName] = useState('');
  const [dragTabId, setDragTabId] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Derived from active tab
  const activeTab = tabs.find(t => t.id === activeTabId) ?? tabs[0];
  const code = activeTab?.code ?? '';
  const fileName = activeTab?.fileName ?? 'file.sea';
  const setCode = useCallback((val: string) => {
    setTabs(prev => prev.map(t => t.id === activeTabId ? { ...t, code: val } : t));
  }, [activeTabId]);

  // Errors — unified
  const [errors, setErrors] = useState<FormattedError[]>([]);
  const [errorPhase, setErrorPhase] = useState<string | null>(null);

  // Execution state
  const [isRunning, setIsRunning] = useState(false);
  const [consoleOutput, setConsoleOutput] = useState("");
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const consoleEndRef = useRef<HTMLDivElement>(null);

  // Interactive input state
  const [needsInput, setNeedsInput] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const inputFieldRef = useRef<HTMLInputElement>(null);

  // Keep a ref to the active fetch reader so Stop can abort it
  const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null);

  // Resize handle state
  const mainContentRef = useRef<HTMLDivElement>(null);
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

  const toggleTheme = (e: React.ChangeEvent<HTMLInputElement>) => {
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
    fileInputRef.current?.click();
  };

  const handleFileSelection = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!file.name.endsWith('.sea')) {
      alert("Please select a valid .sea file.");
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
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
        const handle = await (window as Window & { showSaveFilePicker: (opts: object) => Promise<FileSystemFileHandle> }).showSaveFilePicker({
          suggestedName: fileName,
          types: [{ description: 'SeaStack Source File', accept: { 'text/plain': ['.sea'] } }],
        });
        const writable = await handle.createWritable();
        await writable.write(code);
        await writable.close();
        setTabs(prev => prev.map(t => t.id === activeTabId ? { ...t, fileName: handle.name } : t));
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
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
  const handleCloseTab = (id: number) => {
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
  const handleTabDoubleClick = (id: number) => {
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

  const handleRenameKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleRenameSubmit();
    if (e.key === 'Escape') setRenamingTabId(null);
  };

  // --- Tab Drag Logic ---
  const handleTabDragStart = (e: React.DragEvent, id: number) => {
    setDragTabId(id);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleTabDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleTabDrop = (e: React.DragEvent, targetId: number) => {
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

  const formatLexicalError = (errObj: RawError): FormattedError => {
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
    } else {
      headerStr = foundStr;
    }
    return {
      line: errObj.line,
      col: errObj.col ?? "-",
      errorType: "Lexical Error",
      headerStr,
      sourceCode: null,
      expectedStr,
      isStructured: true
    };
  };

  const formatSyntaxError = (errObj: RawError, sourceCode: string): FormattedError => {
    if (!errObj.line || errObj.line === "?" || errObj.line === "-") {
      return { ...errObj, isStructured: false };
    }
    const lineNum = parseInt(String(errObj.line), 10);
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
      col: errObj.col ?? "-",
      errorType: errObj.error_header || "Syntax Error",
      headerStr: `${errObj.error_header || "Syntax Error"}: '${found}'`,
      sourceCode: actualLine,
      leadingSpaces,
      expectedStr: expected,
      isStructured: true
    };
  };

  const formatSemanticError = (errObj: RawError): FormattedError => {
    if (errObj.line === '?') return { ...errObj, isStructured: false };
    const rawLine = errObj.actual_line || "";
    const leadingSpaces = rawLine.length - rawLine.trimStart().length;
    return {
      line: errObj.line ?? "-",
      col: errObj.col ?? "-",
      errorType: errObj.error_type ?? "Semantic Error",
      headerStr: errObj.error_type ?? "Semantic Error",
      sourceCode: rawLine.trim() || null,
      leadingSpaces,
      expectedStr: errObj.message ?? "",
      isStructured: true,
    };
  };

  const formatRuntimeError = (errObj: RawError): FormattedError => {
    const line = errObj.line || "-";
    const col = (errObj.col !== undefined && errObj.col !== null && errObj.col !== "")
      ? errObj.col
      : "-";
    let sourceCode: string | null = null;
    let leadingSpaces = 0;
    if (errObj.actual_line) {
      const rawLine = errObj.actual_line;
      leadingSpaces = rawLine.length - rawLine.trimStart().length;
      sourceCode = rawLine.trim();
    } else if (line !== "-") {
      const lineNum = parseInt(String(line), 10);
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
      if (!response.body) throw new Error("No response body — streaming not supported.");

      const reader = response.body.getReader();
      readerRef.current = reader;
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const frames = buffer.split('\n\n');
        buffer = frames.pop() ?? '';

        for (const frame of frames) {
          for (const line of frame.split('\n')) {
            if (!line.startsWith('data: ')) continue;
            let event: { type: string; text?: string; error?: RawError; errors?: RawError[]; phase?: string; success?: boolean };
            try {
              event = JSON.parse(line.slice(6));
            } catch {
              continue;
            }

            if (event.type === 'output') {
              setConsoleOutput(prev => prev + (event.text ?? ''));
            } else if (event.type === 'input_needed') {
              setNeedsInput(true);
            } else if (event.type === 'error') {
              setErrors([formatRuntimeError(event.error ?? {})]);
              setErrorPhase("Runtime");
            } else if (event.type === 'compile_error') {
              const phase = event.phase || "Unknown";
              let formatted: FormattedError[] = [];
              if (phase === "Lexical") {
                formatted = (event.errors ?? []).map(e => formatLexicalError(e));
              } else if (phase === "Syntax") {
                formatted = (event.errors ?? []).map(e => formatSyntaxError(e, code));
              } else if (phase === "Semantic") {
                formatted = (event.errors ?? []).map(e => formatSemanticError(e));
              } else {
                formatted = (event.errors ?? []).map(e => ({
                  line: e.line || "-", col: e.col || "-",
                  errorType: phase + " Error",
                  headerStr: e.message || "Unknown error",
                  sourceCode: null,
                  expectedStr: e.message || "",
                  isStructured: true as const,
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
      if ((err as Error).name !== 'AbortError') {
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
    if (readerRef.current) {
      try { readerRef.current.cancel(); } catch {}
    }
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
  const handleResizeMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    const onMouseMove = (moveEvent: MouseEvent) => {
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
  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const value = inputValue;
      setInputValue("");
      setNeedsInput(false);
      setConsoleOutput(prev => prev + value + '\n');
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
  const c = isDarkMode ? {
    success:     '#4ade80',
    errorCount:  '#f87171',
    location:    '#9ca3af',
    divider:     '#475569',
    errorHeader: '#f87171',
    sourceLine:  '#94a3b8',
    caret:       '#94a3b8',
    description: '#cbd5e1',
    rowBorder:   'rgba(255,255,255,0.08)',
    plainText:   '#e5e7eb',
    placeholder: '#6b7280',
  } : {
    success:     '#16a34a',
    errorCount:  '#dc2626',
    location:    '#64748b',
    divider:     '#94a3b8',
    errorHeader: '#dc2626',
    sourceLine:  '#475569',
    caret:       '#64748b',
    description: '#374151',
    rowBorder:   'rgba(0,0,0,0.08)',
    plainText:   '#1e293b',
    placeholder: '#64748b',
  };

  const ErrorList = ({ errors: errs, phaseName }: { errors: FormattedError[]; phaseName: string }) => {
    if (errs.length === 0) {
      return (
        <div style={{ fontSize: '0.85rem', color: c.success, fontWeight: 'bold', fontVariantLigatures: 'none' }}>
          ✓ No errors found. Program compiled and executed successfully.
        </div>
      );
    }
    return (
      <div style={{ fontSize: '0.85rem', fontVariantLigatures: 'none' }}>
        <div style={{ fontWeight: 'bold', color: c.errorCount, marginBottom: '10px', fontSize: '0.9rem' }}>
          ✗ Found {errs.length} {phaseName} Error{errs.length !== 1 ? 's' : ''}
        </div>
        {errs.map((err, i) => (
          <div key={i} style={{ marginBottom: '14px', paddingBottom: '10px', borderBottom: `1px solid ${c.rowBorder}` }}>
            {err.isStructured ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'baseline' }}>
                  <span style={{ color: c.location, minWidth: '110px', flexShrink: 0, fontSize: '0.8rem' }}>
                    Line {err.line}, Col {err.col}
                  </span>
                  <span style={{ color: c.divider, fontSize: '0.8rem' }}>│</span>
                  <span style={{ color: c.errorHeader, fontWeight: 'bold' }}>{err.headerStr}</span>
                </div>
                {err.sourceCode && (
                  <>
                    <div style={{ marginLeft: '130px', color: c.sourceLine, fontStyle: 'italic', fontSize: '0.82rem', whiteSpace: 'pre' }}>
                      {'→ '}{err.sourceCode}
                    </div>
                    {err.col !== "-" && err.col !== undefined && !isNaN(Number(err.col)) && (
                      <div style={{ marginLeft: '130px', color: c.caret, fontSize: '0.82rem', whiteSpace: 'pre' }}>
                        {'  ' + ' '.repeat(Math.max(0, Number(err.col) - 1 - (err.leadingSpaces || 0))) + '^'}
                      </div>
                    )}
                  </>
                )}
                {err.expectedStr && (
                  <div style={{ marginLeft: '130px', color: c.description, fontSize: '0.82rem' }}>
                    {err.expectedStr}
                  </div>
                )}
              </div>
            ) : (
              <div style={{ display: 'flex', gap: '10px', color: c.plainText }}>
                <span style={{ color: c.location, minWidth: '110px', flexShrink: 0 }}>
                  Line {err.line || '-'}, Col {err.col || '-'}
                </span>
                <span style={{ color: c.divider }}>│</span>
                <span style={{ whiteSpace: 'pre-wrap' }}>{err.message || "Unknown error"}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  // ==========================================
  // --- RENDER ---
  // ==========================================
  return (
    <div className="container">
      <header className="header">
        <div className="header-left">
          <Image src="/SeaStack_Logo.png" alt="Logo" width={30} height={30} className="logo" />
          <span className="title">SeaStack</span>
          <nav className="main-nav">
            <ul>
              <li>
                {isRunning ? (
                  <GooeyButton onClick={handleStop} style={{ borderColor: '#e74c3c' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Square size={10} fill="currentColor" />
                      Stop
                    </span>
                  </GooeyButton>
                ) : (
                  <GooeyButton onClick={handleRun} disabled={!code.trim()}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Play size={10} fill="currentColor" />
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
          <div style={{ display: 'flex', gap: '4px' }}>
            <GooeyButton onClick={handleFileBtnClick}>
              <FolderOpen size={15} />
            </GooeyButton>
            <GooeyButton onClick={handleSaveFile}>
              <Download size={15} />
            </GooeyButton>
          </div>

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
                  <Fish size={15} className="tab-icon" />
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
          </div>

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
              {errors.length === 0 && !isRunning && !errorPhase ? (
                <div style={{ fontSize: '0.85rem', color: c.placeholder, fontStyle: 'italic', fontVariantLigatures: 'none' }}>
                  Press Run to compile and execute your SeaStack program.
                </div>
              ) : errors.length === 0 ? (
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
          <div className="console-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}>
            {/* Console Header */}
            <div style={{
              backgroundColor: '#0C2B4E',
              color: '#ffffff',
              padding: '0 15px',
              height: '42px',
              fontWeight: '500',
              fontSize: '0.9rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              flexShrink: 0,
            }}>
              <SquareTerminal size={16} />
              Output Console
            </div>

            {/* Console Body */}
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
                backgroundColor: isDarkMode ? 'rgba(17, 25, 40, 0.59)' : 'rgba(255, 255, 255, 0.78)',
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
                autoComplete="off"
                autoCorrect="off"
                autoCapitalize="off"
                spellCheck={false}
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
