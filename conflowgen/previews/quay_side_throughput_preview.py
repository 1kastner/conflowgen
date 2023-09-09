import typing
from abc import ABC
from datetime import datetime

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.domain_models.distribution_repositories.container_length_distribution_repository import \
    ContainerLengthDistributionRepository
from conflowgen.previews.container_flow_by_vehicle_type_preview import ContainerFlowByVehicleTypePreview
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_validators import validate_distribution_with_one_dependent_variable
from conflowgen.previews.abstract_preview import AbstractPreview
from conflowgen.descriptive_datatypes import InboundAndOutboundContainerVolume, ContainerVolume


class QuaySideThroughputPreview(AbstractPreview, ABC):
    """
    This preview calculates the quayside throughput based on the schedules.

    The preview returns a data structure that can be used for generating reports (e.g., in text or as a figure). The
    preview is intended to provide an estimate of the quayside throughput for the given inputs.
    """

    QUAY_SIDE_VEHICLES = {
        ModeOfTransport.deep_sea_vessel,
        ModeOfTransport.feeder,
        # barges are counted as hinterland here
    }

    def __init__(self, start_date: datetime.date, end_date: datetime.date, transportation_buffer: float):
        super().__init__(start_date, end_date, transportation_buffer)
        self.container_flow_by_vehicle_type = (
            ContainerFlowByVehicleTypePreview(
                self.start_date,
                self.end_date,
                self.transportation_buffer,
            )
        )

    @DataSummariesCache.cache_result
    def hypothesize_with_mode_of_transport_distribution(
            self,
            mode_of_transport_distribution: typing.Dict[ModeOfTransport, typing.Dict[ModeOfTransport, float]]
    ):
        validate_distribution_with_one_dependent_variable(
            mode_of_transport_distribution, ModeOfTransport, ModeOfTransport, values_are_frequencies=True
        )
        self.container_flow_by_vehicle_type.hypothesize_with_mode_of_transport_distribution(
            mode_of_transport_distribution
        )

    @DataSummariesCache.cache_result
    def get_quay_side_throughput(self) -> InboundAndOutboundContainerVolume:
        inbound_to_outbound_flow = self.container_flow_by_vehicle_type.get_inbound_to_outbound_flow()

        quayside_inbound_container_volume_in_teu: int = 0
        quayside_outbound_container_volume_in_teu: int = 0

        inbound_vehicle_type: ModeOfTransport
        outbound_vehicle_type: ModeOfTransport
        for inbound_vehicle_type, to_outbound_flow in inbound_to_outbound_flow.items():
            for outbound_vehicle_type, container_volume in to_outbound_flow.items():
                if inbound_vehicle_type in self.QUAY_SIDE_VEHICLES:
                    quayside_inbound_container_volume_in_teu += container_volume
                if outbound_vehicle_type in self.QUAY_SIDE_VEHICLES:
                    quayside_outbound_container_volume_in_teu += container_volume

        teu_factor = ContainerLengthDistributionRepository().get_teu_factor()

        result = InboundAndOutboundContainerVolume(
            inbound=ContainerVolume(
                teu=quayside_inbound_container_volume_in_teu,
                containers=int(quayside_inbound_container_volume_in_teu / teu_factor)
            ),
            outbound=ContainerVolume(
                teu=quayside_outbound_container_volume_in_teu,
                containers=int(quayside_outbound_container_volume_in_teu / teu_factor)
            )
        )

        return result
