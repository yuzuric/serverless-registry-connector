"""Config loader: YAML + environment variable override."""
import os
import re
from pathlib import Path
import yaml


_ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)(?::-([^}]*))?\}")


def _resolve_env(value):
    if isinstance(value, str):
        def replace(m):
            var = m.group(1)
            default = m.group(2) or ""
            return os.environ.get(var, default)
        return _ENV_PATTERN.sub(replace, value)
    if isinstance(value, dict):
        return {k: _resolve_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env(v) for v in value]
    return value


def load_config(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"config not found: {p}")
    with p.open() as f:
        raw = yaml.safe_load(f)
    return _resolve_env(raw)
