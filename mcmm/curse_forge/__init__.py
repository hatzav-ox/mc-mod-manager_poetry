"""curse_forge is a Mod Provider for Curse Forge(curseforge.com).
"""

import os
import requests
from pathlib import Path
from requests.models import HTTPError
from typing import Dict, Tuple

from ..plugin import DownloadHandler, GenerationHandler, MCMMPlugin, PluginBase

@MCMMPlugin
class CurseForgeModProvider(PluginBase):
	id = "curse_forge"
	help_string = "Curse Forge Mod Provider"

	latest_mc_version = "1.16.5"

	@DownloadHandler
	def download_mod(self, info) -> Tuple[Path, str]:
		id = info["id"]
		name = info["name"]

		r = requests.get(f"https://addons-ecs.forgesvc.net/api/v2/addon/{id}", headers={"User-Agent": "Mozilla/5.0"})
		try:
			r.raise_for_status()
		except HTTPError as e:
			return (Path.cwd(), str(e))

		json_obj = r.json()

		if info["check_file_name"] == None:
			file_id, filename, err_str = self._extract_file(json_obj["gameVersionLatestFiles"])
			if err_str != "":
				return (Path.cwd(), err_str)
		else:
			file_id, filename, err_str = self._extract_file_with_file_name_check(json_obj["gameVersionLatestFiles"], info["check_file_name"])
			if err_str != "":
				return (Path.cwd(), err_str)

		file_download_url = self._gen_download_url(file_id, filename)

		r = requests.get(file_download_url)
		try:
			r.raise_for_status()
		except HTTPError as e:
			return (Path.cwd(), str(e))

		out_file = Path(f"{os.getenv('LOCALAPPDATA')}/mcmm/cache/curse_forge/{name}.jar")

		out_file.parent.mkdir(parents=True, exist_ok=True)

		with out_file.open("wb") as f:
			f.write(r.content)

		return (out_file, "")

	def _extract_file(self, json_obj) -> Tuple[int, str, str]:
		file_id = 0
		filename = ""
		for obj in json_obj:
			if obj["gameVersion"] == self.latest_mc_version:
				file_id = obj["projectFileId"]
				filename = obj["projectFileName"]
				break
		else:
			return (0, "", f"No files for Minecraft {self.latest_mc_version} found!")

		return (file_id, filename, "")

	def _extract_file_with_file_name_check(self, json_obj, search_file_name: str) -> Tuple[int, str, str]:
		file_id = 0
		filename = ""
		for obj in json_obj:
			if obj["gameVersion"] == self.latest_mc_version and search_file_name.lower() in obj["projectFileName"].lower():
				file_id = obj["projectFileId"]
				filename = obj["projectFileName"]
				break
		else:
			return (0, "", f"No files for Minecraft {self.latest_mc_version} found!")

		return (file_id, filename, "")

	def _gen_download_url(self, id: int, filename: str) -> str:
		str_id = str(id)
		return f"https://edge.forgecdn.net/files/{str_id[:4]}/{str_id[4:]}/{filename}"

	@GenerationHandler
	def generate(self) -> Tuple[Dict, str]:
		name = input("Name: ")
		ID = input("ID: ")
		check_file_name = input("Check file name (string that must be in the file name) leave blank for None: ")
		if check_file_name == "":
			check_file_name = None
		return ({"name": name, "id": ID, "check_file_name": check_file_name}, "")
