VERSION = 1.6

PKG = resources

.DEFAULT_GOAL = version
.PHONY: version
version:
	@ echo "Script version:" $(VERSION)


.PHONY: run
run:  
	@ /usr/bin/env python manage.py run


.PHONY: clean
clean:  
	@ find . -name "*.pyc" -delete
	@ find . -name "*.orig" -delete


.PHONY: requirements
requirements:
	@ /usr/bin/env pip install -r requirements.txt

.PHONY: requirements-test
requirements-test:
	@ /bin/true

.PHONY: requirements-dev
requirements-dev:
	@ /usr/bin/env pip install ipython


.PHONY: dependencies
dependencies:
	@ /usr/bin/env pip install -U pip


.PHONY: prepare
prepare: dependencies requirements

.PHONY: prepare-test
prepare-test: prepare requirements-test

.PHONY: prepare-dev
prepare-dev: prepare-test requirements-dev


.PHONY: shell
shell: 
	@ /bin/sh


.PHONY: python
python: 
	@ /usr/bin/env python
