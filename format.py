def format_returns_type(returns_type: str, title: bool = False) -> str:
    return f"{returns_type[0].upper()}{returns_type[1:]} {'r' if not title else 'R'}eturn"

def format_metric(metric: float | str, loss = None) -> str:
    if isinstance(metric, float):
        metric = f"{metric:.2f}"

    return metric