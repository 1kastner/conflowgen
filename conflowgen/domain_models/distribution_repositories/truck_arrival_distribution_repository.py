import math
from typing import Dict

from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution


class TruckArrivalDistributionTableWithDuplicatesException(Exception):
    pass


class TruckArrivalFractionsUnequalOneException(Exception):
    pass


class InvalidHourInTheWeekValue(Exception):
    pass


class TruckArrivalDistributionRepository:

    @staticmethod
    def _verify_truck_arrival_distribution(truck_arrivals: Dict[int, float]):
        hour_in_the_week_values = truck_arrivals.keys()
        if min(hour_in_the_week_values) < 0:
            raise InvalidHourInTheWeekValue(f"{min(hour_in_the_week_values)} is too small")
        if max(hour_in_the_week_values) > (24 * 7):
            raise InvalidHourInTheWeekValue(f"{max(hour_in_the_week_values)} is too large")
        sum_of_all_fractions = sum(truck_arrivals.values())
        if not math.isclose(1, sum_of_all_fractions):
            raise TruckArrivalFractionsUnequalOneException(sum_of_all_fractions)

    @classmethod
    def get_distribution(cls) -> Dict[int, float]:
        truck_arrival_entry: TruckArrivalDistribution
        return {
            truck_arrival_entry.hour_in_the_week:  # pylint: disable=undefined-variable
            truck_arrival_entry.fraction  # pylint: disable=undefined-variable
            for truck_arrival_entry in TruckArrivalDistribution.select()
        }

    @classmethod
    def set_distribution(cls, truck_arrivals: Dict[int, float]):
        cls._verify_truck_arrival_distribution(truck_arrivals)
        TruckArrivalDistribution.delete().execute()  # pylint: disable=no-value-for-parameter
        for hour_in_the_week, fraction in truck_arrivals.items():
            TruckArrivalDistribution.create(
                fraction=fraction,
                hour_in_the_week=hour_in_the_week
            ).save()
