import { StreamLanguage } from "@codemirror/language";

interface SeaRule {
  regex: RegExp;
  token: string;
  next?: string;
}

interface SeaState {
  rules: SeaRule[];
  curState: string;
}

interface SeaGrammar {
  [key: string]: SeaRule[];
}

const seaStackGrammar: SeaGrammar = {
  start: [
    // Comments (Grey)
    { regex: /~\(/, token: "comment", next: "multiLineComment" },
    { regex: /~.*/, token: "comment" },

    // Strings "..." and Chars '...' (Green)
    { regex: /"(?:[^\\]|\\.)*?(?:"|$)/, token: "string" },
    { regex: /'(?:[^\\]|\\.)*?(?:'|$)/, token: "string" },

    // Numbers (Blue)
    { regex: /\d+(\.\d+)?/, token: "number" },

    // Operators & Symbols
    { regex: /[+\-*\/%^=<>!&|]+/, token: "operator" },
    { regex: /[(){}\[\]]/, token: "punctuation" },
    { regex: /!!/, token: "punctuation" },

    // Reserved Words (Red)
    {
      regex: /\b(?:ABYSS|BOOL|COIN|DIME|PARCH|SCROLL)\b/,
      token: "type"
    },
    // Keywords (Yellow)
    {
      regex: /\b(?:ADRIFT|AHOY|ASK|AYE|BACK|CHART|COURSE|DROP|DROPLOOK|ECHO|HAUL-HEAVE|HEAVE|HOIST|LAND|LOCKE|LOOK|MAST|NAY|SAIL)\b/,
      token: "keyword"
    },

    // Identifiers (Purple)
    { regex: /[a-z][a-z0-9_]*/, token: "variable" },
  ],

  // Multi-line comment state
  multiLineComment: [
    { regex: /.*?\)\~/, token: "comment", next: "start" }, // End with )~
    { regex: /.*/, token: "comment" } // Consume line
  ]
};

// Export the Language Support
export const seaStackLanguage = StreamLanguage.define<SeaState>({
  token: (stream, state) => {
    for (const rule of state.rules) {
      const match = stream.match(rule.regex);
      if (match) {
        if (rule.next) {
          state.curState = rule.next;
          state.rules = seaStackGrammar[rule.next];
        }
        return rule.token;
      }
    }
    stream.next();
    return null;
  },
  startState: () => ({ rules: seaStackGrammar.start, curState: "start" }),
});
