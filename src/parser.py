"""Parseur du format de fichier de carte Fly-In."""

from pathlib import Path
from typing import Dict, Tuple, List, Optional
from models.core import Graph, Zone, Connection, Drone

HubData = Tuple[str, Tuple[int, int], Dict[str, str]]


class MapParser:
    """Lit et valide un fichier de carte, puis construit les objets du domaine.

    Attributes:
        path: Chemin vers le fichier de carte.
        nb_drones: Nombre de drones déclaré dans le fichier.
        start_hub: Données de la zone de départ unique.
        end_hub: Données de la zone d'arrivée unique.
        hubs: Données de toutes les zones régulières.
        connections: Triplets (zone1, zone2, capacité) des connexions.
    """

    def __init__(self, path: str) -> None:
        """Initialise le parseur pour le chemin de fichier donné.

        Args:
            path: Chemin système vers le fichier de carte.
        """
        self.path = Path(path)
        self.nb_drones = 0
        self.start_hub: Optional[HubData] = None
        self.end_hub: Optional[HubData] = None
        self.hubs: List[HubData] = []
        self.connections: List[Tuple[str, str, int]] = []

    def parse(self) -> None:
        """Lit le fichier ligne par ligne et remplit les structures internes.

        Raises:
            FileNotFoundError: Si le fichier de carte n'existe pas.
            ValueError: Pour toute erreur de syntaxe ou sémantique,
                avec le numéro de ligne et la cause.
        """
        if not self.path.exists():
            raise FileNotFoundError(f"Le fichier '{self.path}' n'existe pas.")
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
                    raise ValueError(
                        f"Ligne {line_num}: Erreur de syntaxe inattendue -> {e}"
                    )

    def parse_nb_drones(self, line: str, line_num: int) -> None:
        """Analyse une ligne nb_drones et enregistre le nombre de drones.

        Args:
            line: Ligne brute du fichier.
            line_num: Numéro de ligne utilisé dans les messages d'erreur.

        Raises:
            ValueError: Si la valeur est absente ou n'est pas un entier positif.
        """
        if line.startswith("nb_drones"):
            try:
                nb = line.split(":")
                nb1 = nb[1].strip()
                self.nb_drones = int(nb1)
            except (IndexError, ValueError):
                raise ValueError(
                    f"Ligne {line_num}: 'nb_drones' doit être un entier valide."
                )
            if self.nb_drones <= 0:
                raise ValueError(
                    f"Ligne {line_num}: 'nb_drones' doit être un entier positif."
                )

    def parse_hubs(self, line: str, line_num: int) -> None:
        """Analyse une ligne start_hub ou end_hub et enregistre ses données.

        Args:
            line: Ligne brute du fichier.
            line_num: Numéro de ligne utilisé dans les messages d'erreur.

        Raises:
            ValueError: Si la zone est définie plusieurs fois ou si la
                syntaxe est invalide.
        """
        if line.startswith("start_hub"):
            if self.start_hub is not None:
                raise ValueError(
                    f"Ligne {line_num}: 'start_hub' défini plusieurs fois."
                )
            try:
                data = line.split("start_hub:")[1]
                splitted = data.split("[")[0].split()
                name = splitted[0]
                coords = (int(splitted[1]), int(splitted[2]))
                meta = (
                    data.split("[")[1].replace("]", "").strip() if "[" in data else ""
                )
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
                meta = (
                    data.split("[")[1].replace("]", "").strip() if "[" in data else ""
                )
                metadata = self.parse_metadata(meta, line_num)
                self.end_hub = (name, coords, metadata)
            except Exception:
                raise ValueError(f"Ligne {line_num}: Format de 'end_hub' invalide.")

    def parse_hub(self, line: str, line_num: int) -> None:
        """Analyse une ligne hub régulière et l'ajoute à la liste des zones.

        Args:
            line: Ligne brute du fichier.
            line_num: Numéro de ligne utilisé dans les messages d'erreur.

        Raises:
            ValueError: Si la syntaxe de la ligne hub est invalide.
        """
        if line.startswith("hub:"):
            try:
                data = line.split("hub:")[1]
                splitted = data.split("[")[0].split()
                name = splitted[0]
                coords = (int(splitted[1]), int(splitted[2]))
                meta = (
                    data.split("[")[1].replace("]", "").strip() if "[" in data else ""
                )
                metadata = self.parse_metadata(meta, line_num)
                self.hubs.append((name, coords, metadata))
            except Exception:
                raise ValueError(f"Ligne {line_num}: Format du 'hub' invalide.")

    def parse_metadata(self, meta: str, line_num: int) -> Dict[str, str]:
        """Analyse un bloc de métadonnées (contenu entre crochets) en dict clé-valeur.

        Args:
            meta: Chaîne brute de métadonnées, ex. 'zone=restricted color=red'.
            line_num: Numéro de ligne utilisé dans les messages d'erreur.

        Returns:
            Dictionnaire des paires clé-valeur extraites.

        Raises:
            ValueError: Si un token est mal formé ou si le type de zone est inconnu.
        """
        result = {}
        VALID_ZONES = ["normal", "restricted", "priority", "blocked"]
        data = meta.split()
        for item in data:
            splitted = item.split("=")
            if len(splitted) != 2:
                raise ValueError(
                    f"Ligne {line_num}: Métadonnée mal formatée "
                    f"('{item}'). Attendu: clé=valeur."
                )
            result[splitted[0]] = splitted[1]
        if "zone" in result:
            if result["zone"] not in VALID_ZONES:
                raise ValueError(
                    f"Ligne {line_num}: Zone inconnue ('{result['zone']}')."
                )
        return result

    def parse_connection(self, line: str, line_num: int) -> None:
        """Analyse une ligne connection et l'ajoute à la liste des connexions.

        Args:
            line: Ligne brute du fichier.
            line_num: Numéro de ligne utilisé dans les messages d'erreur.

        Raises:
            ValueError: Si la syntaxe est invalide, si une zone référencée est
                inconnue ou si la connexion est définie en double.
        """
        if line.startswith("connection:"):
            try:
                data = line.split("connection:")
                if "-" not in data[1]:
                    raise ValueError(
                        f"Ligne {line_num}: Separateur '-' manquant."
                    )
                splitted = data[1].split("-")
                zone1 = splitted[0].strip()
                zone2 = splitted[1].split("[")[0].strip()
                if "[" in line:
                    cap_str = data[1].split("[")[1].replace("]", "")
                    capacity = int(cap_str.split("=")[1])
                else:
                    capacity = 1
            except Exception:
                raise ValueError(
                    f"Ligne {line_num}: Format de la 'connection' invalide."
                )

            for z1, z2, _ in self.connections:
                if (z1 == zone1 and z2 == zone2) or (z1 == zone2 and z2 == zone1):
                    raise ValueError(
                        f"Ligne {line_num}: Connexion en double détectée entre "
                        f"'{zone1}' et '{zone2}'."
                    )

            known = [h[0] for h in self.hubs]
            if self.start_hub:
                known.append(self.start_hub[0])
            if self.end_hub:
                known.append(self.end_hub[0])

            if zone1 not in known or zone2 not in known:
                raise ValueError(
                    f"Ligne {line_num}: Zone inconnue dans la connexion "
                    f"'{zone1}-{zone2}'."
                )

            self.connections.append((zone1, zone2, capacity))

    def build_models(self) -> Tuple[Graph, List[Drone]]:
        """Construit les objets Graph et Drone à partir des données parsées.

        Returns:
            Tuple (graph, drones) prêts à être utilisés par la simulation.
        """
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

            # Start and End hubs should have infinite capacity by default
            # unless overridden. They can hold all drones at once.
            if self.start_hub and name == self.start_hub[0]:
                max_drones = int(meta.get("max_drones", self.nb_drones))
            elif self.end_hub and name == self.end_hub[0]:
                max_drones = int(meta.get("max_drones", self.nb_drones))
            else:
                max_drones = int(meta.get("max_drones", 1))

            zone_obj = Zone(
                name=name,
                x=coords[0],
                y=coords[1],
                zone_type=zone_type,
                color=color,
                max_drones=max_drones,
            )
            graph.add_zone(zone_obj)

        for z1, z2, capacity in self.connections:
            conn_obj = Connection(zone1=z1, zone2=z2, max_link_capacity=capacity)
            graph.add_connection(conn_obj)

        start_zone_name: Optional[str] = (
            self.start_hub[0] if self.start_hub else None
        )

        for i in range(self.nb_drones):
            drone_obj = Drone(drone_id=i + 1, current_zone=start_zone_name)
            drones.append(drone_obj)
            # Ajouter les drones direct dans la zone de depart si elle existe
            if start_zone_name and start_zone_name in graph.zones:
                graph.zones[start_zone_name].drones.append(str(drone_obj.id))

        return graph, drones
