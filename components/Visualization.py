import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm
import numpy as np

def Visualization(
        orig_returns: pd.Series, 
        stress_returns: pd.Series,
        orig_default_rate: float,
        stress_default_rate: float,
        returns_type: str
    ):
    orig_mean, orig_std = norm.fit(orig_returns)
    orig_pdf_x = np.linspace(
        orig_returns.min(),
        orig_returns.max(),
        num=128
    )
    orig_pdf_y = norm.pdf(orig_pdf_x, orig_mean, orig_std)

    stress_mean, stress_std = norm.fit(stress_returns)
    stress_pdf_x = np.linspace(
        stress_returns.min(),
        stress_returns.max(),
        num=128
    )
    stress_pdf_y = norm.pdf(stress_pdf_x, stress_mean, stress_std)

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
        xaxis_title=f"{returns_type[0].upper()}{returns_type[1:]} return",
        yaxis_title="Density",
        title=f"Normal ({orig_default_rate*100}% default rate) vs. Stressed ({stress_default_rate*100}% default rate) {returns_type[0].upper()}{returns_type[1:]} Returns"
    )
    st.plotly_chart(
        fig,
        use_container_width=True
    )