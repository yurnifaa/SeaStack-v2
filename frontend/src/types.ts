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

export interface QuadRow {
  index:   number;
  op:      string;
  arg1:    string;
  arg2:    string;
  result:  string;
  comment: string;
  line:    number | null;
}

export interface PassSnapshot {
  pass_name:   string;
  stats_delta: Record<string, number>;
  quad_count:  number;
}

export interface OptimizerStats {
  const_folded:     number;
  const_propagated: number;
  copy_propagated:  number;
  strength_reduced: number;
  dead_eliminated:  number;
  jumps_optimized:  number;
}

export interface TacData {
  rawQuads:       QuadRow[];
  optimizedQuads: QuadRow[];
  passSnapshots:  PassSnapshot[];
  optimizerStats: OptimizerStats;
}
