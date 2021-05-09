# Minecraft Mod Manager (mcmm)

## Dependencies

This project uses [Poetry](https://python-poetry.org) to manage dependencies.

## Building a Release

`binary.py` is a special file that imports `mcmm` and runs the `cli` function just as the package does when invoked by Python.

To build a release binary, simply use `poetry run PyInstaller --onefile --name mcmm binary.py` from the root folder and an executable will be available in the `dist/` directory.
