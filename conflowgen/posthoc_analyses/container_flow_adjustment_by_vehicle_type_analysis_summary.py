from __future__ import annotations
from typing import NamedTuple

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.posthoc_analyses.container_flow_adjustment_by_vehicle_type_analysis import \
    ContainerFlowAdjustmentByVehicleTypeAnalysis


class ContainerFlowAdjustedToVehicleType(NamedTuple):
    """
    This is a mapping of all existing vehicle types and the additional entry 'unchanged' to the capacity that has
    been redirected to the respective type.
    """
    unchanged: float
    train: float
    barge: float
    truck: float
    deep_sea_vessel: float
    feeder: float


class ContainerFlowAdjustmentByVehicleTypeAnalysisSummary(ContainerFlowAdjustmentByVehicleTypeAnalysis):
    """
    This analysis summary can be run after the synthetic data has been generated.
    The analysis summary returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport`.
    """

    def get_summary(
            self
    ) -> ContainerFlowAdjustedToVehicleType:
        """
        Under certain circumstances (as explained in
        :meth:`.ContainerFlowAdjustmentByVehicleTypeAnalysis.get_initial_to_adjusted_outbound_flow`),
        the containers must change the vehicle they leave the yard with.
        Thus, the question remains how often this has been the case and which vehicles were the primary target for this
        redirected traffic?
        The capacity is expressed in TEU.
        """
        initial_to_adjusted_outbound_flow = self.get_initial_to_adjusted_outbound_flow()
        initial_to_adjusted_outbound_flow_in_teu = initial_to_adjusted_outbound_flow.TEU
        adjusted_to_dict = {
            "unchanged": 0,
            **{
                str(vehicle_type): 0
                for vehicle_type in ModeOfTransport
            }
        }
        for vehicle_type_initial, distribution in initial_to_adjusted_outbound_flow_in_teu.items():
            for vehicle_type_adjusted, capacity in distribution.items():
                if vehicle_type_initial == vehicle_type_adjusted:
                    adjusted_to_dict["unchanged"] += capacity
                else:
                    adjusted_to_dict[str(vehicle_type_adjusted)] += capacity
        return ContainerFlowAdjustedToVehicleType(**adjusted_to_dict)
