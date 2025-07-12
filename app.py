import streamlit as st
from portfolio import simulate_portfolio
from components.SimulationSettings import SimulationSettings
from components.Visualization import Visualization
from components.MetricsTable import MetricsTable

st.set_page_config(
    page_title="Fannie Mae Stress Testing Visualizer",
    page_icon="🏠"
)

st.title(":primary[Fannie Mae] Stress Testing Visualizer")
st.write("by [Eric Leonen](https://github.com/ericleonen)")

orig_default_rate, stress_default_rate, portfolio_size, returns_type = SimulationSettings()

with st.spinner("Simulating portfolio...", show_time=True):
    orig_returns = simulate_portfolio(
        default_rate=orig_default_rate, 
        n=portfolio_size
    )[returns_type]
    stress_returns = simulate_portfolio(
        default_rate=stress_default_rate, 
        n=portfolio_size
    )[returns_type]

Visualization(orig_returns, stress_returns, orig_default_rate, stress_default_rate, returns_type)

MetricsTable(orig_returns, stress_returns)