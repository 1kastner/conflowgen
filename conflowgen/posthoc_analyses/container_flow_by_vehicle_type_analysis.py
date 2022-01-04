from __future__ import annotations
from typing import Dict

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.posthoc_analyses.abstract_posthoc_analysis import AbstractPostHocAnalysis


class ContainerFlowByVehicleTypeAnalysis(AbstractPostHocAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.ContainerFlowByVehicleTypeAnalysisReport`.
    """
    @staticmethod
    def get_inbound_to_outbound_flow() -> Dict[ModeOfTransport, Dict[ModeOfTransport, float]]:
        """This is the overview of the generated inbound to outbound container flow."""
        inbound_to_outbound_flow: Dict[ModeOfTransport, Dict[ModeOfTransport, float]] = {
            vehicle_type_inbound:
                {
                    vehicle_type_outbound: 0
                    for vehicle_type_outbound in ModeOfTransport
                }
            for vehicle_type_inbound in ModeOfTransport
        }

        container: Container
        for container in Container.select():
            inbound_vehicle_type = container.delivered_by
            outbound_vehicle_type = container.picked_up_by
            teu_factor_of_container: float = ContainerLength.get_factor(container.length)
            inbound_to_outbound_flow[inbound_vehicle_type][outbound_vehicle_type] += teu_factor_of_container

        return inbound_to_outbound_flow
