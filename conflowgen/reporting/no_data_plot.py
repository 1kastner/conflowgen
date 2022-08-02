from matplotlib import pyplot as plt


def no_data_graph() -> plt.Axes:
    fig, ax = plt.subplots()
    no_data_text(ax)
    return ax


def no_data_text(ax: plt.Axes) -> None:
    ax.text(0.35, 0.1, 'No data available for plotting')
