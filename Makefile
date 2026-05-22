PACKAGE := $(shell python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['name'])")
.PHONY: clean venv reinstall test import-check
clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
venv:
	uv venv
install:
	uv tool install -e .
	python -c "import qrtools; print(qrtools.__file__)"
uninstall:
	uv tool uninstall $(PACKAGE) || true
test:
	uv run pytest
import-check:
	uv run python -c "import $(PACKAGE); print($(PACKAGE).__file__)"
reinstall: clean uninstall install
