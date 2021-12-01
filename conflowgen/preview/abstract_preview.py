from __future__ import annotations

import abc
import datetime
from typing import Dict

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class AbstractPreview(abc.ABC):
    def __init__(
            self,
            start_date: datetime.date,
            end_date: datetime.date,
            transportation_buffer: float
    ):
        """
        Args:
            start_date: The earliest day to consider for scheduled vehicles
            end_date: The latest day to consider for scheduled vehicles
            transportation_buffer: The buffer, e.g. 0.2 means that 20% more containers (in TEU) can be put on a vessel
                compared to the amount of containers it had on its inbound journey - as long as the total vehicle
                capacity would not be exceeded.
        """
        self.start_date: datetime.date | None = None
        self.end_date: datetime.date | None = None
        self.transportation_buffer: float | None = None
        self.update(
            start_date=start_date,
            end_date=end_date,
            transportation_buffer=transportation_buffer
        )

    def update(
            self,
            start_date: datetime.date,
            end_date: datetime.date,
            transportation_buffer: float
    ) -> None:
        """
        A preview needs to be updated if the user has input new data since the initialization of this class.

        Args:
            start_date: The earliest day to consider for scheduled vehicles
            end_date: The latest day to consider for scheduled vehicles
            transportation_buffer: The buffer, e.g. 0.2 means that 20% more containers (in TEU) can be put on a vessel
                compared to the amount of containers it had on its inbound journey - as long as the total vehicle
                capacity would not be exceeded.
        """
        assert start_date < end_date
        assert -1 < transportation_buffer

        self.start_date = start_date
        self.end_date = end_date
        self.transportation_buffer = transportation_buffer

    @abc.abstractmethod
    def hypothesize_with_mode_of_transport_distribution(
            self,
            mode_of_transport_distribution: Dict[ModeOfTransport, Dict[ModeOfTransport, float]]
    ) -> None:
        """
        This allows to see the effect of different mode of transport distributions on this preview.

        Args:
            mode_of_transport_distribution: A mode of transport distribution to try out
        """
        return None
