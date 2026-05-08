*This project has been created as part of the 42 curriculum by elsahin.*

# Fly-In — Drone Routing Simulation

## Description

Fly-In is a drone routing simulation system that navigates a fleet of drones through a network of connected zones, from a start hub to an end hub, in the fewest possible simulation turns.

The network is represented as a graph where each zone has a type that determines its movement cost:

| Type | Cost | Description |
|------|------|-------------|
| `normal` | 1 turn | Zone standard |
| `priority` | 1 turn | Zone préférée par le pathfinding |
| `restricted` | 2 turns | Zone sensible — le passage prend 2 tours |
| `blocked` | — | Zone inaccessible |

The simulation handles concurrent drone movement, zone and connection capacity constraints, deadlock avoidance, and animated visual feedback.

## Instructions

### Requirements

- Python 3.10 or later
- Dependencies listed in `requirements.txt` (`flake8`, `mypy`)

### Installation

```bash
make install
```

### Run a simulation

```bash
make run MAP=maps/easy/01_linear_path.txt
```

Or directly:

```bash
python3 src/main.py <path_to_map>
```

### Available maps

```
maps/easy/      — 2 to 4 drones, basic routing
maps/medium/    — 4 to 6 drones, restricted zones and capacity constraints
maps/hard/      — 8 to 15 drones, complex topology
maps/challenger — 25 drones, optional extreme challenge
```

### Other Makefile targets

```bash
make debug              # Runs the simulation under pdb
make clean              # Removes __pycache__, .mypy_cache, .pytest_cache
make lint               # Runs flake8 and mypy
make lint-strict        # Runs mypy --strict
```

### Simulation output

Each turn is logged to `simulation_moves.log` in the format:

```
D1-zone D2-zone
D1-zone D3-zone D2-zone
```

For drones crossing a restricted zone (2-turn transit):

```
D1-zoneA-zoneB      ← turn 1: drone enters the connection
D1-zoneB            ← turn 2: drone arrives at the restricted zone
```

## Algorithm

### Pathfinding — Dijkstra with zone-type costs

Each zone type has a weighted movement cost: `normal=1.0`, `restricted=2.0`, `priority=0.9`, `blocked=excluded`. The graph uses a standard min-heap Dijkstra implementation with result caching by `(start, end, avoid_zones)`.

### Multi-path distribution — penalty-based disjoint paths

To spread drones across parallel routes, the scheduler computes up to 3 paths using an iterative Dijkstra with soft penalties: nodes used in a previous path receive a +3.0 cost penalty in the next iteration. Paths are then distributed to drones in round-robin order.

### Conflict resolution — same-turn liberation

Each turn, the scheduler runs in three phases:

1. **Phase 1** — Drones leaving a restricted zone are forced to move (they cannot wait on a connection).
2. **Phase 2** — Iterative approval: a drone may move if both its target zone and the connection have capacity. Drones leaving a zone free up their slot *within the same turn* (same-turn liberation), allowing chain movements through bottlenecks.
3. **Phase 3** — Atomic application: all approved departures are executed simultaneously to avoid ordering effects.

Circular deadlocks (drone A waits for B's slot, B waits for A's) are handled gracefully — the loop simply produces no new approvals and all involved drones stay in `waiting` state until the next turn.

### Restricted zone mechanics

Moving to a `restricted` zone takes 2 turns. On turn 1, the drone commits to the connection and cannot wait or turn back. On turn 2, it arrives at the destination. The output labels the drone as `D<id>-<zoneFrom>-<zoneTo>` during transit and `D<id>-<zone>` on arrival.

## Visual Representation

The simulation opens a Tkinter window with:

- **Graph view** — Zones are drawn as colored circles at their map coordinates. Zone type and capacity are shown as labels. Connections are drawn as lines.
- **Animated drones** — Each drone is a colored dot that moves smoothly between zones. Colors indicate status: orange = waiting, cyan = in flight, green = arrived.
- **Multi-drone layout** — When multiple drones share a zone, they are spread in a circle to remain readable.
- **Restricted zone animation** — Drones crossing a restricted zone stop at the midpoint of the connection on turn 1, then complete the journey on turn 2.
- **Dashboard** — Turn counter, total moves, and per-status drone counts update in real time.
- **Speed control** — A slider adjusts the animation framerate (2 to 60 frames per step).
- **PLAY/PAUSE and RESET** — Full interactive control over the simulation.

## Resources
- Youtube
- Claude

### References

- Dijkstra's algorithm: [Wikipedia — Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)

### AI usage

AI (Claude) was used during this project for the following tasks:

- **Designing the conflict resolution algorithm** — discussing the "same-turn liberation" approach and iterative approval loop.
- **Debugging the restricted zone 2-turn animation** — identifying the off-by-one in `wait_turns` and `prev_positions` tracking.
- **Writing docstrings** — generating PEP 257-compliant French docstrings for all classes and functions.
- **Code review** — checking type annotations and flake8 compliance before submission.
- **Flake8 & mypy compliance** — fixing linting errors and type annotation issues flagged by flake8 and mypy.
- **Renderer implementation** — assistance with designing and writing the rendering logic.