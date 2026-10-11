from pathlib import Path
from typing import Any

import yaml


def load_config(config_path: Path) -> dict[str, Any]:

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError as e:
        raise RuntimeError(f"Configuration file not found at: {config_path}") from e
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error parsing YAML file: {e}") from e 

    if not isinstance(config, dict):
        raise TypeError("Configuration root must be a YAML mapping.")

    return config