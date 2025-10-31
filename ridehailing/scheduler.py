from typing import List, Tuple
from .models import Vehicle, Order
from .utils import euclidean_distance_km, travel_time_seconds


def km_match(vehicles: List[Vehicle], orders: List[Order], current_time: float = 0.0, max_distance_km: float = 20.0) -> List[Tuple[int,int]]:
    """
    Compute matching pairs (vehicle_index, order_index) using Hungarian algorithm maximizing total score.
    We convert scores to costs by negation. Unmatchable pairs get a large cost.
    """
    try:
        import numpy as np
        from scipy.optimize import linear_sum_assignment
    except Exception:
        # if numpy/scipy not available, fallback to empty matching
        return []
    n = len(vehicles)
    m = len(orders)
    if n == 0 or m == 0:
        return []
    cost = np.full((n, m), 1e6)
    for i, v in enumerate(vehicles):
        vx, vy = v.position_at(current_time)
        for j, o in enumerate(orders):
            dist = euclidean_distance_km(vx, vy, o.x_from, o.y_from)
            if dist <= max_distance_km:
                eta = travel_time_seconds(dist, v.speed_kmph)
                score = -eta  # smaller eta better => higher score; convert to cost by negation
                cost[i, j] = -score
    row_ind, col_ind = linear_sum_assignment(cost)
    pairs = []
    for r, c in zip(row_ind, col_ind):
        if cost[r, c] < 1e5:
            pairs.append((r, c))
    return pairs


def nearest_match(vehicles: List[Vehicle], orders: List[Order], current_time: float = 0.0, max_distance_km: float = 20.0) -> List[Tuple[int,int]]:
    pairs = []
    used_v = set()
    used_o = set()
    for j, o in enumerate(orders):
        best_i = None
        best_dist = float('inf')
        for i, v in enumerate(vehicles):
            if i in used_v:
                continue
            vx, vy = v.position_at(current_time)
            dist = euclidean_distance_km(vx, vy, o.x_from, o.y_from)
            if dist < best_dist and dist <= max_distance_km:
                best_dist = dist
                best_i = i
        if best_i is not None:
            pairs.append((best_i, j))
            used_v.add(best_i)
            used_o.add(j)
    return pairs
