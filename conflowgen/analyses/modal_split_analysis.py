from __future__ import annotations

import datetime
import typing

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.analyses.abstract_analysis import AbstractAnalysis
from conflowgen.analyses.container_flow_by_vehicle_type_analysis import ContainerFlowByVehicleTypeAnalysis
from conflowgen.descriptive_datatypes import TransshipmentAndHinterlandSplit
from conflowgen.descriptive_datatypes import HinterlandModalSplit


class ModalSplitAnalysis(AbstractAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.ModalSplitAnalysisReport`.
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

    def __init__(self):
        """"""  # overwrite explanation of transportation_buffer
        super().__init__()
        self.container_flow_by_vehicle_type_analysis = ContainerFlowByVehicleTypeAnalysis()

    @DataSummariesCache.cache_result
    def get_transshipment_and_hinterland_split(
            self,
            start_date: typing.Optional[datetime.datetime] = None,
            end_date: typing.Optional[datetime.datetime] = None
    ) -> TransshipmentAndHinterlandSplit:
        """
        Args:
            start_date:
                Only include containers that arrive after the given start time.
            end_date:
                Only include containers that depart before the given end time.

        Returns:
            The amount of containers in TEU dedicated for or coming from the hinterland versus the amount of containers
            in TEU that are transshipped.
        """
        inbound_to_outbound_flows = self.container_flow_by_vehicle_type_analysis.get_inbound_to_outbound_flow(
            start_date=start_date,
            end_date=end_date
        )
        inbound_to_outbound_flow = inbound_to_outbound_flows.teu

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
    def get_modal_split_for_hinterland_traffic(
            self,
            inbound: bool,
            outbound: bool,
            start_date: typing.Optional[datetime.datetime] = None,
            end_date: typing.Optional[datetime.datetime] = None
    ) -> HinterlandModalSplit:
        """
        Args:
            inbound: Whether to account for inbound journeys
            outbound: Whether to account for outbound journeys
            start_date:
                Only include containers that arrive after the given start time.
            end_date:
                Only include containers that depart before the given end time.

        Returns:
            The modal split for the hinterland in TEU.
        """
        inbound_to_outbound_flows = self.container_flow_by_vehicle_type_analysis.get_inbound_to_outbound_flow(
            start_date=start_date,
            end_date=end_date
        )
        inbound_to_outbound_flow_in_teu = inbound_to_outbound_flows.teu

        transported_capacity: typing.Dict[ModeOfTransport, float] = {
            ModeOfTransport.truck: 0,
            ModeOfTransport.train: 0,
            ModeOfTransport.barge: 0
        }

        if (not inbound) and (not outbound):
            raise ValueError("The modal split must cover either the inbound traffic, the outbound traffic, or both")

        for inbound_vehicle_type, inbound_capacity in inbound_to_outbound_flow_in_teu.items():
            for outbound_vehicle_type, capacity in inbound_to_outbound_flow_in_teu[inbound_vehicle_type].items():
                if inbound and inbound_vehicle_type in self.vehicles_considered_for_hinterland:
                    transported_capacity[inbound_vehicle_type] += capacity
                if outbound and outbound_vehicle_type in self.vehicles_considered_for_hinterland:
                    transported_capacity[outbound_vehicle_type] += capacity

        return HinterlandModalSplit(
            train_capacity=transported_capacity[ModeOfTransport.train],
            barge_capacity=transported_capacity[ModeOfTransport.barge],
            truck_capacity=transported_capacity[ModeOfTransport.truck]
        )
