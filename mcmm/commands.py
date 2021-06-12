from colorama import Fore
from json import dump, load
from pathlib import Path
from shutil import copy as shutil_copy
from shutil import move as shutil_move
from typing import List

# Own library imports
from .dirs import gen_dot_minecraft
from .dirs import gen_config_dir
from .dirs import gen_jar_storage_dir
from .plugin import HandlerType
from .plugin_internal import ProviderRunner

dot_minecraft: Path = gen_dot_minecraft()
config_dir = gen_config_dir()
jar_storage_dir = gen_jar_storage_dir()

def _activate_dispatcher(args: List[str]) -> None:
	"""Parses out the command line arguments and calls activate.

	Args:
		args (List[str]): Arguments to parse.
	"""
	return activate(args[0])

def activate(profile: str) -> None:
	global dot_minecraft
	# Load profile json
	if not (config_dir / f"profiles/{profile}.json").exists():
		print(f"[{Fore.RED}ERROR{Fore.RESET}] Could not find a profile.json for '{profile}'")
		return

	# Load profile json
	with (config_dir / f"profiles/{profile}.json").open("r") as f:
		profile_obj = load(f)

	try:
		mc_dir = profile_obj["minecraft_folder"]
		if mc_dir != "" and mc_dir != None:
			dot_minecraft = Path(mc_dir)
	except KeyError:
		pass

	mods_folder: Path = dot_minecraft / "mods"

	# Remove mod jars from dot_minecraft/mods
	for file in mods_folder.glob("*.jar"):
		file.unlink()

	# Copy profile jars from jar_storage_dir to dot_minecraft/mods
	for file in (jar_storage_dir / profile).glob("*"):
		shutil_copy(str(file), str(mods_folder / file.name))

	print(f"[{Fore.GREEN}SUCCESS{Fore.RESET}] Profile '{profile}' successfully activated.")

def _download_dispatcher(args: List[str], provider_runner: ProviderRunner) -> None:
	"""Parses out the command line arguments and calls download.

	Args:
		args (List[str]): Arguments to parse.
	"""
	return download(args[0], provider_runner)

def download(profile: str, provider_runner: ProviderRunner) -> None:
	# Load profile json
	with (config_dir / f"profiles/{profile}.json").open("r") as f:
		profile_obj = load(f)

	print(f"[{Fore.GREEN}INFO{Fore.RESET}] Cleaning existing jars from jar storage of profile '{profile}'.")
	# Clean jar storage before downloading new versions (which may have different names which cause the old jars to not be overwritten).
	for file in (jar_storage_dir / profile).glob("*"):
		file.unlink()

	print(f"[{Fore.GREEN}INFO{Fore.RESET}] Downloading new jars for profile '{profile}'.")
	errs = {}
	# Download up-to-date jars
	for mod in profile_obj["mods"]:
		try:
			file_location, err_str = provider_runner.download(mod["provider"], profile_obj["minecraft_version"], mod["metadata"])
			if err_str != "":
				errs[str(mod)] = err_str
				continue
		except Exception as e:
			errs[str(mod)] = e
			continue

		# Move jars to jar_storage_dir/profiles/{wanted_profile_name}/{mod_file_name}
		(jar_storage_dir / profile).mkdir(parents=True, exist_ok=True)
		shutil_move(str(file_location), str(jar_storage_dir / profile / file_location.name))

	for err in errs:
		print(f"{Fore.RED}Error{Fore.RESET}: {errs[str(err)]}  on profile entry: {err}\n")

	print(f"[{Fore.GREEN}SUCCESS{Fore.RESET}] Profile '{profile}' successfully downloaded. If you are currently using this profile and wish to take advantage of the newly downloaded mods, use the {Fore.CYAN}activate{Fore.RESET} command.")

def _generate_dispatcher(args: List[str], provider_runner: ProviderRunner) -> None:
	"""Parses out the command line arguments and calls generate.

	Args:
		args (List[str]): Arguments to parse.
	"""
	return generate(args[0], provider_runner)

def generate(profile: str, provider_runner: ProviderRunner) -> None:
	profile_json_file = config_dir / f"profiles/{profile}.json"

	if profile_json_file.exists():
		overwrite = input(f"Profile '{profile}' already exists. Do you want to overwrite it? (y/n) ")
		if overwrite.lower() != "y":
			print("Quitting...")
			return

	npt = input("Minecraft folder (leave empty for system default): ")

	if npt == "":
		new_prof_obj = {"mods": []}
	else:
		new_prof_obj = {"minecraft_folder": npt, "mods": []}

	npt = input("Minecraft Version (default: 1.17): ")

	if npt == "":
		new_prof_obj["minecraft_version"] = "1.17"
	else:
		new_prof_obj["minecraft_version"] = npt

	while True:
		print("\nAvailable Mod Providers:")
		for mod_id in provider_runner._event_registry[HandlerType.generate]:
			print(f"    {mod_id}")

		mod_prov_id = input("\nEnter a Mod Provider ID or 'finish' to finish: ")
		if mod_prov_id == "finish":
			break

		if mod_prov_id not in provider_runner._event_registry[HandlerType.generate]:
			print(f"[{Fore.RED}ERROR{Fore.RESET}] '{mod_prov_id}' is not a valid Mod Provider ID.")
			continue

		mod_prov_metadata, err_str = provider_runner.generate(mod_prov_id)

		if err_str == "":
			new_prof_obj["mods"].append({"provider": mod_prov_id, "metadata": mod_prov_metadata})
		else:
			print(f"[{Fore.RED}ERROR{Fore.RESET}] The selected mod provider errored with the following explanation: {err_str}")

	with profile_json_file.open("w") as f:
		dump(new_prof_obj, f, indent=4)

	print(f"[{Fore.GREEN}SUCCESS{Fore.RESET}] Profile '{profile}' successfully generated.")

def _list_dispatcher(args: List[str]) -> None:
	"""Parses out the command line arguments and calls list_profiles.

	Args:
		args (List[str]): Arguments to parse.
	"""
	return list_profiles()

def list_profiles():
	profile_storage = config_dir / "profiles"

	for file in profile_storage.glob("*.json"):
		print(file.name.replace(".json", ""))
