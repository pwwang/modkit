PYTHON=python
MSG=

all: test

test:
	$(PYTHON) tests/test.py

build:
	$(PYTHON) setup.py sdist bdist_wheel --universal

dist:
	twine upload --skip-existing dist/* 

publish: modkit.py
	@$(eval CURRVER=$(shell head -1 $< | sed 's/[^0-9.]//g')) \
	echo '- Current version: $(CURRVER)'; \
	ver1=$$(echo $(CURRVER) | cut -d. -f1); \
	ver2=$$(echo $(CURRVER) | cut -d. -f2); \
	ver3=$$(echo $(CURRVER) | cut -d. -f3); \
	newver=$$(echo $$ver1.$$ver2.$$((ver3 + 1)));  \
	echo "- New version: $$newver"; \
	echo "- Replacing the new version in source file ..."; \
	sed -i.bak -r "s/^VERSION *= *('|\").+?\1/VERSION = '$$newver'/" $<; \
	echo "Pushing to github ..."; \
	git commit -a -m "$$newver $(MSG)"; \
	git push; \
	echo "Building the package ..."; \
	$(PYTHON) setup.py sdist bdist_wheel --universal; \
	echo "Uploading to pypi ..."; \
	twine upload --skip-existing dist/* 