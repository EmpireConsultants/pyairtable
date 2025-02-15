.PHONY: test docs

usage:
	cat Makefile

init:
	git config core.hooksPath scripts/githooks

release-test:
	make clean
	python -m build --sdist --wheel --outdir ./dist
	twine upload --repository testpypi ./dist/*

release:
	make clean
	python -m build --sdist --wheel --outdir ./dist
	twine upload ./dist/*

bump:
	@bash -c "./scripts/bump.sh"

test:
	pytest -v

tox:
	tox -e py

coverage:
	pytest --cov=pyairtable --cov-report=html
	open htmlcov/index.html

lint:
	flake8 .
	black --diff .

docs:
	bash -c "cd ./docs; make html"
	# open ./docs/build/html/index.html

clean:
	python3 -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
	python3 -c "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('pytest_cache')]"
	rm -rdf ./docs/build
	rm -rdf ./dist
	rm -rdf ./build
	rm -rdf ./htmlcov
	rm -rdf  pyairtable.egg-info
	rm -rdf  .pytest_cache

