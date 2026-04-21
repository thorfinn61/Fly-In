from typing import List, Dict, Optional

class Zone:
    def __init__(self, name: str, x: int, y: int, zone_type: str, color: str = "none", max_drones: int = 1, drones: Optional[List[str]] = None) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.color: str = color
        self.max_drones: int = max_drones
        self.drones: List[str] = drones if drones is not None else []

class Connection:
    def __init__(self, zone1: str, zone2: str, max_link_capacity: int = 1, drones: Optional[List[str]] = None) -> None:
        self.zone1: str = zone1
        self.zone2: str = zone2
        self.max_link_capacity: int = max_link_capacity
        self.drones: List[str] = drones if drones is not None else []

class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.adjacency: Dict[str, List[str]] = {}
    
    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone
        self.adjacency[zone.name] = []

    def add_connection(self, conn: Connection) -> None:
        self.connections.append(conn)
        # bidirectionnel
        self.adjacency[conn.zone1].append(conn.zone2)
        self.adjacency[conn.zone2].append(conn.zone1)

class Drone:
    def __init__(self, drone_id: int, current_zone: Optional[str] = None) -> None:
        self.id: int = drone_id
        self.current_zone: Optional[str] = current_zone
        self.planned_path: List[str] = []
        self.status: str = "waiting"  # "waiting", "in_flight", "arrived", etc.

class Scheduler:
    def __init__(self, graph: Graph, drones: List[Drone]) -> None:
        self.graph: Graph = graph
        self.drones: List[Drone] = drones

class Renderer:
    def __init__(self, graph: Graph, drones: List[Drone]) -> None:
        self.graph: Graph = graph
        self.drones: List[Drone] = drones

class Simulation:
    def __init__(self, graph: Graph, drones: List[Drone]) -> None:
        self.graph: Graph = graph
        self.drones: List[Drone] = drones
        self.scheduler: Scheduler = Scheduler(self.graph, self.drones)
        self.renderer: Renderer = Renderer(self.graph, self.drones)
        self.turn: int = 0
