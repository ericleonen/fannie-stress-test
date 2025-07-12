import streamlit as st

FANNIE_DATA_URL = "https://capitalmarkets.fanniemae.com/credit-risk-transfer/single-family" \
                  + "-credit-risk-transfer/fannie-mae-single-family-loan-performance-data"

def SimulationSettings() -> tuple[float, float, int, str]:
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
            format_func=lambda t: f"{t[0].upper()}{t[1:]} return",
            index=0
        )

        st.divider()

        st.write(":primary[:small[**Simulation Description**]]")
        st.write(f"We will use a Monte Carlo simulation to approximate the distributions of "
                f"{returns_type} returns of hypothetical portfolios containing {portfolio_size} "
                f"fixed-rate mortgages (FRMs) bought by [Fannie Mae finalized from 2020 to 2024]"
                f"({FANNIE_DATA_URL}). We consider two scenarios: a normal scenario where the "
                f"default rate is {orig_default_rate*100}% and a stressed scenario where the "
                f"default rate is {stress_default_rate*100}%.")
        
    return orig_default_rate, stress_default_rate, portfolio_size, returns_type