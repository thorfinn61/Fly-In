import sys
from models.simulation import Simulation

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 src/main.py <path_to_map>")
        sys.exit(1)
    
    map_path = sys.argv[1]
    sim = Simulation(map_path)
    sim.run()

if __name__ == "__main__":
    main()
