from dataclasses import dataclass
from typing import Any
import json
import os


@dataclass
class Config:
    raw: dict


def load_config(path: str) -> Config:
    """Load configuration from YAML or JSON.

    If the file has a .yaml/.yml extension but PyYAML is not installed,
    raise a clear error instructing the user to install it.
    """
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext in ('.yaml', '.yml'):
        try:
            import yaml
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "PyYAML is required to read YAML config files.\n"
                "Install with: pip install pyyaml"
            ) from e
        with open(path, 'r') as f:
            raw = yaml.safe_load(f)
    elif ext == '.json':
        with open(path, 'r') as f:
            raw = json.load(f)
    else:
        # try YAML if available, otherwise JSON
        try:
            import yaml
            with open(path, 'r') as f:
                raw = yaml.safe_load(f)
        except Exception:
            with open(path, 'r') as f:
                raw = json.load(f)
    return Config(raw)
