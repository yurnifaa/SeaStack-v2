import sys
import os
import json
import threading
import traceback
import re
import io
import queue

# Add project root and backend/ to sys.path for both absolute and bare imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# --- IMPORTS ---
try:
    from backend.lexical.lexer import Lexer
    from backend.syntax.syn_parser import Parser
    from backend.semantic.ast_parser import ASTParser
    from backend.semantic.semantic_analyzer import SemanticAnalyzer
    from backend.codegen.ir_generator import IRGenerator
    from backend.codegen.optimizer import IROptimizer
    from backend.codegen.code_generator import CodeGenerator
except ImportError as e:
    print(f"\n[ERROR] Import Failed! Details: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Suppress "* Serving Flask app" / "* Debug mode" banner
import flask.cli
flask.cli.show_server_banner = lambda *args, **kwargs: None

# Suppress "WARNING: This is a development server. Do not use it in a production deployment."
import logging
class _SuppressDevWarning(logging.Filter):
    def filter(self, record):
        return 'Do not use it in a production deployment' not in record.getMessage()
logging.getLogger('werkzeug').addFilter(_SuppressDevWarning())

# ─── Global state for running programs ───────────────────────────────────────
_running_flags = {}   # session_id → threading.Event  (set = stop requested)
_input_queues  = {}   # session_id → queue.Queue       (frontend → execution thread)


# =============================================================================
#  /api/run  — Full pipeline, streamed as Server-Sent Events (SSE)
#
#  Each SSE frame is:   data: <json>\n\n
#
#  Event shapes sent to the frontend:
#    {"type": "output",        "text":   "..."}           append to console
#    {"type": "input_needed"}                             pause; show input field
#    {"type": "error",         "error":  {...}}           runtime error object
#    {"type": "done",          "success": bool}           program finished
#    {"type": "compile_error", "errors": [...],
#                              "phase":  "..."}           pre-run compile error
# =============================================================================
@app.route('/api/run', methods=['POST'])
def run_code():
    data        = request.json
    code_string = data.get('code', '')
    session_id  = data.get('session_id', 'default')

    def _sse(obj):
        """Wrap a dict as a single SSE data frame."""
        return f"data: {json.dumps(obj)}\n\n"

    # ------------------------------------------------------------------
    # Compile (lex → parse → semantic → IR → optimise → codegen).
    # Fast and synchronous.  Raises _CompileError on any failure.
    # ------------------------------------------------------------------
    def _compile():
        # Lexical
        try:
            lexer = Lexer(code_string)
            tokens, lex_errors = lexer.tokenize()
            if lex_errors:
                clean = []
                for err in lex_errors:
                    if isinstance(err, dict):
                        clean.append(err)
                    else:
                        err_msg = getattr(err, 'error_msg', str(err))
                        err_val = getattr(err, 'value', '?')
                        clean.append({
                            "line": getattr(err, 'line', '?'),
                            "col":  getattr(err, 'col',  '?'),
                            "found": (f"Unknown Character '{err_val}'"
                                      if err_msg == "Unknown Character"
                                      else f"Invalid character '{err_val}'"),
                            "expected": getattr(err, 'expected', ["Valid Token"]),
                            "message": err_msg,
                            "phase": "Lexical"
                        })
                raise _CompileError("Lexical", clean)
        except _CompileError:
            raise
        except Exception as e:
            raise _CompileError("Lexical", [{"line": "-", "col": "-", "found": "CRASH",
                                              "expected": [], "message": f"Lexer crashed: {e}",
                                              "phase": "Lexical"}])

        # Syntax
        try:
            parser = Parser(tokens, code_string)
            syn_errors = parser.parse()
            if syn_errors:
                for e in syn_errors:
                    e['phase'] = 'Syntax'
                raise _CompileError("Syntax", syn_errors)
        except _CompileError:
            raise
        except Exception as e:
            raise _CompileError("Syntax", [{"line": "-", "col": "-", "found": "CRASH",
                                             "expected": [], "message": f"Parser crashed: {e}",
                                             "phase": "Syntax"}])

        # Semantic
        try:
            ast_parser   = ASTParser(tokens, code_string)
            program_node = ast_parser.build()
            analyzer     = SemanticAnalyzer(program_node, code_string)
            sem_errors   = analyzer.analyze()
            if sem_errors:
                for e in sem_errors:
                    e['phase'] = 'Semantic'
                raise _CompileError("Semantic", sem_errors)
        except _CompileError:
            raise
        except Exception as e:
            raise _CompileError("Semantic", [{"line": "-", "col": "-", "found": "CRASH",
                                               "expected": [], "message": f"Semantic analyzer crashed: {e}",
                                               "phase": "Semantic"}])

        # IR Generation
        try:
            ir_gen     = IRGenerator(program_node)
            ir_program = ir_gen.generate()
        except Exception as e:
            raise _CompileError("Code Generation", [{"line": "-", "col": "-", "found": "CRASH",
                                                      "expected": [], "message": f"IR generation failed: {e}",
                                                      "phase": "Code Generation"}])

        # Optimisation
        try:
            ir_program = IROptimizer(ir_program).optimize()
        except Exception as e:
            raise _CompileError("Code Generation", [{"line": "-", "col": "-", "found": "CRASH",
                                                      "expected": [], "message": f"Optimisation failed: {e}",
                                                      "phase": "Code Generation"}])

        # Code Generation
        try:
            return CodeGenerator(ir_program).generate()
        except Exception as e:
            raise _CompileError("Code Generation", [{"line": "-", "col": "-", "found": "CRASH",
                                                      "expected": [], "message": f"Code generation failed: {e}",
                                                      "phase": "Code Generation"}])

    # ------------------------------------------------------------------
    # SSE generator: compile, then stream execution events
    # ------------------------------------------------------------------
    def event_stream():
        # 1. Compile
        try:
            generated_code = _compile()
        except _CompileError as ce:
            yield _sse({"type": "compile_error", "errors": ce.errors, "phase": ce.phase})
            yield _sse({"type": "done", "success": False})
            return

        # 2. Set up per-session queues / stop flag
        output_q   = queue.Queue()
        input_q    = queue.Queue()
        stop_event = threading.Event()
        _running_flags[session_id] = stop_event
        _input_queues[session_id]  = input_q

        # Shared namespace so _map_runtime_error can resad _ss_line/_ss_col
        exec_globals = {'__builtins__': __builtins__, '_ss_line': 0, '_ss_col': 0}

        # Patched print() — routes all output through output_q
        def captured_print(*args, **kwargs):
            end  = kwargs.get('end', '\n')
            sep  = kwargs.get('sep', ' ')
            text = sep.join(str(a) for a in args) + end
            output_q.put(('output', text))

        # Patched input() — signals frontend then BLOCKS until user submits
        def captured_input(prompt=''):
            # Detect the hidden dtype marker injected by the code generator.
            # Format: '__ss:DTYPE:' e.g. '__ss:COIN:' or '__ss:SCROLL:'
            dtype = 'SCROLL'
            display_prompt = prompt
            if isinstance(prompt, str) and prompt.startswith('__ss:'):
                parts = prompt.split(':', 2)
                if len(parts) >= 2:
                    dtype = parts[1]
                display_prompt = ''  # don't echo the internal marker
            if display_prompt:
                output_q.put(('output', str(display_prompt)))
            output_q.put(('input_needed', {'dtype': dtype}))
            # Block until /api/input delivers a value (or stop is requested)
            while not stop_event.is_set():
                try:
                    return input_q.get(timeout=0.5)
                except queue.Empty:
                    continue
            return ''   # program was stopped while waiting for input

        exec_globals['print'] = captured_print
        exec_globals['input'] = captured_input

        # Replace the __main__ guard so _ss_ahoy() runs directly
        modified_code = generated_code.replace(
            "if __name__ == '__main__':\n    _ss_ahoy()",
            "_ss_ahoy()"
        )

        exec_result = {'error': None}
        done_event  = threading.Event()

        def _run():
            try:
                exec(modified_code, exec_globals)  # noqa: S102
            except SystemExit:
                pass
            except Exception as exc:
                if not stop_event.is_set():
                    exec_result['error'] = _map_runtime_error(
                        exc, code_string, generated_code, exec_globals
                    )
            finally:
                output_q.put(('done', None))
                done_event.set()

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

        # Watchdog: hard ceiling of 5 minutes so the server never leaks threads
        def _watchdog():
            if not done_event.wait(timeout=1200):
                stop_event.set()
                output_q.put(('timeout', None))
        threading.Thread(target=_watchdog, daemon=True).start()

        # 3. Stream events until execution finishes
        while True:
            try:
                kind, payload = output_q.get(timeout=1.0)
            except queue.Empty:
                # Keep-alive comment — prevents browser/proxy from closing stream
                yield ": keep-alive\n\n"
                continue

            if kind == 'output':
                yield _sse({"type": "output", "text": payload})

            elif kind == 'input_needed':
                dtype = payload.get('dtype', 'SCROLL') if isinstance(payload, dict) else 'SCROLL'
                yield _sse({"type": "input_needed", "dtype": dtype})
                # The generator stays open here; the execution thread is blocked
                # inside captured_input() waiting for /api/input.

            elif kind == 'timeout':
                yield _sse({
                    "type": "error",
                    "error": {
                        "line": "-", "col": "-",
                        "error_type": "Timeout Error",
                        "message": "Program ran for over 5 minutes and was stopped. Check for infinite loops.",
                        "actual_line": "",
                        "phase": "Runtime"
                    }
                })
                yield _sse({"type": "done", "success": False})
                break

            elif kind == 'done':
                if exec_result['error']:
                    yield _sse({"type": "error", "error": exec_result['error']})
                yield _sse({"type": "done", "success": exec_result['error'] is None})
                break

        # Cleanup
        _running_flags.pop(session_id, None)
        _input_queues.pop(session_id, None)

    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control':     'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )


