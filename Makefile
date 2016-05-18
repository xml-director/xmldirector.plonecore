build:
	virtualenv-2.7 .
	bin/python bootstrap.py -c base.cfg
	bin/buildout -c buildout-plone-4.3.cfg

build-demo:
	virtualenv-2.7 .
	bin/python bootstrap.py -c base.cfg
	bin/buildout -c demo.cfg

build5:
	virtualenv-2.7 .
	bin/python bootstrap.py -c base.cfg
	bin/buildout -c buildout-plone-5.1.cfg

build-demo5:
	virtualenv-2.7 .
	bin/python bootstrap.py -c base.cfg
	bin/buildout -c demo5.cfg


test-demo-local:
	bin/instance run democontent/setup-plone.py local

release:
	mkrelease -p -d pypi

docs:
	cd docs; make html

upload-docs:
	python setup.py upload_docs --upload-dir docs/build/html

test:
	bin/test xmldirector
	bin/test-crex xmldirector

test-coverage:
	unbuffer bin/test --coverage=${PWD}/coverage xmldirector | tee coverage.txt

demo:
	bin/instance run src/xmldirector.demo/democontent/setup-plone.py local

demo-docker:
	bin/instance run src/xmldirector.demo/democontent/setup-plone.py docker
