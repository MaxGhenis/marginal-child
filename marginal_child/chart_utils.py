"""Pure functions for chart data transformation."""

from typing import Any, Dict, List


def transform_data_for_chart(
    data: List[Dict[str, Any]],
    metric: str,
    view: str,
    clip_mtr: bool = True,
) -> List[Dict[str, Any]]:
    """Transform calculation data into Recharts format.

    Args:
        data: Raw calculation data with columns: income, num_children, mtr/net_income
        metric: "net_income" or "mtr"
        view: "absolute" or "marginal"
        clip_mtr: Whether to clip MTR values to [-1, 1] range

    Returns:
        List of dicts suitable for Recharts LineChart
    """
    if not data:
        return []

    # Determine value column
    is_mtr = metric == "mtr"
    value_key = (
        "mtr" if is_mtr and view == "absolute"
        else "marginal_mtr" if is_mtr and view == "marginal"
        else "net_income" if view == "absolute"
        else "marginal_benefit"
    )

    # Get unique children counts
    children_counts = sorted(set(d["num_children"] for d in data))

    # Get unique incomes (from first child count group)
    incomes = sorted(set(d["income"] for d in data if d["num_children"] == children_counts[0]))

    # Build chart data
    chart_data = []
    for income in incomes:
        row = {"income": income}

        for num_children in children_counts:
            # Find matching data point
            matching = next(
                (d for d in data if d["income"] == income and d["num_children"] == num_children),
                None
            )

            if matching and value_key in matching:
                value = matching[value_key]

                # Clip MTR values
                if clip_mtr and is_mtr:
                    value = max(-1, min(1, value))

                row[f"{num_children}_children"] = value

        chart_data.append(row)

    return chart_data


def clip_mtr_value(value: float) -> float:
    """Clip MTR value to [-1, 1] range.

    Args:
        value: MTR value (can be any float)

    Returns:
        Clipped value between -1 and 1
    """
    return max(-1.0, min(1.0, value))


def smooth_marginal_mtr(data: List[Dict[str, Any]], window_size: int = 10) -> List[Dict[str, Any]]:
    """Smooth marginal MTR data using moving average.

    Marginal MTR (change per child) amplifies noise from numerical gradients.
    Apply smoothing to make patterns visible.

    Args:
        data: List of dicts with 'marginal_mtr' values
        window_size: Size of moving average window

    Returns:
        Smoothed data
    """
    if not data or "marginal_mtr" not in data[0]:
        return data

    import numpy as np

    # Group by num_children
    children_counts = sorted(set(d["num_children"] for d in data))

    smoothed = []
    for num_children in children_counts:
        child_data = [d for d in data if d["num_children"] == num_children]
        child_data = sorted(child_data, key=lambda x: x["income"])

        values = np.array([d["marginal_mtr"] for d in child_data])

        # Apply moving average
        if len(values) >= window_size:
            smoothed_values = np.convolve(values, np.ones(window_size)/window_size, mode='same')
        else:
            smoothed_values = values

        for i, d in enumerate(child_data):
            smoothed.append({
                **d,
                "marginal_mtr": float(smoothed_values[i])
            })

    return smoothed
