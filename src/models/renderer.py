from typing import List
from .core import Graph, Drone

class Renderer:
    COLORS = {
        "none": "\033[0m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }

    def __init__(self, graph: Graph, drones: List[Drone]) -> None:
        self.graph: Graph = graph
        self.drones: List[Drone] = drones

    def render(self, turn: int) -> None:
        print(f"\n========== TOUR {turn} ==========")
        
        # Affichage des zones
        print("--- ÉTAT DES ZONES ---")
        for zone_name, zone in self.graph.zones.items():
            color_code = self.COLORS.get(zone.color, self.COLORS["reset"])
            drone_list = ", ".join(str(d) for d in zone.drones)
            occupancy = f"({len(zone.drones)}/{zone.max_drones})"
            
            zone_desc = f"{color_code}[{zone_name} - {zone.zone_type}]{self.COLORS['reset']} {occupancy}"
            if drone_list:
                zone_desc += f" -> Drones présents: {drone_list}"
                
            print(zone_desc)
            
        # Affichage des drones
        print("--- ÉTAT DES DRONES ---")
        for drone in self.drones:
            status_color = self.COLORS["green"] if drone.status == "arrived" else self.COLORS["yellow"]
            print(f"Drone {drone.id} | Statut: {status_color}{drone.status}{self.COLORS['reset']} | Position: {drone.current_zone}")
            
        print("===============================\n")
