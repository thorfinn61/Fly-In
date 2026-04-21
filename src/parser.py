from pathlib import Path
from typing import Dict, Tuple, List
from models import Graph, Zone, Connection, Drone

class MapParser:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.nb_drones = 0
        self.start_hub = None
        self.end_hub = None
        self.hubs = []
        self.connections = []

    def parse(self) -> None:
        if self.path.exists():
            with open(self.path, "r") as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if line.startswith("#") or line == "":
                        continue
                    try:
                        self.parse_nb_drones(line, line_num)
                        self.parse_hubs(line, line_num)
                        self.parse_hub(line, line_num)
                        self.parse_connection(line, line_num)
                    except ValueError as e:
                        if f"Ligne {line_num}:" not in str(e):
                            raise ValueError(f"Ligne {line_num}: {e}")
                        raise
                    except Exception as e:
                        raise ValueError(f"Ligne {line_num}: Erreur de syntaxe inattendue -> {e}")

    def parse_nb_drones(self, line: str, line_num: int) -> None:
        if line.startswith("nb_drones"):
            try:
                nb = line.split(":")
                nb1 = nb[1].strip()
                self.nb_drones = int(nb1)
            except (IndexError, ValueError):
                raise ValueError(f"Ligne {line_num}: 'nb_drones' doit être un entier valide.")
            if self.nb_drones <= 0:
                raise ValueError(f"Ligne {line_num}: 'nb_drones' doit être un entier positif.")

    def parse_hubs(self, line: str, line_num: int) -> None:
        if line.startswith("start_hub"):
            if self.start_hub is not None:
                raise ValueError(f"Ligne {line_num}: 'start_hub' défini plusieurs fois.")
            try:
                data = line.split("start_hub:")[1]
                splitted = data.split("[")[0].split()
                name = splitted[0]
                coords = (int(splitted[1]), int(splitted[2]))
                meta = data.split("[")[1].replace("]", "").strip() if "[" in data else ""
                metadata = self.parse_metadata(meta, line_num)
                self.start_hub = (name, coords, metadata)
            except Exception:
                raise ValueError(f"Ligne {line_num}: Format de 'start_hub' invalide.")

        elif line.startswith("end_hub"):
            if self.end_hub is not None:
                raise ValueError(f"Ligne {line_num}: 'end_hub' défini plusieurs fois.")
            try:
                data = line.split("end_hub:")[1]
                splitted = data.split("[")[0].split()
                name = splitted[0]
                coords = (int(splitted[1]), int(splitted[2]))
                meta = data.split("[")[1].replace("]", "").strip() if "[" in data else ""
                metadata = self.parse_metadata(meta, line_num)
                self.end_hub = (name, coords, metadata)
            except Exception:
                raise ValueError(f"Ligne {line_num}: Format de 'end_hub' invalide.")

    def parse_hub(self, line: str, line_num: int) -> None:
        if line.startswith("hub:"):
            try:
                data = line.split("hub:")[1]
                splitted = data.split("[")[0].split()
                name = splitted[0]
                coords = (int(splitted[1]), int(splitted[2]))
                meta = data.split("[")[1].replace("]", "").strip() if "[" in data else ""
                metadata = self.parse_metadata(meta, line_num)
                self.hubs.append((name, coords, metadata))
            except Exception:
                raise ValueError(f"Ligne {line_num}: Format du 'hub' invalide.")

    def parse_metadata(self, meta: str, line_num: int) -> Dict[str, str]:
        result = {}
        VALID_ZONES = ["normal", "restricted", "priority", "blocked"]
        data = meta.split()
        for item in data:
            splitted = item.split("=")
            if len(splitted) != 2:
                raise ValueError(f"Ligne {line_num}: Métadonnée mal formatée ('{item}'). Attendu: clé=valeur.")
            result[splitted[0]] = splitted[1]
        if "zone" in result:
            if result["zone"] not in VALID_ZONES:
                raise ValueError(f"Ligne {line_num}: Zone inconnue ('{result['zone']}').")
        return result
    
    def parse_connection(self, line: str, line_num: int) -> None:
        if line.startswith("connection:"):
            try:
                data  = line.split("connection:")
                if "-" not in data[1]:
                    raise ValueError(f"Ligne {line_num}: Séparateur '-' manquant.")
                splitted = data[1].split("-")
                zone1 = splitted[0].strip()
                zone2 = splitted[1].split("[")[0].strip()
                if "[" in line:
                    cap_str = data[1].split("[")[1].replace("]","")
                    capacity = int(cap_str.split("=")[1])
                else:
                    capacity = 1
            except Exception:
                raise ValueError(f"Ligne {line_num}: Format de la 'connection' invalide.")
            
            for z1, z2, _ in self.connections:
                if (z1 == zone1 and z2 == zone2) or (z1 == zone2 and z2 == zone1):
                    raise ValueError(f"Ligne {line_num}: Connexion en double détectée entre '{zone1}' et '{zone2}'.")
            
            known = [h[0] for h in self.hubs]
            if self.start_hub:
                known.append(self.start_hub[0])
            if self.end_hub:
                known.append(self.end_hub[0])
            
            if zone1 not in known or zone2 not in known:
                raise ValueError(f"Ligne {line_num}: Zone inconnue dans la connexion '{zone1}-{zone2}'.")
            
            self.connections.append((zone1, zone2, capacity))

    def build_models(self) -> Tuple[Graph, List[Drone]]:
        graph = Graph()
        drones = []

        all_hubs_raw = self.hubs.copy()
        if self.start_hub:
            all_hubs_raw.append(self.start_hub)
        if self.end_hub:
            all_hubs_raw.append(self.end_hub)
            
        for name, coords, meta in all_hubs_raw:
            zone_type = meta.get("zone", "normal")
            color = meta.get("color", "none")
            max_drones = int(meta.get("max_drones", 1))
            
            zone_obj = Zone(name=name, x=coords[0], y=coords[1], zone_type=zone_type, color=color, max_drones=max_drones)
            graph.add_zone(zone_obj)
            
        for z1, z2, capacity in self.connections:
            conn_obj = Connection(zone1=z1, zone2=z2, max_link_capacity=capacity)
            graph.add_connection(conn_obj)
            
        start_zone_name = self.start_hub[0] if self.start_hub else None
        
        for i in range(self.nb_drones):
            drone_obj = Drone(drone_id=i+1, current_zone=start_zone_name)
            drones.append(drone_obj)
            # Ajouter les drones direct dans la zone de départ si elle existe
            if start_zone_name and start_zone_name in graph.zones:
                graph.zones[start_zone_name].drones.append(drone_obj.id)
                
        return graph, drones
