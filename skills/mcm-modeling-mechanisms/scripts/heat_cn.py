"""Constant-coefficient 1D heat equation, homogeneous Dirichlet boundaries.

Original reference implementation. No supplied material code is executed.
"""
import numpy as np
import math
from numbers import Real
from scipy.linalg import solve_banded


def heat_cn(initial, diffusivity, length, final_time, nx, nt):
    """Return x, t, U with U.shape=(nt+1,nx+1), for u_t=C*u_xx.

    nx counts spatial intervals; nt counts time steps. Initial endpoint values
    must represent zero within floating-point roundoff. Crank-Nicolson is
    stable in the linear energy sense; large r can still create oscillations.
    """
    if isinstance(nx, bool) or not isinstance(nx, (int, np.integer)) or nx < 2:
        raise ValueError("nx must be an integer >= 2")
    if isinstance(nt, bool) or not isinstance(nt, (int, np.integer)) or nt < 1:
        raise ValueError("nt must be a positive integer")
    scalars = [diffusivity, length, final_time]
    if any(isinstance(v, (bool, np.bool_)) or not isinstance(v, Real) for v in scalars):
        raise ValueError("C, L and T must be real scalars")
    try:
        diffusivity, length, final_time = map(float, scalars)
    except (ValueError, OverflowError) as exc:
        raise ValueError("C, L and T must be finite real scalars") from exc
    if not all(math.isfinite(v) for v in (diffusivity, length, final_time)) or diffusivity < 0 or length <= 0 or final_time <= 0:
        raise ValueError("require finite C>=0, L>0 and T>0")
    x = np.linspace(0.0, float(length), nx + 1)
    raw_initial = initial(x) if callable(initial) else initial
    if np.iscomplexobj(raw_initial):
        raise ValueError("initial must be real, not complex")
    u0 = np.asarray(raw_initial, dtype=float)
    if u0.shape != (nx + 1,) or not np.isfinite(u0).all():
        raise ValueError("initial must be a finite vector on the spatial grid")
    boundary_tol = 64 * np.finfo(float).eps * max(1.0, float(np.max(np.abs(u0))))
    if abs(u0[0]) > boundary_tol or abs(u0[-1]) > boundary_tol:
        raise ValueError("this implementation requires zero Dirichlet endpoints")
    u0 = u0.copy()
    u0[[0, -1]] = 0.0
    dt, dx = float(final_time) / nt, float(length) / nx
    if dt <= 0 or dx <= 0:
        raise ValueError("time or spatial step underflow; rescale units")
    # Split binary exponents so C*dt and dx**2 need not be representable.
    if diffusivity == 0:
        r = 0.0
    else:
        cm, ce = math.frexp(diffusivity)
        tm, te = math.frexp(dt)
        xm, xe = math.frexp(dx)
        try:
            r = math.ldexp(cm * tm / (xm * xm), ce + te - 2 * xe)
        except OverflowError as exc:
            raise ValueError("step ratio overflow") from exc
    if not np.isfinite(r):
        raise ValueError("step ratio overflow")
    interior_count = nx - 1
    ab = np.zeros((3, interior_count), dtype=float)
    ab[0, 1:] = -r / 2
    ab[1, :] = 1 + r
    ab[2, :-1] = -r / 2
    U = np.zeros((nt + 1, nx + 1), dtype=float)
    U[0] = u0
    for k in range(nt):
        v = U[k, 1:-1]
        rhs = (1 - r) * v
        rhs[:-1] += (r / 2) * v[1:]
        rhs[1:] += (r / 2) * v[:-1]
        if not np.isfinite(rhs).all():
            raise FloatingPointError("non-finite heat step right-hand side; rescale field")
        U[k + 1, 1:-1] = solve_banded((1, 1), ab, rhs, check_finite=False)
    if not np.isfinite(U).all():
        raise FloatingPointError("non-finite computed heat field")
    return x, np.linspace(0.0, float(final_time), nt + 1), U
