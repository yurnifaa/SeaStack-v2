"use client";
import React from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { createTheme } from '@uiw/codemirror-themes';
import { EditorView } from '@codemirror/view'; 

// 1. DEFINE THE GLASS STYLING
const glassStyle = EditorView.theme({
  // --- EDITOR CONTAINER ---
  "&": {
    height: "100%",
    backgroundColor: "transparent !important"
  },
  
  // --- THE GUTTER (Side Strip) ---
  ".cm-gutters": {
    backgroundColor: "rgba(0, 0, 0, 0.15) !important", // Slightly clearer
    color: "rgba(255, 255, 255, 0.4)", 
    border: "none",
    borderRight: "1px solid rgba(255, 255, 255, 0.05)",
  },

  // --- INDIVIDUAL LINE NUMBERS ---
  ".cm-gutterElement": {
    padding: "0 15px 0 10px !important",
    display: "flex",
    alignItems: "center",
    justifyContent: "flex-end",
    fontFamily: '"Fira Code", monospace',
    transition: "color 0.2s ease", // Smooth transition when moving lines
  },

  // --- THE ACTIVE LINE NUMBER ---
  ".cm-activeLineGutter": {
    backgroundColor: "transparent !important",
    color: "#fbca1f !important", // Bright Yellow
    fontWeight: "700",
    position: "relative",
    textShadow: "0 0 10px rgba(251, 202, 31, 0.5)", // Text Glow
  },

  // --- THE GLOW BAR (Redesigned) ---
  // Instead of a full-height border, we make a floating 'pill'
  ".cm-activeLineGutter::before": {
    content: '""',
    position: "absolute",
    left: "0",
    top: "50%",
    transform: "translateY(-50%)", // Center vertically
    height: "60%", // Don't span the full height (looks cleaner)
    width: "4px",
    backgroundColor: "#fbca1f",
    borderRadius: "0 4px 4px 0", // Rounded edge
    boxShadow: "2px 0 12px rgba(251, 202, 31, 0.8)", // Intense Glow
  },

  // --- THE ACTIVE CODE LINE BACKGROUND ---
  // A gradient looks much better than a solid color on dark backgrounds
  ".cm-activeLine": {
    backgroundImage: "linear-gradient(to right, rgba(251, 202, 31, 0.1), rgba(251, 202, 31, 0.05) 30%, transparent) !important",
    backgroundColor: "transparent !important", 
    borderLeft: "none", // Clean look
  },

  // --- CURSOR ---
  ".cm-content": {
    caretColor: "#fbca1f !important",
    fontFamily: '"Fira Code", monospace',
  },
  
  // --- SELECTION (When highlighting text) ---
  ".cm-selectionBackground, ::selection": {
      backgroundColor: "rgba(251, 202, 31, 0.2) !important"
  },

  // --- SCROLLBARS ---
  ".cm-scroller::-webkit-scrollbar": { width: "8px", height: "8px" },
  ".cm-scroller::-webkit-scrollbar-track": { background: "transparent" },
  ".cm-scroller::-webkit-scrollbar-thumb": { 
      backgroundColor: "rgba(255, 255, 255, 0.1)", 
      borderRadius: "4px" 
  },
  ".cm-scroller::-webkit-scrollbar-thumb:hover": { 
      backgroundColor: "rgba(255, 255, 255, 0.2)" 
  }
});

// 2. Base Themes (Updated for Transparency)
const seaLight = createTheme({
  theme: 'light',
  settings: {
    background: '#fafafa',
    foreground: '#000000',
    caret: '#000000',
    selection: '#d7d4f0',
    selectionMatch: '#d7d4f0',
    gutterBackground: '#fafafa',
    gutterForeground: '#000000',
  },
});

// For Dark Mode, we set basic colors, but `glassStyle` will override most structural CSS
const seaDark = createTheme({
  theme: 'dark',
  settings: {
    background: 'transparent', // Important!
    foreground: '#e2e8f0',       
    caret: '#fbca1f',
    selection: 'rgba(251, 202, 31, 0.2)', // Yellow selection tint        
    selectionMatch: 'rgba(251, 202, 31, 0.3)',
    gutterBackground: 'transparent', 
    gutterForeground: 'rgba(255,255,255,0.3)', 
  },
});


export default function SeaStackEditor({ code, setCode, isDarkMode }) {
  
  const onChange = React.useCallback((val) => {
    setCode(val);
  }, [setCode]);

  // Combine extensions
  // If Dark Mode: Use seaDark settings + our custom Glass CSS
  // If Light Mode: Use seaLight settings (Standard look)
  const currentExtensions = isDarkMode 
    ? [glassStyle] 
    : [];

  return (
    <div className="code-editor-area" style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        flexGrow: 1, 
        overflow: 'hidden',
        // Optional: Force rounded corners on the editor itself if needed
        borderRadius: '0 0 12px 12px' 
    }}>
      <CodeMirror
        key={isDarkMode ? "dark-editor" : "light-editor"} 
        value={code}
        height="100%"
        theme={isDarkMode ? seaDark : seaLight} 
        
        // Merge the glass styles into extensions
        extensions={currentExtensions} 
        
        onChange={onChange}
        basicSetup={{
          lineNumbers: true,
          foldGutter: true,
          highlightActiveLine: true, 
          highlightActiveLineGutter: true, // MUST BE TRUE for custom gutter CSS to work
        }}
        style={{ height: '100%', fontSize: '14px' }}
      />
    </div>
  );
}