from conflowgen.application_models.container_flow_generation_properties import ContainerFlowGenerationProperties


class DuplicatedContainerFlowGenerationPropertiesEntryException(Exception):
    pass


class InvalidTimeRangeException(Exception):
    pass


class MinimumNotStrictlySmallerThanMaximumException(Exception):
    pass


class ContainerFlowGenerationPropertiesRepository:

    @staticmethod
    def _verify(properties) -> None:
        if properties.end_date < properties.start_date:
            raise InvalidTimeRangeException(
                f"start date '{properties.start_date}' is later than end date '{properties.end_date}'"
            )
        if (properties.minimum_dwell_time_of_import_containers_in_hours
                >= properties.maximum_dwell_time_of_import_containers_in_hours):
            raise MinimumNotStrictlySmallerThanMaximumException(
                f"{properties.minimum_dwell_time_of_import_containers_in_hours} "
                f">= {properties.maximum_dwell_time_of_import_containers_in_hours}"
            )
        if (properties.minimum_dwell_time_of_export_containers_in_hours
                >= properties.maximum_dwell_time_of_export_containers_in_hours):
            raise MinimumNotStrictlySmallerThanMaximumException(
                f"{properties.minimum_dwell_time_of_export_containers_in_hours} "
                f">= {properties.maximum_dwell_time_of_export_containers_in_hours}"
            )

    @staticmethod
    def get_container_flow_generation_properties() -> ContainerFlowGenerationProperties:
        all_properties = ContainerFlowGenerationProperties.select().execute()  # pylint: disable=E1120
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
        cls._verify(properties)
        properties.save()
        number_properties_entries = ContainerFlowGenerationProperties().select().count()  # pylint: disable=E1120
        if number_properties_entries > 1:
            raise DuplicatedContainerFlowGenerationPropertiesEntryException(
                f"Number of updated rows were {number_properties_entries} but expected only one entry"
            )
