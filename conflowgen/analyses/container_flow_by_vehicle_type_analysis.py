from __future__ import annotations
from typing import Dict

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.analyses.abstract_analysis import AbstractAnalysis


class ContainerFlowByVehicleTypeAnalysis(AbstractAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.ContainerFlowByVehicleTypeAnalysisReport`.
    """
    @staticmethod
    def get_inbound_to_outbound_flow(
            in_teu: bool = True
    ) -> Dict[ModeOfTransport, Dict[ModeOfTransport, float]]:
        """
        This is the overview of the generated inbound to outbound container flow by vehicle type.

        Arguments:
            in_teu: Whether to report the container volume in TEU or in boxes.
        """
        inbound_to_outbound_flow: Dict[ModeOfTransport, Dict[ModeOfTransport, float]] = {
            vehicle_type_inbound:
                {
                    vehicle_type_outbound: 0
                    for vehicle_type_outbound in ModeOfTransport
                }
            for vehicle_type_inbound in ModeOfTransport
        }

        unit_steps = 1  # each container counts as one container, this is overwritten later in case of counting TEU

        container: Container
        for container in Container.select():
            inbound_vehicle_type = container.delivered_by
            outbound_vehicle_type = container.picked_up_by
            if in_teu:  # in case it is counted as TEU, the TEU factor replaces the default constant '1'
                unit_steps = ContainerLength.get_factor(container.length)
            inbound_to_outbound_flow[inbound_vehicle_type][outbound_vehicle_type] += unit_steps

        return inbound_to_outbound_flow
