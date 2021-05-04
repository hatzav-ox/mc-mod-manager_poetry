"""curse_forge provides a basic API for downloading mods from Curse Forge.
"""

import requests

latest_mc_version = "1.16.5"

def download_mod(id: int) -> str:
	r = requests.get(f"https://addons-ecs.forgesvc.net/api/v2/addon/{id}", headers={"User-Agent": "Mozilla/5.0"})

	r.raise_for_status() # I'm not in love with throwing an error, but I guess this is more robust than checking status_code ourselves.

	json_obj = r.json()

	latest_file_id = 0
	for obj in json_obj["gameVersionLatestFiles"]:
		if obj["gameVersion"] == latest_mc_version:
			latest_file_id = obj["projectFileId"]
			break
	else:
		raise RuntimeError(f"No files for Minecraft {latest_mc_version} found!")

	file_download_url = ""
	for obj in json_obj["latestFiles"]:
		if obj["id"] == latest_file_id:
			file_download_url = obj["downloadUrl"]
			break
	else:
		raise RuntimeError("Could not find file in latestFiles.")

	r = requests.get(file_download_url)

	with open("test.jar", "wb") as f:
		f.write(r.content)
