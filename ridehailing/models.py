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
