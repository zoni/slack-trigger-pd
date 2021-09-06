MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

.PHONY: all
all: install-deps requirements.txt

.PHONY: install-deps
install-deps: pyproject.toml
	poetry install

requirements.txt: pyproject.toml
	poetry export --without-hashes > requirements.txt

.PHONY: serve-local
serve-local:
	ngrok http 7071 --log stderr --log-format term --inspect &
	poetry run func start
