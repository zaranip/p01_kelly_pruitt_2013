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

def jupyter_to_python(notebook_path, output_dir=OUTPUT_DIR):
    return f"jupyter nbconvert --to python --output-dir={output_dir} {notebook_path}"
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


# def task_pull_CRSP_stock():
#     """Pull CRSP stock data from WRDS (skips if all data files already exist)"""
#     targets = [
#         DATA_DIR / "CRSP_monthly_stock.parquet",
#         DATA_DIR / "CRSP_MSIX.parquet",
#         DATA_DIR / "CRSP_market_returns.parquet",
#     ]
    
#     def all_targets_exist():
#         """Return True if all target files exist (skip the pull)."""
#         return all(t.exists() for t in targets)
    
#     return {
#         "actions": [
#             "python ./src/settings.py",
#             "python ./src/pull_CRSP_stock.py",
#         ],
#         "targets": targets,
#         "file_dep": ["./src/settings.py", "./src/pull_CRSP_stock.py"],
#         "uptodate": [all_targets_exist],
#         "verbosity": 2,
#         "clean": True,
#     }


# def task_pull_CRSP_Compustat():
#     """Pull Compustat fundamentals and CCM link table from WRDS (skips if all data files already exist)"""
#     targets = [
#         DATA_DIR / "Compustat.parquet",
#         DATA_DIR / "CRSP_Comp_Link_Table.parquet",
#         DATA_DIR / "FF_FACTORS.parquet",
#     ]
    
#     def all_targets_exist():
#         """Return True if all target files exist (skip the pull)."""
#         return all(t.exists() for t in targets)
    
#     return {
#         "actions": [
#             "python ./src/settings.py",
#             "python ./src/pull_CRSP_Compustat.py",
#         ],
#         "targets": targets,
#         "file_dep": ["./src/settings.py", "./src/pull_CRSP_Compustat.py"],
#         "uptodate": [all_targets_exist],
#         "verbosity": 2,
#         "clean": True,
#     }


def task_pull_ken_french():
    """Pull Fama-French and Portfolio datasets"""
    datasets = [
        "F-F_Research_Data_Factors",
        "6_Portfolios_2x3",
        "25_Portfolios_5x5",
        "100_Portfolios_10x10"
    ]
    
    targets = [DATA_DIR / f"{ds}.xlsx" for ds in datasets]
    
    def all_targets_exist():
        """Return True if all target Excel files exist."""
        return all(t.exists() for t in targets)
        
    return {
        "actions": [
            "python ./src/pull_ken_french_data.py",
        ],
        "targets": targets,
        "file_dep": ["./src/settings.py", "./src/pull_ken_french_data.py"],
        "uptodate": [all_targets_exist],
        "verbosity": 2,
        "clean": True,
    }

def task_clean_kelly_pruitt_data():
    """Clean Fama-French datasets and generate Parquet files"""
    datasets = [
        "6_Portfolios_2x3",
        "25_Portfolios_5x5",
        "100_Portfolios_10x10"
    ]
    
    # Establish expected output targets based on load_data.py
    targets = [DATA_DIR / "Market_Returns.parquet"]
    for ds in datasets:
        targets.append(DATA_DIR / f"{ds}_Returns.parquet")
        targets.append(DATA_DIR / f"{ds}_BM.parquet")

    return {
        "actions": [
            "python ./src/load_data.py",
        ],
        "targets": targets,
        "file_dep": [
            "./src/settings.py", 
            "./src/load_data.py",
            "./src/pull_ken_french_data.py"
        ],
        "task_dep": ["pull_ken_french"],
        "verbosity": 2,
        "clean": True,
    }

def task_run_replication():
    """Run Kelly & Pruitt (2013) math regressions and save raw data as CSVs."""
    return {
        "actions": [
            "python ./src/replication.py",
        ],
        "targets": [
            OUTPUT_DIR / "data_sparsity.csv",
            OUTPUT_DIR / "summary_statistics.csv",
            OUTPUT_DIR / "stage_1_phi.csv",
            OUTPUT_DIR / "stage_2_factor.csv",
            OUTPUT_DIR / "stage_3_predictive.csv",
            OUTPUT_DIR / "table_1_results.csv",
        ],
        "file_dep": [
            "./src/settings.py",
            "./src/replication.py",
            "./src/pls_regression.py", 
            "./src/regression_tools.py",
            "./src/load_data.py"
        ],
        "task_dep": ["clean_kelly_pruitt_data"],
        "clean": True,
    }

