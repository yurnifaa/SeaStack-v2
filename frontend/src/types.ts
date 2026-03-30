export interface Tab {
  id: number;
  fileName: string;
  code: string;
}

export interface RawError {
  line?: string | number;
  col?: string | number;
  message?: string;
  found?: string;
  expected?: string[];
  error_header?: string;
  error_type?: string;
  actual_line?: string;
}

export interface StructuredError {
  isStructured: true;
  line: string | number;
  col: string | number;
  errorType: string;
  headerStr: string;
  sourceCode: string | null;
  leadingSpaces?: number;
  expectedStr: string;
}

export interface UnstructuredError {
  isStructured: false;
  line?: string | number;
  col?: string | number;
  message?: string;
}

export type FormattedError = StructuredError | UnstructuredError;
