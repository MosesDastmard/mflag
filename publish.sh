#!/bin/bash
rm -rf dist/
python setup.py sdist bdist_wheel
wait
twine upload dist/* --verbose