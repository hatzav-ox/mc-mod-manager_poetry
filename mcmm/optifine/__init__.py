"""optifine is a Mod Provider for Curse Forge(curseforge.com).
"""

import os, platform, requests
from bs4 import BeautifulSoup as BS
from pathlib import Path
from requests.models import HTTPError
from typing import Dict, Tuple

from ..plugin import DownloadHandler, GenerationHandler, MCMMPlugin, PluginBase

if platform.system() == "Windows":
	cache_dir = Path(f"{os.getenv('LOCALAPPDATA')}/mcmm/cache/optifine")
else:
	cache_dir = Path(f"{os.getenv('HOME')}/.cache/mcmm/optifine")
cache_dir.mkdir(exist_ok=True, parents=True)

@MCMMPlugin
class OptifineModProvider(PluginBase):
	id = "optifine"
	help_string = "Optifine Mod Provider"

	@DownloadHandler
	def download_mod(self, mc_version, info) -> Tuple[Path, str]:
		prerel_allowed = info["allow_prerelease"] if "allow_prerelease" in info else False

		r = requests.get("https://optifine.net/downloads")
		try:
			r.raise_for_status()
		except HTTPError as e:
			return Path.cwd(), str(e)

		downloads_page = BS(r.text, "html.parser")

		def check_bs4_tag_wrapper(tag: BS) -> bool:
			return self._check_bs4_tag(tag, mc_version, prerel_allowed)

		file_download_page_url = downloads_page.find_all(check_bs4_tag_wrapper)[1].attrs["href"]

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

		out_file = cache_dir / "optifine.jar"

		out_file.parent.mkdir(parents=True, exist_ok=True)

		with out_file.open("wb") as f:
			f.write(r.content)

		# OptiFine with OptiFabric seems to work, but it might not when using Forge.
		# https://github.com/sp614x/optifine/issues/5323 explains how to command-line extract the mod jar.

		return (out_file, "")

	def _check_bs4_tag(self, tag: BS, mc_version: str, allow_prerelease: bool) -> bool:
		has_target_version = tag.has_attr("href") and mc_version in tag.attrs["href"]
		is_prerel = tag.has_attr("href") and "pre" in tag.attrs["href"]
		return has_target_version and not is_prerel if not allow_prerelease else has_target_version

	@GenerationHandler
	def generate(self) -> Tuple[Dict, str]:
		return ({"allow_prerelease": input("Allow Pre-Release versions (y/N)? ").lower() == "y"}, "")
