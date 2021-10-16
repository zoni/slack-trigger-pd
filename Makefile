MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

ALL_PY_FILES := $(wildcard **/*.py)

.PHONY: all
all: install-deps requirements.txt lint-all

.PHONY: lint-all
lint-all: linter-mypy linter-pylint

.PHONY: install-deps
install-deps: pyproject.toml
	poetry install

requirements.txt: pyproject.toml
	poetry export --without-hashes > requirements.txt

.PHONY: ngrok
ngrok:
	ngrok http 7071

.PHONY: serve-local
serve-local:
	poetry run func start

.PHONY: linter-mypy
linter-mypy:
	poetry run mypy $(ALL_PY_FILES)

.PHONY: linter-pylint
linter-pylint:
	poetry run pylint $(ALL_PY_FILES)
