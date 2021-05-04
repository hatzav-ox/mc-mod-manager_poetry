"""curse_forge is a Mod Provider for Curse Forge(curseforge.com).
"""

import os
import requests
from typing import Tuple
from pathlib import Path

latest_mc_version = "1.16.5"

def download_mod(info) -> Path:
	id = info["id"]
	name = info["name"]

	r = requests.get(f"https://addons-ecs.forgesvc.net/api/v2/addon/{id}", headers={"User-Agent": "Mozilla/5.0"})
	r.raise_for_status() # I'm not in love with throwing an error, but I guess this is more robust than checking status_code ourselves.

	json_obj = r.json()

	if info["check_file_name"] == None:
		file_id, filename = _extract_file(json_obj["gameVersionLatestFiles"])
	else:
		file_id, filename = _extract_file_with_file_name_check(json_obj["gameVersionLatestFiles"], info["check_file_name"])

	file_download_url = _gen_download_url(file_id, filename)

	r = requests.get(file_download_url)
	r.raise_for_status()

	out_file = Path(f"{os.getenv('LOCALAPPDATA')}/mc_mod/cache/curse_forge/{name}.jar")

	out_file.parent.mkdir(parents=True, exist_ok=True)

	with out_file.open("wb") as f:
		f.write(r.content)

	return out_file

def _extract_file(json_obj) -> Tuple[int, str]:
	file_id = 0
	filename = ""
	for obj in json_obj:
		if obj["gameVersion"] == latest_mc_version:
			file_id = obj["projectFileId"]
			filename = obj["projectFileName"]
			break
	else:
		raise RuntimeError(f"No files for Minecraft {latest_mc_version} found!")

	return file_id, filename

def _extract_file_with_file_name_check(json_obj, search_file_name: str) -> Tuple[int, str]:
	file_id = 0
	filename = ""
	for obj in json_obj:
		if obj["gameVersion"] == latest_mc_version and search_file_name.lower() in obj["projectFileName"].lower():
			file_id = obj["projectFileId"]
			filename = obj["projectFileName"]
			break
	else:
		raise RuntimeError(f"No files for Minecraft {latest_mc_version} found!")

	return file_id, filename

def _gen_download_url(id: int, filename: str) -> str:
	str_id = str(id)
	return f"https://edge.forgecdn.net/files/{str_id[:4]}/{str_id[4:]}/{filename}"
