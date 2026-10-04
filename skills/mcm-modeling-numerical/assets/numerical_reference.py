"""Original stdlib references for Newton interpolation and safeguarded bisection."""
from dataclasses import dataclass
import math
from numbers import Integral, Real


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a real number")
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


def newton_coefficients(nodes, values):
    """Return divided differences; arbitrary distinct node order is supported."""
    xs = [_number(v, "node") for v in nodes]
    coef = [_number(v, "value") for v in values]
    if not xs or len(xs) != len(coef):
        raise ValueError("nodes and values must have the same nonzero length")
    if len(set(xs)) != len(xs):
        raise ValueError("interpolation nodes must be distinct")
    for order in range(1, len(xs)):
        for j in range(len(xs) - 1, order - 1, -1):
            numerator = coef[j] - coef[j - 1]
            denominator = xs[j] - xs[j - order]
            if not math.isfinite(numerator) or not math.isfinite(denominator):
                raise ValueError("divided-difference subtraction overflowed; rescale inputs")
            coef[j] = numerator / denominator
            if coef[j] == 0 and numerator != 0:
                raise ValueError("divided difference underflowed; rescale inputs")
            if not math.isfinite(coef[j]):
                raise ValueError("divided differences overflowed; rescale the nodes")
    return coef


def newton_evaluate(nodes, coefficients, x):
    xs = [_number(v, "node") for v in nodes]
    cs = [_number(v, "coefficient") for v in coefficients]
    x = _number(x, "query")
    if not xs or len(xs) != len(cs) or len(set(xs)) != len(xs):
        raise ValueError("distinct nodes and coefficients need equal nonzero lengths")
    result = cs[-1]
    for j in range(len(xs) - 2, -1, -1):
        result = cs[j] + (x - xs[j]) * result
    if not math.isfinite(result):
        raise ValueError("polynomial evaluation overflowed")
    return result


def newton_interpolate(nodes, values, x):
    nodes = list(nodes)
    return newton_evaluate(nodes, newton_coefficients(nodes, values), x)


@dataclass(frozen=True)
class BisectionResult:
    root: float
    bracket: tuple
    iterations: int
    residual: float
    stopped_by: str


def bisect(function, left, right, *, xtol=1e-10, ftol=1e-12, max_iter=200):
    """Bracket a root of a continuous real function, with explicit termination."""
    left, right = _number(left, "left"), _number(right, "right")
    xtol, ftol = _number(xtol, "xtol"), _number(ftol, "ftol")
    if left >= right or xtol <= 0 or ftol < 0:
        raise ValueError("need left < right, xtol > 0, ftol >= 0")
    if isinstance(max_iter, bool) or not isinstance(max_iter, Integral) or max_iter <= 0:
        raise ValueError("max_iter must be a positive integer")
    fl, fr = _number(function(left), "f(left)"), _number(function(right), "f(right)")
    if fl == 0:
        return BisectionResult(left, (left, left), 0, abs(fl), "endpoint")
    if fr == 0:
        return BisectionResult(right, (right, right), 0, abs(fr), "endpoint")
    if (fl > 0) == (fr > 0):
        raise ValueError("endpoints do not bracket a sign change")
    for iteration in range(1, max_iter + 1):
        midpoint = left / 2 + right / 2
        fm = _number(function(midpoint), "f(midpoint)")
        if abs(fm) <= ftol:
            return BisectionResult(midpoint, (left, right), iteration, abs(fm), "residual")
        if right / 2 - left / 2 <= xtol:
            return BisectionResult(midpoint, (left, right), iteration, abs(fm), "interval")
        if midpoint == left or midpoint == right:
            raise RuntimeError("floating-point bracket cannot shrink to the requested tolerance")
        if (fm > 0) == (fl > 0):
            left, fl = midpoint, fm
        else:
            right, fr = midpoint, fm
    raise RuntimeError("bisection reached max_iter without meeting tolerance")
