# Other library imports
import os
from typing import Dict
from json import load
from pathlib import Path
from shutil import move as shutil_move
from sys import argv

# Own library imports
from . import curse_forge
from . import optifine

__version__ = "0.0.1-alpha.1"

# TODO: Cross-platform locations
dot_minecraft = Path(os.getenv("APPDATA")) / ".minecraft"
config_dir = Path(os.getenv("APPDATA")) / "mc_mod"
profile_jars_dir = Path(os.getenv("LOCALAPPDATA")) / "mc_mod/profiles"

# Ensure our directories are valid
config_dir.mkdir(parents=True, exist_ok=True)
profile_jars_dir.mkdir(parents=True, exist_ok=True)

mod_providers: Dict = {"curse_forge": curse_forge, "optifine": optifine}

def cli():
	"""cli parses out sys.argv and dispatches the appropriate commands.
	"""
	command = argv[1] # mc_mod [command]

	if command == "switch":
		wanted_profile_name = argv[2] # mc_mod switch [profile_name]

		# Load profile from APPDATA/mc_mod/profiles/{wanted_profile_name}.json
		with (config_dir / f"profiles/{wanted_profile_name}.json").open("r") as f:
			profile_obj = load(f)

		# TODO: Remove mod jars from dot_minecraft/mods

		# TODO: Copy profile jars from LOCALAPPDATA to dot_minecraft/mods

	elif command == "update":
		wanted_profile_name = argv[2] # mc_mod update [profile_name]

		# Load profile from APPDATA/mc_mod/profiles/{wanted_profile_name}.json
		with (config_dir / f"profiles/{wanted_profile_name}.json").open("r") as f:
			profile_obj = load(f)

		# Download up-to-date jars
		for mod in profile_obj["mods"]:
			file_location: Path = mod_providers[mod["type"]].download_mod(mod["info"])
			print(file_location)

			# Move jars to profile_jars_dir/profiles/{wanted_profile_name}/{mod_file_name}
			(profile_jars_dir / wanted_profile_name).mkdir(parents=True, exist_ok=True)
			shutil_move(str(file_location), str(profile_jars_dir / wanted_profile_name / file_location.name))
