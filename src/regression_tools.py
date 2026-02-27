import pandas as pd
import statsmodels.api as sm

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
    v_df_aligned = v_df[phi.index]

    F_values = {}
    for date, row in v_df_aligned.iterrows():
        # Drop portfolios with missing BM at this date
        valid = row.dropna()
        if len(valid) < 3:
            continue
        phi_valid = phi[valid.index]
        var_phi = phi_valid.var()
        if var_phi == 0:
            continue
        F_values[date] = valid.cov(phi_valid) / var_phi

    return pd.Series(F_values).astype(float)


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