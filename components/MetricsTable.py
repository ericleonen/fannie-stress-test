import pandas as pd
import numpy as np
from scipy.stats import skew, kurtosis
import streamlit as st

def value_at_risk(returns: pd.Series, alpha: float = 0.05) -> float:
    VaR = np.quantile(returns, alpha)

    return VaR if VaR < 0 else "None"

def expected_shortfall(returns: pd.Series, alpha: float = 0.05) -> float:
    VaR = value_at_risk(returns, alpha)

    return "None" if VaR == "None" else returns[returns <= VaR].mean()

def format_metric(metric: float | str) -> str:
    if isinstance(metric, float):
        metric = f"{metric:.2f}"

    return metric

def MetricsTable(orig_returns: pd.Series, stress_returns: pd.Series):
    metrics_df = pd.DataFrame({
        ":gray-badge[**Normal**]": [
            value_at_risk(orig_returns),
            expected_shortfall(orig_returns),
            orig_returns.std(ddof=1),
            skew(orig_returns),
            kurtosis(orig_returns)
        ],
        ":red-badge[**Stressed**]": [
            value_at_risk(stress_returns),
            expected_shortfall(stress_returns),
            stress_returns.std(ddof=1),
            skew(stress_returns),
            kurtosis(stress_returns)
        ]
    })
    metrics_df.index = [f":primary-badge[{metric}]" for metric in ["VaR", "ES", "Vol.", "Skew", "Ku."]]
    metrics_df = metrics_df.map(format_metric)

    st.table(metrics_df)

    with st.expander("Don't know what a metric means?", icon="🤔"):
        st.markdown("""
            - **VaR** (*Value at Risk*): The maximum expected loss over a given time period at a
                        95\% confidence level
                
            - **ES** (*Expected Shortfall*): The average loss in scenarios where the loss exceeds
                        the VaR threshold
                
            - **Vol.** (*Volatility*): A measure of how much returns fluctuate
                
            - **Skew** (*Skewness*): Indicates whether returns are asymmetric
                
            - **Kurt.** (*Kurtosis*): Measures how fat the tails of the return distribution are
        """)