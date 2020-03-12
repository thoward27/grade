# Helper functions.
define commit
$(shell git rev-parse HEAD)
endef

define tag
$(or $(strip $(shell git tag --sort=taggerdate | tail -1)),undefined)
endef

COMMIT := $(call commit)
TAG := $(call tag)

NEW_VERSION = $(if $(filter-out $(TAG),$(call tag)),1,)

init:
	python -m pip install -q --upgrade pip
	python -m pip install -q --upgrade poetry
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
	@if [ "$(NEW_VERSION)" = "1" ]; \
	then \
		echo "Generating changelog." \
		&& echo "## " $(call tag) > tmp.md \
		&& poetry run semantic-release changelog >> tmp.md \
		&& cat CHANGELOG.md >> tmp.md \
		&& mv tmp.md CHANGELOG.md; \
	else \
		echo "No changelog needed. Same version."; \
	fi	

deps:
	poetry export --dev -f requirements.txt > requirements.txt

# Builds a new release.
publish: version changelog deps
	@if [ "$(NEW_VERSION)" = "1" ]; \
	then \
		echo "Creating a release" \
		&& git commit -a --amend --no-edit \
		&& poetry build \
		&& poetry publish -u PYPI_USERNAME -p PYPI_PASSWORD \
		&& hub release create $(strip $(call tag)); \
	else echo "Skipping release, no new version to publish"; fi
