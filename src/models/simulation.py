from typing import List
from .core import Graph, Drone
from .scheduler import Scheduler
from .renderer import Renderer
from parser import MapParser

class Simulation:
    def __init__(self, map_path: str) -> None:
        self.map_path = map_path
        self.renderer = Renderer(self)
        self.is_running = False
        self.reset()
        
    def reset(self) -> None:
        parser = MapParser(self.map_path)
        parser.parse()
        self.graph, self.drones = parser.build_models()
        self.end_hub = parser.end_hub[0] if parser.end_hub else "goal"
        self.scheduler = Scheduler(self.graph, self.drones)
        self.turn = 0
        
        self.renderer.graph = self.graph
        self.renderer.drones = self.drones
        self.renderer.setup_from_graph()

    def step(self) -> None:
        if all(d.status == "arrived" for d in self.drones) or self.turn >= 500:
            self.is_running = False
            return
            
        start = self.drones[0].current_zone if self.drones else "START"
        self.scheduler.assign_paths(start, self.end_hub)
        self.scheduler.resolve_conflicts()
        self.renderer.render(self.turn)
        self.turn += 1

    def run(self) -> None:
        self.renderer.root.mainloop()
