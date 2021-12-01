import abc

from conflowgen.application_models.repositories.container_flow_generation_properties_repository import \
    ContainerFlowGenerationPropertiesRepository
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class AbstractPosthocAnalysisReport(abc.ABC):

    order_of_vehicle_types_in_report = [
        ModeOfTransport.deep_sea_vessel,
        ModeOfTransport.feeder,
        ModeOfTransport.barge,
        ModeOfTransport.train,
        ModeOfTransport.truck
    ]

    def __init__(self):
        self.container_flow_generation_properties_repository = ContainerFlowGenerationPropertiesRepository()
        self.transportation_buffer = None
        self.reload()

    def reload(self):
        properties = self.container_flow_generation_properties_repository.get_container_flow_generation_properties()
        self.transportation_buffer = properties.transportation_buffer
        assert -1 < self.transportation_buffer

    @abc.abstractmethod
    def get_report_as_text(self) -> str:
        """
        The report as a text is represented as a table suitable for logging. It uses a human-readable formatting style.

        Returns: The report in text format (possibly spanning over several lines).
        """
        return ""

    def get_report_as_graph(self) -> object:
        raise NotImplementedError("No graph representation of this report has yet been defined.")
