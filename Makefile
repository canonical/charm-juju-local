JUJU_REPOSITORY=$(dir $(realpath $(MAKEFILE_LIST)))
CHARM_NAME=$(shell cat ${JUJU_REPOSITORY}/metadata.yaml | grep -E "^name:" | awk '{print $$2}')

help:
	@echo "This project supports the following targets"
	@echo ""
	@echo " make help - show this text"
	@echo " make lint - run flake8"
	@echo " make unittests - run the tests defined in the unittest subdirectory"
	@echo " make test - run the functests and lint"
	@echo " make functional - run the tests defined in the functional subdirectory"
	@echo " make release - build the charm"
	@echo " make clean - remove unneeded files"
	@echo ""

lint:
	@echo "Running flake8"
	@-tox -e lint

unittests:
	@echo "No unit tests available at the moment"

test: lint functional

functional: build
	@JUJU_REPOSITORY=$(JUJU_REPOSITORY) tox -e func -- ${FUNC_ARGS}

build:
	@echo "Building charm to base directory $(JUJU_REPOSITORY)"
	@charmcraft pack --verbose
	@bash -c ./rename.sh

release: clean build
	@echo "Charm is built at $(JUJU_REPOSITORY)/$(CHARM_NAME).charm"

clean:
	@echo "Cleaning files"
	@rm -rf .tox
	@find . -iname __pycache__ -exec rm -r {} +
	@$(RM) $(JUJU_REPOSITORY)/$(CHARM_NAME).charm

# The targets below don't depend on a file
.PHONY: lint test functional functional31 build release clean help

