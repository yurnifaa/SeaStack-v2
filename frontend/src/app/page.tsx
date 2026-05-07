"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import Image from "next/image";
import { Fish, Play, Square, FolderOpen, Download, SquareTerminal, Table2, TableProperties } from "lucide-react";
import SeaStackEditor from "../components/CodeEditor";
import { simplifyRuntimeMessage } from "../utils/runtimeErrorMsg";
import type { Tab, FormattedError, RawError, TacData } from "../types";

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

const TAC_CATEGORIES: Record<string, string> = {
  ADD:'arith', SUB:'arith', MUL:'arith', DIV:'arith', MOD:'arith', POW:'arith',
  UNARY_NEG:'arith', LITERAL:'arith',
  LABEL:'ctrl', JUMP:'ctrl', JUMP_FALSE:'ctrl', JUMP_TRUE:'ctrl', BREAK:'ctrl', CONTINUE:'ctrl',
  LT:'cmp', GT:'cmp', LE:'cmp', GE:'cmp', EQ:'cmp', NE:'cmp',
  LOG_AND:'cmp', LOG_OR:'cmp', LOG_NOT:'cmp', LOG_DNOT:'cmp',
  INPUT:'io', OUTPUT:'io',
  DECL_VAR:'decl', DECL_CONST:'decl', DECL_ARR:'decl',
  DECL_STRUCT_TYPE:'decl', DECL_STRUCT_VAR:'decl', PARAM_DECL:'decl',
  ARR_INIT_1D:'decl', ARR_INIT_2D:'decl', STRUCT_INIT:'decl',
  FUNC_BEGIN:'func', FUNC_END:'func', AHOY_BEGIN:'func', AHOY_END:'func',
  PROG_START:'func', PROG_END:'func',
  ARG:'func', CALL:'func', CALL_VOID:'func', RETURN:'func', RETURN_VOID:'func',
  ASSIGN:'assign', COMP_ASSIGN:'assign',
  ASSIGN_ARR:'assign', ASSIGN_ARR2:'assign', ASSIGN_MEMBER:'assign',
  LOAD_ARR:'assign', LOAD_ARR2:'assign', LOAD_MEMBER:'assign',
  UNARY_INC:'assign', UNARY_DEC:'assign',
  CONCAT:'str', SCROLL_CHAR:'str',
};

