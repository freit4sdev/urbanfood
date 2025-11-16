import os
from pathlib import Path


def get_project_root():
    return Path(__file__).parent.parent.parent


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def get_assets_path(subfolder=""):
    root = get_project_root()
    assets_path = root / "assets"
    if subfolder:
        assets_path = assets_path / subfolder
    ensure_dir(assets_path)
    return assets_path
