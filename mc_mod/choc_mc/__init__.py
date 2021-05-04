"""choc_mc is a Mod Provider for chocolateminecraft.com.
"""

import os
import requests
from bs4 import BeautifulSoup as BS
from typing import Tuple
from pathlib import Path

latest_mc_version = "1.16.5"

def download_mod(info) -> Path:
	return Path.cwd()
