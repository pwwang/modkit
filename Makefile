PYTHON=python

all: moduleall modulealldelegate moduleexports moduleban modulealias

moduleall:
	$(PYTHON) tests/testModuleAll.py
	@echo "----------------------"

modulealldelegate:
	$(PYTHON) tests/testAllDelegate.py
	@echo "----------------------"

moduleexports:
	$(PYTHON) tests/testExports.py
	@echo "----------------------"

moduleban:
	$(PYTHON) tests/testBan.py
	@echo "----------------------"

modulealias:
	$(PYTHON) tests/testAlias.py
	@echo "----------------------"