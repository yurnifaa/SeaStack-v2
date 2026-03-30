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
    { tag: t.typeName, color: '#1d4ed8' },      // Datatypes: Deep Blue
    { tag: t.keyword, color: '#c2410c' },       // Keywords: Deep Orange
    { tag: t.comment, color: '#6b7280' },       // Comments: Medium Grey
    { tag: t.string, color: '#15803d' },        // Strings: Deep Green
    { tag: t.number, color: '#1d4ed8' },        // Numbers: Deep Blue
    { tag: t.variableName, color: '#111827' },  // Identifiers: Near Black
    { tag: t.operator, color: '#6d28d9' },      // Operators: Deep Purple
    { tag: t.punctuation, color: '#374151' },
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
    { tag: t.typeName, color: '#6675ff' },      // Datatypes: Blue
    { tag: t.keyword, color: '#cc91ff' },       // Keywords: Purple
    { tag: t.comment, color: '#9CA3AF' },       // Comments: Grey
    { tag: t.string, color: '#7abdff' },        // Strings: Light Blue
    { tag: t.number, color: '#93C5FD' },        // Numbers: Soft Blue
    { tag: t.variableName, color: '#E2E8F0' },  // Identifiers: White
    { tag: t.operator, color: '#F87171' },      // Operators: Soft Red
    { tag: t.punctuation, color: '#E2E8F0' },
  ],
});

// --- Highlighting Styles ---
const lightHighlightStyle = EditorView.theme({
  "&": { backgroundColor: "transparent !important" },
  ".cm-activeLine": { backgroundColor: "rgba(59, 130, 246, 0.08) !important" },
  ".cm-activeLineGutter": { backgroundColor: "rgba(59, 130, 246, 0.06) !important" },
  ".cm-gutters": { backgroundColor: "transparent !important", borderRight: "1px solid rgba(0,0,0,0.07)" }
});

const darkHighlightStyle = EditorView.theme({
  "&": { backgroundColor: "transparent !important" },
  ".cm-activeLine": { backgroundColor: "rgba(41, 128, 185, 0.15) !important" },
  ".cm-activeLineGutter": { backgroundColor: "transparent !important" },
  ".cm-gutters": { backgroundColor: "transparent !important", borderRight: "none" }
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
