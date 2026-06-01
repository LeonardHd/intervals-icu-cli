from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Optional

DEFAULT_BASE_URL = "https://intervals.icu"


def config_dir() -> Path:
    """Return the directory holding the CLI config, honoring XDG_CONFIG_HOME."""
    xdg = os.getenv("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "intervals-icu"


def config_path() -> Path:
    """Return the path to the credentials config file."""
    return config_dir() / "config.toml"


def read_config_file() -> dict[str, str]:
    """Read the config file, returning an empty dict when it does not exist."""
    path = config_path()
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def write_config_file(
    *, athlete_id: str, api_key: str, base_url: Optional[str] = None
) -> Path:
    """Write credentials to the config file with owner-only (0600) permissions."""
    directory = config_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = config_path()

    lines = [
        f'athlete_id = "{_toml_escape(athlete_id)}"',
        f'api_key = "{_toml_escape(api_key)}"',
    ]
    if base_url:
        lines.append(f'base_url = "{_toml_escape(base_url)}"')
    content = "\n".join(lines) + "\n"

    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(content)
    os.chmod(path, 0o600)
    return path


def delete_config_file() -> bool:
    """Delete the config file. Returns True if a file was removed."""
    path = config_path()
    if path.exists():
        path.unlink()
        return True
    return False
