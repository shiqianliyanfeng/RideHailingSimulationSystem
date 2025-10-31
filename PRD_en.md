Based on the business requirements for a ride-hailing dispatch system, I designed a complete simulation architecture. The system follows a layered design and covers core modules including user interaction, dispatch optimization, vehicle simulation, and data analysis.

Core functional modules

Order Management Module

Handles user ride requests, order lifecycle tracking and order cancellation. When a user submits a trip request with pickup and drop-off locations, the system creates a pending order for dispatch. Users may cancel orders before a vehicle arrives; the system must update order states in real time. This module records key information such as order creation time, estimated fare, and actual completion time to support downstream analytics.

Vehicle Management Module

Manages vehicle metadata and real-time status. Each vehicle has a unique identifier, current location, state (idle, en route to pickup, en route to dropoff), capacity, etc. Vehicle positions are obtained from a GPS device and can be visualized on a system map. The vehicle state machine defines valid transitions to ensure the dispatch logic is consistent.

Dispatch Optimization Module

This is the core component; it uses the KM algorithm for optimal vehicle-order assignment. The system runs a dispatch round every minute, builds a bipartite graph between available vehicles and unassigned orders, and computes edge weights based on estimated time for a vehicle to reach the passenger, route alignment, vehicle-type compatibility, and other factors. The KM (Hungarian) algorithm finds the maximum-weight matching in polynomial time, maximizing overall dispatch efficiency.

Routing Module

Provides route planning for vehicles. Dijkstra or A* can be used to compute shortest paths, taking into account real-time traffic and road restrictions.

Simulation Engine

Drives the entire system, maintaining the simulation clock and an event queue. The engine advances time in fixed steps (or by events), coordinates modules, and ensures timeline consistency across the simulation.

Dispatch Algorithm Implementation

KM implements one-to-one vehicle-order matching during each dispatch round. The algorithm builds a bipartite graph where one partition is available vehicles and the other is pending orders. Edge weights are computed from multiple factors, including vehicle ETA to pickup, route alignment, and vehicle type match. By updating labels and finding augmenting paths, KM/Hungarian yields the maximum-weight matching.

Logging

From the moment a user places an order, events are logged to a file. The dispatch module polls available vehicles and pending orders then runs the KM algorithm. Assignments are dispatched to vehicles, vehicle state transitions are logged (en route to pickup, pickup, en route to dropoff, completion), and after completion the vehicle returns to the idle state. All state changes are persisted to logs.

This design addresses practical ride-hailing dispatch needs: modularity, optimization-based matching, and thorough logging for analysis.
