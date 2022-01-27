import datetime
from typing import Union, Dict, Optional

from conflowgen.application.repositories.container_flow_generation_properties_repository import \
    ContainerFlowGenerationPropertiesRepository
from conflowgen.flow_generator.container_flow_generation_service import \
    ContainerFlowGenerationService


class ContainerFlowGenerationManager:
    """
    This manager provides the interface to set the properties (i.e., not the distributions that are handled elsewhere)
    and trigger the synthetic container flow generation.
    If not provided, for many of these values `default values <notebooks/input_distributions.ipynb#Default-Values>`_
    exist.
    """

    def __init__(self):
        self.container_flow_generation_service = ContainerFlowGenerationService()
        self.container_flow_generation_properties_repository = ContainerFlowGenerationPropertiesRepository()

    def set_properties(
            self,
            start_date: datetime.date,
            end_date: datetime.date,
            name: Optional[str] = None,
            minimum_dwell_time_of_import_containers_in_hours: Optional[int] = None,
            maximum_dwell_time_of_import_containers_in_hours: Optional[int] = None,
            minimum_dwell_time_of_export_containers_in_hours: Optional[int] = None,
            maximum_dwell_time_of_export_containers_in_hours: Optional[int] = None,
            minimum_dwell_time_of_transshipment_containers_in_hours: Optional[int] = None,
            maximum_dwell_time_of_transshipment_containers_in_hours: Optional[int] = None,
            transportation_buffer: Optional[float] = None
    ) -> None:
        """
        Args:
            start_date: The earliest day any scheduled vehicle arrives. Trucks that drop off containers might arrive
                earlier though.
            end_date: The latest day any scheduled vehicle arrives. Trucks that pick up containers might arrive later
                though.
            name: The name of the generated synthetic container flow which helps to distinguish different scenarios.
            minimum_dwell_time_of_import_containers_in_hours: No vehicle arrives earlier than this amount of hours
                to pick up an import container that has previously been dropped off.
            maximum_dwell_time_of_import_containers_in_hours: No vehicles arrives later than this amount of hours after
                the previous vehicle which has dropped off the import container has arrived.
            minimum_dwell_time_of_export_containers_in_hours: No vehicle arrives earlier than this amount of hours
                to pick up an export container that has previously been dropped off.
            maximum_dwell_time_of_export_containers_in_hours: No vehicles arrives later than this amount of hours after
                the previous vehicle which has dropped off the export container has arrived.
            minimum_dwell_time_of_transshipment_containers_in_hours: No vehicle arrives earlier than this amount of
                hours to pick up a transshipment container that has previously been dropped off.
            maximum_dwell_time_of_transshipment_containers_in_hours: No vehicles arrives later than this amount of hours
                after the previous vehicle which has dropped off the transshipment container has arrived.
            transportation_buffer: Determines how many percent more of the inbound journey capacity is used at most to
                transport containers on the outbound journey.
        """
        properties = self.container_flow_generation_properties_repository.get_container_flow_generation_properties()

        if name is not None:
            properties.name = name

        properties.start_date = start_date
        properties.end_date = end_date

        if minimum_dwell_time_of_import_containers_in_hours is not None:
            properties.minimum_dwell_time_of_import_containers_in_hours = \
                minimum_dwell_time_of_import_containers_in_hours

        if maximum_dwell_time_of_import_containers_in_hours is not None:
            properties.maximum_dwell_time_of_import_containers_in_hours = \
                maximum_dwell_time_of_import_containers_in_hours

        if minimum_dwell_time_of_export_containers_in_hours is not None:
            properties.minimum_dwell_time_of_export_containers_in_hours = \
                minimum_dwell_time_of_export_containers_in_hours

        if maximum_dwell_time_of_export_containers_in_hours is not None:
            properties.maximum_dwell_time_of_export_containers_in_hours = \
                maximum_dwell_time_of_export_containers_in_hours

        if minimum_dwell_time_of_transshipment_containers_in_hours is not None:
            properties.minimum_dwell_time_of_transshipment_containers_in_hours = \
                minimum_dwell_time_of_transshipment_containers_in_hours

        if maximum_dwell_time_of_transshipment_containers_in_hours is not None:
            properties.maximum_dwell_time_of_transshipment_containers_in_hours = \
                maximum_dwell_time_of_transshipment_containers_in_hours

        if transportation_buffer is not None:
            properties.transportation_buffer = transportation_buffer

        self.container_flow_generation_properties_repository.set_container_flow_generation_properties(
            properties
        )

    def get_properties(self) -> Dict[str, Union[str, datetime.date, float, int]]:
        """
        Returns:
            The properties of the container flow
        """
        properties = self.container_flow_generation_properties_repository.get_container_flow_generation_properties()
        return {
            'name': properties.name,
            'start_date': properties.start_date,
            'end_date': properties.end_date,
            'transportation_buffer': properties.transportation_buffer,
            'minimum_dwell_time_of_import_containers_in_hours':
                properties.minimum_dwell_time_of_import_containers_in_hours,
            'minimum_dwell_time_of_export_containers_in_hours':
                properties.minimum_dwell_time_of_export_containers_in_hours,
            'minimum_dwell_time_of_transshipment_containers_in_hours':
                properties.minimum_dwell_time_of_transshipment_containers_in_hours,
            'maximum_dwell_time_of_import_containers_in_hours':
                properties.maximum_dwell_time_of_import_containers_in_hours,
            'maximum_dwell_time_of_export_containers_in_hours':
                properties.maximum_dwell_time_of_export_containers_in_hours,
            'maximum_dwell_time_of_transshipment_containers_in_hours':
                properties.maximum_dwell_time_of_transshipment_containers_in_hours
        }

    def generate(self) -> None:
        """
        Generate the synthetic container flow according to all the information stored in the database so far.
        This triggers a multistep procedure of generating vehicles and the containers which are delivered or picked up
        by the vehicles.
        More is described in the Section
        `Data Generation Process <background.rst#data-generation-process>`_.
        """
        self.container_flow_generation_service.generate()
