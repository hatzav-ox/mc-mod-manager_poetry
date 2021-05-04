from mc_mod import curse_forge
import os
from json import load
from pathlib import Path
from sys import argv

__version__ = "0.0.1-alpha.1"

dot_minecraft = Path(os.getenv("APPDATA")) / ".minecraft"

def cli():
	"""cli parses out sys.argv and dispatches the appropriate commands.
	"""
	command = argv[1] # mc_mod [command]

	if command == "switch":
		wanted_profile_name = argv[2] # mc_mod switch [profile_name]

		# TODO: Load profile from APPDATA/mc_mod/profiles/{wanted_profile_name}.json
		with Path(f"{os.getenv('APPDATA')}/mc_mod/profiles/{wanted_profile_name}.json").open("r") as f:
			profile_obj = load(f)

		# TODO: Update mod jars in cache
		curse_forge.download_mod(profile_obj["mods"][0]["info"]["id"])

		# TODO: Remove mod jars from dot_minecraft

		# TODO: Copy profile jars to dot_minecraft
