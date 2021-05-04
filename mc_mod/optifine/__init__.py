"""optifine provides a basic API for downloading OptiFine from optifine.net.
"""

import os
import requests
from bs4 import BeautifulSoup as BS
from typing import Tuple
from pathlib import Path

latest_mc_version = "1.16.5"

def download_mod(info) -> Path:
	r = requests.get("https://optifine.net/downloads")
	r.raise_for_status()

	downloads_page = BS(r.text, "html.parser")

	file_download_url = downloads_page.find_all(_check_bs4_tag)[1].attrs["href"]

	r = requests.get(file_download_url)
	r.raise_for_status()

	out_file = Path(f"{os.getenv('LOCALAPPDATA')}/mc_mod/cache/optifine/optifine.jar")

	out_file.parent.mkdir(parents=True, exist_ok=True)

	with out_file.open("wb") as f:
		f.write(r.content)

	return out_file

def _check_bs4_tag(tag: BS) -> bool:
	return tag.has_attr("href") and latest_mc_version in tag.attrs["href"] and not "pre" in tag.attrs["href"]
