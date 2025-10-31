import os
import json
import heapq
from typing import List, Tuple
from .models import Vehicle, Order, VehicleState, OrderState
from .config import load_config
from .scheduler import km_match, nearest_match
from .utils import euclidean_distance_km, travel_time_seconds
from .metrics import Metrics


class Simulator:
    """Event-driven simulator.

    Events: ('order_arrival', order_id), ('dispatch', None), ('pickup', order_id), ('complete', order_id)
    """

    def __init__(self, cfg_path: str):
        cfg = load_config(cfg_path).raw
        self.cfg = cfg
        self.time = 0.0
        self.vehicles: List[Vehicle] = []
        self.orders: List[Order] = []
        self.logs_dir = cfg['output'].get('logs_dir', 'logs')
        self.out_dir = cfg['output'].get('out_dir', 'output')
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.out_dir, exist_ok=True)
        self.logf = open(os.path.join(self.logs_dir, 'events.jsonl'), 'w')
        self.event_queue: List[Tuple[float, int, Tuple[str, int]]] = []  # (time, seq, (etype, id))
        self.seq = 0
        self.metrics = Metrics()

    def load_data(self, vehicles_csv: str, orders_csv: str):
        import pandas as pd
        vdf = pd.read_csv(vehicles_csv)
        odf = pd.read_csv(orders_csv)
        self.vehicles = [Vehicle(int(r.vid), float(r.x), float(r.y)) for _, r in vdf.iterrows()]
        self.orders = [Order(int(r.oid), float(r.x_from), float(r.y_from), float(r.x_to), float(r.y_to), float(r.request_time)) for _, r in odf.iterrows()]
        # push order arrival events
        for o in self.orders:
            self._push_event(o.request_time, ('order_arrival', o.oid))
        # schedule first dispatch at t=0
        self._push_event(0.0, ('dispatch', -1))

    def _push_event(self, t: float, payload: Tuple[str, int]):
        heapq.heappush(self.event_queue, (t, self.seq, payload))
        self.seq += 1

    def log_event(self, obj: dict):
        self.logf.write(json.dumps(obj) + "\n")

    def _find_vehicle_by_vid(self, vid: int):
        return next((v for v in self.vehicles if v.vid == vid), None)

    def _find_order_by_oid(self, oid: int):
        return next((o for o in self.orders if o.oid == oid), None)

    def run(self):
        duration_hours = self.cfg['simulation'].get('duration_hours', 1)
        end_time = duration_hours * 3600.0
        strategy = self.cfg['scheduler'].get('strategy', 'km')
        max_dist = self.cfg['scheduler'].get('max_match_distance_km', 20.0)
        dispatch_interval = self.cfg['simulation'].get('dispatch_interval_sec', 60)

        while self.event_queue:
            t, _, payload = heapq.heappop(self.event_queue)
            if t > end_time:
                break
            self.time = t
            etype, oid = payload
            if etype == 'order_arrival':
                o = self._find_order_by_oid(oid)
                if o is None:
                    continue
                # orders are already in PENDING by default
                self.log_event({'time': self.time, 'event': 'order_arrival', 'oid': o.oid})
            elif etype == 'dispatch':
                # collect pending orders and idle & online vehicles
                pending_orders = [o for o in self.orders if o.state == OrderState.PENDING and o.request_time <= self.time]
                idle_vehicles = [v for v in self.vehicles if v.state == VehicleState.IDLE and v.available_at <= self.time and v.online]
                if pending_orders and idle_vehicles:
                    if strategy == 'km':
                        pairs = km_match(idle_vehicles, pending_orders, max_distance_km=max_dist)
                    else:
                        pairs = nearest_match(idle_vehicles, pending_orders, max_distance_km=max_dist)
                    for vi_idx, oi_idx in pairs:
                        v = idle_vehicles[vi_idx]
                        o = pending_orders[oi_idx]
                        # assign and set vehicle to to-pickup state
                        v.state = VehicleState.TO_PICKUP
                        v.target_order_id = o.oid
                        # mark order as being picked up
                        o.state = OrderState.BEING_PICKED_UP
                        o.assigned_vid = v.vid
                        # schedule pickup arrival event
                        dist = euclidean_distance_km(v.x, v.y, o.x_from, o.y_from)
                        tt = travel_time_seconds(dist, v.speed_kmph)
                        pickup_time = self.time + tt
                        self._push_event(pickup_time, ('pickup', o.oid))
                        self.log_event({'time': self.time, 'event': 'assigned', 'vid': v.vid, 'oid': o.oid, 'eta': tt})
                # schedule next dispatch
                self._push_event(self.time + dispatch_interval, ('dispatch', -1))
            elif etype == 'pickup':
                o = self._find_order_by_oid(oid)
                if o is None or o.state != OrderState.BEING_PICKED_UP:
                    continue
                v = self._find_vehicle_by_vid(o.assigned_vid)
                if v is None:
                    continue
                # vehicle arrives at pickup: update states
                o.pickup_time = self.time
                v.x, v.y = o.x_from, o.y_from
                v.state = VehicleState.TO_DROPOFF
                o.state = OrderState.BEING_DROPPED_OFF
                # schedule completion
                trip_dist = euclidean_distance_km(o.x_from, o.y_from, o.x_to, o.y_to)
                trip_tt = travel_time_seconds(trip_dist, v.speed_kmph)
                complete_time = self.time + trip_tt
                self._push_event(complete_time, ('complete', o.oid))
                # record waiting time metric
                wait = o.pickup_time - o.request_time
                self.metrics.record_wait_time(o.request_time, wait)
                self.log_event({'time': self.time, 'event': 'pickup', 'vid': v.vid, 'oid': o.oid, 'wait': wait, 'trip_eta': trip_tt})
            elif etype == 'complete':
                o = self._find_order_by_oid(oid)
                if o is None or o.state not in (OrderState.ASSIGNED, OrderState.PENDING):
                    continue
                v = self._find_vehicle_by_vid(o.assigned_vid) if o.assigned_vid is not None else None
                o.complete_time = self.time
                o.state = OrderState.COMPLETED
                if v:
                    # move vehicle to dropoff point and free it
                    v.x, v.y = o.x_to, o.y_to
                    v.state = VehicleState.IDLE
                    v.target_order_id = None
                    v.available_at = self.time
                # record trip metric
                trip_time = o.complete_time - (o.pickup_time or o.request_time)
                self.metrics.record_trip(o.request_time, trip_time)
                self.log_event({'time': self.time, 'event': 'complete', 'vid': v.vid if v else None, 'oid': o.oid, 'trip_time': trip_time})

        # finish
        self.logf.close()
        # write metrics
        metrics_csv = os.path.join(self.out_dir, 'metrics.csv')
        self.metrics.to_csv(metrics_csv)
        # optionally generate a simple plot
        try:
            import matplotlib.pyplot as plt
            times, waits = self.metrics.timeseries()
            plt.plot(times, waits)
            plt.xlabel('time (s)')
            plt.ylabel('avg wait (s)')
            plt.title('Average wait time')
            plt.tight_layout()
            plt.savefig(os.path.join(self.out_dir, 'avg_wait.png'))
            plt.close()
        except Exception:
            pass
