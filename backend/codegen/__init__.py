# =============================================================================
# codegen/__init__.py — SeaStack Code Generation Phase
#
# This package provides the full pipeline for:
#   1. IR Generation  — AST → Three-Address Code (Quadruples)
#   2. Optimization   — TAC → Optimized TAC
#   3. Code Generation — Optimized TAC → Executable Python
#
# Usage:
#   from codegen.ir_generator import IRGenerator
#   from codegen.optimizer import IROptimizer
#   from codegen.code_generator import StructuralCodeGenerator
#
#   ir = IRGenerator(ast).generate()          # Step 1: AST → IR
#   ir = IROptimizer(ir).optimize()           # Step 2: Optimize IR
#   python_code = StructuralCodeGenerator(ir).generate()  # Step 3: IR → Python
# =============================================================================

from codegen.ir_instructions import IRProgram, Quad
from codegen.ir_generator import IRGenerator
from codegen.optimizer import IROptimizer
from codegen.code_generator import StructuralCodeGenerator

__all__ = [
    'IRProgram', 'Quad',
    'IRGenerator', 'IROptimizer', 'StructuralCodeGenerator',
]
