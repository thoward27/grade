init:
	poetry install
	git config core.hooksPath .hooks

test:
	poetry run python -m unittest discover

coverage:
	poetry run python -m coverage run -m unittest discover
	python -m coverage xml -i
