from __future__ import annotations

import datetime
from typing import NamedTuple, Optional

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.analyses.container_flow_adjustment_by_vehicle_type_analysis import \
    ContainerFlowAdjustmentByVehicleTypeAnalysis


class ContainerFlowAdjustedToVehicleType(NamedTuple):
    """
    During the automatic assignment of containers to outbound journeys, sometimes a container cannot be assigned to the
    previously randomly selected vehicle.
    This happens, e.g., during the ramp-down phase when no vessels arrive and thus transshipment is impossible.
    However, in the end trucks can still be generated to empty the container yard.
    This data structure holds how much volume had to be re-assigned.
    """

    #: The container volume (e.g., counted in boxes or TEU) that was assigned a vehicle of the pre-defined vehicle type
    unchanged: float

    #: The container volume (e.g., counted in boxes or TEU) that was re-assigned to be transported by train
    train: float

    #: The container volume (e.g., counted in boxes or TEU) that was re-assigned to be transported by barge
    barge: float

    #: The container volume (e.g., counted in boxes or TEU) that was re-assigned to be transported by truck
    truck: float

    #: The container volume (e.g., counted in boxes or TEU) that was re-assigned to be transported by deep sea vessel
    deep_sea_vessel: float

    #: The container volume (e.g., counted in boxes or TEU) that was re-assigned to be transported by feeder
    feeder: float


class ContainerFlowAdjustmentByVehicleTypeAnalysisSummary(ContainerFlowAdjustmentByVehicleTypeAnalysis):
    """
    This analysis summary can be run after the synthetic data has been generated.
    The analysis summary returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport`.
    """

    def get_summary(
            self,
            start_time: Optional[datetime.datetime] = None,
            end_time: Optional[datetime.datetime] = None
    ) -> ContainerFlowAdjustedToVehicleType:
        """
        Under certain circumstances (as explained in
        :meth:`.ContainerFlowAdjustmentByVehicleTypeAnalysis.get_initial_to_adjusted_outbound_flow`),
        the containers must change the vehicle they leave the yard with.
        Thus, the question remains how often this has been the case and which vehicles were the primary target for this
        redirected traffic?
        The capacity is expressed in TEU.

        Args:
            start_time: The earliest arriving container that is included. Consider all containers if :obj:`None`.
            end_time: The latest departing container that is included. Consider all containers if :obj:`None`.
        """
        initial_to_adjusted_outbound_flow = self.get_initial_to_adjusted_outbound_flow(
            start_time=start_time,
            end_time=end_time
        )

        initial_to_adjusted_outbound_flow_in_teu = initial_to_adjusted_outbound_flow.teu
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
