import os
from typing import List
from .core import Graph, Drone
from .scheduler import Scheduler
from .renderer import Renderer
from parser import MapParser


class Simulation:
    def __init__(self, map_path: str) -> None:
        self.map_path = map_path
        self.is_running = False
        self.log_file = "simulation_moves.log"
        
        # Effacer le log au démarrage
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
            
        with open(self.log_file, "w") as f:
            pass # Plus de header
        
        # Charger les données avant de lancer le rendu
        parser = MapParser(self.map_path)
        parser.parse()
        self.graph, self.drones = parser.build_models()
        self.end_hub = parser.end_hub[0] if parser.end_hub else "goal"
        self.scheduler = Scheduler(self.graph, self.drones)
        self.turn = 0
        
        self.renderer = Renderer(self)
        self.renderer.graph = self.graph
        self.renderer.drones = self.drones
        self.renderer.setup_from_graph()

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
        moves = self.scheduler.resolve_conflicts()
        
        # Enregistrement des mouvements dans le log
        if moves:
            # Trie les mouvements pour avoir un ordre consistant, ex: D1, D2, etc. (facultatif mais plus propre)
            moves.sort(key=lambda x: int(x.split('-')[0][1:]))
            with open(self.log_file, "a") as f:
                f.write(" ".join(moves) + "\n")
                    
        self.renderer.render(self.turn)
        self.turn += 1

    def run(self) -> None:
        self.renderer.root.mainloop()
