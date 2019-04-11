all: moduleall modulealldelegate moduleexports moduleban modulealias

moduleall:
	python tests/testModuleAll.py
	@echo "----------------------"

modulealldelegate:
	python tests/testAllDelegate.py
	@echo "----------------------"

moduleexports:
	python tests/testExports.py
	@echo "----------------------"

moduleban:
	python tests/testBan.py
	@echo "----------------------"

modulealias:
	python tests/testAlias.py
	@echo "----------------------"