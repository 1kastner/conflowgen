import datetime
import logging
import typing

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.application.repositories.container_flow_generation_properties_repository import \
    ContainerFlowGenerationPropertiesRepository
from conflowgen.flow_generator.container_flow_generation_service import \
    ContainerFlowGenerationService


class ContainerFlowGenerationManager:
    """
    This manager provides the interface to set the properties (i.e., not the distributions that are handled elsewhere)
    and trigger the synthetic container flow generation.
    If not provided, `default values <notebooks/input_distributions.ipynb#Default-Values>`_ are used automatically.
    """

    def __init__(self):
        self.container_flow_generation_service = ContainerFlowGenerationService()
        self.container_flow_generation_properties_repository = ContainerFlowGenerationPropertiesRepository()
        self.logger = logging.getLogger("conflowgen")

    def set_properties(
            self,
            start_date: datetime.date,
            end_date: datetime.date,
            name: typing.Optional[str] = None,
            transportation_buffer: typing.Optional[float] = None
    ) -> None:
        """
        Args:
            start_date: The earliest day any scheduled vehicle arrives. Trucks that drop off containers might arrive
                earlier though.
            end_date: The latest day any scheduled vehicle arrives. Trucks that pick up containers might arrive later
                though.
            name: The name of the generated synthetic container flow which helps to distinguish different scenarios.
            transportation_buffer: Determines how many percent more of the inbound journey capacity is used at most to
                transport containers on the outbound journey.
        """
        properties = self.container_flow_generation_properties_repository.get_container_flow_generation_properties()

        if name is not None:
            properties.name = name

        properties.start_date = start_date
        properties.end_date = end_date

        if transportation_buffer is not None:
            properties.transportation_buffer = transportation_buffer

        self.container_flow_generation_properties_repository.set_container_flow_generation_properties(
            properties
        )
        DataSummariesCache.reset_cache()

    def get_properties(self) -> typing.Dict[str, typing.Union[str, datetime.date, float, int]]:
        """
        Returns:
            The properties of the container flow.
        """
        properties = self.container_flow_generation_properties_repository.get_container_flow_generation_properties()
        return {
            'name': properties.name,
            'start_date': properties.start_date,
            'end_date': properties.end_date,
            'transportation_buffer': properties.transportation_buffer,
        }

    def container_flow_data_exists(self) -> bool:
        """
        When an existing database is opened, pre-existing container flow data could already be stored inside.
        Invoking :meth:`.ContainerFlowGenerationManager.generate` again would reset that stored data.
        You might want to skip that set and just re-use the data already stored in the database.

        Returns:
            Whether container flow data exists in the database.
        """
        return self.container_flow_generation_service.container_flow_data_exists()

    def generate(self, overwrite: bool = True) -> None:
        """
        Generate the synthetic container flow according to all the information stored in the database so far.
        This triggers a multistep procedure of generating vehicles and the containers which are delivered or picked up
        by the vehicles.
        This process is described in the Section
        `Data Generation Process <background.rst#data-generation-process>`_.
        The invocation of this method overwrites any already existent data in the database.
        Consider checking for
        :meth:`.ContainerFlowGenerationManager.container_flow_data_exists`
        and skip invoking this method.

        Arguments:
            overwrite:
                Whether to overwrite existing container flow data.
                Defaults to :py:obj:`True`.
        """
        if not overwrite and self.container_flow_data_exists():
            self.logger.debug("Data already exists and it was not asked to overwrite existent data, skip this.")
            return
        self.container_flow_generation_service.generate()
