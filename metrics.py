import pandas as pd
import numpy as np

def value_at_risk(returns: pd.Series, alpha: float = 0.05) -> float:
    """
    Computes the Value at Risk (VaR) of a portfolio.

    Parameters
    ----------
    returns : pd.Series
        Series of net or percentage returns
    alpha : float, optional (default=0.05)
        `1 - confidence level` for VaR

    Returns
    -------
    float
        The VaR threshold. There is an `alpha` chance that returns will be worse than this threshold.
    """
    VaR = np.quantile(returns, alpha)

    return VaR if VaR < 0 else "None"

def expected_shortfall(returns: pd.Series, alpha: float = 0.05) -> float:
    """
    Computes the Expected Shortfall (ES) of a portfolio.

    Parameters
    ----------
    returns : pd.Series
        Series of net or percentage returns
    alpha : float, optional (default=0.05)
        `1 - confidence level` for VaR

    Returns
    -------
    float
        The ES value. This is the average losses in the tail beyond VaR calculated at the
        `1 - alpha`  confidence level.
    """
    VaR = value_at_risk(returns, alpha)

    return "None" if VaR == "None" else returns[returns <= VaR].mean()