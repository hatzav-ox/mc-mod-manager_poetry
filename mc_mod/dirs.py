"""dirs.py contains functions for generating the directories required for mc_mod based on the current OS.
"""

import platform
from os import getenv
from pathlib import Path

current_os = platform.system() # Can be 'Linux', 'Darwin', or 'Windows'

def gen_dot_minecraft() -> Path:
	if current_os == "Linux":
		_dir = Path(getenv("HOME"))
	elif current_os == "Darwin":
		_dir = Path(f"{getenv('HOME')}/Library/Application Support/minecraft")
	elif current_os == "Windows":
		_dir = Path(getenv("APPDATA"))

	_dir: Path = _dir / ".minecraft"
	if not _dir.exists():
		raise RuntimeError(f"Could not find '.minecraft' folder at {_dir}")

	return _dir

def gen_config_dir() -> Path:
	if current_os == "Linux" or current_os == "Darwin":
		# Technically, the "correct" location for configuration on Unix is $XDG_CONFIG_HOME, but for consistency, $HOME/.config is fine.
		_dir = Path(getenv("HOME")) / ".config"
	elif current_os == "Windows":
		_dir = Path(getenv("APPDATA"))

	_dir: Path = _dir / "mc_mod"
	_dir.mkdir(parents=True, exist_ok=True)

	return _dir

def gen_profile_jars_dir() -> Path:
	if current_os == "Linux" or current_os == "Darwin":
		_dir = Path(getenv("HOME"))
	elif current_os == "Windows":
		_dir = Path(getenv("LOCALAPPDATA"))

	_dir: Path = _dir / "mc_mod/profiles"
	_dir.mkdir(parents=True, exist_ok=True)

	return _dir
