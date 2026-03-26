from codegen.ir_instructions import (
    IRProgram, Quad,
    PROGRAM_START, PROGRAM_END, FUNC_BEGIN, FUNC_END, PARAM_DECL,
    AHOY_BEGIN, AHOY_END,
    DECL_VAR, DECL_CONST, DECL_ARR, DECL_STRUCT_TYPE, DECL_STRUCT_VAR,
    ARR_INIT_1D, ARR_INIT_2D, STRUCT_INIT,
    ASSIGN, ASSIGN_ARR, ASSIGN_ARR2, ASSIGN_MEMBER, COMPOUND_ASSIGN,
    ADD, SUB, MUL, DIV, MOD, POW,
    LT, GT, LE, GE, EQ, NE,
    LOG_AND, LOG_OR, LOG_NOT, LOG_DNOT,
    UNARY_NEG, UNARY_INC, UNARY_DEC,
    CONCAT, SCROLL_CHAR,
    LOAD_ARR, LOAD_ARR2, LOAD_MEMBER,
    LABEL, JUMP, JUMP_FALSE, JUMP_TRUE, BREAK, CONTINUE,
    ARG, CALL, CALL_VOID, RETURN, RETURN_VOID,
    INPUT, OUTPUT, NOP, LITERAL, COMMENT,
    ARITH_OP_MAP, REL_OP_MAP, LOG_OP_MAP, COMPOUND_OP_MAP,
)


# =================================================================================================
# IR GENERATOR CLASS: walks every AST node and emits a flat list of IR quadruples
# =================================================================================================