function getTacCategory(op: string): string {
  return TAC_CATEGORIES[op] ?? 'default';
}

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

  // Token table state
  const [tokenRows, setTokenRows] = useState<{ lexeme: string; token: string }[]>([]);
  const [rightTab, setRightTab] = useState<'console' | 'tokens' | 'tac'>('console');
  const [isTokenizing, setIsTokenizing] = useState(false);

  // TAC simulation state
  const [tacData, setTacData] = useState<TacData | null>(null);
  const [tacView, setTacView] = useState<'raw' | 'optimized'>('optimized');
  const [isTacLoading, setIsTacLoading] = useState(false);

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
  // --- TOKENIZE (lexer only, always runs) ---
  // ==========================================
  const fetchTokens = async (sourceCode: string) => {
    setIsTokenizing(true);
    try {
      const res = await fetch(`${API_URL}/api/tokenize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: sourceCode }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.tokens) setTokenRows(data.tokens);
      }
    } catch {
      // silently ignore — tokenize is best-effort
    } finally {
      setIsTokenizing(false);
    }
  };

  // ==========================================
  // --- TAC (IR + optimizer visualization) ---
  // ==========================================
  const fetchTac = async (sourceCode: string) => {
    setIsTacLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/tac`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: sourceCode }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.success) {
          setTacData({
            rawQuads:       data.raw_quads,
            optimizedQuads: data.optimized_quads,
            passSnapshots:  data.pass_snapshots,
            optimizerStats: data.optimizer_stats,
          });
        }
      }
    } catch {
      // silently ignore — tac is best-effort
    } finally {
      setIsTacLoading(false);
    }
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
    setTokenRows([]);
    setTacData(null);
    setIsRunning(true);

    // Always tokenize + generate TAC so both side tabs are populated even if compile fails
    fetchTokens(code);
    fetchTac(code);

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
          No errors found. Program compiled and executed successfully.
        </div>
      );
    }
    return (
      <div style={{ fontSize: '0.85rem', fontVariantLigatures: 'none' }}>
        <div style={{ fontWeight: 'bold', color: c.errorCount, marginBottom: '10px', fontSize: '0.9rem' }}>
          Found {errs.length} {phaseName} Error{errs.length !== 1 ? 's' : ''}
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
          <Image
            src="/SeaStack_Logo.png"
            alt="Logo"
            width={30}
            height={30}
            className="logo"
          />
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

        {/* Right Panel — Output Console + Token Table */}
        <div className="panel panel-right">
          <div className="console-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}>

            {/* Right Panel Tab Bar */}
            <div style={{
              backgroundColor: '#0C2B4E',
              display: 'flex',
              alignItems: 'stretch',
              flexShrink: 0,
              height: '42px',
            }}>
              <button
                onClick={() => setRightTab('console')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '7px',
                  padding: '0 16px',
                  background: 'none',
                  border: 'none',
                  borderBottom: rightTab === 'console' ? '2px solid #3498db' : '2px solid transparent',
                  color: rightTab === 'console' ? '#ffffff' : 'rgba(255,255,255,0.55)',
                  fontWeight: rightTab === 'console' ? '600' : '400',
                  fontSize: '0.88rem',
                  cursor: 'pointer',
                  fontFamily: 'inherit',
                  transition: 'color 0.15s',
                  whiteSpace: 'nowrap',
                }}
              >
                <SquareTerminal size={15} />
                Output Console
              </button>
              <button
                onClick={() => setRightTab('tokens')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '7px',
                  padding: '0 16px',
                  background: 'none',
                  border: 'none',
                  borderBottom: rightTab === 'tokens' ? '2px solid #3498db' : '2px solid transparent',
                  color: rightTab === 'tokens' ? '#ffffff' : 'rgba(255,255,255,0.55)',
                  fontWeight: rightTab === 'tokens' ? '600' : '400',
                  fontSize: '0.88rem',
                  cursor: 'pointer',
                  fontFamily: 'inherit',
                  transition: 'color 0.15s',
                  whiteSpace: 'nowrap',
                }}
              >
                <Table2 size={15} />
                Token Table
                {tokenRows.length > 0 && (
                  <span style={{
                    backgroundColor: '#3498db',
                    color: '#fff',
                    borderRadius: '999px',
                    padding: '1px 6px',
                    fontSize: '0.7rem',
                    fontWeight: 'bold',
                    marginLeft: '2px',
                  }}>
                    {tokenRows.length}
                  </span>
                )}
              </button>

              {/* TAC Simulation tab button */}
              <button
                onClick={() => setRightTab('tac')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '7px',
                  padding: '0 16px',
                  background: 'none',
                  border: 'none',
                  borderBottom: rightTab === 'tac' ? '2px solid #8b5cf6' : '2px solid transparent',
                  color: rightTab === 'tac' ? '#ffffff' : 'rgba(255,255,255,0.55)',
                  fontWeight: rightTab === 'tac' ? '600' : '400',
                  fontSize: '0.88rem',
                  cursor: 'pointer',
                  fontFamily: 'inherit',
                  transition: 'color 0.15s',
                  whiteSpace: 'nowrap',
                }}
              >
                <TableProperties size={15} />
                TAC Simulation
                {tacData && (
                  <span style={{
                    backgroundColor: '#8b5cf6',
                    color: '#fff',
                    borderRadius: '999px',
                    padding: '1px 6px',
                    fontSize: '0.7rem',
                    fontWeight: 'bold',
                    marginLeft: '2px',
                  }}>
                    {tacView === 'raw' ? tacData.rawQuads.length : tacData.optimizedQuads.length}
                  </span>
                )}
              </button>
            </div>

            {/* Console Body */}
            <div
              style={{
                display: rightTab === 'console' ? 'block' : 'none',
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

            {/* Token Table Body */}
            <div
              style={{
                display: rightTab === 'tokens' ? 'flex' : 'none',
                flex: 1,
                flexDirection: 'column',
                overflowY: 'auto',
                overflowX: 'auto',
                backgroundColor: isDarkMode ? 'rgba(17, 25, 40, 0.59)' : 'rgba(255, 255, 255, 0.78)',
                backdropFilter: 'blur(16px) saturate(180%)',
                WebkitBackdropFilter: 'blur(16px) saturate(180%)',
              }}
            >
              {tokenRows.length === 0 ? (
                <span style={{
                  color: '#6b7280',
                  fontStyle: 'italic',
                  fontFamily: '"Fira Code", monospace',
                  fontSize: '1rem',
                  padding: '12px 15px',
                }}>
                  {isTokenizing ? "Tokenizing..." : "Run a program to see its tokens here."}
                </span>
              ) : (
                <table style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  fontFamily: '"Fira Code", monospace',
                  fontVariantLigatures: 'none',
                  fontSize: '1rem',
                }}>
                  <thead>
                    <tr style={{
                      position: 'sticky',
                      top: 0,
                      backgroundColor: isDarkMode ? '#0f1f35' : '#dbeafe',
                      zIndex: 1,
                    }}>
                      <th style={{
                        padding: '8px 16px',
                        textAlign: 'center',
                        fontWeight: '600',
                        color: isDarkMode ? '#93c5fd' : '#1e40af',
                        borderBottom: `1px solid ${isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                        width: '50%',
                      }}>
                        Lexeme
                      </th>
                      <th style={{
                        padding: '8px 16px',
                        textAlign: 'center',
                        fontWeight: '600',
                        color: isDarkMode ? '#93c5fd' : '#1e40af',
                        borderBottom: `1px solid ${isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                        width: '50%',
                      }}>
                        Token
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {tokenRows.map((row, i) => (
                      <tr
                        key={i}
                        style={{
                          backgroundColor: i % 2 === 0
                            ? 'transparent'
                            : isDarkMode ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)',
                          borderBottom: `1px solid ${isDarkMode ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}`,
                        }}
                      >
                        <td style={{
                          padding: '5px 16px',
                          color: isDarkMode ? '#e2e8f0' : '#1e293b',
                        }}>
                          {row.lexeme}
                        </td>
                        <td style={{
                          padding: '5px 16px',
                          color: isDarkMode ? '#7dd3fc' : '#1d4ed8',
                        }}>
                          {row.token}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            {/* TAC Simulation Body */}
            <div
              style={{
                display: rightTab === 'tac' ? 'flex' : 'none',
                flex: 1,
                flexDirection: 'column',
                overflowY: 'hidden',
                backgroundColor: isDarkMode ? 'rgba(17, 25, 40, 0.59)' : 'rgba(255, 255, 255, 0.78)',
                backdropFilter: 'blur(16px) saturate(180%)',
                WebkitBackdropFilter: 'blur(16px) saturate(180%)',
              }}
            >
              {!tacData ? (
                <span style={{
                  color: '#6b7280',
                  fontStyle: 'italic',
                  fontFamily: '"Fira Code", monospace',
                  fontSize: '1rem',
                  padding: '12px 15px',
                }}>
                  {isTacLoading ? 'Generating TAC...' : 'Run a program to see its three-address code here.'}
                </span>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>

                  {/* Optimizer stats chips
                  <div className="tac-stats-bar">
                    {([
                      { label: 'Folded',     key: 'const_folded'     as const, color: '#3b82f6' },
                      { label: 'Propagated', key: 'const_propagated' as const, color: '#8b5cf6' },
                      { label: 'Copied',     key: 'copy_propagated'  as const, color: '#06b6d4' },
                      { label: 'Reduced',    key: 'strength_reduced' as const, color: '#f59e0b' },
                      { label: 'Eliminated', key: 'dead_eliminated'  as const, color: '#ef4444' },
                      { label: 'Jumps',      key: 'jumps_optimized'  as const, color: '#10b981' },
                    ] as { label: string; key: keyof typeof tacData.optimizerStats; color: string }[]).map(({ label, key, color }) => (
                      <span key={key} className="tac-stat-chip" style={{ borderColor: color, color: isDarkMode ? '#e2e8f0' : '#1e293b' }}>
                        <span style={{ color, fontWeight: 700 }}>{tacData.optimizerStats[key]}</span>{' '}{label}
                      </span>
                    ))}
                  </div> */}

                  {/* Per-pass breakdown
                  {tacData.passSnapshots.length > 0 && (
                    <div className="tac-pass-list">
                      {tacData.passSnapshots.map((snap, i) => {
                        const total = Object.values(snap.stats_delta).reduce((a, b) => a + b, 0);
                        return (
                          <div key={i} className="tac-pass-row" style={{ color: isDarkMode ? '#94a3b8' : '#64748b' }}>
                            <span style={{ color: isDarkMode ? '#e2e8f0' : '#1e293b', fontWeight: 600 }}>{snap.pass_name}</span>
                            <span>— {total} change{total !== 1 ? 's' : ''}</span>
                            <span style={{ marginLeft: 'auto', color: isDarkMode ? '#475569' : '#94a3b8' }}>{snap.quad_count} quads</span>
                          </div>
                        );
                      })}
                    </div>
                  )} */}

                  {/* Sub-tab: Raw IR | Optimized IR */}
                  <div className="tac-subtab-bar">
                    {(['raw', 'optimized'] as const).map(view => (
                      <button
                        key={view}
                        onClick={() => setTacView(view)}
                        className={`tac-subtab-btn${tacView === view ? ' active' : ''}`}
                        style={{
                          color: tacView === view
                            ? (isDarkMode ? '#ffffff' : '#1e293b')
                            : (isDarkMode ? 'rgba(255,255,255,0.45)' : 'rgba(0,0,0,0.45)'),
                          borderBottomColor: tacView === view ? '#8b5cf6' : 'transparent',
                        }}
                      >
                        {view === 'raw' ? 'Raw IR' : 'Optimized IR'}
                        <span className="tac-subtab-count">
                          {view === 'raw' ? tacData.rawQuads.length : tacData.optimizedQuads.length}
                        </span>
                      </button>
                    ))}
                  </div>

                  {/* Quadruple table */}
                  <div className="tac-table-wrapper">
                    <table className="tac-table">
                      <thead>
                        <tr style={{ backgroundColor: isDarkMode ? '#0f1f35' : '#dbeafe' }}>
                          {['#', 'Opcode', 'Arg1', 'Arg2', 'Result', 'Comment'].map(col => (
                            <th key={col} style={{ textAlign: 'center', color: isDarkMode ? '#93c5fd' : '#1e40af' }}>{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {(tacView === 'raw' ? tacData.rawQuads : tacData.optimizedQuads).map((q, i) => (
                          <tr
                            key={i}
                            className={`tac-row tac-row--${getTacCategory(q.op)}`}
                            style={{
                              backgroundColor: i % 2 === 0
                                ? 'transparent'
                                : isDarkMode ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)',
                            }}
                          >
                            <td className="tac-cell tac-cell--index">{q.index}</td>
                            <td className="tac-cell tac-cell--op">{q.op}</td>
                            <td className="tac-cell">{q.arg1}</td>
                            <td className="tac-cell">{q.arg2}</td>
                            <td className="tac-cell">{q.result}</td>
                            <td className="tac-cell tac-cell--comment">{q.comment}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                </div>
              )}
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
