release:
	mkrelease -p -d pypi

docs:
	cd docs; make html

upload-docs:
	python setup.py upload_docs --upload-dir docs/build/html
