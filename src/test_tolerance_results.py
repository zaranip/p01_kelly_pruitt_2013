import pytest
import pandas as pd
import numpy as np
from pandas.testing import assert_series_equal

import regression 

def test_kelly_pruitt_table_1_replication():
    """
    Tests whether the replicated R-squared values for Kelly & Pruitt (2013) Table 1 
    match the published paper within a reasonable tolerance.
    """
    
    # HARDCODE THE EXPECTED VALUES FROM THE PAPER
    expected_table_1 = pd.DataFrame({
        "1-Year IS": {"6 Portfolios": 7.72, "25 Portfolios": 13.50, "100 Portfolios": 18.05},
        "1-Year OOS": {"6 Portfolios": 5.81, "25 Portfolios": 3.49, "100 Portfolios": 13.07},
        "1-Month IS": {"6 Portfolios": 0.60, "25 Portfolios": 1.12, "100 Portfolios": 2.38},
        "1-Month OOS": {"6 Portfolios": 0.65, "25 Portfolios": 0.77, "100 Portfolios": 0.93},
    })
    expected_table_1.index.name = "Portfolio Set"
    
    # Ensure regression.replicate_table_1() returns df_results
    actual_results = regression.replicate_table_1()
    
    assert isinstance(actual_results, pd.DataFrame), "replicate_table_1() must return a DataFrame."
    
    # Absolute tolerance of 1.5 (+/- 1.5% R-squared)
    TOLERANCE = 1.5
    
    for column in expected_table_1.columns:
        np.testing.assert_allclose(
            actual_results[column].values,
            expected_table_1[column].values,
            atol=TOLERANCE,
            err_msg=f"R-squared values for '{column}' exceeded tolerance of {TOLERANCE}%."
        )