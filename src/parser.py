
from pathlib import Path


class MapParser:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.nb_drones = 0
        self.start_hub = None
        self.end_hub = None
        self.hubs = []

    def parser(self, path: str) -> None:
        if self.path.exists():
            with open(self.path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("#") or line == "":
                        continue
                    self.parse_nb_drones(line)
                    self.parse_hubs(line)
                    self.parse_hub(line)

    def parse_nb_drones(self, line: str) -> None:
        if line.startswith("nb_drones"):
            nb = line.split(":")
            nb1 = nb[1].strip()
            try:
                self.nb_drones = int(nb1)
            except ValueError:
                raise ValueError("nb_drones doit être un entier")
            if self.nb_drones <= 0:
                raise ValueError("nb_drones doit être un entier positif")

    def parse_hubs(self, line: str) -> None:
        if line.startswith("start_hub"):
            if self.start_hub is not None:
                raise ValueError("start_hub défini plusieurs fois")
            data = line.split("start_hub:")[1]
            splitted = data.split("[")[0].split()
            name = splitted[0]
            coords = (int(splitted[1]), int(splitted[2]))
            meta = data.split("[")[1].replace("]", "").strip() if "[" in data else ""
            metadata = meta
            self.start_hub = (name, coords, metadata)

        elif line.startswith("end_hub"):
            if self.end_hub is not None:
                raise ValueError("end_hub défini plusieurs fois")
            data = line.split("end_hub:")[1]
            splitted = data.split("[")[0].split()
            name = splitted[0]
            coords = (int(splitted[1]), int(splitted[2]))
            meta = data.split("[")[1].replace("]", "").strip() if "[" in data else ""
            self.end_hub = (name, coords, meta)

    def parse_hub(self, line:str):
        if line.startswith("hub:"):
            data = line.split("hub:")[1]
            splitted = data.split("[")[0].split()
            name = splitted[0]
            coords = (int(splitted[1]), int(splitted[2]))
            meta = data.split("[")[1].replace("]", "").strip() if "[" in data else ""
            self.hubs.append((name, coords, meta))