from colorama import init as colorama_init
from colorama import Fore
from json import load
from sys import argv
from types import ModuleType
from typing import List, Union

from . import curse_forge, github, optifine, modrinth
from .commands import _activate_dispatcher, _deactivate_dispatcher, _download_dispatcher, _generate_dispatcher, _list_dispatcher
from .dirs import gen_config_dir
from .plugin_internal import load_providers

__version__ = "0.0.5"

def cli():
	"""cli parses out sys.argv and dispatches the appropriate commands.
	"""
	colorama_init()

	if "--help" in argv:
		help()
		return

	if "--version" in argv:
		version()
		return

	if len(argv) == 1:
		print(f"[{Fore.RED}ERROR{Fore.RESET}] Expected at least one argument.")
		return

	command = argv[1] # mcmm [command]

	if command == "activate":
		_activate_dispatcher(argv[2:])

	elif command == "deactivate":
		_deactivate_dispatcher(argv[2:])

	elif command == "download":
		mod_providers = load_providers(aggregate_mod_provider_list())
		_download_dispatcher(argv[2:], mod_providers)

	elif command == "generate":
		mod_providers = load_providers(aggregate_mod_provider_list())
		_generate_dispatcher(argv[2:], mod_providers)

	elif command == "list":
		_list_dispatcher(argv[2:])

def help():
	print(f"""Minecraft Mod Manager (mcmm) {__version__} Help

Commands:
    - activate <profile> - Removes all existing jars from the .minecraft/mods folder and copies the jars associated with <profile> into .minecraft/mods.

	- deactivate [minecraft folder] - Removes all existing jars from the default installation, or a specific installation, if one is provided.

    - download <profile> - Downloads all jars defined in <profile> to a storage location.
        --mc-version <version> - Forces a download of jars for Minecraft Version <version> in all supporting Mod Providers.

    - generate <profile> - Creates a new profile.

    - list               - Lists all available profiles.

""")

def version():
	print(f"Minecraft Mod Manager (mcmm) Version {__version__}")

def aggregate_mod_provider_list() -> List[Union[str, ModuleType]]:
	internal_mps = [curse_forge, optifine, github, modrinth]
	config_dir = gen_config_dir()
	config_file = config_dir / "config.json"

	if not config_file.exists():
		with config_file.open("w") as f:
			f.write(r'{"mod_providers": []}')

	with config_file.open("r") as f:
		user_conf = load(f)

	return user_conf["mod_providers"] + internal_mps
