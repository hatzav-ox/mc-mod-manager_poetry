"""file is a Mod Provider for files on the local system.
"""

import os, platform, requests
from pathlib import Path
from requests.models import HTTPError
from typing import Dict, Tuple

from ..plugin import DownloadHandler, GenerationHandler, MCMMPlugin, PluginBase

if platform.system() == "Windows":
    cache_dir = Path(f"{os.getenv('LOCALAPPDATA')}/mcmm/cache/file")
else:
    cache_dir = Path(f"{os.getenv('HOME')}/.cache/mcmm/file")
cache_dir.mkdir(exist_ok=True, parents=True)


@MCMMPlugin
class FileModProvider(PluginBase):
    id = "file"
    help_string = "Local File Mod Provider"

    @DownloadHandler
    def download_mod(self, mc_version, info) -> Tuple[Path, str]:
        file_path = Path(info["file_path"])

        out_file = cache_dir / f"{file_path.name}"

        out_file.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("rb") as in_f:
            with out_file.open("wb") as f:
                f.write(in_f.read())

        return (out_file, "")

    @GenerationHandler
    def generate(self) -> Tuple[Dict, str]:
        file_path = input("File Path: ")
        return ({"file_path": file_path}, "")
