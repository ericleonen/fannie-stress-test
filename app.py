import streamlit as st
from portfolio import simulate_portfolio
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm
import numpy as np

st.set_page_config(
    page_title="Fannie Mae Stress Testing Visualizer",
    page_icon="🏠"
)

st.title(":blue[Fannie Mae] Stress Testing Visualizer")

with st.container(border=True):
    st.text("Simulation Settings")

    default_rate = st.slider(
        "Default rate", 
        value=0.2, 
        min_value=0.0, 
        max_value=100.0, 
        step=0.1
    ) / 100
    portfolio_size = st.select_slider(
        "Portfolio size", 
        options=[10**k for k in range(2, 6 + 1)],
    )

with st.container(border=True):
    distribution_type = st.radio(
        "I want to analyze:", 
        options=["Net Return", "Percentage Return"],
        index=0
    )

    with st.spinner("Simulating portfolio...", show_time=True):
        result = simulate_portfolio(
            default_rate=default_rate, 
            n=portfolio_size
        )
        mu, sigma = norm.fit(result[distribution_type].dropna())

    fig = px.histogram(
        result,
        x=distribution_type,
        nbins=128,
        histnorm="probability density",
        title=f"Distribution of {distribution_type}"
    )
    fig.update_layout(bargap=0.01)

    x_curve = np.linspace(
        result[distribution_type].min(),
        result[distribution_type].max(),
        128
    )
    pdf_curve = norm.pdf(x_curve, mu, sigma)

    fig.add_trace(
        go.Scatter(
            x=x_curve,
            y=pdf_curve,
            mode="lines",
            name="Fitted Normal PDF",
            line={
                "color": "red",
                "width": 2
            }
        )
    )

    st.plotly_chart(fig, use_container_width=True)