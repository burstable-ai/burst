rm -fr build dist
python setup.py sdist bdist_wheel
python3 -m twine upload --verbose dist/*
