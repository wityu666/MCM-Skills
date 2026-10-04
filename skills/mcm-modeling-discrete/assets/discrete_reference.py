"""Original stdlib 0-1 knapsack and nonnegative-weight shortest-path references."""
from collections.abc import Mapping
from dataclasses import dataclass
import heapq
import itertools
import math
from numbers import Integral, Real


def _number(value, name):
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


def _integer(value, name):
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return int(value)


@dataclass(frozen=True)
class KnapsackResult:
    selected: tuple
    value: float
    weight: int
    table_value: float


def knapsack01(values, weights, capacity, *, max_states=5_000_000):
    """Solve finite 0-1 knapsack; zero-weight items are allowed once each."""
    values = [_number(v, "value") for v in values]
    weights = [_integer(w, "weight") for w in weights]
    capacity = _integer(capacity, "capacity")
    if len(values) != len(weights):
        raise ValueError("values and weights have different lengths")
    max_states = _integer(max_states, "max_states")
    if not values:
        return KnapsackResult((), 0.0, 0, 0.0)
    n = len(values)
    if (n + 1) * (capacity + 1) > max_states:
        raise ValueError("DP state budget exceeded; use a sparse DP or integer solver")
    table = [[0.0] * (capacity + 1) for _ in range(n + 1)]
    for i, (value, weight) in enumerate(zip(values, weights), 1):
        for available in range(capacity + 1):
            best = table[i - 1][available]
            if weight <= available:
                candidate = table[i - 1][available - weight] + value
                if not math.isfinite(candidate):
                    raise ValueError("objective accumulation overflowed")
                previous = table[i - 1][available - weight]
                if previous.is_integer() and value.is_integer() and int(candidate) != int(previous) + int(value):
                    raise ValueError("objective accumulation loses integer precision; use exact arithmetic")
                best = max(best, candidate)
            table[i][available] = best
    selected = []
    remaining = capacity
    for i in range(n, 0, -1):
        if table[i][remaining] != table[i - 1][remaining]:
            selected.append(i - 1)
            remaining -= weights[i - 1]
    selected.reverse()
    value = math.fsum(values[i] for i in selected)
    weight = sum(weights[i] for i in selected)
    return KnapsackResult(tuple(selected), value, weight, table[n][capacity])


@dataclass(frozen=True)
class ShortestPathResult:
    source: object
    distances: dict
    predecessors: dict

    def path_to(self, target):
        if target not in self.distances:
            raise ValueError("target is absent from the graph")
        if math.isinf(self.distances[target]):
            return None
        path = [target]
        while path[-1] != self.source:
            parent = self.predecessors[path[-1]]
            if parent not in self.distances or parent in path:
                raise RuntimeError("invalid predecessor chain")
            path.append(parent)
        return list(reversed(path))


def dijkstra(graph, source):
    """Adjacency maps may contain zero edges; missing edges are absent keys."""
    if not isinstance(graph, Mapping) or not graph:
        raise ValueError("graph must be a nonempty adjacency mapping")
    adjacency = {}
    for node, edges in graph.items():
        if not isinstance(edges, Mapping):
            raise ValueError("each adjacency row must be a mapping")
        adjacency[node] = {}
        for target, value in edges.items():
            weight = _number(value, "edge weight")
            if weight < 0:
                raise ValueError("Dijkstra requires nonnegative edge weights")
            adjacency[node][target] = weight
    for target in {v for edges in adjacency.values() for v in edges}:
        adjacency.setdefault(target, {})
    if source not in adjacency:
        raise ValueError("source is absent from the graph")
    distance = {node: math.inf for node in adjacency}
    parent = {node: None for node in adjacency}
    distance[source] = 0.0
    serial = itertools.count()
    queue = [(0.0, next(serial), source)]
    overflow_targets = set()
    while queue:
        cost, _, node = heapq.heappop(queue)
        if cost != distance[node]:
            continue
        for target, weight in adjacency[node].items():
            candidate = cost + weight
            if not math.isfinite(candidate):
                # This nonminimal walk may overflow while a finite route exists.
                overflow_targets.add(target)
                continue
            if candidate < distance[target]:
                distance[target], parent[target] = candidate, node
                heapq.heappush(queue, (candidate, next(serial), target))
    if any(math.isinf(distance[target]) for target in overflow_targets):
        raise ValueError("reachable shortest-path cost cannot be represented")
    return ShortestPathResult(source, distance, parent)
