import re

with open("src/models.py", "r") as f:
    content = f.read()

# Extract models part
models_part = re.split(r'class Scheduler:', content)[0].strip() + "\n"

# Rewrite models.py
with open("src/models.py", "w") as f:
    f.write(models_part)

# Write scheduler.py
with open("src/scheduler.py", "w") as f:
    f.write("""from typing import List\nfrom models import Graph, Drone\n\nclass Scheduler:\n""")
    # Extract Scheduler body
    scheduler_body = re.search(r'class Scheduler:(.*?)class Renderer:', content, re.DOTALL).group(1)
    f.write(scheduler_body.strip() + "\n")

# Write renderer.py
with open("src/renderer.py", "w") as f:
    f.write("""from typing import List\nfrom models import Graph, Drone\n\nclass Renderer:\n""")
    renderer_body = re.search(r'class Renderer:(.*?)class Simulation:', content, re.DOTALL).group(1)
    f.write(renderer_body.strip() + "\n")

# Write simulation.py
with open("src/simulation.py", "w") as f:
    f.write("""from typing import List\nfrom models import Graph, Drone\nfrom scheduler import Scheduler\nfrom renderer import Renderer\n\nclass Simulation:\n""")
    simulation_body = re.split(r'class Simulation:', content)[1]
    f.write(simulation_body.strip() + "\n")

