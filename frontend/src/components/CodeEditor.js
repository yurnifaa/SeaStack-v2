"use client";
import React from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { createTheme } from '@uiw/codemirror-themes';
import { EditorView } from '@codemirror/view'; 

// --- Light Theme ---
const seaLight = createTheme({
  theme: 'light',
  settings: {
    background: 'transparent',
    foreground: '#000000',
    caret: '#0C2B4E',
    selection: '#bae6fd',
    selectionMatch: '#bae6fd',
    gutterBackground: 'transparent',
    gutterForeground: '#424f61',
  },
});

// --- Dark Theme ---
const seaDark = createTheme({
  theme: 'dark',
  settings: {   
    background: 'transparent',
    foreground: '#e2e8f0',       
    caret: '#fbca1f',
    selection: 'rgba(41, 128, 185, 0.3)',
    selectionMatch: 'rgba(41, 128, 185, 0.5)',
    gutterBackground: 'transparent',
    gutterForeground: '#5c7c9c', 
  },
});

// --- Highlighting Styles ---
const lightHighlightStyle = EditorView.theme({
  "&": { backgroundColor: "transparent !important" },
  ".cm-activeLine": { backgroundColor: "rgba(255, 255, 255, 0.4) !important" },
  ".cm-activeLineGutter": { backgroundColor: "transparent !important" },
  ".cm-gutters": { backgroundColor: "transparent !important", borderRight: "none" }
});

const darkHighlightStyle = EditorView.theme({
  "&": { backgroundColor: "transparent !important" },
  ".cm-activeLine": { backgroundColor: "rgba(41, 128, 185, 0.15) !important" },
  ".cm-activeLineGutter": { backgroundColor: "transparent !important" },
  ".cm-gutters": { backgroundColor: "transparent !important", borderRight: "none" }
});

export default function SeaStackEditor({ code, setCode, isDarkMode }) {
  
  const onChange = React.useCallback((val) => {
    setCode(val);
  }, [setCode]);

  return (
    <div className="code-editor-area" style={{ display: 'flex', flexDirection: 'column', flexGrow: 1, overflow: 'hidden' }}>
      <CodeMirror
        key={isDarkMode ? "dark-editor" : "light-editor"} 
        value={code}
        height="100%"
        theme={isDarkMode ? seaDark : seaLight} 
        extensions={[isDarkMode ? darkHighlightStyle : lightHighlightStyle]} 
        onChange={onChange}
        basicSetup={{
          lineNumbers: true,
          foldGutter: true,
          highlightActiveLine: true, 
        }}
        style={{ height: '100%', fontSize: '15px', backgroundColor: 'transparent' }} 
      />
    </div>
  );
}