import os
from pathlib import Path

import pandas as pd
import numpy as np
from pandas import Timestamp
from pandas.testing import assert_frame_equal

# Assuming the provided code is saved in pull_ken_french_data.py
import pull_ken_french_data as pkf
from settings import config

DATA_DIR = config("DATA_DIR")

def test_pull_ken_french_excel_creates_file():
    """Test that the pulling function successfully downloads and saves an Excel file."""
    dataset_name = "F-F_Research_Data_Factors"
    expected_file_path = Path(DATA_DIR) / f"{dataset_name}.xlsx"
    
    # Remove the file if it exists to ensure we are testing the download
    if expected_file_path.exists():
        os.remove(expected_file_path)
        
    # Pull the data
    output_path = pkf.pull_ken_french_excel(dataset_name=dataset_name, data_dir=DATA_DIR, log=False)
    
    # Assert that the function returns the correct path and the file exists
    assert output_path == expected_file_path
    assert expected_file_path.exists(), f"Expected Excel file was not created at {expected_file_path}"


def test_load_returns_weighting():
    """Test that load_returns correctly accesses value-weighted vs equal-weighted sheets."""
    dataset_name = "Portfolios_Formed_on_INV"
    
    # Pull the data
    pkf.pull_ken_french_excel(dataset_name=dataset_name, data_dir=DATA_DIR, log=False)
    
    # Load value-weighted (Sheet 0) and equal-weighted (Sheet 1)
    vw_returns = pkf.load_returns(dataset_name, weighting="value-weighted", data_dir=DATA_DIR)
    ew_returns = pkf.load_returns(dataset_name, weighting="equal-weighted", data_dir=DATA_DIR)
    
    # Assert both return DataFrames
    assert isinstance(vw_returns, pd.DataFrame)
    assert isinstance(ew_returns, pd.DataFrame)
    
    # Value-weighted and equal-weighted returns should not be exactly identical
    # We test that at least one column (e.g., the first portfolio column) is different
    # Skipping the 'Date' column if it exists
    data_col = vw_returns.columns[1] if vw_returns.columns[0] == 'Date' else vw_returns.columns[0]
    
    is_identical = np.allclose(vw_returns[data_col].dropna(), ew_returns[data_col].dropna(), atol=1e-4)
    assert not is_identical, "Value-weighted and equal-weighted returns are incorrectly identical."