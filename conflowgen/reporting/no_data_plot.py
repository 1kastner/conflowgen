from matplotlib import pyplot as plt


def no_data_graph():
    axs = plt.subplots()
    no_data_text()
    return axs


def no_data_text():
    plt.text(0.35, 0.5, 'No data available for plotting', dict(size=30))