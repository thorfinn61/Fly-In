"""Orchestrateur principal de la simulation de drones."""

import os
from .scheduler import Scheduler
from .renderer import Renderer
from parser import MapParser


class Simulation:
    """Orchestre le parseur, le planificateur et le rendu visuel tour par tour.

    Attributes:
        map_path: Chemin vers le fichier de carte utilisé.
        is_running: Indique si la simulation est en cours d'exécution.
        log_file: Chemin du fichier de log des mouvements.
        graph: Graphe du réseau de zones.
        drones: Liste des drones de la simulation.
        end_hub: Nom de la zone d'arrivée.
        scheduler: Planificateur de mouvements.
        turn: Numéro du tour courant.
        renderer: Interface graphique Tkinter.
    """

    def __init__(self, map_path: str) -> None:
        """Initialise la simulation à partir d'un fichier de carte.

        Parse le fichier, construit le graphe et les drones, prépare
        le planificateur et configure la fenêtre graphique.

        Args:
            map_path: Chemin vers le fichier de carte.
        """
        self.map_path = map_path
        self.is_running = False
        self.log_file = "simulation_moves.log"

        # Effacer le log au demarrage
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

        with open(self.log_file, "w"):
            pass  # Plus de header

        # Charger les donnees avant de lancer le rendu
        parser = MapParser(self.map_path)
        parser.parse()
        self.graph, self.drones = parser.build_models()
        self.end_hub: str = (
            parser.end_hub[0] if parser.end_hub else "goal"
        )
        self.scheduler = Scheduler(self.graph, self.drones)
        self.turn = 0

        self.renderer = Renderer(self)
        self.renderer.setup_from_graph()

    def reset(self) -> None:
        """Reparse le fichier de carte et réinitialise l'état de la simulation."""
        parser = MapParser(self.map_path)
        parser.parse()
        self.graph, self.drones = parser.build_models()
        self.end_hub = parser.end_hub[0] if parser.end_hub else "goal"
        self.scheduler = Scheduler(self.graph, self.drones)
        self.turn = 0

        self.renderer.setup_from_graph()

    def step(self) -> None:
        """Exécute un tour : assigne les chemins, résout les conflits et logue.

        Arrête la simulation si tous les drones sont arrivés ou si le nombre
        maximum de tours (500) est atteint.
        """
        terminal = {"arrived", "no_path"}
        if (
            all(d.status in terminal for d in self.drones)
            or self.turn >= 500
        ):
            self.is_running = False
            return

        start = self.drones[0].current_zone if self.drones else "START"
        self.scheduler.assign_paths(start, self.end_hub)
        moves = self.scheduler.resolve_conflicts()

        # Enregistrement des mouvements dans le log
        if moves:
            # Trie les mouvements pour avoir un ordre consistant
            moves.sort(key=lambda x: int(x.split('-')[0][1:]))
            with open(self.log_file, "a") as f:
                f.write(" ".join(moves) + "\n")

        self.renderer.render(self.turn)
        self.turn += 1

    def run(self) -> None:
        """Lance la boucle principale Tkinter et démarre l'interface graphique."""
        self.renderer.root.mainloop()
