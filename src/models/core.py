from typing import List, Dict, Optional, Tuple
import heapq

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
        self._path_cache: Dict[Tuple[str, str], Optional[List[str]]] = {}
    
    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone
        self.adjacency[zone.name] = []

    def add_connection(self, conn: Connection) -> None:
        self.connections.append(conn)
        # bidirectionnel
        self.adjacency[conn.zone1].append(conn.zone2)
        self.adjacency[conn.zone2].append(conn.zone1)

    def get_neighbors(self, zone_name: str) -> List[str]:
        return self.adjacency.get(zone_name, [])

    def find_shortest_path(self, start: str, end: str, avoid_zones: Optional[List[str]] = None) -> Optional[List[str]]:
        if start not in self.zones or end not in self.zones:
            return None
            
        avoid = avoid_zones if avoid_zones is not None else []

        # Vérifier le cache (la clé doit inclure les zones à éviter)
        cache_key = (start, end, tuple(sorted(avoid)))
        if cache_key in self._path_cache:
            return self._path_cache[cache_key]

        distances: Dict[str, float] = {node: float('inf') for node in self.zones}
        distances[start] = 0.0
        previous_nodes: Dict[str, Optional[str]] = {node: None for node in self.zones}

        # File de priorité: (coût_cumulé, nom_zone)
        pq: List[Tuple[float, str]] = [(0.0, start)]

        while pq:
            current_distance, current_zone = heapq.heappop(pq)

            if current_zone == end:
                break

            if current_distance > distances[current_zone]:
                continue

            for neighbor in self.adjacency.get(current_zone, []):
                neighbor_zone = self.zones[neighbor]
                
                # Exclure les zones blocked ET les zones à éviter temporairement
                if neighbor_zone.zone_type == "blocked" or neighbor in avoid:
                    continue

                # Calcul du coût du tronçon
                cost = 1.0 # default/normal
                if neighbor_zone.zone_type == "restricted":
                    cost = 2.0
                elif neighbor_zone.zone_type == "priority":
                    cost = 0.9 # Moins que 1 pour favoriser

                distance = current_distance + cost

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_zone
                    heapq.heappush(pq, (distance, neighbor))

        if distances[end] == float('inf'):
            self._path_cache[cache_key] = None
            return None

        # Reconstruire le chemin
        path = []
        curr = end
        while curr is not None:
            path.append(curr)
            curr = previous_nodes[curr]
            
        path.reverse()
        
        # Sauvegarder dans le cache
        self._path_cache[cache_key] = path
        return path

    def find_disjoint_paths(self, start: str, end: str, max_paths: int = 3) -> List[List[str]]:
        paths = []
        avoid_zones = []
        
        for _ in range(max_paths):
            new_path = self.find_shortest_path(start, end, avoid_zones)
            if not new_path:
                break # Plus de chemin disponible
                
            paths.append(new_path)
            
            # Ajouter les noeuds intermédiaires de ce chemin aux zones à éviter
            # On n'ajoute ni le noeud de départ, ni le noeud d'arrivée
            for node in new_path[1:-1]:
                if node not in avoid_zones:
                    avoid_zones.append(node)
                    
        return paths

class Drone:
    def __init__(self, drone_id: int, current_zone: Optional[str] = None) -> None:
        self.id: int = drone_id
        self.current_zone: Optional[str] = current_zone
        self.planned_path: List[str] = []
        self.status: str = "waiting"  # "waiting", "in_flight", "arrived", etc.
