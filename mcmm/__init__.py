from json import load
from sys import argv
from types import ModuleType
from typing import List, Union

from . import curse_forge, github, optifine, modrinth
from .commands import _activate_dispatcher
from .commands import _download_dispatcher
from .commands import _generate_dispatcher
from .dirs import gen_config_dir
from .plugin_internal import load_providers

__version__ = "0.0.1-alpha.1"

def cli():
	"""cli parses out sys.argv and dispatches the appropriate commands.
	"""
	command = argv[1] # mcmm [command]

	if command == "activate":
		_activate_dispatcher(argv[2:])

	elif command == "download":
		mod_providers = load_providers(aggregate_mod_provider_list())
		_download_dispatcher(argv[2:], mod_providers)

	elif command == "generate":
		mod_providers = load_providers(aggregate_mod_provider_list())
		_generate_dispatcher(argv[2:], mod_providers)

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
