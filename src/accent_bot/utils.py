import json
import os
from pathlib import Path

def from_env(name, default, bool=False):
    val = os.getenv(name, default)
    if val.lower() in ("false", "true"):
        return val.lower() == "true"
    return os.getenv(name, default)


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent

def get_credentials():
    root = get_project_root()
    cred_path = os.path.join(root, "credentials.json")
    with open(cred_path) as f:
        return json.load(f)