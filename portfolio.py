import numpy as np
import pandas as pd

DATA = pd.concat([
    pd.read_csv(f"data/{year}.csv")
    for year in range(2020, 2024 + 1)
]).reset_index().drop(columns=["index"])

def simulate_portfolio(
    data: pd.DataFrame = DATA,
    default_rate: float = None,
    N=10_000,
    n=100
) -> np.ndarray:
    defaulted = data["defaulted"]

    if default_rate is None:
        default_rate = defaulted.mean()

    n_paid = int(n * (1 - default_rate))
    n_defaulted = int(n * default_rate)

    investment_paid = data["orig_upb"][~defaulted].values
    investment_defaulted = data["orig_upb"][defaulted].values

    net_paid = data["net"][~defaulted].values
    net_defaulted = data["net"][defaulted].values

    index_paid = np.random.randint(0, len(net_paid), size=(N, n_paid))
    index_defaulted = np.random.randint(0, len(net_defaulted), size=(N, n_defaulted))

    investment = np.take(investment_paid, index_paid).sum(axis=1) + \
        np.take(investment_defaulted, index_defaulted).sum(axis=1)
    net = np.take(net_paid, index_paid).sum(axis=1) + \
        np.take(net_defaulted, index_defaulted).sum(axis=1)

    return pd.DataFrame({
        "Net Return": net,
        "Percentage Return": net / investment
    })