import sys
from parser import MapParser
from models.simulation import Simulation

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 src/main.py <path_to_map>")
        sys.exit(1)
        
    map_path = sys.argv[1]
    
    # 1. Parser la carte
    parser = MapParser(map_path)
    parser.parse()
    
    # 2. Construire les modèles
    graph, drones = parser.build_models()
    
    # 3. Récupérer la destination (end_hub)
    end_hub = parser.end_hub[0] if parser.end_hub else None
    if not end_hub:
        print("Erreur: Aucun end_hub défini dans la map.")
        sys.exit(1)
        
    # 4. Initialiser et lancer la simulation
    sim = Simulation(graph=graph, drones=drones, end_hub=end_hub)
    print(f"Début de la simulation sur {map_path} avec {len(drones)} drones.")
    sim.run()

if __name__ == "__main__":
    main()
