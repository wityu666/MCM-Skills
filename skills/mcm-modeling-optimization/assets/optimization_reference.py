"""Original independent linear objective/feasibility checks and bounded enumeration."""
import itertools
import math
from numbers import Integral, Real


def _finite(value, name):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be real")
    original = value
    try:
        value = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} is outside floating-point range") from exc
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if isinstance(original, Integral) and int(value) != original:
        raise ValueError(f"{name} loses integer precision; rescale or use exact arithmetic")
    return value


def _vector(values, size, name):
    values = [_finite(x, name) for x in values]
    if len(values) != size:
        raise ValueError(f"{name} dimension mismatch")
    return values


def _dot(row, values):
    try:
        result = math.fsum(a * b for a, b in zip(row, values))
    except OverflowError as exc:
        raise ValueError("computed scalar overflowed") from exc
    if not math.isfinite(result):
        raise ValueError("computed scalar is nonfinite")
    if all(a.is_integer() and b.is_integer() for a, b in zip(row, values)):
        exact = sum(int(a) * int(b) for a, b in zip(row, values))
        if int(result) != exact:
            raise ValueError("computed scalar loses integer precision; rescale or use exact arithmetic")
    return result


def check_linear_candidate(c, x, *, A_ub=None, b_ub=None, A_eq=None, b_eq=None,
                           lower=None, upper=None, integer_indices=(), atol=1e-9, rtol=1e-9):
    """Check explicit constraints only; no default nonnegativity is invented."""
    c = [_finite(value, "objective coefficient") for value in c]
    if not c:
        raise ValueError("objective must contain at least one variable")
    n = len(c)
    x = _vector(x, n, "candidate")
    atol, rtol = _finite(atol, "atol"), _finite(rtol, "rtol")
    if atol < 0 or rtol < 0:
        raise ValueError("tolerances must be nonnegative")
    checks = []
    def add(kind, index, lhs, rhs, violation, tolerance):
        if not math.isfinite(violation) or not math.isfinite(tolerance):
            raise ValueError("constraint residual or tolerance overflowed; rescale units")
        checks.append(dict(kind=kind, index=index, lhs=lhs, rhs=rhs,
                           violation=violation, allowed=tolerance, passed=violation <= tolerance))
    for kind, matrix, rhs in (('inequality', A_ub, b_ub), ('equality', A_eq, b_eq)):
        if matrix is None:
            if rhs is not None:
                raise ValueError(f"{kind} right-hand sides have no matrix")
            continue
        rows = [_vector(row, n, kind) for row in matrix]
        if rhs is None:
            raise ValueError(f"{kind} matrix has no right-hand sides")
        rhs = _vector(rhs, len(rows), kind + ' rhs')
        for i, (row, limit) in enumerate(zip(rows, rhs)):
            lhs = _dot(row, x)
            violation = max(lhs - limit, 0.0) if kind == 'inequality' else abs(lhs - limit)
            add(kind, i, lhs, limit, violation, atol + rtol * max(abs(lhs), abs(limit)))
    lower = [None] * n if lower is None else list(lower)
    upper = [None] * n if upper is None else list(upper)
    if len(lower) != n or len(upper) != n:
        raise ValueError("bound dimension mismatch")
    for i in range(n):
        lo = None if lower[i] is None else _finite(lower[i], "lower bound")
        hi = None if upper[i] is None else _finite(upper[i], "upper bound")
        if lo is not None and hi is not None and lo > hi:
            raise ValueError("lower bound exceeds upper bound")
        if lo is not None:
            add('lower', i, x[i], lo, max(lo - x[i], 0.0), atol + rtol * max(abs(x[i]), abs(lo)))
        if hi is not None:
            add('upper', i, x[i], hi, max(x[i] - hi, 0.0), atol + rtol * max(abs(x[i]), abs(hi)))
    for i in integer_indices:
        if isinstance(i, bool) or not isinstance(i, Integral) or not 0 <= i < n:
            raise ValueError("invalid integer-variable index")
        # Relative tolerance is deliberately not applied to integrality.
        add('integer', i, x[i], round(x[i]), abs(x[i] - round(x[i])), atol)
    return dict(objective=_dot(c, x), feasible=all(row['passed'] for row in checks),
                checks=checks, tolerance_rule='atol+rtol*max(abs(lhs),abs(rhs)); integers use atol')


def enumerate_integer_box(c, bounds, *, A_ub=None, b_ub=None, A_eq=None, b_eq=None,
                          max_points=1_000_000, atol=1e-9, rtol=1e-9):
    """Exact finite-box search for a minimization problem; not an unbounded solver."""
    c = list(c);bounds = list(bounds)
    if not c or len(c) != len(bounds):
        raise ValueError("objective and integer bounds need equal nonzero dimensions")
    if isinstance(max_points, bool) or not isinstance(max_points, Integral) or max_points <= 0:
        raise ValueError("max_points must be a positive integer")
    ranges=[];count=1
    for pair in bounds:
        if len(pair) != 2:
            raise ValueError("each bound must be a lower/upper pair")
        lo,hi=pair
        if any(isinstance(v, bool) or not isinstance(v, Integral) for v in (lo,hi)) or lo > hi:
            raise ValueError("finite ordered integer bounds are required")
        lo, hi = int(lo), int(hi)
        count *= hi - lo + 1
        if count > max_points:
            raise ValueError("enumeration budget exceeded")
        ranges.append(range(lo, hi + 1))
    # A one-shot iterator must define the same constraints at every point.
    A_ub = None if A_ub is None else [list(row) for row in A_ub]
    A_eq = None if A_eq is None else [list(row) for row in A_eq]
    b_ub = None if b_ub is None else list(b_ub)
    b_eq = None if b_eq is None else list(b_eq)
    best=None;feasible=0
    for point in itertools.product(*ranges):
        report=check_linear_candidate(c, point, A_ub=A_ub,b_ub=b_ub,A_eq=A_eq,b_eq=b_eq,
                                      atol=atol,rtol=rtol)
        if report['feasible']:
            feasible+=1
            if best is None or report['objective'] < best['objective']:
                best=dict(x=point,objective=report['objective'],checks=report['checks'])
    return dict(status='OPTIMAL_ENUMERATED' if best else 'INFEASIBLE_ENUMERATED',
                objective=None if best is None else best['objective'],
                x=None if best is None else best['x'],search_points=count,
                feasible_points=feasible,scope='provided finite integer box only')
