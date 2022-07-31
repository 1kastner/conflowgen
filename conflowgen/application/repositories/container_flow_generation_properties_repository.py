from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties


class DuplicatedContainerFlowGenerationPropertiesEntryException(Exception):
    pass


class InvalidTimeRangeException(Exception):
    pass


class MinimumNotStrictlySmallerThanMaximumException(Exception):
    pass


class ContainerFlowGenerationPropertiesRepository:

    @staticmethod
    def get_container_flow_generation_properties() -> ContainerFlowGenerationProperties:
        all_properties = ContainerFlowGenerationProperties.select().execute()
        number_found_rows = len(all_properties)
        if not (0 <= number_found_rows <= 1):
            raise DuplicatedContainerFlowGenerationPropertiesEntryException(
                f"Number of found rows were {number_found_rows} but expected only one entry"
            )
        if len(all_properties) == 1:
            return all_properties[0]

        return ContainerFlowGenerationProperties.create()

    @classmethod
    def set_container_flow_generation_properties(cls, properties: ContainerFlowGenerationProperties) -> None:
        if properties.start_date >= properties.end_date:
            raise InvalidTimeRangeException()
        properties.save()
        number_properties_entries: int = ContainerFlowGenerationProperties().select().count()
        if number_properties_entries > 1:
            raise DuplicatedContainerFlowGenerationPropertiesEntryException(
                f"Number of updated rows were {number_properties_entries} but expected only one entry"
            )
