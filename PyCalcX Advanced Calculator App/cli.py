"""Simple CLI for PyCalcX calculator."""
from pycalcx.calculator import Calculator, CalcError
import sys


def repl():
    calc = Calculator()
    print("PyCalcX v0.1.0 — type expressions, or :help for commands")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line.startswith(":"):
            cmd = line[1:].strip().lower()
            if cmd in ("q", "exit"):
                break
            if cmd == "help":
                print(":vars — show variables")
                print(":history — show history")
                print(":undo — undo last assignment")
                print(":clear — clear vars and history")
                print(":trace on/off — toggle step tracing for each eval (not global)")
                print(":quit — exit")
                continue
            if cmd == "vars":
                if not calc.vars:
                    print("(no vars)")
                for k, v in calc.vars.items():
                    print(f"{k} = {v}")
                continue
            if cmd == "history":
                for e, v in calc.history:
                    print(f"{e} -> {v}")
                continue
            if cmd == "undo":
                try:
                    calc.undo()
                    print("Undone")
                except CalcError as e:
                    print(f"Error: {e}")
                continue
            if cmd == "clear":
                calc.clear()
                print("Cleared")
                continue
            print("Unknown command. Use :help")
            continue

        # expression — support optional trailing 'trace' to enable
        trace = False
        if line.endswith(" trace"):
            trace = True
            expr = line[: -len(" trace")].rstrip()
        else:
            expr = line

        try:
            val, trace_lines = calc.eval(expr, trace=trace)
            print(val)
            if trace and trace_lines:
                print("Trace:")
                for t in trace_lines:
                    print("  ", t)
        except CalcError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    repl()