class IRGenerator:
    """Walks the semantic-checked AST and emits TAC quadruples."""

    def __init__(self, ast):
        self.ast = ast
        self.ir = IRProgram()
        self._temp_counter = 0
        self._label_counter = 0
        # Track loop labels for LAND (break) and SAIL (continue)
        self._loop_end_stack = []    # label to jump to on LAND
        self._loop_start_stack = []  # label to jump to on SAIL
        # Track chart end label for LAND inside CHART
        self._chart_end_stack = []

    # ── Utility ──────────────────────────────────────────────────────────

    def _new_temp(self):
        t = f"_t{self._temp_counter}"
        self._temp_counter += 1
        return t

    def _new_temp_typed(self, dtype):
        """Allocate a new temporary and register its type in temp_types."""
        t = self._new_temp()
        if dtype:
            self.ir.temp_types[t] = dtype
        return t

    def _new_label(self):
        lbl = f"_L{self._label_counter}"
        self._label_counter += 1
        return lbl

    def _line(self, node):
        tok = getattr(node, 'token', None)
        if tok:
            return getattr(tok, 'line', None)
        return None

    def _col(self, node):
        tok = getattr(node, 'token', None)
        if tok:
            return getattr(tok, 'col', None)
        return None

    # ── Entry Point ──────────────────────────────────────────────────────

    def generate(self):
        self.visit(self.ast)
        return self.ir

    # ── Visitor Dispatch ─────────────────────────────────────────────────

    def visit(self, node):
        if node is None:
            return None
        method = f'visit_{type(node).__name__}'
        visitor = getattr(self, method, None)
        if visitor is None:
            # Fallback: just return None silently
            return None
        return visitor(node)

    # =====================================================================
    # PROGRAM STRUCTURE
    # =====================================================================

    def visit_ProgramNode(self, node):
        self.ir.emit(PROGRAM_START, comment="SeaStack program")
        for d in node.global_decls:
            self.visit(d)
        self.visit(node.ahoy_body)
        self.ir.emit(PROGRAM_END)

    def visit_AhoyNode(self, node):
        self.ir.emit(AHOY_BEGIN, comment="main function", line=self._line(node), col=self._col(node))
        for d in node.local_decls:
            self.visit(d)
        for s in node.statements:
            self.visit(s)
        self.ir.emit(AHOY_END)

    # =====================================================================
    # DECLARATIONS
    # =====================================================================

    def visit_ConstDeclNode(self, node):
        val_temp = self._emit_expr(node.value)
        self.ir.emit(DECL_CONST, node.name, node.dtype, val_temp,
                     comment=f"LOCKE {node.dtype} {node.name}", line=self._line(node), col=self._col(node))

    def visit_VarDeclNode(self, node):
        init_temp = None
        if node.init_value is not None:
            init_temp = self._emit_expr(node.init_value)
        self.ir.emit(DECL_VAR, node.name, node.dtype, init_temp,
                     comment=f"{node.dtype} {node.name}", line=self._line(node), col=self._col(node))

    def visit_ArrayDeclNode(self, node):
        dims = tuple(node.dimensions)
        self.ir.emit(DECL_ARR, node.name, node.dtype, dims,
                     comment=f"array {node.dtype} {node.name}{dims}", line=self._line(node), col=self._col(node))
        if node.init_values is not None:
            if node.is_2d:
                rows = []
                for row in node.init_values:
                    row_temps = [self._emit_expr(elem) for elem in row]
                    rows.append(row_temps)
                self.ir.emit(ARR_INIT_2D, node.name, rows, line=self._line(node), col=self._col(node))
            else:
                val_temps = [self._emit_expr(elem) for elem in node.init_values]
                self.ir.emit(ARR_INIT_1D, node.name, val_temps, line=self._line(node), col=self._col(node))

    def visit_StructDefNode(self, node):
        members = {}
        order = []
        for m in node.members:
            members[m.name] = m.dtype
            order.append(m.name)
        self.ir.struct_types[node.name] = members
        self.ir.struct_orders[node.name] = order
        self.ir.emit(DECL_STRUCT_TYPE, node.name, members,
                     comment=f"MAST {node.name}", line=self._line(node), col=self._col(node))

    def visit_MemberDeclNode(self, node):
        pass  # handled inside StructDefNode

    def visit_StructVarDeclNode(self, node):
        self.ir.emit(DECL_STRUCT_VAR, node.var_name, node.struct_type,
                     comment=f"MAST {node.struct_type} {node.var_name}", line=self._line(node), col=self._col(node))
        if node.inits:
            init_dict = {}
            order = self.ir.struct_orders.get(node.struct_type, [])
            pos = 0
            for init in node.inits:
                cn = type(init).__name__
                if cn == 'NamedInitNode':
                    val_temp = self._emit_expr(init.value)
                    init_dict[init.member_name] = val_temp
                    if init.member_name in order:
                        pos = order.index(init.member_name) + 1
                elif cn == 'PositionalInitNode':
                    if pos < len(order):
                        val_temp = self._emit_expr(init.value)
                        init_dict[order[pos]] = val_temp
                        pos += 1
            self.ir.emit(STRUCT_INIT, node.var_name, init_dict, line=self._line(node), col=self._col(node))

    def visit_PositionalInitNode(self, node):
        return self._emit_expr(node.value)

    def visit_NamedInitNode(self, node):
        return self._emit_expr(node.value)

    # =====================================================================
    # FUNCTION DEFINITIONS
    # =====================================================================

    def visit_FuncDefNode(self, node):
        self.ir.func_signatures[node.name] = (
            node.return_type,
            [(p.dtype, p.name) for p in node.params]
        )
        self.ir.emit(FUNC_BEGIN, node.name, node.return_type,
                     comment=f"{'ABYSS' if node.return_type == 'ABYSS' else node.return_type} {node.name}()",
                     line=self._line(node), col=self._col(node))
        for p in node.params:
            self.ir.emit(PARAM_DECL, p.name, p.dtype)
        for d in node.local_decls:
            self.visit(d)
        for s in node.body:
            self.visit(s)
        if node.return_type != 'ABYSS' and node.return_expr is not None:
            ret_temp = self._emit_expr(node.return_expr)
            self.ir.emit(RETURN, ret_temp, comment="BACK")
        self.ir.emit(FUNC_END, node.name)

    def visit_ParamNode(self, node):
        pass

    # =====================================================================
    # STATEMENTS
    # =====================================================================

    def visit_AssignNode(self, node):
        val_temp = self._emit_expr(node.value)
        if node.target_kind == 'var':
            self.ir.emit(ASSIGN, val_temp, None, node.var_name,
                         comment=f"{node.var_name} = ...", line=self._line(node), col=self._col(node))
        elif node.target_kind == 'array1d':
            idx = self._emit_expr(node.index1)
            self.ir.emit(ASSIGN_ARR, node.var_name, idx, val_temp,
                         line=self._line(node), col=self._col(node))
        elif node.target_kind == 'array2d':
            idx1 = self._emit_expr(node.index1)
            idx2 = self._emit_expr(node.index2)
            self.ir.emit(ASSIGN_ARR2, node.var_name, (idx1, idx2), val_temp,
                         line=self._line(node), col=self._col(node))
        elif node.target_kind == 'member':
            self.ir.emit(ASSIGN_MEMBER, node.var_name, node.member, val_temp,
                         line=self._line(node), col=self._col(node))

    def visit_CompoundAssignNode(self, node):
        # Load current value of target
        target_temp = self._load_target(node.var_name, node.target_kind,
                                        node.index1, node.index2, node.member)
        val_temp = self._emit_expr(node.value)
        # Perform the arithmetic operation
        arith_op = COMPOUND_OP_MAP.get(node.operator, '+')
        ir_op = ARITH_OP_MAP.get(arith_op, ADD)
        result = self._new_temp()
        self.ir.emit(ir_op, target_temp, val_temp, result, line=self._line(node), col=self._col(node))
        # Store back
        self._store_target(node.var_name, node.target_kind,
                           node.index1, node.index2, node.member, result)

    def _load_target(self, var_name, target_kind, index1, index2, member):
        if target_kind == 'var':
            return var_name
        elif target_kind == 'array1d':
            idx = self._emit_expr(index1)
            t = self._new_temp()
            self.ir.emit(LOAD_ARR, var_name, idx, t)
            return t
        elif target_kind == 'array2d':
            i1 = self._emit_expr(index1)
            i2 = self._emit_expr(index2)
            t = self._new_temp()
            self.ir.emit(LOAD_ARR2, var_name, (i1, i2), t)
            return t
        elif target_kind == 'member':
            t = self._new_temp()
            self.ir.emit(LOAD_MEMBER, var_name, member, t)
            return t
        return var_name

    def _store_target(self, var_name, target_kind, index1, index2, member, val_temp):
        if target_kind == 'var':
            self.ir.emit(ASSIGN, val_temp, None, var_name)
        elif target_kind == 'array1d':
            idx = self._emit_expr(index1)
            self.ir.emit(ASSIGN_ARR, var_name, idx, val_temp)
        elif target_kind == 'array2d':
            i1 = self._emit_expr(index1)
            i2 = self._emit_expr(index2)
            self.ir.emit(ASSIGN_ARR2, var_name, (i1, i2), val_temp)
        elif target_kind == 'member':
            self.ir.emit(ASSIGN_MEMBER, var_name, member, val_temp)

    # ── I/O ──────────────────────────────────────────────────────────────

    def visit_AskNode(self, node):
        target_infos = []
        for tgt in node.targets:
            info = {
                'var_name': tgt.var_name,
                'target_kind': tgt.target_kind,
                'index1': self._emit_expr(tgt.index1) if tgt.index1 else None,
                'index2': self._emit_expr(getattr(tgt, 'index2', None)) if getattr(tgt, 'index2', None) else None,
                'member': getattr(tgt, 'member', None),
            }
            target_infos.append(info)
        self.ir.emit(INPUT, node.format_string, target_infos,
                     comment="ASK", line=self._line(node), col=self._col(node))

    def visit_AddressNode(self, node):
        pass  # handled within AskNode

    def visit_EchoNode(self, node):
        arg_temps = [self._emit_expr(a) for a in node.args]
        self.ir.emit(OUTPUT, node.format_string, arg_temps,
                     comment="ECHO", line=self._line(node), col=self._col(node))

    # ── Conditionals ─────────────────────────────────────────────────────

    def visit_LookNode(self, node):
        # LOOK (if)
        end_label = self._new_label()
        next_label = self._new_label()

        cond_temp = self._emit_expr(node.condition)
        self.ir.emit(JUMP_FALSE, cond_temp, next_label,
                     comment="LOOK", line=self._line(node), col=self._col(node))
        for s in node.body:
            self.visit(s)
        self.ir.emit(JUMP, end_label)
        self.ir.emit(LABEL, next_label)

        # DROPLOOK (elif) chains
        for (dl_cond, dl_body) in node.droplooks:
            next_label = self._new_label()
            dl_temp = self._emit_expr(dl_cond)
            self.ir.emit(JUMP_FALSE, dl_temp, next_label, comment="DROPLOOK")
            for s in dl_body:
                self.visit(s)
            self.ir.emit(JUMP, end_label)
            self.ir.emit(LABEL, next_label)

        # DROP (else)
        if node.drop_body is not None:
            for s in node.drop_body:
                self.visit(s)

        self.ir.emit(LABEL, end_label)

    def visit_ChartNode(self, node):
        # CHART (switch)
        end_label = self._new_label()
        self._chart_end_stack.append(end_label)
        expr_temp = self._emit_expr(node.expr)

        next_label = self._new_label()
        for i, course in enumerate(node.courses):
            val_temp = self._emit_expr(course.value)
            cmp_temp = self._new_temp()
            self.ir.emit(EQ, expr_temp, val_temp, cmp_temp,
                         comment=f"COURSE {i}")
            body_label = self._new_label()
            self.ir.emit(JUMP_FALSE, cmp_temp, next_label)
            self.ir.emit(LABEL, body_label)
            for s in course.body:
                self.visit(s)
            self.ir.emit(JUMP, end_label)
            self.ir.emit(LABEL, next_label)
            next_label = self._new_label()

        # ADRIFT (default)
        if node.adrift_body is not None:
            for s in node.adrift_body:
                self.visit(s)

        self.ir.emit(LABEL, end_label)
        self._chart_end_stack.pop()

    def visit_CourseNode(self, node):
        pass  # handled by ChartNode

    # ── Loops ────────────────────────────────────────────────────────────

    def visit_HoistNode(self, node):
        # HOIST (for)
        start_label = self._new_label()
        update_label = self._new_label()
        end_label = self._new_label()

        self._loop_start_stack.append(update_label)  # SAIL goes to update
        self._loop_end_stack.append(end_label)        # LAND goes to end

        # Initialization
        for init in node.inits:
            self._emit_hoist_init(init)

        # Condition check
        self.ir.emit(LABEL, start_label)
        cond_temp = self._emit_expr(node.condition)
        self.ir.emit(JUMP_FALSE, cond_temp, end_label, comment="HOIST condition")

        # Body
        for s in node.body:
            self.visit(s)

        # Update
        self.ir.emit(LABEL, update_label)
        for upd in node.updates:
            self._emit_hoist_update(upd)

        self.ir.emit(JUMP, start_label)
        self.ir.emit(LABEL, end_label)

        self._loop_start_stack.pop()
        self._loop_end_stack.pop()

    def _emit_hoist_init(self, init_node):
        val_temp = self._emit_expr(init_node.value)
        if init_node.declares_new:
            self.ir.emit(DECL_VAR, init_node.var_name, 'COIN', val_temp,
                         comment=f"HOIST init COIN {init_node.var_name}")
        else:
            self.ir.emit(ASSIGN, val_temp, None, init_node.var_name,
                         comment=f"HOIST init {init_node.var_name}")

    def _emit_hoist_update(self, upd_node):
        if upd_node.update_kind == 'unary':
            if upd_node.unary_op == '+#':
                self.ir.emit(UNARY_INC, upd_node.var_name,
                             comment=f"+#{upd_node.var_name}")
            else:
                self.ir.emit(UNARY_DEC, upd_node.var_name,
                             comment=f"-#{upd_node.var_name}")
        elif upd_node.update_kind == 'compound':
            target = upd_node.var_name
            val_temp = self._emit_expr(upd_node.value)
            arith_op = COMPOUND_OP_MAP.get(upd_node.operator, '+')
            ir_op = ARITH_OP_MAP.get(arith_op, ADD)
            result = self._new_temp()
            self.ir.emit(ir_op, target, val_temp, result)
            self.ir.emit(ASSIGN, result, None, target)

    def visit_HeaveNode(self, node):
        # HEAVE (while)
        start_label = self._new_label()
        end_label = self._new_label()

        self._loop_start_stack.append(start_label)
        self._loop_end_stack.append(end_label)

        self.ir.emit(LABEL, start_label)
        cond_temp = self._emit_expr(node.condition)
        self.ir.emit(JUMP_FALSE, cond_temp, end_label, comment="HEAVE")

        for s in node.body:
            self.visit(s)

        self.ir.emit(JUMP, start_label)
        self.ir.emit(LABEL, end_label)

        self._loop_start_stack.pop()
        self._loop_end_stack.pop()

    def visit_HaulHeaveNode(self, node):
        # HAUL-HEAVE (do-while)
        start_label = self._new_label()
        end_label = self._new_label()

        self._loop_start_stack.append(start_label)
        self._loop_end_stack.append(end_label)

        self.ir.emit(LABEL, start_label)

        for s in node.body:
            self.visit(s)

        cond_temp = self._emit_expr(node.condition)
        self.ir.emit(JUMP_TRUE, cond_temp, start_label, comment="HAUL-HEAVE")
        self.ir.emit(LABEL, end_label)

        self._loop_start_stack.pop()
        self._loop_end_stack.pop()

    # ── Jump Statements ──────────────────────────────────────────────────

    def visit_SailNode(self, node):
        if self._loop_start_stack:
            self.ir.emit(JUMP, self._loop_start_stack[-1], comment="SAIL")
        else:
            self.ir.emit(CONTINUE, comment="SAIL")

    def visit_LandNode(self, node):
        if self._loop_end_stack:
            self.ir.emit(JUMP, self._loop_end_stack[-1], comment="LAND")
        elif self._chart_end_stack:
            self.ir.emit(JUMP, self._chart_end_stack[-1], comment="LAND (chart)")
        else:
            self.ir.emit(BREAK, comment="LAND")

    def visit_ReturnNode(self, node):
        val_temp = self._emit_expr(node.value)
        self.ir.emit(RETURN, val_temp, comment="BACK <value>")

    def visit_BackNode(self, node):
        self.ir.emit(RETURN_VOID, comment="BACK!!")

    # ── Unary Statement (standalone +# / -#) ─────────────────────────────

    def visit_UnaryStmtNode(self, node):
        if node.operator == '+#':
            self.ir.emit(UNARY_INC, node.var_name,
                         comment=f"+#{node.var_name}", line=self._line(node), col=self._col(node))
        elif node.operator == '-#':
            self.ir.emit(UNARY_DEC, node.var_name,
                         comment=f"-#{node.var_name}", line=self._line(node), col=self._col(node))

    def visit_FuncCallStmtNode(self, node):
        self._emit_expr(node.call_expr)

    # =====================================================================
    # EXPRESSIONS  — each returns the temp (or literal) holding the value
    # =====================================================================

    def _emit_expr(self, node):
        """Emit IR for an expression subtree.  Returns the temp/literal name."""
        if node is None:
            return None
        return self.visit(node)

    def visit_LiteralNode(self, node):
        # Overflow Checks for COIN and DIME
        if node.dtype == 'COIN':
            val_str = str(node.value).lstrip('-')
            if len(val_str) > 16:
                raise ValueError(f"Overflow Error: COIN literal '{node.value}' is too large. It exceeds the 16-digit limit.")
                
        elif node.dtype == 'DIME':
            val_str = str(node.value).lstrip('-')
            if '.' in val_str:
                int_part, dec_part = val_str.split('.')
            else:
                int_part, dec_part = val_str, ''

            if len(int_part) > 16:
                raise ValueError(f"Overflow Error: DIME literal '{node.value}' is too large. Integer part exceeds 16-digit limit.")
            if len(dec_part) > 8:
                raise ValueError(f"Overflow Error: DIME literal '{node.value}' is too large. Decimal part exceeds 8-digit limit.")

        t = self._new_temp_typed(node.dtype)
        self.ir.emit(LITERAL, node.dtype, node.value, t)
        return t

    def visit_IdentNode(self, node):
        # Variables are referenced by name; no extra instruction needed
        return node.name

    def visit_ArrayAccessNode(self, node):
        t = self._new_temp_typed(getattr(node, 'resolved_type', None))
        if getattr(node, 'resolved_type', None) == 'SCROLL':
            idx = self._emit_expr(node.indices[0])
            self.ir.emit(SCROLL_CHAR, node.name, idx, t)
        elif len(node.indices) == 1:
            idx = self._emit_expr(node.indices[0])
            self.ir.emit(LOAD_ARR, node.name, idx, t)
        else:
            i1 = self._emit_expr(node.indices[0])
            i2 = self._emit_expr(node.indices[1])
            self.ir.emit(LOAD_ARR2, node.name, (i1, i2), t)
        return t

    def visit_MemberAccessNode(self, node):
        t = self._new_temp_typed(getattr(node, 'resolved_type', None))
        self.ir.emit(LOAD_MEMBER, node.var_name, node.member_name, t)
        return t

    def visit_ScrollCharAccessNode(self, node):
        scroll_temp = self._emit_expr(node.scroll_expr)
        idx_temp = self._emit_expr(node.index)
        t = self._new_temp_typed('SCROLL')
        self.ir.emit(SCROLL_CHAR, scroll_temp, idx_temp, t)
        return t

    def visit_StringConcatNode(self, node):
        if not node.operands:
            return self._new_temp_typed('SCROLL')
        result = self._emit_expr(node.operands[0])
        for operand in node.operands[1:]:
            right = self._emit_expr(operand)
            t = self._new_temp_typed('SCROLL')
            self.ir.emit(CONCAT, result, right, t)
            result = t
        return result

    def visit_FuncCallNode(self, node):
        arg_temps = []
        for a in node.args:
            arg_temps.append(self._emit_expr(a))
        for at in arg_temps:
            self.ir.emit(ARG, at)

        # Use resolved_type stamped by semantic analyzer; fall back to sig lookup
        resolved = getattr(node, 'resolved_type', None)
        if resolved is None:
            sig = self.ir.func_signatures.get(node.name)
            resolved = sig[0] if sig else None

        if resolved == 'ABYSS' or resolved is None:
            self.ir.emit(CALL_VOID, node.name, len(arg_temps))
            return None
        else:
            t = self._new_temp_typed(resolved)
            self.ir.emit(CALL, node.name, len(arg_temps), t)
            return t

    def visit_BinaryOpNode(self, node):
        left_temp = self._emit_expr(node.left)
        right_temp = self._emit_expr(node.right)
        t = self._new_temp_typed(getattr(node, 'resolved_type', None))
        op = node.operator
        if op in ARITH_OP_MAP:
            self.ir.emit(ARITH_OP_MAP[op], left_temp, right_temp, t,
                         line=self._line(node), col=self._col(node))
        elif op in REL_OP_MAP:
            self.ir.emit(REL_OP_MAP[op], left_temp, right_temp, t,
                         line=self._line(node), col=self._col(node))
        elif op in LOG_OP_MAP:
            self.ir.emit(LOG_OP_MAP[op], left_temp, right_temp, t,
                         line=self._line(node), col=self._col(node))
        else:
            self.ir.emit(NOP, comment=f"unknown binary op: {op}")
            return left_temp
        return t

    def visit_UnaryOpNode(self, node):
        operand_temp = self._emit_expr(node.operand)
        t = self._new_temp_typed(getattr(node, 'resolved_type', None))
        if node.operator == '-':
            self.ir.emit(UNARY_NEG, operand_temp, None, t,
                         line=self._line(node), col=self._col(node))
        elif node.operator == '!':
            self.ir.emit(LOG_NOT, operand_temp, None, t,
                         line=self._line(node), col=self._col(node))
        elif node.operator == '!#':
            self.ir.emit(LOG_DNOT, operand_temp, None, t,
                         line=self._line(node), col=self._col(node))
        else:
            return operand_temp
        return t

    # ── Nodes that should just visit children ────────────────────────────

    def visit_HoistInitNode(self, node):
        self._emit_hoist_init(node)

    def visit_HoistUpdateNode(self, node):
        self._emit_hoist_update(node)