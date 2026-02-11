"use client";
import React from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { createTheme } from '@uiw/codemirror-themes';
import { tags as t } from '@lezer/highlight';
import { seaStackLanguage } from './seaStackLang'; 

// --- Light Mode Palette ---
const seaLight = createTheme({
  theme: 'light',
  settings: {
    background: 'transparent',
    foreground: '#000000',
    caret: '#0C2B4E',
    selection: '#73a5bf',
    selectionMatch: '#73a5bf',
    gutterBackground: 'transparent',
    gutterForeground: '#64748b',
  },
  styles: [
    { tag: t.typeName, color: '#db1616' },      // Datatypes: Light Red
    { tag: t.keyword, color: '#d16619' },       // Keywords: Soft Orange
    { tag: t.comment, color: '#9CA3AF' },       // Comments: Grey
    { tag: t.string, color: '#119141' },        // Strings: Soft Green
    { tag: t.number, color: '#2563EB' },        // Numbers: Soft Blue
    { tag: t.variableName, color: '#000000' },  // Identifiers: Black
    { tag: t.operator, color: '#7518c9' },      // Operators: Purple
    { tag: t.punctuation, color: '#000000' },   
  ],
});

// --- Dark Mode Palette ---
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
  styles: [
    { tag: t.typeName, color: '#F87171' },      // Datatypes: Light Red
    { tag: t.keyword, color: '#FDE047' },       // Keywords: Soft Yellow
    { tag: t.comment, color: '#9CA3AF' },       // Comments: Grey
    { tag: t.string, color: '#86EFAC' },        // Strings: Light Soft Green
    { tag: t.number, color: '#93C5FD' },        // Numbers: Soft Blue
    { tag: t.variableName, color: '#E2E8F0' },  // Identifiers: White/Grey
    { tag: t.operator, color: '#C491FA' },      // Operators: Soft Purple
    { tag: t.punctuation, color: '#E2E8F0' },
  ],
});

// --- Highlighting Styles ---
import { EditorView } from '@codemirror/view'; 

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
        extensions={[
            isDarkMode ? darkHighlightStyle : lightHighlightStyle,
            seaStackLanguage
        ]} 
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