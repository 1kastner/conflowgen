from __future__ import annotations
import datetime
from typing import Dict

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.previews.abstract_preview import AbstractPreview
from conflowgen.previews.container_flow_by_vehicle_type_preview import \
    ContainerFlowByVehicleTypePreview
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.descriptive_datatypes import TransshipmentAndHinterlandSplit
from conflowgen.descriptive_datatypes import HinterlandModalSplit


class ModalSplitPreview(AbstractPreview):
    """
    This preview examines the inbound and/or outbound journeys and estimates the modal split. This is separated into
    two different aspects. First, the transshipment share is indicated. For the hinterland, the modal split is reported.

    The preview returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.ModalSplitPreviewReport`.
    The preview is intended to provide a first estimate before running the expensive
    :meth:`.ContainerFlowGenerationManager.generate` method.
    The preview does not consider all restrictions (such as container dwell times in combination with the schedules)
    into consideration, thus later deviations might exist.
    """

    vessels_considered_for_transshipment = {
        ModeOfTransport.deep_sea_vessel,
        ModeOfTransport.feeder
    }

    vehicles_considered_for_hinterland = {
        ModeOfTransport.truck,
        ModeOfTransport.barge,
        ModeOfTransport.train
    }

    def __init__(
            self,
            start_date: datetime.date,
            end_date: datetime.date,
            transportation_buffer: float
    ):
        """
        Args:
            start_date: The earliest day to consider when checking the vehicles that move according to schedules
            end_date: The latest day to consider when checking the vehicles that move according to schedules
            transportation_buffer: The fraction of how much more a vehicle takes with it on an outbound journey
                compared to an inbound journey as long as the total vehicle capacity is not exceeded.
        """
        super().__init__(
            start_date=start_date,
            end_date=end_date,
            transportation_buffer=transportation_buffer
        )
        self.container_flow_by_vehicle_type_preview = ContainerFlowByVehicleTypePreview(
            start_date=start_date,
            end_date=end_date,
            transportation_buffer=transportation_buffer
        )

    @DataSummariesCache.cache_result
    def hypothesize_with_mode_of_transport_distribution(
            self,
            mode_of_transport_distribution: Dict[ModeOfTransport, Dict[ModeOfTransport, float]]
    ):
        self.container_flow_by_vehicle_type_preview.hypothesize_with_mode_of_transport_distribution(
            mode_of_transport_distribution
        )

    @DataSummariesCache.cache_result
    def get_transshipment_and_hinterland_split(self) -> TransshipmentAndHinterlandSplit:
        """
        Returns:
             The amount of containers in TEU dedicated for or coming from the hinterland versus the amount of
             containers in TEU that are transshipped.
        """
        inbound_to_outbound_flow = self.container_flow_by_vehicle_type_preview.get_inbound_to_outbound_flow()

        transshipment_capacity = 0
        hinterland_capacity = 0

        for inbound_vehicle_type in inbound_to_outbound_flow.keys():
            for outbound_vehicle_type, capacity in inbound_to_outbound_flow[inbound_vehicle_type].items():
                if (inbound_vehicle_type in self.vessels_considered_for_transshipment
                        and outbound_vehicle_type in self.vessels_considered_for_transshipment):
                    transshipment_capacity += capacity
                else:
                    hinterland_capacity += capacity

        return TransshipmentAndHinterlandSplit(
            transshipment_capacity=transshipment_capacity,
            hinterland_capacity=hinterland_capacity
        )

    @DataSummariesCache.cache_result
    def get_modal_split_for_hinterland(
            self,
            inbound: bool,
            outbound: bool
    ) -> HinterlandModalSplit:
        """
        Args:
            inbound: Whether to account for inbound journeys
            outbound: Whether to account for outbound journeys

        Returns:
             The estimated modal split for the hinterland
        """
        assert inbound or outbound, "Checking for a modal split if neither inbound nor outbound journeys are " \
                                    "considered is not reasonable."

        inbound_to_outbound_flow = self.container_flow_by_vehicle_type_preview.get_inbound_to_outbound_flow()

        transported_capacity: Dict[ModeOfTransport, float] = {
            ModeOfTransport.truck: 0,
            ModeOfTransport.train: 0,
            ModeOfTransport.barge: 0
        }

        if (not inbound) and (not outbound):
            raise ValueError("The modal split must cover either the inbound traffic, the outbound traffic, or both")

        for inbound_vehicle_type, inbound_capacity in inbound_to_outbound_flow.items():
            for outbound_vehicle_type, capacity in inbound_to_outbound_flow[inbound_vehicle_type].items():
                if inbound and inbound_vehicle_type in self.vehicles_considered_for_hinterland:
                    transported_capacity[inbound_vehicle_type] += capacity
                if outbound and outbound_vehicle_type in self.vehicles_considered_for_hinterland:
                    transported_capacity[outbound_vehicle_type] += capacity

        return HinterlandModalSplit(
            train_capacity=transported_capacity[ModeOfTransport.train],
            barge_capacity=transported_capacity[ModeOfTransport.barge],
            truck_capacity=transported_capacity[ModeOfTransport.truck]
        )
