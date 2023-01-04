#!/bin/bash
rm -rf dist/
python setup.py sdist
wait
twine upload dist/* --verbose