"""Original direction-aware min-max entropy weighting and vector TOPSIS.

Entropy weights measure sample discrimination, not decision-maker preference.
No supplied example code is executed or copied.
"""
import numpy as np


def _oriented(X, benefit=None):
    if np.iscomplexobj(X):
        raise ValueError("indicators must be real, not complex")
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[0] < 2 or X.shape[1] < 1 or not np.isfinite(X).all():
        raise ValueError("require a finite 2D matrix with >=2 objects and >=1 indicator")
    if benefit is None:
        benefit = np.ones(X.shape[1], dtype=bool)
    else:
        benefit = np.asarray(benefit)
        if benefit.dtype != bool or benefit.shape != (X.shape[1],):
            raise ValueError("benefit must be one Boolean per indicator")
    low, high = X.min(axis=0), X.max(axis=0)
    with np.errstate(over="ignore", invalid="ignore"):
        span = high - low
    if not np.isfinite(span).all():
        raise ValueError("indicator range overflow; rescale units first")
    active = span > 0
    Z = np.zeros_like(X)
    Z[:, active] = (X[:, active] - low[active]) / span[active]
    cost = active & ~benefit
    Z[:, cost] = 1 - Z[:, cost]
    return Z, active


def entropy_profile(X, benefit=None):
    Z, active = _oriented(X, benefit)
    n, m = Z.shape
    P = np.full_like(Z, 1.0/n)
    P[:, active] = Z[:, active] / Z[:, active].sum(axis=0)
    plogp = np.zeros_like(P)
    nonzero = P > 0
    plogp[nonzero] = P[nonzero] * np.log(P[nonzero])
    entropy = np.clip(-plogp.sum(axis=0)/np.log(n), 0., 1.)
    information = np.maximum(1 - entropy, 0.)
    information[~active] = 0.
    total = information.sum()
    weights = information/total if total > 0 else np.zeros(m)
    return dict(weights=weights, probabilities=P, entropy=entropy, active=active,
                oriented=Z, status="OK" if total > 0 else "NO_DISCRIMINATION")


def topsis(X, weights, benefit=None):
    Z, active = _oriented(X, benefit)
    if np.iscomplexobj(weights):
        raise ValueError("weights must be real, not complex")
    w = np.asarray(weights, dtype=float)
    if w.shape != (Z.shape[1],) or not np.isfinite(w).all() or np.any(w < 0):
        raise ValueError("weights must be finite, nonnegative, one per indicator")
    scale = float(np.max(w))
    if scale <= 0:
        if active.any(): raise ValueError("nonconstant indicators require positive total weight")
        return dict(scores=np.full(Z.shape[0], .5), status="NO_DISCRIMINATION", weights=w.copy())
    # Scaling first avoids overflow of the sum for individually finite weights.
    positive = w > 0
    w = w/scale
    w = w/w.sum()
    if np.any(positive & active & (w == 0)):
        raise ValueError("active weight ratio underflow; remove constant indicators or revise weight range")
    norm = np.linalg.norm(Z, axis=0)
    R = np.zeros_like(Z)
    np.divide(Z, norm, out=R, where=norm > 0)
    # Euclidean homogeneity: cancel a common active weight scale before
    # multiplication/squaring, and form closeness before restoring distances.
    distance_scale = float(np.max(w[active])) if active.any() else 0.0
    if distance_scale > 0:
        relative_weights = np.zeros_like(w)
        relative_weights[active] = w[active]/distance_scale
        V = R*relative_weights
        best, worst = V.max(axis=0), V.min(axis=0)
        scaled_plus = np.linalg.norm(V-best, axis=1)
        scaled_minus = np.linalg.norm(V-worst, axis=1)
    else:
        scaled_plus = np.zeros(Z.shape[0])
        scaled_minus = np.zeros(Z.shape[0])
    den = scaled_plus+scaled_minus
    scores = np.full(Z.shape[0], .5)
    np.divide(scaled_minus, den, out=scores, where=den > 0)
    return dict(scores=scores, weights=w, distance_best=scaled_plus*distance_scale,
                distance_worst=scaled_minus*distance_scale, distance_scale=distance_scale,
                scaled_distance_best=scaled_plus, scaled_distance_worst=scaled_minus,
                status="OK" if np.any(den > 0) else "NO_DISCRIMINATION")


def entropy_topsis(X, benefit=None):
    profile = entropy_profile(X, benefit)
    result = topsis(X, profile["weights"], benefit)
    result["entropy_profile"] = profile
    return result
