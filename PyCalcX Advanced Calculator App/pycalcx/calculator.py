"""Calculator core for PyCalcX.

Provides a Calculator class that safely evaluates arithmetic expressions using
ast, supports variable assignment, math functions, history and step-by-step
tracing of evaluation.
"""
from __future__ import annotations

import ast
import operator
import math
from typing import Any, Dict, List, Tuple


class CalcError(Exception):
    pass


SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


SAFE_FUNCS = {name: getattr(math, name) for name in (
    "sin",
    "cos",
    "tan",
    "sqrt",
    "log",
    "log10",
    "exp",
    "factorial",
    "floor",
    "ceil",
    "fabs",
)}
SAFE_CONSTS = {"pi": math.pi, "e": math.e}


class Calculator:
    """Safe evaluator with variables, history and step tracing.

    Contract:
    - Input: string expressions (e.g. '2+3', 'a = 5', 'sqrt(2)')
    - Output: numeric results (int/float) and trace steps
    - Errors: raises CalcError for invalid inputs or unsafe operations
    """

    def __init__(self) -> None:
        self.vars: Dict[str, float] = {}
        self.history: List[Tuple[str, Any]] = []

    def eval(self, text: str, trace: bool = False) -> Tuple[Any, List[str]]:
        """Evaluate an expression or assignment.

        Returns (result, trace_lines). For assignments, result is the value
        assigned.
        """
        text = text.strip()
        if not text:
            raise CalcError("Empty expression")

        # assignment? e.g. a = expr
        if "=" in text:
            parts = text.split("=", 1)
            var = parts[0].strip()
            expr = parts[1].strip()
            if not var.isidentifier():
                raise CalcError(f"Invalid variable name: {var}")
            val, trace_lines = self._eval_expr(expr, trace)
            self.vars[var] = val
            self.history.append((text, val))
            return val, trace_lines

        val, trace_lines = self._eval_expr(text, trace)
        self.history.append((text, val))
        return val, trace_lines

    def undo(self) -> None:
        """Undo last history item (removes var assignment if any)."""
        if not self.history:
            raise CalcError("Nothing to undo")
        expr, val = self.history.pop()
        if "=" in expr:
            var = expr.split("=", 1)[0].strip()
            if var in self.vars:
                del self.vars[var]

    def clear(self) -> None:
        self.vars.clear()
        self.history.clear()

    def _eval_expr(self, expr: str, trace: bool) -> Tuple[Any, List[str]]:
        try:
            node = ast.parse(expr, mode="eval")
        except SyntaxError as e:
            raise CalcError(f"Syntax error: {e.msg}")

        tracer: List[str] = []

        def _eval(node_: ast.AST) -> Any:
            if isinstance(node_, ast.Expression):
                return _eval(node_.body)

            if isinstance(node_, ast.Num):  # type: ignore[attr-defined]
                tracer.append(f"num: {node_.n}")
                return node_.n

            if isinstance(node_, ast.Constant):
                tracer.append(f"const: {node_.value}")
                return node_.value

            if isinstance(node_, ast.BinOp):
                left = _eval(node_.left)
                right = _eval(node_.right)
                op_type = type(node_.op)
                if op_type in SAFE_OPERATORS:
                    res = SAFE_OPERATORS[op_type](left, right)
                    tracer.append(f"{left} {node_.op.__class__.__name__} {right} -> {res}")
                    return res
                raise CalcError(f"Unsupported operator: {op_type}")

            if isinstance(node_, ast.UnaryOp):
                operand = _eval(node_.operand)
                op_type = type(node_.op)
                if op_type in SAFE_OPERATORS:
                    res = SAFE_OPERATORS[op_type](operand)
                    tracer.append(f"{node_.op.__class__.__name__} {operand} -> {res}")
                    return res
                raise CalcError(f"Unsupported unary operator: {op_type}")

            if isinstance(node_, ast.Call):
                if not isinstance(node_.func, ast.Name):
                    raise CalcError("Only simple function calls allowed")
                fname = node_.func.id
                if fname not in SAFE_FUNCS:
                    raise CalcError(f"Function not allowed: {fname}")
                args = [_eval(a) for a in node_.args]
                res = SAFE_FUNCS[fname](*args)
                tracer.append(f"{fname}({', '.join(map(str,args))}) -> {res}")
                return res

            if isinstance(node_, ast.Name):
                idn = node_.id
                if idn in self.vars:
                    val = self.vars[idn]
                    tracer.append(f"var {idn} -> {val}")
                    return val
                if idn in SAFE_CONSTS:
                    val = SAFE_CONSTS[idn]
                    tracer.append(f"const {idn} -> {val}")
                    return val
                raise CalcError(f"Unknown identifier: {idn}")

            raise CalcError(f"Unsupported expression: {ast.dump(node_)}")

        result = _eval(node)
        if not trace:
            tracer = []
        return result, tracer
