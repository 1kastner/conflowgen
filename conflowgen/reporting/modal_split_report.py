import matplotlib.pyplot as plt
import pandas as pd

from conflowgen.descriptive_datatypes import TransshipmentAndHinterlandSplit, HinterlandModalSplit
from conflowgen.reporting.no_data_plot import no_data_text


def _plt_modal_split_instance(
        modal_split: HinterlandModalSplit,
        name: str,
        ax: plt.axis
) -> None:
    series_modal_split_inbound = pd.Series({
        "train": modal_split.train_capacity,
        "truck": modal_split.truck_capacity,
        "barge": modal_split.barge_capacity
    }, name=name)
    if sum(series_modal_split_inbound) == 0:
        no_data_text(ax)
    else:
        series_modal_split_inbound.plot.pie(
            legend=False,
            autopct='%1.1f%%',
            label="",
            title=name,
            ax=ax
        )


def plot_modal_splits(
        transshipment_and_hinterland_split: TransshipmentAndHinterlandSplit,
        modal_split_for_hinterland_both: HinterlandModalSplit,
        modal_split_for_hinterland_inbound: HinterlandModalSplit,
        modal_split_for_hinterland_outbound: HinterlandModalSplit
) -> plt.Axes:
    fig, axes = plt.subplots(2, 2)

    series_hinterland_and_transshipment = pd.Series({
        "hinterland capacity": transshipment_and_hinterland_split.hinterland_capacity,
        "transshipment capacity": transshipment_and_hinterland_split.transshipment_capacity
    }, name="Transshipment share")
    if sum(series_hinterland_and_transshipment) == 0:
        no_data_text(axes[0, 0])
    else:
        series_hinterland_and_transshipment.plot.pie(
            legend=False,
            autopct='%1.1f%%',
            label="",
            title="Transshipment share",
            ax=axes[0, 0]
        )

    modal_splits = [
        {
            "modal_split": modal_split_for_hinterland_both,
            "name": "Modal split for hinterland (inbound and outbound)",
            "ax": axes[1, 0]
        },
        {
            "modal_split": modal_split_for_hinterland_inbound,
            "name": "Modal split for hinterland (inbound)",
            "ax": axes[0, 1]
        },
        {
            "modal_split": modal_split_for_hinterland_outbound,
            "name": "Modal split for hinterland (outbound)",
            "ax": axes[1, 1]
        },
    ]

    for modal_split in modal_splits:
        _plt_modal_split_instance(**modal_split)

    return axes
