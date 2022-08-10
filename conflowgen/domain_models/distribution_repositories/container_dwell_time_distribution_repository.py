from __future__ import annotations

from typing import Dict, Any, Type

from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistribution
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_validators import validate_distribution_with_two_dependent_variables
from conflowgen.tools.continuous_distribution import ContinuousDistribution


class ContainerDwellTimeDistributionRepository:

    @staticmethod
    def _get_distribution_entry(
            delivered_by: ModeOfTransport,
            picked_up_by: ModeOfTransport,
            storage_requirement: StorageRequirement
    ) -> Type[ContinuousDistribution]:
        """Loads the distribution for the given transport direction and container type."""

        entry: ContainerDwellTimeDistribution = ContainerDwellTimeDistribution.get(
            (ContainerDwellTimeDistribution.delivered_by == delivered_by)
            & (ContainerDwellTimeDistribution.picked_up_by == picked_up_by)
            & (ContainerDwellTimeDistribution.storage_requirement == storage_requirement)
        )

        distribution_class: Type[ContinuousDistribution] | None = \
            ContinuousDistribution.distribution_types.get(entry.distribution_name, None)
        if distribution_class is None:
            raise NotImplementedError(f"No implementation found for '{entry.distribution_name}'")
        return distribution_class.from_database_entry(entry)

    @classmethod
    def get_distributions(
            cls
    ) -> Dict[ModeOfTransport, Dict[ModeOfTransport, Dict[StorageRequirement, ContinuousDistribution]]]:
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
            Dict[ModeOfTransport, Dict[ModeOfTransport, Dict[
                StorageRequirement, Dict[str, Any] | ContinuousDistribution]]]
    ) -> None:
        validate_distribution_with_two_dependent_variables(
            distributions, ModeOfTransport, ModeOfTransport, StorageRequirement, values_are_frequencies=False
        )
        ContainerDwellTimeDistribution.delete().execute()
        for delivered_by, picked_up_by_distribution in distributions.items():
            for picked_up_by, storage_requirement_distribution in picked_up_by_distribution.items():
                for storage_requirement, container_dwell_time_distribution in storage_requirement_distribution.items():
                    if isinstance(container_dwell_time_distribution, ContinuousDistribution):
                        distribution_properties = container_dwell_time_distribution.to_dict()
                    elif isinstance(container_dwell_time_distribution, dict):
                        distribution_properties = container_dwell_time_distribution
                    else:
                        raise Exception(
                            f"The container dwell time distribution representation "
                            f"'{container_dwell_time_distribution}' could not be casted."
                        )
                    ContainerDwellTimeDistribution.create(
                        delivered_by=delivered_by,
                        picked_up_by=picked_up_by,
                        storage_requirement=storage_requirement,
                        **distribution_properties
                    )
