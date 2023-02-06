#!/bin/bash
rm -rf dist/
python setup.py sdist bdist_wheel
wait
python -m twine upload dist/* --verbose