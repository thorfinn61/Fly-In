from typing import List
from .core import Graph, Drone

class Scheduler:
    def __init__(self, graph: Graph, drones: List[Drone]) -> None:
        self.graph: Graph = graph
        self.drones: List[Drone] = drones

    def assign_paths(self, start: str, end: str) -> None:
        # Trouver plusieurs chemins disjoints (par ex. 3) pour éviter les bouchons
        paths = self.graph.find_disjoint_paths(start, end, max_paths=3)
        if not paths:
            return
            
        # Assigne les chemins en boucle (Round-Robin) pour paralléliser les drones
        path_idx = 0
        for drone in self.drones:
            if not drone.planned_path and drone.status != "arrived":
                drone.planned_path = paths[path_idx].copy()
                drone.status = "waiting"
                path_idx = (path_idx + 1) % len(paths)

    def resolve_conflicts(self) -> None:
        # 1. Initialiser l'usage des connexions pour ce tour
        link_usage = {}
        for conn in self.graph.connections:
            # Clé unique pour chaque arête peu importe le sens
            key = tuple(sorted([conn.zone1, conn.zone2]))
            link_usage[key] = {'used': 0, 'max': conn.max_link_capacity}

        move_intents = []
        for drone in self.drones:
            if drone.planned_path and len(drone.planned_path) > 1:
                move_intents.append({
                    'drone': drone,
                    'from': drone.planned_path[0],
                    'to': drone.planned_path[1]
                })

        approved_moves = []
        moved_drones = set()

        # Phase 1: Les drones en zone "restricted" DOIVENT FORCÉMENT transiter.
        for intent in move_intents:
            drone = intent['drone']
            curr_zone = self.graph.zones[intent['from']]
            if curr_zone.zone_type == "restricted":
                approved_moves.append(intent)
                moved_drones.add(drone.id)
                
                link_key = tuple(sorted([intent['from'], intent['to']]))
                if link_key in link_usage:
                    link_usage[link_key]['used'] += 1

        # Phase 2: Autorisation itérative avec "Libération même tour"
        # On passe en boucle jusqu'à ce qu'il n'y ait plus de nouveaux mouvements possibles
        changed = True
        while changed:
            changed = False
            for intent in move_intents:
                drone = intent['drone']
                if drone.id in moved_drones:
                    continue
                    
                target_zone = self.graph.zones[intent['to']]
                link_key = tuple(sorted([intent['from'], intent['to']]))
                
                # Check 1: La connexion a-t-elle de la place ?
                if link_key in link_usage and link_usage[link_key]['used'] >= link_usage[link_key]['max']:
                    drone.status = "waiting"
                    continue
                
                # Check 2: Capacité de la zone cible avec anticipation de libération
                # Drones y étant physiquement...
                current_occupants = set(target_zone.drones)
                # ... moins ceux qui ont eu l'autorisation d'en partir ce tour-ci
                for am in approved_moves:
                    if am['from'] == target_zone.name:
                        current_occupants.discard(str(am['drone'].id))
                # ... plus ceux qui ont déjà obtenu l'autorisation d'y entrer
                incoming = sum(1 for am in approved_moves if am['to'] == target_zone.name)
                
                projected_occupancy = len(current_occupants) + incoming
                
                if projected_occupancy < target_zone.max_drones:
                    approved_moves.append(intent)
                    moved_drones.add(drone.id)
                    if link_key in link_usage:
                        link_usage[link_key]['used'] += 1
                    changed = True
                else:
                    # En attente, peut-être débloqué à la prochaine itération si qqn s'en va
                    drone.status = "waiting"

        # Note: Pour un deadlock complet circulaire (A veut aller sur B, B sur A, zones pleines), 
        # la boucle `while` s'arrêtera sagement sans rien approuver. Ils restent "waiting".
        
        # Phase 3: Application "atomique"
        # On retire les drones de partout d'abord
        for move in approved_moves:
            drone = move['drone']
            current_zone = move['from']
            if str(drone.id) in self.graph.zones[current_zone].drones:
                self.graph.zones[current_zone].drones.remove(str(drone.id))
        
        # On les rajoute à l'arrivée
        for move in approved_moves:
            drone = move['drone']
            target_zone = move['to']
            self.graph.zones[target_zone].drones.append(str(drone.id))
            
            drone.current_zone = target_zone
            drone.planned_path.pop(0)
            drone.moves += 1
            drone.status = "in_flight"

            if len(drone.planned_path) == 1:
                drone.status = "arrived"
                # Important: On pourrait gérer ici s'ils libèrent la zone d'arrivée une fois posés ou non