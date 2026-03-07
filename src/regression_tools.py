"""
Implements the core statistical mechanics of the three-pass regression filter.

Provides dedicated functions for the three required OLS regression stages: 
estimating time-series sensitivities (Stage 1), extracting the cross-sectional 
latent factor (Stage 2), and evaluating the predictive time-series 
relationship (Stage 3).
"""

import pandas as pd
import statsmodels.api as sm
import numpy as np
import warnings


def first_stage_regressions(v_df, y_series, h=1):
    """
    Stage 1: Time-Series Regressions (Paper eq. 11)
    For each portfolio i, regress v_{i,t} on y_{t+h} to estimate phi_i.
    Replicating: v_{i,t} = phi_{i,0} + phi_i * y_{t+h} + e_{i,t} (thus need y_shifted)
    OLS slope = Cov(v_i, y) / Var(y)
    """
    y_shifted = y_series.shift(-h)

    phi = {}
    for col in v_df.columns:
        # Align this specific column with y, dropping NaNs in EITHER series
        # This also helps ensure when calculating OLS slope (Cov(X,Y) / Var(X)) that variance matches
        pair = pd.concat([v_df[col], y_shifted], axis=1).dropna()

        if len(pair) < 3:
            continue
        v_col = pair.iloc[:, 0]
        y_col = pair.iloc[:, 1]
        # Var(y) computed over the same matched sample as Cov(v_i, y)
        var_y = y_col.var()
        if var_y == 0:
            continue
        phi[col] = v_col.cov(y_col) / var_y

    return pd.Series(phi).dropna()


def second_stage_regressions(v_df, phi):
    """
    Stage 2: Cross-Sectional Regressions (Paper eq. 12)
    At each time t, regress the cross-section of v_{i,t} on phi_i to recover F_t.
    Replicating v_{i,t} = {c}_t + {F}_t * phi_i + w_{i,t}
    OLS slope = Cov(v_t, phi) / Var(phi)
    """
    v_aligned = v_df[phi.index]
    valid_mask = v_aligned.notna()
    n_valid = valid_mask.sum(axis=1)

    # Broadcast phi across all dates
    phi_vals = phi.values.astype(float)
    phi_broadcast = np.where(valid_mask.values, phi_vals, np.nan)

    # NaN-aware means per date (axis=1)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        v_vals = np.where(valid_mask.values, v_aligned.values, np.nan)
        mean_v = np.nanmean(v_vals, axis=1)
        mean_phi = np.nanmean(phi_broadcast, axis=1)
        mean_vphi = np.nanmean(
            np.where(valid_mask.values, v_aligned.values * phi_vals, np.nan), axis=1
        )

        # Cov(v_t, phi) = E[v*phi] - E[v]*E[phi]
        cov_val = mean_vphi - mean_v * mean_phi

        # Var(phi) for valid portfolios at each date
        var_phi = np.nanvar(phi_broadcast, axis=1, ddof=0)

    # F_t = Cov / Var
    with np.errstate(divide='ignore', invalid='ignore'):
        F_arr = cov_val / var_phi

    # Build Series, filter: >= 3 valid, non-zero var, finite result
    F_series = pd.Series(F_arr, index=v_aligned.index)
    mask = (n_valid >= 3) & (var_phi > 0) & np.isfinite(F_arr)
    F_series = F_series[mask.values]

    return F_series.astype(float)


def third_stage_regression(F_series, y_series, h=1):
    """
    Stage 3: Predictive Time-Series Regression (Paper eq. in Section II.C)
    Replicating  y_{t+h} = beta_0 + beta * {F}_t + u_{t+h}, (thus need shifted y)
    Regress future market returns on the lagged factor F_t.
    """
    y_future = y_series.shift(-h).rename('future_target')

    # Align dates between the factor and the realized future returns
    df = pd.concat([y_future, F_series.rename('F_t')], axis=1).dropna()

    Y = df['future_target']
    X = sm.add_constant(df['F_t'])

    model = sm.OLS(Y, X).fit()

    return model