# =============================================================================
#  /api/tokenize  — Run only the lexer; always returns valid tokens even on error
# =============================================================================
@app.route('/api/tokenize', methods=['POST'])
def tokenize_code():
    data        = request.json
    code_string = data.get('code', '')

    SKIP_TYPES = {'eof', 'EOF'}

    _WS_LABEL = {'\n': 'newline', ' ': 'whitespace', '\t': 'tab', '\r': 'carriage_return'}

    def _token_row(t):
        if t.type == 'whitespace':
            label = _WS_LABEL.get(t.value, 'whitespace')
            return {"lexeme": label, "token": label}
        return {"lexeme": t.value, "token": t.type}

    try:
        lexer = Lexer(code_string)
        tokens, lex_errors = lexer.tokenize()

        ui_tokens = [
            _token_row(t)
            for t in tokens
            if t.type not in SKIP_TYPES
        ]

        formatted_errors = []
        for err in lex_errors:
            if isinstance(err, dict):
                formatted_errors.append(err)
            else:
                formatted_errors.append({
                    "line":    getattr(err, 'line',      '?'),
                    "col":     getattr(err, 'col',       '?'),
                    "found":   getattr(err, 'value',     '?'),
                    "message": getattr(err, 'error_msg', str(err)),
                })

        return jsonify({
            "success":     True,
            "tokens":      ui_tokens,
            "errors":      formatted_errors,
            "error_count": len(formatted_errors),
        })
    except Exception as e:
        return jsonify({
            "success":     False,
            "tokens":      [],
            "errors":      [{"line": "-", "col": "-", "found": "CRASH", "message": str(e)}],
            "error_count": 1,
        })


