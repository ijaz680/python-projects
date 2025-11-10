import math
import pytest
from pycalcx.calculator import Calculator, CalcError


def test_basic_arithmetic():
    c = Calculator()
    assert c.eval("2+3")[0] == 5
    assert c.eval("10 - 4")[0] == 6
    assert c.eval("2*3 + 1")[0] == 7


def test_power_and_mod():
    c = Calculator()
    assert c.eval("2**3")[0] == 8
    assert c.eval("10 % 3")[0] == 1


def test_functions_and_consts():
    c = Calculator()
    val, _ = c.eval("sin(pi/2)")
    assert pytest.approx(val, rel=1e-6) == 1.0
    val, _ = c.eval("sqrt(16)")
    assert val == 4


def test_assign_and_vars_and_undo():
    c = Calculator()
    val, _ = c.eval("a = 5")
    assert val == 5
    assert c.vars["a"] == 5
    c.eval("b = a * 2")
    assert c.vars["b"] == 10
    c.undo()
    assert "b" not in c.vars


def test_history():
    c = Calculator()
    c.eval("1+1")
    c.eval("x=3")
    assert len(c.history) == 2


def test_trace_output():
    c = Calculator()
    val, trace = c.eval("2+3*4", trace=True)
    assert val == 14
    assert any("Mult" in t or "num" in t or "Add" in t for t in trace)


def test_errors():
    c = Calculator()
    with pytest.raises(CalcError):
        c.eval("import os")
