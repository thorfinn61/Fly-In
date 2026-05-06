from typing import List
from .core import Graph, Drone
from .scheduler import Scheduler
from .renderer import Renderer

class Simulation:
    def __init__(self, graph: Graph, drones: List[Drone], end_hub: str) -> None:
        self.graph: Graph = graph
        self.drones: List[Drone] = drones
        self.end_hub: str = end_hub
        self.scheduler: Scheduler = Scheduler(self.graph, self.drones)
        self.renderer: Renderer = Renderer(self.graph, self.drones)
        self.turn: int = 0

    def step(self) -> None:
        # Trouver la zone de départ d'après le premier drone
        start = self.drones[0].current_zone if self.drones else "START"
        self.scheduler.assign_paths(start, self.end_hub)
        self.scheduler.resolve_conflicts()
        self.renderer.render(self.turn)
        self.turn += 1

    def run(self) -> None:
        while any(d.status != "arrived" for d in self.drones) and self.turn < 100:
            self.step()
