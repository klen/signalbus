VIRTUAL_ENV ?= env

$(VIRTUAL_ENV): pyproject.toml
	@poetry install --with dev
	@poetry run pre-commit install --hook-type pre-push
	@touch $(VIRTUAL_ENV)

.PHONY: test
test t: $(VIRTUAL_ENV)
	@poetry run pytest

.PHONY: mypy
mypy: $(VIRTUAL_ENV)
	@poetry run mypy


VPART	?= minor

.PHONY: release
release:
	@poetry version $(VPART)
	@git commit -am "Bump version: `poetry version -s`"
	@git tag `poetry version -s`
	@git checkout main
	@git merge develop
	@git checkout develop
	@git push origin develop main
	@git push --tags

.PHONY: minor
minor:
	make release VPART=minor

.PHONY: patch
patch:
	make release VPART=patch

.PHONY: major
major:
	make release VPART=major
