"""modrinth is a Mod Provider for Modrinth(modrinth.com).
"""

import platform, requests
from os import getenv
from pathlib import Path
from requests.models import HTTPError
from typing import Dict, Tuple

from ..plugin import DownloadHandler, GenerationHandler, MCMMPlugin, PluginBase

current_os = platform.system()
if current_os == "Windows":
	save_dir = Path(getenv("LOCALAPPDATA")) / "mcmm/cache/modrinth"
else:
	save_dir = Path(getenv("HOME")) / ".cache/mcmm/modrinth"
save_dir.mkdir(exist_ok=True, parents=True)

@MCMMPlugin
class ModrinthModProvider(PluginBase):
	id = "modrinth"
	help_string = "Modrinth Mod Provider"
	latest_game_version = "1.16.5"

	@DownloadHandler
	def download(self, metadata: Dict) -> Tuple[Path, str]:
		_id = metadata["id"]
		allow_prereleases = metadata["allow_prereleases"]
		mod_loader = metadata["mod_loader"]
		must_contain = metadata["must_contain"]
		must_not_contain = metadata["must_not_contain"]

		r = requests.get(f"https://api.modrinth.com/api/v1/mod/{_id}/version")
		try:
			r.raise_for_status()
		except HTTPError as e:
			return (Path.cwd(), str(e))

		json_obj = r.json()

		for file in json_obj:
			if not allow_prereleases and file["version_type"] != "release":
				continue

			if mod_loader not in file["loaders"]:
				continue

			if self.latest_game_version not in file["game_versions"]:
				continue

			for f in file["files"]:
				filename = f["filename"]

				invalid = False
				for s in must_contain:
					if s not in filename:
						invalid = True
						break
				if invalid:
					continue

				for s in must_not_contain:
					if s in filename:
						invalid = True
						break
				if invalid:
					continue

				r = requests.get(f["url"])
				try:
					r.raise_for_status()
				except HTTPError as e:
					return (Path.cwd(), str(e))

				out_file: Path = save_dir / filename

				with out_file.open("wb") as f:
					f.write(r.content)

				return (out_file, "")

		return (Path.cwd(), "Valid file not found.")

	@GenerationHandler
	def generate(self) -> Tuple[Dict, str]:
		_id = input("Mod ID: ")
		allow_prereleases = input("Allow Pre-Releases (y/n): ").lower() == "y"
		mod_loader = input("Mod Loader (ex. 'fabric' or 'forge'): ").lower()

		must_contain = []
		while True:
			npt = input("Words that the file must contain (one per line, enter to continue): ")
			if npt == "":
				break
			must_contain.append(npt)

		must_not_contain = []
		while True:
			npt = input("Words that the file must not contain (one per line, enter to continue): ")
			if npt == "":
				break
			must_not_contain.append(npt)

		return ({
			"id": _id,
			"allow_prereleases": allow_prereleases,
			"mod_loader": mod_loader,
			"must_contain": must_contain,
			"must_not_contain": must_not_contain
		}, "")
