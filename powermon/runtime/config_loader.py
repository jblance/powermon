from pathlib import Path
import yaml
from pyaml_env import parse_config
from pydantic import ValidationError

from powermon._config import PowermonConfig


def load_yaml_with_env(path: Path) -> dict:
    """
    Load YAML config with environment variable substitution.
    """
    try:
        return parse_config(str(path))
    except yaml.YAMLError as exc:
        raise RuntimeError(f"Error parsing YAML: {exc}") from exc
    except FileNotFoundError as exc:
        raise RuntimeError(f"Config file not found: {path}") from exc


def load_config(path: Path) -> PowermonConfig:
    """
    Load and validate PowermonConfig from YAML.
    """
    raw = load_yaml_with_env(path)
    try:
        return PowermonConfig.model_validate(raw)
    except ValidationError as exc:
        raise RuntimeError(f"Config validation failed:\n{exc}") from exc
