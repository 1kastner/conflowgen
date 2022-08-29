from typing import Optional

from matplotlib import pyplot as plt
import matplotlib.axes


def no_data_graph() -> matplotlib.axes.Axes:
    fig, ax = plt.subplots()
    no_data_text(ax)
    return ax


def no_data_text(ax: Optional[matplotlib.axes.Axes]) -> matplotlib.axes.Axes:
    if ax is None:
        ax = plt.gca()
    ax.text(0.1, 0.1, 'No data')
    return ax