def task_generate_figures():
    """Read analytical results from CSVs and generate LaTeX/PNG files."""
    return {
        "actions": ["python ./src/generate_figures.py"],
        "targets": [
            "./reports/paths.tex",
            OUTPUT_DIR / "report_date.txt",
            OUTPUT_DIR / "table_1_replication.tex",
            OUTPUT_DIR / "summary_statistics.tex",
            OUTPUT_DIR / "data_sparsity.png",
            OUTPUT_DIR / "stage_1_sensitivities.png",
            OUTPUT_DIR / "stage_2_factor.png",
            OUTPUT_DIR / "stage_3_predictive.png",
        ],
        "file_dep": [
            "./src/generate_figures.py",
            OUTPUT_DIR / "data_sparsity.csv",
            OUTPUT_DIR / "summary_statistics.csv",
            OUTPUT_DIR / "stage_1_phi.csv",
            OUTPUT_DIR / "stage_2_factor.csv",
            OUTPUT_DIR / "stage_3_predictive.csv",
            OUTPUT_DIR / "table_1_results.csv",
        ],
        "task_dep": ["run_replication"],
        "clean": True,
    }


def task_compile_replication_report():
    """Compile the replication report LaTeX document to PDF."""
    return {
        "actions": [
            "latexmk -pdf -interaction=nonstopmode -cd ./reports/replication_report.tex",
        ],
        "file_dep": [
            "./reports/replication_report.tex",
            "./reports/handout.cls",
            OUTPUT_DIR / "report_date.txt",
            OUTPUT_DIR / "data_sparsity.png",
            OUTPUT_DIR / "summary_statistics.tex",
            OUTPUT_DIR / "stage_1_sensitivities.png",
            OUTPUT_DIR / "stage_2_factor.png",
            OUTPUT_DIR / "stage_3_predictive.png",
            OUTPUT_DIR / "table_1_replication.tex",
        ],
        "task_dep": ["generate_figures"],
        "targets": ["./reports/replication_report.pdf"],
        "clean": True,
    }

# def task_exploratory_charts():
#     """Generate exploratory charts to verify data was pulled successfully"""
#     return {
#         "actions": [
#             "python ./src/generate_exploratory_charts.py",
#         ],
#         "targets": [
#             OUTPUT_DIR / "chart_market_returns.html",
#             OUTPUT_DIR / "chart_compustat_coverage.html",
#         ],
#         "file_dep": [
#             "./src/settings.py",
#             "./src/generate_exploratory_charts.py",
#         ],
#         "task_dep": ["pull_CRSP_stock", "pull_CRSP_Compustat"],
#         "clean": True,
#     }


# def task_build_chartbook_site():
#     """Build the chartbook documentation site"""
#     return {
#         "actions": [
#             "chartbook build -f",
#         ],
#         "targets": ["./docs/index.html"],
#         "file_dep": [
#             "./README.md",
#             "./chartbook.toml",
#         ],
#         "task_dep": ["exploratory_charts"],
#         "clean": True,
#     }

##############################
## Notebook Tasks
##############################

notebook_tasks = {
    "summary_statistics.ipynb": {
        "file_dep": [
            OUTPUT_DIR / "data_sparsity.png",
            OUTPUT_DIR / "summary_statistics.csv",
            OUTPUT_DIR / "stage_1_sensitivities.png",
            OUTPUT_DIR / "stage_2_factor.png",
            OUTPUT_DIR / "stage_3_predictive.png",
        ],
        "task_dep": ["generate_figures"],
        "targets": [],
    },
}

def task_convert_notebooks_to_scripts():
    """Convert notebooks to script form to detect changes to source code rather
    than to the notebook's metadata.
    """
    build_dir = Path(OUTPUT_DIR)

    for notebook in notebook_tasks.keys():
        notebook_name = notebook.split(".")[0]
        notebook_path = Path("./src") / notebook
        yield {
            "name": notebook,
            "actions": [
                jupyter_clear_output(notebook_path),
                jupyter_to_python(notebook_path, build_dir),
            ],
            "file_dep": [notebook_path],
            "targets": [OUTPUT_DIR / f"{notebook_name}.py"],
            "clean": True,
            "verbosity": 0,
        }

def task_run_notebooks():
    """Preps the notebooks for presentation format.
    Execute notebooks if the script version of it has been changed.
    """
    for notebook in notebook_tasks.keys():
        notebook_name = notebook.split(".")[0]
        notebook_path = Path("./src") / notebook
        yield {
            "name": notebook,
            "actions": [
                f"""python -c "import sys; from datetime import datetime; print(f'Start {notebook}: {{datetime.now()}}', file=sys.stderr)" """,
                jupyter_execute_notebook(notebook_path),
                jupyter_to_html(notebook_path, OUTPUT_DIR),
                copy_file(
                    notebook_path,
                    OUTPUT_DIR / f"{notebook_name}.ipynb",
                    mkdir=True,
                ),
                jupyter_clear_output(notebook_path),
                f"""python -c "import sys; from datetime import datetime; print(f'End {notebook}: {{datetime.now()}}', file=sys.stderr)" """,
            ],
            "file_dep": [
                OUTPUT_DIR / f"{notebook_name}.py",
                *notebook_tasks[notebook]["file_dep"],
            ],
            "targets": [
                OUTPUT_DIR / f"{notebook_name}.html",
                OUTPUT_DIR / f"{notebook_name}.ipynb",
                *notebook_tasks[notebook]["targets"],
            ],
            "clean": True,
        }