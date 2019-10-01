help:
	@echo "This project supports the following targets"
	@echo ""
	@echo " make help - show this text"
	@echo " make lint - run flake8"
	@echo " make test - run the functests and lint"
	@echo " make functional - run the tests defined in the functional subdirectory"
	@echo " make release - build the charm"
	@echo " make clean - remove unneeded files"
	@echo ""

lint:
	@echo "Running flake8"
	@-tox -e lint

test: lint functional

functional: build
	@tox -e functional

build:
	@echo "Building charm to base directory $(JUJU_REPOSITORY)"
	@LAYER_PATH=./layers INTERFACE_PATH=./interfaces TERM=linux \
		JUJU_REPOSITORY=$(JUJU_REPOSITORY) charm build . --force

release: clean build
	@echo "Charm is built at $(JUJU_REPOSITORY)/builds"

clean:
	@echo "Cleaning files"
	@rm -rf .tox
	@find . -iname __pycache__ -exec rm -r {} +

# The targets below don't depend on a file
.PHONY: lint test functional build release clean help

