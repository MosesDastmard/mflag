#!/bin/bash
rm -rf dist/
python setup.py sdist
wait
python -m twine upload dist/* --verbose