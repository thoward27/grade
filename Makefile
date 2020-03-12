# Helper functions.
define commit
$(shell git rev-parse HEAD)
endef

define tag
$(or $(strip $(shell git tag --sort=taggerdate | tail -1)),undefined)
endef

COMMIT := $(call commit)
TAG := $(call tag)

NEW_VERSION = $(if $(filter-out $(TAG),$(call tag)),1,0)

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
ifeq ("$(NEW_VERSION)","1")
	@echo "Generating changelog."
	@echo "## " $(call tag) > tmp.md
	@poetry run semantic-release changelog >> tmp.md
	@cat CHANGELOG.md >> tmp.md
	@mv tmp.md CHANGELOG.md
endif

deps:
	poetry export --dev -f requirements.txt > requirements.txt

debug: debug-1
	echo $(NEW_VERSION)
	echo $(if $(NEW_VERSION),"fuck","you")
	@echo "$(shell make --version)"
	@echo $(COMMIT) $(call commit)
	@echo $(TAG) $(call tag)
	@echo $(filter-out $(call tag),$(TAG))

debug-1:
ifneq ("$(NEW_VERSION)","0")
	@echo "in debug-1"
endif

# Builds a new release.
publish: version changelog deps debug
ifneq ($(NEW_VERSION),"")
	@echo "Creating a release"
	# If we get into here, we know we have a new commit to ammend (includes changelog and deps)
	git commit -a --amend --no-edit
	poetry build
	# poetry publish -u PYPI_USERNAME -p PYPI_PASSWORD
	# hub release create $(strip $(call tag))
	# git push
else
	@echo "Nothing to publish. $(COMMIT) == $(call commit)"
endif
