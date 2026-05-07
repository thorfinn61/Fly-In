import sys
import os
from models.simulation import Simulation


def main() -> None:
    if len(sys.argv) < 2:
        print("Erreur : Aucun fichier de carte fourni.")
        print("Usage: python3 src/main.py <path_to_map>")
        sys.exit(1)

    map_path = sys.argv[1]

    if not os.path.exists(map_path):
        print(f"Erreur : Le fichier '{map_path}' n'existe pas.")
        sys.exit(1)

    try:
        sim = Simulation(map_path)
        sim.run()
    except Exception as e:
        print(f"Erreur lors du lancement de la simulation : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
