from typing import List
from .core import Graph, Drone

class Renderer:
    def __init__(self, graph: Graph, drones: List[Drone]) -> None:
        self.graph: Graph = graph
        self.drones: List[Drone] = drones

    def render(self, turn: int) -> None:
        print(f"--- Tour {turn} ---")
        for drone in self.drones:
            print(f"Drone {drone.id}: {drone.current_zone} -> {drone.status}")
