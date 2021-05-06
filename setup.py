from setuptools import setup
from mcmm import __version__ as mcmm_version

with open("README.md") as fh:
	long_description = fh.read()

setup(name="mcmm",
	version=mcmm_version,
	description="",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="http://github.com/BrenekH/mc-mod-manager",
	author="Brenek Harrison",
	author_email="brenekharrison@gmail.com",
	packages=["mcmm"],
	zip_safe=False,
	classifiers=[
		"Programming Language :: Python :: 3",
		"Operating System :: OS Independent",
	],
	python_requires=">=3.6")

# Commands to deploy
# Clean step: (linux) rm -rf dist;  (Windows CMD) rmdir /s /q dist;  (Windows Powershell)  rm dist -r -force
# Build step: python setup.py sdist bdist_wheel
# Release step: python -m twine upload dist/*
