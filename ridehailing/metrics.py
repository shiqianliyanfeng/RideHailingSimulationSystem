from typing import List, Tuple
import csv


class Metrics:
    def __init__(self):
        self.waits: List[float] = []
        self.trips: List[float] = []
        # timeseries buckets (simple): record avg wait per hour
        self.wait_buckets = {}

    def record_wait_time(self, request_time: float, wait_sec: float):
        self.waits.append(wait_sec)
        hour = int(request_time // 3600)
        self.wait_buckets.setdefault(hour, []).append(wait_sec)

    def record_trip(self, request_time: float, trip_sec: float):
        self.trips.append(trip_sec)

    def to_csv(self, path: str):
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['metric', 'value'])
            if self.waits:
                w.writerow(['avg_wait_s', sum(self.waits) / len(self.waits)])
            else:
                w.writerow(['avg_wait_s', ''])
            if self.trips:
                w.writerow(['avg_trip_s', sum(self.trips) / len(self.trips)])
            else:
                w.writerow(['avg_trip_s', ''])

    def timeseries(self):
        hours = sorted(self.wait_buckets.keys())
        times = []
        values = []
        for h in hours:
            times.append(h * 3600)
            vals = self.wait_buckets.get(h, [])
            values.append(sum(vals) / len(vals) if vals else 0.0)
        return times, values
