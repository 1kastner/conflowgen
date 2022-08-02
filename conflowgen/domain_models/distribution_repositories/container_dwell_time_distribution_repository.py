from typing import Dict, Any

from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistribution
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_validators import validate_distribution_with_two_dependent_variables
from conflowgen.tools.continuous_distribution import ContinuousDistribution, ClippedLogNormal


class ContainerDwellTimeDistributionRepository:

    @staticmethod
    def _get_distribution_entry(
            delivered_by: ModeOfTransport,
            picked_up_by: ModeOfTransport,
            storage_requirement: StorageRequirement
    ) -> ContinuousDistribution:
        """Loads the distribution for the given transport direction and container type."""

        entry: ContainerDwellTimeDistribution = ContainerDwellTimeDistribution.get(
            (ContainerDwellTimeDistribution.delivered_by == delivered_by)
            & (ContainerDwellTimeDistribution.picked_up_by == picked_up_by)
            & (ContainerDwellTimeDistribution.storage_requirement == storage_requirement)
        )
        if entry.distribution_name == "lognormal":
            return ClippedLogNormal(
                average=entry.average_number_of_hours,
                variance=entry.variance,
                minimum=entry.minimum_number_of_hours,
                maximum=entry.maximum_number_of_hours,
                unit="h"
            )
        if entry.distribution_name:
            raise RuntimeError(f"Distribution '{entry.distribution_name}' currently not supported")
        raise RuntimeError(f"Distribution is not valid: {repr(entry.distribution_name)}")

    @classmethod
    def get_distributions(
            cls
    ) -> Dict[ModeOfTransport, Dict[ModeOfTransport, Dict[StorageRequirement, ContinuousDistribution]]]:
        """Loads a distribution for which all fractions are normalized to sum up to 1 for each mode of transportation.
        """
        distributions = {
            mode_of_transport_i: {
                mode_of_transport_j: {
                    storage_requirement: cls._get_distribution_entry(
                        mode_of_transport_i, mode_of_transport_j, storage_requirement
                    )
                    for storage_requirement in StorageRequirement
                }
                for mode_of_transport_j in ModeOfTransport
            }
            for mode_of_transport_i in ModeOfTransport
        }
        return distributions

    @staticmethod
    def set_distributions(
            distributions:
            Dict[ModeOfTransport, Dict[ModeOfTransport, Dict[StorageRequirement, Dict[str, Any]]]]
    ) -> None:
        validate_distribution_with_two_dependent_variables(
            distributions, ModeOfTransport, ModeOfTransport, StorageRequirement, values_are_frequencies=False
        )
        ContainerDwellTimeDistribution.delete().execute()
        for delivered_by, picked_up_by_distribution in distributions.items():
            for picked_up_by, storage_requirement_distribution in picked_up_by_distribution.items():
                for storage_requirement, distribution_properties in storage_requirement_distribution.items():
                    ContainerDwellTimeDistribution.create(
                        delivered_by=delivered_by,
                        picked_up_by=picked_up_by,
                        storage_requirement=storage_requirement,
                        **distribution_properties
                    )
