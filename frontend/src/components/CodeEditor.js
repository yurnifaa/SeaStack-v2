"use client";
import React from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { createTheme } from '@uiw/codemirror-themes';
import { EditorView } from '@codemirror/view'; 

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

const seaDark = createTheme({
  theme: 'dark',
  settings: {
    background: '#1a202c',       
    foreground: '#e2e8f0',       
    caret: '#ffffff',
    selection: '#3e4c62',        
    selectionMatch: '#3e4c62',
    gutterBackground: '#2d3748', 
    gutterForeground: '#a0aec0', 
  },
});

const lightHighlightStyle = EditorView.theme({
  ".cm-activeLine": { backgroundColor: "#eaeaea !important" },
  ".cm-activeLineGutter": { backgroundColor: "transparent !important" }
});

const darkHighlightStyle = EditorView.theme({
  ".cm-activeLine": { backgroundColor: "#252f3f !important" },
  ".cm-activeLineGutter": { backgroundColor: "transparent !important" }
});

export default function SeaStackEditor({ code, setCode, isDarkMode }) {
  
  const onChange = React.useCallback((val) => {
    setCode(val);
  }, [setCode]);

  return (
    <div className="code-editor-area" style={{ display: 'flex', flexDirection: 'column', flexGrow: 1, overflow: 'hidden' }}>
      <CodeMirror
        key={isDarkMode ? "dark-editor" : "light-editor"} 
        // -----------------------
        
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
        style={{ height: '100%', fontSize: '16px' }}
      />
    </div>
  );
}