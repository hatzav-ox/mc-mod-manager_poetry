"""github is a Mod Provider for GitHub(github.com).
"""

import os
import random
import requests
from dateutil.parser import isoparse
from github_release import get_releases
from pathlib import Path
from requests.models import HTTPError
from shutil import rmtree as shutil_rmtree
from shutil import move as shutil_move
from subprocess import Popen
from typing import Dict, Tuple

from ..plugin import DownloadHandler, GenerationHandler, MCMMPlugin, PluginBase

save_dir = Path(f"{os.getenv('LOCALAPPDATA')}/mcmm/cache/github")

save_dir.mkdir(parents=True, exist_ok=True)

@MCMMPlugin
class GitHubModProvider(PluginBase):
	id = "github"
	help_string = "GitHub Mod Provider"

	@DownloadHandler
	def download_mod(self, info: Dict) -> Tuple[Path, str]:
		repo = info["repo"]

		if info["releases"] != None:
			return self._releases(repo, info["releases"])
		elif info["compile"] != None:
			return self._compile(repo, info["compile"])
		else:
			return (Path.cwd(), "'releases' or 'compile' must be defined")

	def _releases(self, repo: str, info: Dict) -> Path:
		if info["latest"]:
			r = requests.get(f"https://api.github.com/repos/{repo}/releases/latest")
			try:
				r.raise_for_status()
			except HTTPError as e:
				return (Path.cwd(), str(e))

			latest_release = r.json()

			for asset in latest_release["assets"]:
				invalid = False
				for s in info["must_contain"]:
					if s not in asset["name"]:
						invalid = True
						break
				if invalid:
					continue

				for s in info["must_not_contain"]:
					if s in asset["name"]:
						invalid = True
						break
				if invalid:
					continue

				r = requests.get(asset["browser_download_url"])
				try:
					r.raise_for_status()
				except HTTPError as e:
					return (Path.cwd(), str(e))

				out_file: Path = save_dir / asset["name"]

				with out_file.open("wb") as f:
					f.write(r.content)

				return (out_file, "")

			return (Path.cwd(), f"Could not locate a valid binary for {info}")

		else: # We have to evaluate all tags against info["tag"]
			matching_releases = [release for release in get_releases(repo) if info["tag"] in release["tag_name"]]

			times = [isoparse(r["published_at"]) for r in matching_releases]

			most_recent_release_time = max(times)

			most_recent_release = [r for r in matching_releases if isoparse(r["published_at"]) == most_recent_release_time][0]

			for asset in most_recent_release["assets"]:
				invalid = False
				for s in info["must_contain"]:
					if s not in asset["name"]:
						invalid = True
						break
				if invalid:
					continue

				for s in info["must_not_contain"]:
					if s in asset["name"]:
						invalid = True
						break
				if invalid:
					continue

				r = requests.get(asset["browser_download_url"])
				try:
					r.raise_for_status()
				except HTTPError as e:
					return (Path.cwd(), str(e))

				out_file: Path = save_dir / asset["name"]

				with out_file.open("wb") as f:
					f.write(r.content)

				return (out_file, "")

			return (Path.cwd(), f"Could not locate a valid binary for {info}")

	def _compile(self, repo: str, info: Dict) -> Path:
		clone_dir = save_dir / (repo.replace("/", "") + f"-{random.randint(0, 99999999)}")
		os.system(f"git clone https://github.com/{repo} {clone_dir}")

		p = Popen(["git", "checkout", info["branch"]], cwd=str(clone_dir), shell=True)
		p.wait()

		p = Popen(info["command"], cwd=str(clone_dir), shell=True)
		p.wait()

		jar_dir: Path = clone_dir / info["dir"]

		for jar in jar_dir.glob("*.jar"):
				invalid = False
				for s in info["must_contain"]:
					if s not in jar.name:
						invalid = True
						break
				if invalid:
					continue

				for s in info["must_not_contain"]:
					if s in jar.name:
						invalid = True
						break
				if invalid:
					continue

				out_file: Path = save_dir / jar.name

				shutil_move(str(jar), str(out_file))

				shutil_rmtree(str(clone_dir), ignore_errors=True)
				return (out_file, "")

		# Unfortunately, shutil_rmtree leaves behind some files in .git because of permission errors
		shutil_rmtree(str(clone_dir), ignore_errors=True)
		return (Path.cwd(), f"Could not locate a binary for info: {info}")

	@GenerationHandler
	def generate(self) -> Tuple[Dict, str]:
		repo = input("Repo name (ex. 'BrenekH/mc-mod-manager'): ")
		while True:
			npt = input("Input 'release' or 'compile': ")
			if npt.lower() == "release":
				latest = input("Use latest release (y/n): ") == "y"

				tag = input("Target tag(empty for None): ")
				if tag == "":
					tag = None

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
					"repo": repo,
					"compile": None,
					"releases": {
						"latest": latest,
						"tag": tag,
						"must_contain": must_contain,
						"must_not_contain": must_not_contain,
					}
				}, "")
			elif npt.lower() == "compile":
				branch = input("Branch: ")
				dir = input("Relative directory to find jars in: ")

				command = []
				while True:
					npt = input("Command for building jar (one argument per line): ")
					if npt == "":
						break
					command.append(npt)

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
					"repo": repo,
					"releases": None,
					"compile": {
						"branch": branch,
						"command": command,
						"dir": dir,
						"must_not_contain": must_not_contain,
						"must_contain": must_contain,
					},
				}, "")
			else:
				pass
