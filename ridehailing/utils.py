import math

KM_IN_KM = 1.0

def euclidean_distance_km(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    return math.hypot(dx, dy)

def travel_time_seconds(distance_km: float, speed_kmph: float, speed_scale: float = 1.0) -> float:
    # speed_scale models traffic: <1 slower, >1 faster
    if speed_kmph <= 0:
        return float('inf')
    hours = distance_km / (speed_kmph * speed_scale)
    return hours * 3600.0
