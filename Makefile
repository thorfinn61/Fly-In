PYTHON = python3
PIP = pip3
MAIN = src/main.py
MAP ?= maps/easy/01_linear_path.txt

.PHONY: install run debug clean lint lint-strict

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(MAP)

debug:
	$(PYTHON) -m pdb $(MAIN) $(MAP)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

lint:
	flake8 src
	$(PYTHON) -m mypy src

lint-strict:
	flake8 src
	$(PYTHON) -m mypy src --strict