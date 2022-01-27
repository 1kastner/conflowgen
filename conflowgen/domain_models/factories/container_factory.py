from __future__ import annotations

import math
import random
from typing import Dict, MutableSequence, Sequence

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_repositories.container_length_distribution_repository import \
    ContainerLengthDistributionRepository
from conflowgen.domain_models.distribution_repositories.container_weight_distribution_repository import \
    ContainerWeightDistributionRepository
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.distribution_repositories.container_storage_requirement_distribution_repository import \
    ContainerStorageRequirementDistributionRepository
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.repositories.large_scheduled_vehicle_repository import LargeScheduledVehicleRepository
from conflowgen.domain_models.vehicle import AbstractLargeScheduledVehicle, LargeScheduledVehicle
from conflowgen.tools.distribution_approximator import DistributionApproximator


class ContainerFactory:
    """
    Creates containers according to the distributions which are either hard-coded or stored in the database.
    """

    ignored_capacity = ContainerLength.get_factor(ContainerLength.other)

    def __init__(self):
        self.mode_of_transportation_distribution = None
        self.container_length_distribution = None
        self.container_weight_distribution = None
        self.storage_requirement_distribution = None
        self.large_scheduled_vehicle_repository = LargeScheduledVehicleRepository()

    def reload_distributions(self):
        """The user might change the distributions at any time, so reload them at a meaningful point of time!"""
        self.mode_of_transportation_distribution = ModeOfTransportDistributionRepository.get_distribution()
        self.container_length_distribution = ContainerLengthDistributionRepository.get_distribution()
        self.container_weight_distribution = ContainerWeightDistributionRepository.get_distribution()
        self.storage_requirement_distribution = ContainerStorageRequirementDistributionRepository.get_distribution()

    def create_containers_for_large_scheduled_vehicle(
            self,
            large_scheduled_vehicle_as_subtype: AbstractLargeScheduledVehicle
    ) -> Sequence[Container]:
        """
        Creates all containers a large vehicle delivers to a terminal.
        """

        self.large_scheduled_vehicle_repository.reset_cache()

        created_containers: MutableSequence[Container] = []

        delivered_by = large_scheduled_vehicle_as_subtype.get_mode_of_transport()

        large_scheduled_vehicle: LargeScheduledVehicle = large_scheduled_vehicle_as_subtype.large_scheduled_vehicle

        free_capacity_in_teu = self.large_scheduled_vehicle_repository.get_free_capacity_for_inbound_journey(
            large_scheduled_vehicle_as_subtype
        )

        # this is based on the assumption that the smallest container is a 20' container
        maximum_number_of_containers = int(math.ceil(free_capacity_in_teu))
        self._load_distribution_approximators(maximum_number_of_containers, delivered_by)

        while (self.large_scheduled_vehicle_repository.get_free_capacity_for_inbound_journey(
                large_scheduled_vehicle_as_subtype
        ) > self.ignored_capacity):
            container = self._create_single_container_for_large_scheduled_vehicle(
                delivered_by_large_scheduled_vehicle_as_subtype=large_scheduled_vehicle_as_subtype
            )
            created_containers.append(container)
            is_exhausted = self.large_scheduled_vehicle_repository.block_capacity_for_inbound_journey(
                vehicle=large_scheduled_vehicle_as_subtype,
                container=container
            )
            if is_exhausted and not large_scheduled_vehicle.capacity_exhausted_while_determining_onward_transportation:
                large_scheduled_vehicle.capacity_exhausted_while_determining_onward_transportation = True
                large_scheduled_vehicle.save()

        free_capacity = self.large_scheduled_vehicle_repository.get_free_capacity_for_inbound_journey(
            large_scheduled_vehicle_as_subtype
        )
        assert free_capacity >= 0, \
               f"The vehicle {large_scheduled_vehicle_as_subtype.large_scheduled_vehicle.vehicle_name} does not " \
               f"have sufficient free capacity (in TEU): {free_capacity}."

        return created_containers

    def _load_distribution_approximators(
            self,
            number_of_containers: int,
            delivered_by: ModeOfTransport
    ) -> None:
        self.distribution_approximators: Dict[str, DistributionApproximator] = {
            "length": DistributionApproximator.from_distribution(
                self.container_length_distribution,
                number_of_containers),
            "picked_up_by": DistributionApproximator.from_distribution(
                self.mode_of_transportation_distribution[delivered_by],
                number_of_containers)
        }

    @staticmethod
    def _update_weight_according_to_container_type(
            storage_requirement: StorageRequirement,
            length: ContainerLength
    ) -> int | None:
        weight = None
        # TODO: restructure code so that this translation table can be determined by the user in the
        # ContainerWeightDistributionManager
        if storage_requirement == StorageRequirement.empty:
            if length == ContainerLength.twenty_feet:
                weight = 2
            else:
                weight = 4
        return weight

    def _create_single_container_for_large_scheduled_vehicle(
            self,
            delivered_by_large_scheduled_vehicle_as_subtype: AbstractLargeScheduledVehicle
    ) -> Container:
        """Creates a generic single container delivered by a specific large scheduled vehicle"""

        delivered_by = delivered_by_large_scheduled_vehicle_as_subtype.get_mode_of_transport()
        delivered_by_large_scheduled_vehicle = \
            delivered_by_large_scheduled_vehicle_as_subtype.large_scheduled_vehicle

        length = self.distribution_approximators["length"].sample()
        weight = random.choices(
            population=list(self.container_weight_distribution[length].keys()),
            weights=list(self.container_weight_distribution[length].values()),
            k=1
        )[0]
        picked_up_by = self.distribution_approximators["picked_up_by"].sample()
        storage_requirement = random.choices(
            population=list(self.storage_requirement_distribution[length].keys()),
            weights=list(self.storage_requirement_distribution[length].values()),
            k=1
        )[0]
        new_weight = self._update_weight_according_to_container_type(
            storage_requirement=storage_requirement,
            length=length
        )
        weight = new_weight if new_weight is not None else weight
        container = Container.create(
            weight=weight,
            length=length,
            storage_requirement=storage_requirement,
            delivered_by=delivered_by,
            picked_up_by=picked_up_by,  # this field is adjusted as needed
            picked_up_by_initial=picked_up_by,  # this field is later never touched again
            delivered_by_large_scheduled_vehicle=delivered_by_large_scheduled_vehicle,
            delivered_by_truck=None
        )
        container.save()
        return container

    def create_container_for_delivering_truck(
            self,
            picked_up_by_large_scheduled_vehicle_subtype: AbstractLargeScheduledVehicle
    ) -> Container:
        """Creates a generic single container delivered by a truck"""

        picked_up_by_large_scheduled_vehicle = picked_up_by_large_scheduled_vehicle_subtype.large_scheduled_vehicle
        picked_up_by = picked_up_by_large_scheduled_vehicle_subtype.get_mode_of_transport()

        self._load_distribution_approximators(
            number_of_containers=1,
            delivered_by=ModeOfTransport.truck
        )

        length = self.distribution_approximators["length"].sample()
        weight = random.choices(
            population=list(self.container_weight_distribution[length].keys()),
            weights=list(self.container_weight_distribution[length].values()),
            k=1
        )[0]
        storage_requirement = random.choices(
            population=list(self.storage_requirement_distribution[length].keys()),
            weights=list(self.storage_requirement_distribution[length].values()),
            k=1
        )[0]
        new_weight = self._update_weight_according_to_container_type(
            storage_requirement=storage_requirement,
            length=length
        )
        weight = new_weight if new_weight is not None else weight
        container = Container.create(
            weight=weight,
            length=length,
            storage_requirement=storage_requirement,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=picked_up_by,  # This field is used for the actual pickup
            picked_up_by_initial=picked_up_by,  # This field is only set here and is used for later evaluation
            delivered_by_large_scheduled_vehicle=None,
            delivered_by_truck=None,  # Information is missing yet, inserted later
            picked_up_by_large_scheduled_vehicle=picked_up_by_large_scheduled_vehicle,
            picked_up_by_truck=None  # This container is not picked up by a truck
        )
        container.save()
        return container
