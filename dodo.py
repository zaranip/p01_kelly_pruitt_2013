#######################################
## Configuration and Helpers for PyDoit
#######################################
import sys

sys.path.insert(1, "./src/")

import shutil
from os import environ, getcwd, path
from pathlib import Path

from settings import config

DATA_DIR = Path(config("DATA_DIR"))
OUTPUT_DIR = Path(config("OUTPUT_DIR"))
OS_TYPE = config("OS_TYPE")

## Helpers for handling Jupyter Notebook tasks
environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"


# fmt: off
def jupyter_execute_notebook(notebook_path):
    return f"jupyter nbconvert --execute --to notebook --ClearMetadataPreprocessor.enabled=True --inplace {notebook_path}"

def jupyter_to_html(notebook_path, output_dir=OUTPUT_DIR):
    return f"jupyter nbconvert --to html --output-dir={output_dir} {notebook_path}"

def jupyter_clear_output(notebook_path):
    return f"jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --inplace {notebook_path}"
# fmt: on


def copy_file(origin_path, destination_path, mkdir=True):
    """Create a Python action for copying a file."""
    def _copy_file():
        origin = Path(origin_path)
        dest = Path(destination_path)
        if mkdir:
            dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, dest)
    return _copy_file


##################################
## Begin rest of PyDoit tasks here
##################################


def task_config():
    """Create empty directories for data and output if they don't exist"""
    return {
        "actions": ["python ./src/settings.py"],
        "targets": [DATA_DIR, OUTPUT_DIR],
        "file_dep": ["./src/settings.py"],
        "clean": [],
    }


def task_pull_CRSP_stock():
    """Pull CRSP stock data from WRDS (skips if all data files already exist)"""
    targets = [
        DATA_DIR / "CRSP_monthly_stock.parquet",
        DATA_DIR / "CRSP_MSIX.parquet",
        DATA_DIR / "CRSP_market_returns.parquet",
    ]
    
    def all_targets_exist():
        """Return True if all target files exist (skip the pull)."""
        return all(t.exists() for t in targets)
    
    return {
        "actions": [
            "python ./src/settings.py",
            "python ./src/pull_CRSP_stock.py",
        ],
        "targets": targets,
        "file_dep": ["./src/settings.py", "./src/pull_CRSP_stock.py"],
        "uptodate": [all_targets_exist],
        "verbosity": 2,
        "clean": True,
    }


def task_pull_CRSP_Compustat():
    """Pull Compustat fundamentals and CCM link table from WRDS (skips if all data files already exist)"""
    targets = [
        DATA_DIR / "Compustat.parquet",
        DATA_DIR / "CRSP_Comp_Link_Table.parquet",
        DATA_DIR / "FF_FACTORS.parquet",
    ]
    
    def all_targets_exist():
        """Return True if all target files exist (skip the pull)."""
        return all(t.exists() for t in targets)
    
    return {
        "actions": [
            "python ./src/settings.py",
            "python ./src/pull_CRSP_Compustat.py",
        ],
        "targets": targets,
        "file_dep": ["./src/settings.py", "./src/pull_CRSP_Compustat.py"],
        "uptodate": [all_targets_exist],
        "verbosity": 2,
        "clean": True,
    }


def task_exploratory_charts():
    """Generate exploratory charts to verify data was pulled successfully"""
    return {
        "actions": [
            "python ./src/generate_exploratory_charts.py",
        ],
        "targets": [
            OUTPUT_DIR / "chart_market_returns.html",
            OUTPUT_DIR / "chart_compustat_coverage.html",
        ],
        "file_dep": [
            "./src/settings.py",
            "./src/generate_exploratory_charts.py",
        ],
        "task_dep": ["pull_CRSP_stock", "pull_CRSP_Compustat"],
        "clean": True,
    }


def task_build_chartbook_site():
    """Build the chartbook documentation site"""
    return {
        "actions": [
            "chartbook build -f",
        ],
        "targets": ["./docs/index.html"],
        "file_dep": [
            "./README.md",
            "./chartbook.toml",
        ],
        "task_dep": ["exploratory_charts"],
        "clean": True,
    }
