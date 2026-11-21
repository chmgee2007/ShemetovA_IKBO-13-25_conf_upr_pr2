# Определяем путь к Python (если есть venv - берем оттуда)
ifeq ($(OS),Windows_NT)
    PYTHON = .venv/Scripts/python.exe
    RM = rmdir /s /q
else
    PYTHON = .venv/bin/python
    RM = rm -rf
endif

.PHONY: run test lint clean

run:
	$(PYTHON) -m src.main --config examples/config.toml

reverse:
	$(PYTHON) -m src.main --config examples/config.toml --reverse D

test:
	$(PYTHON) -m pytest tests/ -v

lint:
	$(PYTHON) -m flake8 src/ tests/ --max-line-length=80

clean:
	-$(RM) __pycache__ src/__pycache__ tests/__pycache__ .pytest_cache