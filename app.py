import streamlit as st
from portfolio import simulate_portfolio
import altair as alt

st.set_page_config(
    page_title="Fannie Mae Stress Testing Visualizer",
    page_icon="🏠"
)

st.title(":blue[Fannie Mae] Stress Testing Visualizer")

with st.container(border=True):
    st.text("Simulation Settings")

    default_rate = st.slider("Default rate", value=0.2, min_value=0.0, max_value=100.0, step=0.1) / 100
    portfolio_size = st.select_slider("Portfolio size", options=[10**k for k in range(1, 5)])

with st.container(border=True):
    with st.spinner("Simulating portfolio...", show_time=True):
        result = simulate_portfolio(default_rate=default_rate, n=portfolio_size)

    hist_net = alt.Chart(result).mark_bar().encode(
        alt.X("net:Q", bin=alt.Bin(maxbins=64), title="Net"),
        alt.Y("count()", title="Density")
    )
    st.altair_chart(hist_net)