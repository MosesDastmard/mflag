#!/bin/bash
# python -m jupyter nbconvert --to markdown README.ipynb
wait
rm -rf dist/
python setup.py sdist bdist_wheel
wait
python -m twine upload dist/* --verbose