# Makefile for managing this FileSystemAgent project

# 1) Install: Set up dependencies with Poetry
install:
	poetry install

# 2) Test: Run pytest
test:
	poetry run pytest tests.py

# 3) Start: Launch the FileSystemAgent
start:
	poetry run python agent.py

# 4) Clean: Remove temporary files, caches, etc.
clean:
	rm -rf __pycache__ .pytest_cache coverage* *.egg-info
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.log" -delete
	find . -name "*.tmp" -delete