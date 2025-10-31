from dataclasses import dataclass
from enum import Enum
from typing import Optional


class VehicleState(str, Enum):
    OFFLINE = "offline"
    IDLE = "idle"  # online and waiting
    TO_PICKUP = "to_pickup"  # 接驾中
    TO_DROPOFF = "to_dropoff"  # 送驾中


@dataclass
class Vehicle:
    vid: int
    x: float
    y: float
    speed_kmph: float = 40.0
    state: VehicleState = VehicleState.IDLE
    online: bool = True
    target_order_id: Optional[int] = None
    available_at: float = 0.0  # simulation time when vehicle becomes available
    # movement tracking: when vehicle is moving, record start/end positions and times
    move_start_time: Optional[float] = None
    move_end_time: Optional[float] = None
    move_start_x: Optional[float] = None
    move_start_y: Optional[float] = None
    move_end_x: Optional[float] = None
    move_end_y: Optional[float] = None

    def position_at(self, t: float):
        """Return interpolated (x,y) position of the vehicle at simulation time t.

        If vehicle is not moving or t is outside the movement interval, return current x,y.
        """
        if self.move_start_time is None or self.move_end_time is None:
            return self.x, self.y
        if t <= self.move_start_time:
            return self.move_start_x if self.move_start_x is not None else self.x, self.move_start_y if self.move_start_y is not None else self.y
        if t >= self.move_end_time:
            return self.move_end_x if self.move_end_x is not None else self.x, self.move_end_y if self.move_end_y is not None else self.y
        # linear interpolation
        span = self.move_end_time - self.move_start_time
        if span <= 0:
            return self.move_end_x if self.move_end_x is not None else self.x, self.move_end_y if self.move_end_y is not None else self.y
        frac = (t - self.move_start_time) / span
        sx = self.move_start_x if self.move_start_x is not None else self.x
        sy = self.move_start_y if self.move_start_y is not None else self.y
        ex = self.move_end_x if self.move_end_x is not None else self.x
        ey = self.move_end_y if self.move_end_y is not None else self.y
        x = sx + (ex - sx) * frac
        y = sy + (ey - sy) * frac
        return x, y


class OrderState(str, Enum):
    PENDING = "pending"
    CANCELLED = "cancelled"
    ASSIGNED = "assigned"
    BEING_PICKED_UP = "being_picked_up"  # 被接驾中
    BEING_DROPPED_OFF = "being_dropped_off"  # 被送驾中
    COMPLETED = "completed"


@dataclass
class Order:
    oid: int
    x_from: float
    y_from: float
    x_to: float
    y_to: float
    request_time: float
    passengers: int = 1
    state: OrderState = OrderState.PENDING
    assigned_vid: Optional[int] = None
    pickup_time: Optional[float] = None
    complete_time: Optional[float] = None
