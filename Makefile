# ----------------------------------------------------------
# ENV VARS
# ----------------------------------------------------------
BASEDIR := $(shell pwd)
SHELL   := /usr/local/bin/bash

# ----------------------------------------------------------
# ACTIONS
# ----------------------------------------------------------
env:
	@uv sync --group dev

lint:
	@uv run ruff check .

run:
	@uv run python main.py $(ARGS)

clean:
	@rm -f history-*.sh
