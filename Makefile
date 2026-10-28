.PHONY: help test lint demo clean

help:
	@echo "make test   run the suite"
	@echo "make demo   show the capability card"
	@echo "make check  validate an empty payload"
	@echo "make clean  remove caches"

test:
	python -m pytest

demo:
	python -m gbt_handoff info

check:
	python -m gbt_handoff check --payload '{}'

lint:
	python -m compileall -q src

clean:
	rm -rf .pytest_cache src/*.egg-info **/__pycache__