# =============================================================================
#  /api/stop  — Signal a running program to stop
# =============================================================================
@app.route('/api/stop', methods=['POST'])
def stop_code():
    data       = request.json
    session_id = data.get('session_id', 'default')

    if session_id in _running_flags:
        _running_flags[session_id].set()
        # Unblock any pending input() so the execution thread exits cleanly
        if session_id in _input_queues:
            try:
                _input_queues[session_id].put_nowait('')
            except queue.Full:
                pass
        return jsonify({"success": True, "message": "Stop signal sent."})

    return jsonify({"success": False, "message": "No running program found."})


# =============================================================================
#  /api/input  — Deliver a line of user input to a waiting program
# =============================================================================
@app.route('/api/input', methods=['POST'])
def provide_input():
    data       = request.json
    session_id = data.get('session_id', 'default')
    user_input = data.get('input', '')

    if session_id in _input_queues:
        _input_queues[session_id].put(user_input)
        return jsonify({"success": True})

    return jsonify({"success": False, "message": "No running program is waiting for input."})


# =============================================================================
#  Runtime error mapper
# =============================================================================
def _map_runtime_error(exc, source_code, generated_code, exec_globals=None):
    """Translate a Python exception into a SeaStack-context error object."""
    tb      = traceback.extract_tb(exc.__traceback__)
    py_line = None
    for frame in reversed(tb):
        if frame.filename == '<string>':
            py_line = frame.lineno
            break

    exc_msg = str(exc)

    # ── Friendly, jargon-free messages ──────────────────────────────────
    if isinstance(exc, ZeroDivisionError):
        error_type = "Division by Zero"
        message    = "Cannot divide by zero. Check your arithmetic expressions for a denominator that evaluates to 0."
    elif isinstance(exc, TypeError):
        error_type = "Type Error"
        message    = "Incompatible types in operation. Check that your variables and expressions use matching types."
    elif isinstance(exc, IndexError):
        error_type = "Index Out of Bounds"
        message    = "Array index is out of bounds. The index used exceeds the declared size of the array."
    elif isinstance(exc, KeyError):
        error_type = "Undefined Member"
        message    = f"Attempted to access an undefined struct member: {exc_msg}"
    elif isinstance(exc, NameError):
        match    = re.search(r"name '(\w+)' is not defined", exc_msg)
        var_name = match.group(1) if match else "unknown"
        error_type = "Undefined Variable"
        message    = f"Variable '{var_name}' is not defined at this point in execution."
    elif isinstance(exc, ValueError):
        error_type = "Value Error"
        m = exc_msg.lower()
        if 'aye' in m or 'nay' in m:
            message = "Invalid BOOL input. Enter AYE for true or NAY for false."
        elif 'int' in m or 'base 10' in m:
            message = ("Invalid input: a whole number (COIN) was expected but what you "
                       "entered cannot be converted. Make sure you type only digits.")
        elif 'float' in m:
            message = ("Invalid input: a decimal number (DIME) was expected but what you "
                       "entered cannot be converted. Make sure you type a valid number.")
        else:
            message = f"{exc_msg}"
    elif isinstance(exc, OverflowError):
        error_type = "Overflow Error"
        message    = "Numeric result is too large. Check for very large exponents or multiplication values."
    elif isinstance(exc, RecursionError):
        error_type = "Stack Overflow"
        message    = "Too many nested function calls. Check for runaway recursion."
    elif isinstance(exc, SyntaxError):
        error_type = "Syntax Error"
        m = exc_msg
        m = re.sub(r'\s*\(<[^)]*>,\s*line\s*\d+\)', '', m).strip()
        if "'break'" in m or 'break' in m.lower():
            message = "LAND!! can only be used inside a loop or CHART block."
        elif "'continue'" in m or 'continue' in m.lower():
            message = "SAIL!! can only be used inside a loop."
        elif "'return'" in m or 'return' in m.lower():
            message = "BACK can only be used inside a function."
        else:
            message = _sanitize_py_message(m)
    else:
        error_type = "Runtime Error"
        m = re.sub(r'\s*\(<[^)]*>,\s*line\s*\d+\)', '', exc_msg).strip()
        message = _sanitize_py_message(m)

    # ── Map to SeaStack source line ─────────────────────────────────────
    ss_line     = "-"
    ss_col      = "-"
    actual_line = ""

    # Prefer the _ss_line / _ss_col trackers the code generator injects
    if exec_globals:
        raw_line = exec_globals.get('_ss_line', 0)
        raw_col  = exec_globals.get('_ss_col',  0)
        if raw_line and int(raw_line) > 0:
            ss_line = str(raw_line)
            if raw_col:
                ss_col = str(raw_col)
            src_lines = source_code.split('\n') if source_code else []
            idx = int(raw_line) - 1
            if 0 <= idx < len(src_lines):
                actual_line = src_lines[idx]

    # Fallback: scan source for identifiers from the failing Python line
    if ss_line == "-" and py_line and generated_code:
        gen_lines = generated_code.split('\n')
        if 0 < py_line <= len(gen_lines):
            py_code_line = gen_lines[py_line - 1].strip()
            src_lines    = source_code.split('\n') if source_code else []
            for si, sl in enumerate(src_lines):
                stripped = sl.strip()
                if stripped and not stripped.startswith('~'):
                    if any(w in stripped for w in _extract_identifiers(py_code_line)):
                        ss_line     = str(si + 1)
                        actual_line = sl
                        break

    return {
        "line":        ss_line,
        "col":         ss_col,
        "found":       error_type,
        "expected":    [],
        "message":     message,
        "actual_line": actual_line,
        "phase":       "Runtime",
        "error_type":  error_type,
    }


