"""Modèles du domaine : Zone, Connection, Graph et Drone."""

from typing import List, Dict, Optional, Tuple
import heapq


class Zone:
    """Nœud du réseau de drones avec un type, une capacité et une position.

    Attributes:
        name: Identifiant unique de la zone.
        x: Coordonnée X sur la carte.
        y: Coordonnée Y sur la carte.
        zone_type: Type parmi 'normal', 'restricted', 'priority' ou 'blocked'.
        color: Couleur d'affichage pour le rendu visuel.
        max_drones: Nombre maximum de drones autorisés simultanément.
        drones: Liste des identifiants de drones présents dans cette zone.
    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str,
        color: str = "none",
        max_drones: int = 1,
        drones: Optional[List[str]] = None,
    ) -> None:
        """Initialise une Zone.

        Args:
            name: Identifiant unique de la zone.
            x: Coordonnée X.
            y: Coordonnée Y.
            zone_type: Type de comportement de la zone.
            color: Couleur de rendu (défaut 'none').
            max_drones: Limite de capacité (défaut 1).
            drones: Occupants pré-existants (défaut liste vide).
        """
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.color: str = color
        self.max_drones: int = max_drones
        self.drones: List[str] = drones if drones is not None else []


class Connection:
    """Représente un arc bidirectionnel entre deux zones avec une limite de capacité.

    Attributes:
        zone1: Nom de la première zone.
        zone2: Nom de la deuxième zone.
        max_link_capacity: Nombre maximum de drones pouvant traverser simultanément.
        drones: Identifiants des drones en transit sur cette connexion.
    """

    def __init__(
        self,
        zone1: str,
        zone2: str,
        max_link_capacity: int = 1,
        drones: Optional[List[str]] = None,
    ) -> None:
        """Initialise une Connection.

        Args:
            zone1: Nom de la première zone.
            zone2: Nom de la deuxième zone.
            max_link_capacity: Limite de traversée simultanée (défaut 1).
            drones: Drones actuellement sur ce lien (défaut liste vide).
        """
        self.zone1: str = zone1
        self.zone2: str = zone2
        self.max_link_capacity: int = max_link_capacity
        self.drones: List[str] = drones if drones is not None else []


class Graph:
    """Graphe de zones et connexions avec recherche de chemin par Dijkstra.

    Attributes:
        zones: Association nom de zone → objet Zone.
        connections: Liste de tous les objets Connection du réseau.
        adjacency: Liste d'adjacence indexée par nom de zone.
    """

    def __init__(self) -> None:
        """Initialise un graphe vide."""
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.adjacency: Dict[str, List[str]] = {}
        self._path_cache: Dict[
            Tuple[str, str, Tuple[str, ...]], Optional[List[str]]
        ] = {}

    def add_zone(self, zone: Zone) -> None:
        """Enregistre une zone dans le graphe.

        Args:
            zone: La Zone à ajouter.
        """
        self.zones[zone.name] = zone
        self.adjacency[zone.name] = []

    def add_connection(self, conn: Connection) -> None:
        """Enregistre une connexion bidirectionnelle entre deux zones.

        Args:
            conn: La Connection à ajouter.
        """
        self.connections.append(conn)
        # bidirectionnel
        self.adjacency[conn.zone1].append(conn.zone2)
        self.adjacency[conn.zone2].append(conn.zone1)

    def get_neighbors(self, zone_name: str) -> List[str]:
        """Retourne la liste des zones adjacentes à la zone donnée.

        Args:
            zone_name: La zone à interroger.

        Returns:
            Liste des noms de zones voisines.
        """
        return self.adjacency.get(zone_name, [])

    def find_shortest_path(
        self, start: str, end: str, avoid_zones: Optional[List[str]] = None
    ) -> Optional[List[str]]:
        """Trouve le chemin le moins coûteux de start à end (algorithme de Dijkstra).

        Coûts de déplacement : normal=1, restricted=2, priority=0.9, blocked=exclu.
        Les résultats sont mis en cache par (start, end, avoid_zones).

        Args:
            start: Nom de la zone de départ.
            end: Nom de la zone de destination.
            avoid_zones: Zones à exclure de la recherche (ex. zones occupées).

        Returns:
            Liste ordonnée de noms de zones de start à end, ou None si inaccessible.
        """
        if start not in self.zones or end not in self.zones:
            return None

        avoid = avoid_zones if avoid_zones is not None else []

        # Vérifier le cache (la clé doit inclure les zones à éviter)
        cache_key = (start, end, tuple(sorted(avoid)))
        if cache_key in self._path_cache:
            return self._path_cache[cache_key]

        distances: Dict[str, float] = {node: float("inf") for node in self.zones}
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
                cost = 1.0  # default/normal
                if neighbor_zone.zone_type == "restricted":
                    cost = 2.0
                elif neighbor_zone.zone_type == "priority":
                    cost = 0.9  # Moins que 1 pour favoriser

                distance = current_distance + cost

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_zone
                    heapq.heappush(pq, (distance, neighbor))

        if distances[end] == float("inf"):
            self._path_cache[cache_key] = None
            return None

        # Reconstruire le chemin
        path: List[str] = []
        curr: Optional[str] = end
        while curr is not None:
            path.append(curr)
            curr = previous_nodes[curr]

        path.reverse()

        # Sauvegarder dans le cache
        self._path_cache[cache_key] = path
        return path

    def find_disjoint_paths(
        self, start: str, end: str, max_paths: int = 5
    ) -> List[List[str]]:
        """Trouve plusieurs chemins à faible chevauchement via Dijkstra avec pénalités.

        Chaque itération ajoute une pénalité aux nœuds des chemins précédents
        afin d'orienter les chemins suivants vers d'autres routes, améliorant
        ainsi la répartition de charge des drones.

        Args:
            start: Nom de la zone de départ.
            end: Nom de la zone de destination.
            max_paths: Nombre maximum de chemins à calculer (défaut 5).

        Returns:
            Liste de chemins (chacun une liste de noms de zones). Retombe sur
            le chemin le plus court si aucune route différente n'existe.
        """
        paths: List[List[str]] = []
        penalty_weights: Dict[str, float] = {
            node: 0.0 for node in self.zones
        }

        for _ in range(max_paths):
            # Custom Dijkstra with soft penalties instead of strict avoidance
            distances: Dict[str, float] = {
                node: float("inf") for node in self.zones
            }
            distances[start] = 0.0
            previous_nodes: Dict[str, Optional[str]] = {
                node: None for node in self.zones
            }
            pq: List[Tuple[float, str]] = [(0.0, start)]

            while pq:
                current_distance, current_zone = heapq.heappop(pq)
                if current_zone == end:
                    break
                if current_distance > distances[current_zone]:
                    continue

                for neighbor in self.adjacency.get(current_zone, []):
                    neighbor_zone = self.zones[neighbor]
                    if neighbor_zone.zone_type == "blocked":
                        continue

                    cost = 1.0
                    if neighbor_zone.zone_type == "restricted":
                        cost = 2.0
                    elif neighbor_zone.zone_type == "priority":
                        cost = 0.9

                    # Add penalty for load balancing
                    cost += penalty_weights.get(neighbor, 0.0)

                    distance = current_distance + cost
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous_nodes[neighbor] = current_zone
                        heapq.heappush(pq, (distance, neighbor))

            if distances[end] == float("inf"):
                break

            # Rebuild path
            path: List[str] = []
            curr: Optional[str] = end
            while curr is not None:
                path.append(curr)
                curr = previous_nodes[curr]
            path.reverse()

            # Use path if it's new, else just break to avoid infinite useless loops
            if path not in paths:
                paths.append(path)
                # Apply penalty to intermediates
                for node in path[1:-1]:
                    # Heavy penalty encourages other routes
                    penalty_weights[node] += 3.0
            else:
                break

        return paths if paths else [self.find_shortest_path(start, end) or []]


class Drone:
    """Représente un drone individuel naviguant dans le réseau de zones.

    Attributes:
        id: Identifiant numérique unique.
        current_zone: Nom de la zone actuellement occupée par le drone.
        planned_path: Séquence de noms de zones restant à parcourir.
        status: État courant — 'waiting', 'in_flight' ou 'arrived'.
        moves: Nombre total de déplacements réussis.
        wait_turns: Tours restants avant de quitter une zone restricted.
        pending_connection: Label de connexion utilisé dans la sortie lors
            d'un passage en zone restricted sur deux tours (ex. 'zoneA-zoneB').
    """

    def __init__(
        self, drone_id: int, current_zone: Optional[str] = None
    ) -> None:
        """Initialise un Drone à une zone donnée.

        Args:
            drone_id: Identifiant entier unique.
            current_zone: Nom de la zone de départ (défaut chaîne vide).
        """
        self.id: int = drone_id
        self.current_zone: str = current_zone if current_zone is not None else ""
        self.planned_path: List[str] = []
        self.status: str = "waiting"  # "waiting", "in_flight", "arrived", etc.
        self.moves: int = 0
        self.wait_turns: int = 0
        self.pending_connection: str = ""
