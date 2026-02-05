"""Load project configurations from .env files.
Provides easy access to paths and credentials used in the project.

For information about the rationale behind decouple and this module,
see https://pypi.org/project/python-decouple/
"""

from pathlib import Path
from platform import system

from decouple import Config, RepositoryEnv
from pandas import to_datetime


def get_os():
    os_name = system()
    if os_name == "Windows":
        return "windows"
    elif os_name == "Darwin":
        return "nix"
    elif os_name == "Linux":
        return "nix"
    else:
        return "unknown"


# Absolute path to root directory of the project (parent of src/)
BASE_DIR = Path(__file__).absolute().parent.parent

# Load .env from project root
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    _config = Config(RepositoryEnv(str(_env_file)))
else:
    # Fallback to default decouple behavior (env vars, etc.)
    from decouple import config as _config


def if_relative_make_abs(path):
    """If a relative path is given, make it absolute, assuming
    that it is relative to the project root directory (BASE_DIR)
    """
    path = Path(path)
    if path.is_absolute():
        abs_path = path.resolve()
    else:
        abs_path = (d["BASE_DIR"] / path).resolve()
    return abs_path


d = {}

d["OS_TYPE"] = get_os()
d["BASE_DIR"] = BASE_DIR

# fmt: off
## Project-specific settings for Kelly & Pruitt (2013) replication
# The paper uses data from approximately 1930-2011
d["START_DATE"] = _config("START_DATE", default="1930-01-01", cast=to_datetime)
d["END_DATE"] = _config("END_DATE", default="2024-12-31", cast=to_datetime)

## Paths - relative to project root (BASE_DIR)
d["DATA_DIR"] = if_relative_make_abs(_config('DATA_DIR', default=Path('_data'), cast=Path))
d["OUTPUT_DIR"] = if_relative_make_abs(_config('OUTPUT_DIR', default=Path('_output'), cast=Path))

## WRDS credentials
d["WRDS_USERNAME"] = _config("WRDS_USERNAME", default="")
# fmt: on


def config(*args, **kwargs):
    key = args[0]
    default = kwargs.get("default", None)
    cast = kwargs.get("cast", None)
    if key in d:
        var = d[key]
        if default is not None:
            raise ValueError(
                f"Default for {key} already exists. Check your settings.py file."
            )
        if cast is not None:
            if type(cast(var)) is not type(var):
                raise ValueError(
                    f"Type for {key} is already set. Check your settings.py file."
                )
    else:
        var = _config(*args, **kwargs)
    return var


def create_dirs():
    """Create necessary directories if they don't exist."""
    d["DATA_DIR"].mkdir(parents=True, exist_ok=True)
    d["OUTPUT_DIR"].mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    create_dirs()
