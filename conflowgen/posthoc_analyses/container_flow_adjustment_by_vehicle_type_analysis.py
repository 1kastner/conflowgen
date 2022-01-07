from __future__ import annotations
from typing import Dict

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.posthoc_analyses.abstract_posthoc_analysis import AbstractPostHocAnalysis, \
    ContainersAndTEUContainerFlowPair


class ContainerFlowAdjustmentByVehicleTypeAnalysis(AbstractPostHocAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.ContainerFlowAdjustmentByVehicleTypeAnalysisReport`.
    """

    @staticmethod
    def get_initial_to_adjusted_outbound_flow() -> ContainersAndTEUContainerFlowPair:
        """
        When containers are generated, in order to obey the maximum dwell time, the vehicle type that is used for
        onward transportation might change. The initial outbound vehicle type is the vehicle type that is drawn
        randomly for a container at the time of generation. The adjusted vehicle type is the vehicle type that is drawn
        in case no vehicle of the initial outbound vehicle type is left within the maximum dwell time.

        Returns:
            The data structure describes how often an initial outbound vehicle type had to be adjusted with which other
            vehicle type.
        """

        # Initialize empty data structures
        initial_to_adjusted_outbound_flow_in_containers: Dict[ModeOfTransport, Dict[ModeOfTransport, float]] = {
            vehicle_type_initial:
                {
                    vehicle_type_adjusted: 0
                    for vehicle_type_adjusted in ModeOfTransport
                }
            for vehicle_type_initial in ModeOfTransport
        }
        initial_to_adjusted_outbound_flow_in_teu: Dict[ModeOfTransport, Dict[ModeOfTransport, float]] = {
            vehicle_type_initial:
                {
                    vehicle_type_adjusted: 0
                    for vehicle_type_adjusted in ModeOfTransport
                }
            for vehicle_type_initial in ModeOfTransport
        }

        # Iterate over all containers and count number of containers / used TEU capacity
        container: Container
        for container in Container.select():
            vehicle_type_initial = container.picked_up_by_initial
            vehicle_type_adjusted = container.picked_up_by
            teu_factor_of_container: float = ContainerLength.get_factor(container.length)
            initial_to_adjusted_outbound_flow_in_containers[vehicle_type_initial][vehicle_type_adjusted] += 1
            initial_to_adjusted_outbound_flow_in_teu[vehicle_type_initial][vehicle_type_adjusted] += \
                teu_factor_of_container

        return ContainersAndTEUContainerFlowPair(
            containers=initial_to_adjusted_outbound_flow_in_containers,
            TEU=initial_to_adjusted_outbound_flow_in_teu
        )
