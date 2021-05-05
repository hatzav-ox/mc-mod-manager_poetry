"""github is a Mod Provider for GitHub(github.com).
"""

import os
import random
import requests
from dateutil.parser import isoparse
from github_release import get_releases
from pathlib import Path
from shutil import rmtree as shutil_rmtree
from shutil import move as shutil_move
from subprocess import Popen
from typing import Dict

save_dir = Path(f"{os.getenv('LOCALAPPDATA')}/mc_mod/cache/github")

save_dir.mkdir(parents=True, exist_ok=True)

def download_mod(info: Dict) -> Path:
	repo = info["repo"]

	if info["releases"] != None:
		return _releases(repo, info["releases"])
	elif info["compile"] != None:
		return _compile(repo, info["compile"])
	else:
		raise RuntimeError("'releases' or 'compile' must be defined")

def _releases(repo: str, info: Dict) -> Path:
	if info["latest"]:
		r = requests.get(f"https://api.github.com/repos/{repo}/releases/latest")
		r.raise_for_status()

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
			r.raise_for_status()

			out_file: Path = save_dir / asset["name"]

			with out_file.open("wb") as f:
				f.write(r.content)

			return out_file

		raise RuntimeError(f"Could not locate a valid binary for {info}")

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
			r.raise_for_status()

			out_file: Path = save_dir / asset["name"]

			with out_file.open("wb") as f:
				f.write(r.content)

			return out_file

		raise RuntimeError(f"Could not locate a valid binary for {info}")

def _compile(repo: str, info: Dict) -> Path:
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
			return out_file

	# Unfortunately, shutil_rmtree leaves behind some files in .git because of permission errors
	shutil_rmtree(str(clone_dir), ignore_errors=True)
	raise RuntimeError(f"Could not locate a binary for info: {info}")
