"""Original reference only: seasonal naive and numeric-time split checks.

The split helper checks observation ordering, not availability of each feature.
gap_steps is a number of sorted observation rows, not elapsed wall-clock time.
"""
from math import isfinite
from numbers import Integral, Real


def _nonnegative_integer(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, Integral) or value < int(positive):
        raise ValueError(f'{name} must be an integer >= {int(positive)}')
    return int(value)


def _numeric_sequence(values, name):
    if isinstance(values, (str, bytes)):
        raise ValueError(f'{name} must be a numeric sequence')
    try:
        result = [float(x) for x in values]
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f'{name} must contain finite numeric values') from exc
    if not all(isfinite(x) for x in result):
        raise ValueError(f'{name} must contain finite numeric values')
    return result


def seasonal_naive(history, period, horizon):
    period = _nonnegative_integer(period, 'period', positive=True)
    horizon = _nonnegative_integer(horizon, 'horizon')
    values = _numeric_sequence(history, 'history')
    if len(values) < period or not all(isfinite(x) for x in values):
        raise ValueError('history must contain at least period finite values')
    cycle = values[-period:]
    return [cycle[i % period] for i in range(horizon)]


def check_temporal_split(times, train_indices, test_indices, gap_steps=0,
                         groups=None, require_group_disjoint=False):
    gap_steps = _nonnegative_integer(gap_steps, 'gap_steps')
    if type(require_group_disjoint) is not bool:
        raise ValueError('require_group_disjoint must be a boolean')
    numeric_times = _numeric_sequence(times, 'times')
    if not numeric_times or not all(isfinite(x) for x in numeric_times):
        raise ValueError('times must be finite numeric observation times')
    if any(a > b for a, b in zip(numeric_times, numeric_times[1:])):
        raise ValueError('observations must be sorted by time')
    train, test = list(train_indices), list(test_indices)
    for name, idx in [('train', train), ('test', test)]:
        if any(isinstance(i, bool) or not isinstance(i, Integral) or not 0 <= i < len(numeric_times) for i in idx):
            raise ValueError(f'{name} index out of bounds or not integer')
        if not idx or len(idx) != len(set(idx)):
            raise ValueError(f'{name} indices must be nonempty and unique')
    train, test = [int(i) for i in train], [int(i) for i in test]
    if set(train) & set(test):
        raise ValueError('train/test rows overlap')
    if max(numeric_times[i] for i in train) >= min(numeric_times[i] for i in test):
        raise ValueError('training times must strictly precede test times')
    if min(test) - max(train) - 1 < gap_steps:
        raise ValueError('insufficient observation-row gap')
    if groups is not None:
        groups = list(groups)
        if len(groups) != len(numeric_times):
            raise ValueError('groups length must equal times length')
    if require_group_disjoint:
        if groups is None:
            raise ValueError('groups are required for group isolation')
        try:
            for index in train + test:
                value = groups[index]
                if value is None or isinstance(value, Real) and not isinstance(value, Integral) and not isfinite(value):
                    raise ValueError('group isolation needs known finite group identifiers')
                hash(value)
        except TypeError as exc:
            raise ValueError('group identifiers must be hashable') from exc
        if {groups[i] for i in train} & {groups[i] for i in test}:
            raise ValueError('train/test groups overlap')
    return {'status': 'PASS', 'train_count': len(train), 'test_count': len(test),
            'gap_steps': gap_steps, 'group_isolation_checked': require_group_disjoint,
            'feature_availability_checked': False}
