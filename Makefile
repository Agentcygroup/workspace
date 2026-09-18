.PHONY: install test sbom clean

install:
	pip install -e packages/core -e packages/cli
	pip install pytest

test:
	python -m pytest -q

sbom:
	mkdir -p sbom
	cyclonedx-py environment -o sbom/current.json

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
	rm -rf build dist sbom
