# Helper functions.
define commit
	$(shell git rev-parse HEAD)
endef

define tag
	$(strip $(shell git tag --sort=taggerdate | tail -1))
endef

COMMIT := $(call commit)
TAG := $(call tag)

init:
	python -m pip install --upgrade pip
	python -m pip install --upgrade poetry
	poetry install
	git config core.hooksPath .hooks

test:
	poetry run python -m unittest discover

coverage:
	poetry run python -m coverage run -m unittest discover
	poetry run python -m coverage xml -i

# If version bump is needed, this bumps version, commits the change, and tags it.
version:
	@poetry run semantic-release version

# Generates changelog if necessary.
changelog:
ifneq ($(TAG), $(call tag))
	@echo "Generating changelog."
	@echo "##" $(call tag) > tmp.md
	@poetry run semantic-release changelog >> tmp.md
	@cat CHANGELOG.md >> tmp.md
	@mv tmp.md CHANGELOG.md
else
	@echo "No changelog generated, $(TAG) == $(call tag)"
endif

deps:
	poetry export --dev -f requirements.txt > requirements.txt

# Builds a new release.
publish: version changelog deps
ifneq ($(TAG), $(call tag))
	@echo "Creating a release"
	# If we get into here, we know we have a new commit to ammend (includes changelog and deps)
	git commit -a --amend --no-edit
	hub release create $(strip $(call tag))
	poetry build
	poetry publish -u PYPI_USERNAME -p PYPI_PASSWORD
else
	@echo "Nothing to publish. $(TAG) == $(call tag)
endif
