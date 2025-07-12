import streamlit as st
from portfolio import simulate_portfolio
import plotly.graph_objects as go
from scipy.stats import norm, skew, kurtosis
import numpy as np
from metrics import value_at_risk, expected_shortfall
from format import format_returns_type, format_metric
import pandas as pd

FANNIE_DATA_URL = "https://capitalmarkets.fanniemae.com/credit-risk-transfer/single-family-credit-risk-transfer/fannie-mae-single-family-loan-performance-data"

st.set_page_config(
    page_title="Fannie Mae Stress Testing Visualizer",
    page_icon="🏠"
)

st.title(":primary[Fannie Mae] Stress Testing Visualizer")
st.write("by [Eric Leonen](https://github.com/ericleonen)")

with st.expander(":primary[**Simulation Settings**]", icon="⚙️"):
    orig_default_rate = st.slider(
        "Normal default rate",
        value=2.0,
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        format="%f%%"
    ) / 100
    stress_default_rate = st.slider(
        "Stressed default rate", 
        value=10.0, 
        min_value=0.0, 
        max_value=100.0, 
        step=0.1
    ) / 100
    portfolio_size = st.select_slider(
        "Portfolio size", 
        options=[100, 500, 1000, 5000, 10000],
        value=1000
    )
    returns_type = st.radio(
        "I want to analyze:", 
        options=["net", "percentage"],
        format_func=format_returns_type,
        index=0
    )

    st.divider()

    st.write(":primary[:small[**Simulation Description**]]")
    st.write(f"We will use a Monte Carlo simulation to approximate the distributions of "
             f"{returns_type} returns of hypothetical portfolios containing {portfolio_size} "
             f"fixed-rate mortgages (FRMs) bought by [Fannie Mae finalized from 2020 to 2024]"
             f"({FANNIE_DATA_URL}). We consider two scenarios: a normal scenario where the "
             f"default rate is {orig_default_rate*100}% and a stressed scenario where the default "
             f"rate is {stress_default_rate*100}%.")

with st.container():
    with st.spinner("Simulating portfolio...", show_time=True):
        orig_returns = simulate_portfolio(
            default_rate=orig_default_rate, 
            n=portfolio_size
        )[returns_type]
        stress_returns = simulate_portfolio(
            default_rate=stress_default_rate, 
            n=portfolio_size
        )[returns_type]
    
    orig_mean, orig_std = norm.fit(orig_returns)
    orig_pdf_x = np.linspace(
        orig_returns.min(),
        orig_returns.max(),
        num=128
    )
    orig_pdf_y = norm.pdf(orig_pdf_x, orig_mean, orig_std)

    orig_hist = go.Histogram(
        x=orig_returns,
        nbinsx=64,
        histnorm="probability density",
        opacity=0.4,
        marker=dict(
            color="gray"
        ),
        name="Normal returns"
    )
    orig_pdf = go.Scatter(
        x=orig_pdf_x,
        y=orig_pdf_y,
        mode="lines",
        line=dict(
            color="gray",
            width=3
        ),
        showlegend=False,
        name="Normal returns PDF"
    )

    stress_mean, stress_std = norm.fit(stress_returns)
    stress_pdf_x = np.linspace(
        stress_returns.min(),
        stress_returns.max(),
        num=128
    )
    stress_pdf_y = norm.pdf(stress_pdf_x, stress_mean, stress_std)

    stress_hist = go.Histogram(
        x=stress_returns,
        nbinsx=64,
        histnorm="probability density",
        opacity=0.4,
        marker=dict(
            color="red"
        ),
        name="Stressed returns"
    )
    stress_pdf = go.Scatter(
        x=stress_pdf_x,
        y=stress_pdf_y,
        mode="lines",
        line=dict(
            color="red",
            width=3
        ),
        showlegend=False,
        name="Stressed returns PDF"
    )

    fig = go.Figure(data=[orig_hist, orig_pdf, stress_hist, stress_pdf])
    fig.update_layout(
        bargap=0,
        xaxis_title=format_returns_type(returns_type),
        yaxis_title="Density",
        title=f"Normal ({orig_default_rate*100}% default rate) vs. Stressed ({stress_default_rate*100}% default rate) {format_returns_type(returns_type, title=True)}s"
    )
    st.plotly_chart(
        fig,
        use_container_width=True
    )

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

