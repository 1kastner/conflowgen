from typing import Optional

from matplotlib import pyplot as plt


def no_data_graph() -> plt.Axes:
    fig, ax = plt.subplots()
    no_data_text(ax)
    return ax


def no_data_text(ax: Optional[plt.Axes]) -> plt.Axes:
    if ax is None:
        ax = plt.gca()
    ax.text(0.1, 0.1, 'No data')
    return ax
