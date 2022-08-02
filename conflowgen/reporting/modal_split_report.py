import matplotlib.pyplot as plt
import numpy as np
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
        modal_split_in_hinterland_both_directions: HinterlandModalSplit,
        modal_split_in_hinterland_inbound_traffic: HinterlandModalSplit,
        modal_split_in_hinterland_outbound_traffic: HinterlandModalSplit
) -> plt.Axes:
    fig, axes = plt.subplots(2, 2)

    series_hinterland_and_transshipment = pd.Series({
        "Inland gateway traffic": transshipment_and_hinterland_split.hinterland_capacity,
        "Transshipment traffic": transshipment_and_hinterland_split.transshipment_capacity
    }, name="Role in network")

    if series_hinterland_and_transshipment.sum() == 0:
        no_data_text(axes[0, 0])
    else:
        series_hinterland_and_transshipment.plot.pie(
            legend=False,
            autopct='%1.1f%%',
            label="",
            title=series_hinterland_and_transshipment.name,
            ax=axes[0, 0]
        )

    modal_splits = [
        {
            "modal_split": modal_split_in_hinterland_both_directions,
            "name": "Modal split in hinterland traffic\n(both inbound and outbound traffic)",
            "ax": axes[1, 0]
        },
        {
            "modal_split": modal_split_in_hinterland_inbound_traffic,
            "name": "Modal split in hinterland traffic\n(only inbound traffic)",
            "ax": axes[0, 1]
        },
        {
            "modal_split": modal_split_in_hinterland_outbound_traffic,
            "name": "Modal split in hinterland traffic\n(only outbound traffic)",
            "ax": axes[1, 1]
        },
    ]

    for modal_split in modal_splits:
        _plt_modal_split_instance(**modal_split)

    plt.tight_layout()

    return axes


def insert_values_in_template(
        transshipment_and_hinterland_split: TransshipmentAndHinterlandSplit,
        modal_split_in_hinterland_inbound_traffic: HinterlandModalSplit,
        modal_split_in_hinterland_outbound_traffic: HinterlandModalSplit,
        modal_split_in_hinterland_traffic_both_directions: HinterlandModalSplit,
) -> str:

    transshipment_as_fraction = np.nan
    if sum(transshipment_and_hinterland_split) > 0:
        transshipment_as_fraction = (
                transshipment_and_hinterland_split.transshipment_capacity /
                (transshipment_and_hinterland_split.transshipment_capacity
                 + transshipment_and_hinterland_split.hinterland_capacity)
        )

    inbound_total = sum(modal_split_in_hinterland_inbound_traffic)
    if inbound_total == 0:
        inbound_total = np.nan

    outbound_total = sum(modal_split_in_hinterland_outbound_traffic)
    if outbound_total == 0:
        outbound_total = np.nan

    inbound_and_outbound_total = sum(modal_split_in_hinterland_traffic_both_directions)
    if inbound_and_outbound_total == 0:
        inbound_and_outbound_total = np.nan

    # create string representation
    report = "\nRole in network\n"
    report += f"transshipment traffic (in TEU):  {transshipment_and_hinterland_split.transshipment_capacity:>10.2f} "
    report += f"({transshipment_as_fraction * 100:.2f}%)\n"
    report += f"inland gateway traffic (in TEU): {transshipment_and_hinterland_split.hinterland_capacity:>10.2f} "
    report += f"({(1 - transshipment_as_fraction) * 100:.2f}%)\n"
    report += "\n"
    report += "Modal split in hinterland traffic (only inbound traffic)\n"
    report += f"trucks (in TEU): {modal_split_in_hinterland_inbound_traffic.truck_capacity:>10.1f} "
    report += f"({modal_split_in_hinterland_inbound_traffic.truck_capacity / inbound_total * 100:.2f}%)\n"
    report += f"barges (in TEU): {modal_split_in_hinterland_inbound_traffic.barge_capacity:>10.1f} "
    report += f"({modal_split_in_hinterland_inbound_traffic.barge_capacity / inbound_total * 100:.2f}%)\n"
    report += f"trains (in TEU): {modal_split_in_hinterland_inbound_traffic.train_capacity:>10.1f} "
    report += f"({modal_split_in_hinterland_inbound_traffic.train_capacity / inbound_total * 100:.2f}%)\n\n"

    report += "Modal split in hinterland traffic (only outbound traffic)\n"
    report += f"trucks (in TEU): {modal_split_in_hinterland_outbound_traffic.truck_capacity:>10.1f} "
    report += f"({modal_split_in_hinterland_outbound_traffic.truck_capacity / outbound_total * 100:.2f}%)\n"
    report += f"barges (in TEU): {modal_split_in_hinterland_outbound_traffic.barge_capacity:>10.1f} "
    report += f"({modal_split_in_hinterland_outbound_traffic.barge_capacity / outbound_total * 100:.2f}%)\n"
    report += f"trains (in TEU): {modal_split_in_hinterland_outbound_traffic.train_capacity:>10.1f} "
    report += f"({modal_split_in_hinterland_outbound_traffic.train_capacity / outbound_total * 100:.2f}%)\n\n"

    modal_split_both = modal_split_in_hinterland_traffic_both_directions  # introduce shorthand for template

    report += "Modal split in hinterland traffic (both inbound and outbound traffic)\n"
    report += f"trucks (in TEU): {modal_split_both.truck_capacity:>10.1f} "
    report += f"({modal_split_both.truck_capacity / inbound_and_outbound_total * 100:.2f}%)\n"
    report += f"barges (in TEU): {modal_split_both.barge_capacity:>10.1f} "
    report += f"({modal_split_both.barge_capacity / inbound_and_outbound_total * 100:.2f}%)\n"
    report += f"trains (in TEU): {modal_split_both.train_capacity:>10.1f} "
    report += f"({modal_split_both.train_capacity / inbound_and_outbound_total * 100:.2f}%)\n"

    report = report.replace("(nan%)", "(-%)")
    report += "(rounding errors might exist)\n"

    return report
