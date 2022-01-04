from __future__ import annotations
import datetime
from typing import List, Tuple, Union, Dict


class InvalidDistributionSliceException(Exception):
    pass


class WeeklyDistribution:

    HOURS_IN_WEEK = 168

    def __init__(
            self,
            hour_fraction_pairs: List[Union[Tuple[int, float], Tuple[int, int]]],
            considered_time_window_in_hours: float,
            minimum_dwell_time_in_hours: float
    ):
        self.considered_time_window_in_hours = considered_time_window_in_hours
        self.minimum_dwell_time_in_hours = minimum_dwell_time_in_hours
        self.hour_of_the_week_fraction_pairs = []
        number_of_weeks_to_consider = 2 + int(considered_time_window_in_hours / 24 / 7)
        for week in range(number_of_weeks_to_consider):
            for hour, fraction in hour_fraction_pairs:
                hour_relative_to_first_monday = (week * self.HOURS_IN_WEEK) + hour
                self.hour_of_the_week_fraction_pairs.append(
                    (
                        hour_relative_to_first_monday,
                        fraction
                    )
                )
        self.time_window_length_in_hours = (
                self.hour_of_the_week_fraction_pairs[1][0]
                - self.hour_of_the_week_fraction_pairs[0][0]
        )

    @classmethod
    def _get_hour_of_the_week_from_datetime(cls, point_in_time: datetime.datetime) -> int:
        # Get the monday at midnight before the given point in time
        monday = (point_in_time - datetime.timedelta(days=point_in_time.weekday())).date()
        assert monday.weekday() == 0, "This is actually not a Monday"
        monday_at_midnight = datetime.datetime.combine(monday, datetime.time())
        # Get the hours since monday midnight
        time_since_monday_in_hours = (point_in_time - monday_at_midnight).total_seconds() / 3600
        assert 0 <= time_since_monday_in_hours <= cls.HOURS_IN_WEEK, \
            f"Time since Monday in hours: {time_since_monday_in_hours}"
        completed_hours_since_monday = int(time_since_monday_in_hours)
        assert 0 <= completed_hours_since_monday <= cls.HOURS_IN_WEEK, \
            f"Time since Monday in completed hours: {completed_hours_since_monday}"
        return completed_hours_since_monday

    def get_distribution_slice(self, _datetime: datetime.datetime) -> Dict[int, float]:
        start_hour = self._get_hour_of_the_week_from_datetime(_datetime)
        end_hour = start_hour + self.considered_time_window_in_hours
        assert 0 <= start_hour <= self.HOURS_IN_WEEK, "Start hour must be in first week"
        assert start_hour < end_hour, "Start hour must be before end hour"

        if end_hour - start_hour < self.minimum_dwell_time_in_hours:
            raise InvalidDistributionSliceException(
                f"start_hour: {start_hour} and end_hour: {end_hour} are too close given "
                f"minimum_dwell_time_in_hours: {self.minimum_dwell_time_in_hours}"
            )

        not_normalized_distribution_slice = [
            ((hour_of_the_week - start_hour), fraction)
            for (hour_of_the_week, fraction) in self.hour_of_the_week_fraction_pairs
            if start_hour <= hour_of_the_week <= end_hour
        ]

        # Fix first entry because of minimum dwell time
        need_to_modify_first_entry = False
        previous_fraction = None
        for i, (hour_after_start, fraction) in enumerate(not_normalized_distribution_slice):
            if hour_after_start > self.minimum_dwell_time_in_hours:
                if need_to_modify_first_entry:
                    del not_normalized_distribution_slice[:i]
                    not_normalized_distribution_slice.insert(
                        0,
                        (self.minimum_dwell_time_in_hours, previous_fraction)
                    )
                break
            need_to_modify_first_entry = True
            previous_fraction = fraction

        # If first entry fix failed, this is the last rescue
        if not_normalized_distribution_slice[-1][0] <= self.minimum_dwell_time_in_hours:
            not_normalized_distribution_slice = [(self.minimum_dwell_time_in_hours, 1)]

        total_fraction_sum = sum([fraction for _, fraction in not_normalized_distribution_slice])
        distribution_slice = {
            hour_after_start: (hour_fraction / total_fraction_sum)
            for (hour_after_start, hour_fraction) in not_normalized_distribution_slice
        }
        return distribution_slice