def _sanitize_py_message(msg):
    """Replace Python-specific terms with SeaStack equivalents in error messages."""
    replacements = [
        ("'break'",    "LAND!!"),
        ("'continue'", "SAIL!!"),
        ("'return'",   "BACK"),
        ("'pass'",     "NOP"),
        ("'int'",      "'COIN'"),
        ("'float'",    "'DIME'"),
        ("'str'",      "'SCROLL'"),
        ("'bool'",     "'BOOL'"),
        ("'list'",     "'array'"),
        ("'dict'",     "'struct'"),
        (" int ",      " COIN "),
        (" float ",    " DIME "),
        (" str ",      " SCROLL "),
        (" bool ",     " BOOL "),
        (" list ",     " array "),
        ("<string>",   "the program"),
        ("<module>",   "the program"),
    ]
    for old, new in replacements:
        msg = msg.replace(old, new)
    return msg


def _extract_identifiers(code_line):
    """Extract SeaStack-style identifiers from a Python code line."""
    return [m for m in re.findall(r'\b([a-z][a-z0-9_]*)\b', code_line)
            if m not in {'print', 'input', 'int', 'float', 'str', 'bool',
                         'true', 'false', 'none', 'not', 'and', 'or',
                         'if', 'else', 'while', 'for', 'return', 'def',
                         'pass', 'break', 'continue', 'math', 'sys',
                         'end', 'format', 'self', 'flush'}]


# ─── Internal compile-error sentinel ─────────────────────────────────────────
class _CompileError(Exception):
    def __init__(self, phase, errors):
        self.phase  = phase
        self.errors = errors


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)