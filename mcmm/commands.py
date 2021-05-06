from json import load
from pathlib import Path
from shutil import copy as shutil_copy
from shutil import move as shutil_move
from types import ModuleType
from typing import Dict, List

# Own library imports
from .dirs import gen_dot_minecraft
from .dirs import gen_config_dir
from .dirs import gen_profile_jars_dir

from . import curse_forge
from . import github
from . import optifine

dot_minecraft = gen_dot_minecraft()
config_dir = gen_config_dir()
profile_jars_dir = gen_profile_jars_dir()

mod_providers: Dict[str, ModuleType] = {"curse_forge": curse_forge, "optifine": optifine, "github": github}

def _activate_dispatcher(args: List[str]) -> None:
	"""Parses out the command line arguments and calls switch.

	Args:
		args (List[str]): Arguments to parse.
	"""
	return activate(args[0])

def activate(profile: str) -> None:
	# Load profile from APPDATA/mcmm/profiles/{wanted_profile_name}.json
	if not (config_dir / f"profiles/{profile}.json").exists():
		raise RuntimeError(f"Could not find a profile.json for '{profile}'")

	# Remove mod jars from dot_minecraft/mods
	for file in (dot_minecraft / "mods").glob("*.jar"):
		file.unlink()

	# Copy profile jars from LOCALAPPDATA to dot_minecraft/mods
	for file in (profile_jars_dir / profile).glob("*"):
		shutil_copy(str(file), str(dot_minecraft / "mods" / file.name))

def _download_dispatcher(args: List[str]) -> None:
	"""Parses out the command line arguments and calls update.

	Args:
		args (List[str]): Arguments to parse.
	"""
	return download(args[0])

def download(profile: str) -> None:
	# Load profile from APPDATA/mcmm/profiles/{wanted_profile_name}.json
	with (config_dir / f"profiles/{profile}.json").open("r") as f:
		profile_obj = load(f)

	# Clean jar storage before downloading new versions (which may have different names which cause the old jars to not be overwritten).
	for file in (profile_jars_dir / profile).glob("*"):
		file.unlink()

	errs = {}
	# Download up-to-date jars
	for mod in profile_obj["mods"]:
		try:
			file_location: Path = mod_providers[mod["type"]].download_mod(mod["info"])
		except Exception as e:
			errs[str(mod)] = e
			continue

		# Move jars to profile_jars_dir/profiles/{wanted_profile_name}/{mod_file_name}
		(profile_jars_dir / profile).mkdir(parents=True, exist_ok=True)
		shutil_move(str(file_location), str(profile_jars_dir / profile / file_location.name))

	for err in errs:
		print(f"Error: {errs[str(err)]}  on profile entry: {err}\n")

	print(f"Downloaded profile '{profile}'. If you are currently using this profile and wish to take advantage of the newly downloaded mods, use the activate command.")
