from typing import Optional, Tuple

from matplotlib import pyplot as plt
import matplotlib.axes
import matplotlib.figure


def no_data_graph() -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    fig, ax = plt.subplots()
    no_data_text(ax)
    return fig, ax


def no_data_text(ax: Optional[matplotlib.axes.Axes] = None) -> matplotlib.axes.Axes:
    if ax is None:
        ax = plt.gca()
    ax.text(0.1, 0.1, 'No data')
    return ax
