"use client";
import React from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { createTheme } from '@uiw/codemirror-themes';
import { tags as t } from '@lezer/highlight';
import { seaStackLanguage } from './seaStackLang';
import { EditorView } from '@codemirror/view';

interface SeaStackEditorProps {
  code: string;
  setCode: (val: string) => void;
  isDarkMode: boolean;
}

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
    { tag: t.typeName, color: '#1d4ed8', fontWeight: 'bold' },      // Datatypes: Deep Blue
    { tag: t.keyword, color: '#c2410c', fontWeight: 'bold' },       // Keywords: Deep Orange
    { tag: t.comment, color: '#6b7280', fontWeight: 'bold' },       // Comments: Medium Grey
    { tag: t.string, color: '#15803d', fontWeight: 'bold' },        // Strings: Deep Green
    { tag: t.number, color: '#1d4ed8', fontWeight: 'bold' },        // Numbers: Deep Blue
    { tag: t.variableName, color: '#111827', fontWeight: 'semibold' },  // Identifiers: Near Black
    { tag: t.operator, color: '#6d28d9', fontWeight: 'black' },      // Operators: Deep Purple
    { tag: t.punctuation, color: '#374151', fontWeight: 'bold' },     // Punctuation: Dark Grey
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
    { tag: t.typeName, color: '#6675ff', fontWeight: 'bold' },      // Datatypes: Blue
    { tag: t.keyword, color: '#cc91ff', fontWeight: 'bold' },       // Keywords: Purple
    { tag: t.comment, color: '#9CA3AF', fontWeight: 'bold' },       // Comments: Grey
    { tag: t.string, color: '#7abdff', fontWeight: 'bold' },        // Strings: Light Blue
    { tag: t.number, color: '#93C5FD', fontWeight: 'bold' },        // Numbers: Soft Blue
    { tag: t.variableName, color: '#E2E8F0' },                      // Identifiers: White
    { tag: t.operator, color: '#F87171', fontWeight: 'bold' },      // Operators: Soft Red
    { tag: t.punctuation, color: '#E2E8F0', fontWeight: 'bold' },   // Punctuation: Dark Grey 
  ],
});

// --- Highlighting Styles ---
const scrollbarBase = {
  ".cm-scroller": { overflow: "auto" },
  ".cm-scroller::-webkit-scrollbar": { width: "8px", height: "8px" },
  ".cm-scroller::-webkit-scrollbar-track": { background: "transparent" },
  ".cm-scroller::-webkit-scrollbar-thumb": { background: "transparent", borderRadius: "4px" },
  ".cm-scroller::-webkit-scrollbar-corner": { background: "transparent" },
  "&:hover .cm-scroller::-webkit-scrollbar-thumb": { background: "rgba(100,116,139,0.45)" },
  "&:hover .cm-scroller::-webkit-scrollbar-thumb:hover": { background: "rgba(100,116,139,0.7)" },
};

const lightHighlightStyle = EditorView.theme({
  "&": { backgroundColor: "transparent !important" },
  ".cm-activeLine": { backgroundColor: "rgba(59, 130, 246, 0.08) !important" },
  ".cm-activeLineGutter": { backgroundColor: "rgba(59, 130, 246, 0.06) !important" },
  ".cm-gutters": { backgroundColor: "transparent !important", borderRight: "1px solid rgba(0,0,0,0.07)" },
  ...scrollbarBase,
});

const darkHighlightStyle = EditorView.theme({
  "&": { backgroundColor: "transparent !important" },
  ".cm-activeLine": { backgroundColor: "rgba(41, 128, 185, 0.15) !important" },
  ".cm-activeLineGutter": { backgroundColor: "transparent !important" },
  ".cm-gutters": { backgroundColor: "transparent !important", borderRight: "none" },
  ...scrollbarBase,
});

export default function SeaStackEditor({ code, setCode, isDarkMode }: SeaStackEditorProps) {

  const onChange = React.useCallback((val: string) => {
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
