"""optifine is a Mod Provider for Curse Forge(curseforge.com).
"""

import os
import requests
from bs4 import BeautifulSoup as BS
from pathlib import Path
from requests.models import HTTPError
from typing import Dict, Tuple

from ..plugin import DownloadHandler, GenerationHandler, MCMMPlugin, PluginBase

@MCMMPlugin
class OptifineModProvider(PluginBase):
	id = "optifine"
	help_string = "Optifine Mod Provider"

	latest_mc_version = "1.16.5"

	@DownloadHandler
	def download_mod(self, info) -> Tuple[Path, str]:
		r = requests.get("https://optifine.net/downloads")
		try:
			r.raise_for_status()
		except HTTPError as e:
			return Path.cwd(), str(e)

		downloads_page = BS(r.text, "html.parser")

		file_download_page_url = downloads_page.find_all(self._check_bs4_tag)[1].attrs["href"]

		r = requests.get(file_download_page_url)
		try:
			r.raise_for_status()
		except HTTPError as e:
			return Path.cwd(), str(e)

		file_download_page = BS(r.text, "html.parser")

		file_download_url = f"https://optifine.net/{file_download_page.find(lambda tag: tag.has_attr('href') and 'downloadx' in tag['href'])['href']}"

		r = requests.get(file_download_url)
		try:
			r.raise_for_status()
		except HTTPError as e:
			return Path.cwd(), str(e)

		out_file = Path(f"{os.getenv('LOCALAPPDATA')}/mc_mod/cache/optifine/optifine.jar")

		out_file.parent.mkdir(parents=True, exist_ok=True)

		with out_file.open("wb") as f:
			f.write(r.content)

		# OptiFine with OptiFabric seems to work, but it might not when using Forge.
		# https://github.com/sp614x/optifine/issues/5323 explains how to command-line extract the mod jar.

		return (out_file, "")

	def _check_bs4_tag(self, tag: BS) -> bool:
		return tag.has_attr("href") and self.latest_mc_version in tag.attrs["href"] and not "pre" in tag.attrs["href"]

	@GenerationHandler
	def generate(self) -> Tuple[Dict, str]:
		return ({}, "")
