# services/math_kernel.py
from typing import Dict, Any, List, Optional
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, convert_xor, implicit_multiplication_application
)

TRANSFORMS = standard_transformations + (convert_xor, implicit_multiplication_application)

SAFE_FUNCS = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "exp": sp.exp, "log": sp.log,
    "sqrt": sp.sqrt, "Eq": sp.Eq, "diff": sp.diff, "integrate": sp.integrate,
    "Symbol": sp.Symbol
}

def _parse(s: str):
    return parse_expr(s, local_dict=SAFE_FUNCS, transformations=TRANSFORMS)

def compute(task: str, expr: str, solve_for: Optional[List[str]] = None, subs: Optional[Dict[str, Any]] = None):
    """
    task: 'symbolic' | 'numeric'
    expr: SymPy string or Eq(...)
    solve_for: symbols to solve for
    subs: dict like {"M":"1.0", "r":"4"} (strings parsed via SymPy)
    """
    out = {"steps": [], "symbolic": None, "numeric": None, "interpretation": ""}

    try:
        e = _parse(expr)
        out["steps"].append(f"Parsed: {e}")

        if subs:
            sdict = {sp.Symbol(k): (_parse(v) if isinstance(v, str) else v) for k, v in subs.items()}
            e = e.subs(sdict)
            out["steps"].append(f"Substitutions: {sdict}")

        if task == "symbolic":
            if solve_for:
                syms = [sp.Symbol(n) for n in solve_for]
                sol = sp.solve(e, *syms, dict=True)
                out["symbolic"] = str(sol)
                out["interpretation"] = "Solved symbolically."
            else:
                out["symbolic"] = str(sp.simplify(e))
                out["interpretation"] = "Simplified symbolically."

        elif task == "numeric":
            val = float(e.evalf())
            out["numeric"] = {"value": val}
            out["interpretation"] = "Numeric evaluation complete."

        else:
            out["interpretation"] = "Unknown task."

        return out
    except Exception as err:
        out["interpretation"] = f"Error: {err}"
        return out