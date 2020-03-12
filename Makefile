# Helper functions.
define commit
$(shell git rev-parse HEAD)
endef

define tag
$(or $(strip $(shell git tag --sort=taggerdate | tail -1)),undefined)
endef

COMMIT := $(call commit)
TAG := $(call tag)

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
	@echo "Generating changelog."
	@echo "## " $(call tag) > tmp.md
	@poetry run semantic-release changelog >> tmp.md
	@cat CHANGELOG.md >> tmp.md
	@mv tmp.md CHANGELOG.md

deps:
	poetry export --dev -f requirements.txt > requirements.txt

debug: debug-1 debug-2
	@echo make --version
	@echo $(COMMIT) $(call commit)
	@echo $(TAG) $(call tag)
	@echo $(filter-out $(call tag),$(TAG))

debug-1:
ifeq ($(filter-out $(call tag),$(TAG)),)
	@echo "in debug-1"
endif

debug-2:
ifneq ($(filter-out $(call tag),$(TAG)),)
	@echo "in debug-2"
endif

debug-3:
ifeq ($(TAG),$(call tag))
	@echo "in debug-3"
endif

# Builds a new release.
publish: version changelog deps debug
ifneq ("$(COMMIT)","$(call commit)")
	@echo "Creating a release"
	# If we get into here, we know we have a new commit to ammend (includes changelog and deps)
	git commit -a --amend --no-edit
	hub release create $(strip $(call tag))
	poetry build
	poetry publish -u PYPI_USERNAME -p PYPI_PASSWORD
else
	@echo "Nothing to publish. $(COMMIT) == $(call commit)"
endif
