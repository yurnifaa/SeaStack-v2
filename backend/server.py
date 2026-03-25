import sys
import os
import json
import threading
import queue

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from backend.run_error_msg import map_runtime_error, map_timeout_error

try:
    from backend.lexical.lexer import Lexer
    from backend.syntax.syn_parser import Parser
    from backend.semantic.ast_parser import ASTParser
    from backend.semantic.semantic_analyzer import SemanticAnalyzer
    from backend.codegen.ir_generator import IRGenerator
    from backend.codegen.optimizer import IROptimizer
    from backend.codegen.code_generator import StructuralCodeGenerator
except ImportError as e:
    print(f"\n[ERROR] Import Failed! Details: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

import flask.cli
flask.cli.show_server_banner = lambda *args, **kwargs: None

import logging
class _SuppressDevWarning(logging.Filter):
    def filter(self, record):
        return 'Do not use it in a production deployment' not in record.getMessage()
logging.getLogger('werkzeug').addFilter(_SuppressDevWarning())

_running_flags = {}  # session_id → threading.Event
_input_queues  = {}  # session_id → queue.Queue


# =============================================================================
#  /api/run
# =============================================================================
@app.route('/api/run', methods=['POST'])
def run_code():
    data        = request.json
    code_string = data.get('code', '')
    session_id  = data.get('session_id', 'default')

    def _sse(obj):
        return f"data: {json.dumps(obj)}\n\n"

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
                            "line":     getattr(err, 'line', '?'),
                            "col":      getattr(err, 'col',  '?'),
                            "found":    (f"Unknown Character '{err_val}'"
                                         if err_msg == "Unknown Character"
                                         else f"Invalid character/s: '{err_val}'"),
                            "expected": getattr(err, 'expected', []),
                            "message":  err_msg,
                            "phase":    "Lexical"
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
            return StructuralCodeGenerator(ir_program).generate()
        except Exception as e:
            raise _CompileError("Code Generation", [{"line": "-", "col": "-", "found": "CRASH",
                                                      "expected": [], "message": f"Code generation failed: {e}",
                                                      "phase": "Code Generation"}])

    def event_stream():
        try:
            generated_code = _compile()
        except _CompileError as ce:
            yield _sse({"type": "compile_error", "errors": ce.errors, "phase": ce.phase})
            yield _sse({"type": "done", "success": False})
            return

        output_q   = queue.Queue()
        input_q    = queue.Queue()
        stop_event = threading.Event()
        _running_flags[session_id] = stop_event
        _input_queues[session_id]  = input_q

        exec_globals = {'__builtins__': __builtins__, '_ss_line': 0, '_ss_col': 0}

        def captured_print(*args, **kwargs):
            end  = kwargs.get('end', '\n')
            sep  = kwargs.get('sep', ' ')
            text = sep.join(str(a) for a in args) + end
            output_q.put(('output', text))

        def captured_input(prompt=''):
            dtype = 'SCROLL'
            display_prompt = prompt
            if isinstance(prompt, str) and prompt.startswith('__ss:'):
                parts = prompt.split(':', 2)
                if len(parts) >= 2:
                    dtype = parts[1]
                display_prompt = ''
            if display_prompt:
                output_q.put(('output', str(display_prompt)))
            output_q.put(('input_needed', {'dtype': dtype}))
            while not stop_event.is_set():
                try:
                    return input_q.get(timeout=0.5)
                except queue.Empty:
                    continue
            return ''

        exec_globals['print'] = captured_print
        exec_globals['input'] = captured_input

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
                    exec_result['error'] = map_runtime_error(
                        exc, code_string, generated_code, exec_globals
                    )
            finally:
                output_q.put(('done', None))
                done_event.set()

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

        def _watchdog():
            if not done_event.wait(timeout=300):
                stop_event.set()
                output_q.put(('timeout', None))
        threading.Thread(target=_watchdog, daemon=True).start()

        while True:
            try:
                kind, payload = output_q.get(timeout=1.0)
            except queue.Empty:
                yield ": keep-alive\n\n"
                continue

            if kind == 'output':
                yield _sse({"type": "output", "text": payload})
            elif kind == 'input_needed':
                dtype = payload.get('dtype', 'SCROLL') if isinstance(payload, dict) else 'SCROLL'
                yield _sse({"type": "input_needed", "dtype": dtype})
            elif kind == 'timeout':
                yield _sse({"type": "error", "error": map_timeout_error()})
                yield _sse({"type": "done", "success": False})
                break
            elif kind == 'done':
                if exec_result['error']:
                    yield _sse({"type": "error", "error": exec_result['error']})
                yield _sse({"type": "done", "success": exec_result['error'] is None})
                break

        _running_flags.pop(session_id, None)
        _input_queues.pop(session_id, None)

    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control':     'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection':        'keep-alive',
        }
    )


# =============================================================================
#  /api/stop
# =============================================================================
@app.route('/api/stop', methods=['POST'])
def stop_code():
    data       = request.json
    session_id = data.get('session_id', 'default')
    if session_id in _running_flags:
        _running_flags[session_id].set()
        if session_id in _input_queues:
            try:
                _input_queues[session_id].put_nowait('')
            except queue.Full:
                pass
        return jsonify({"success": True, "message": "Stop signal sent."})
    return jsonify({"success": False, "message": "No running program found."})


# =============================================================================
#  /api/input
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



class _CompileError(Exception):
    def __init__(self, phase, errors):
        self.phase  = phase
        self.errors = errors


if __name__ == '__main__':
    app.run(debug=True, port=5000)
