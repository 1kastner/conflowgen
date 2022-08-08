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
            considered_time_window_in_hours: int,
            minimum_dwell_time_in_hours: int,
            context: str = ""
    ):
        self.considered_time_window_in_hours = considered_time_window_in_hours
        self.minimum_dwell_time_in_hours = minimum_dwell_time_in_hours
        self.context = context

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

    @property
    def maximum_dwell_time_in_hours(self):
        return self.minimum_dwell_time_in_hours + self.considered_time_window_in_hours

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

    def get_distribution_slice(self, start_as_datetime: datetime.datetime) -> Dict[int, float]:

        # Convert the datetime into the week hour. Hour 36 corresponds to a Tuesday at 12:00 noon.
        start_hour = self._get_hour_of_the_week_from_datetime(start_as_datetime)

        # Calculate the week hour of when to end the distribution slice
        end_hour = start_hour + self.considered_time_window_in_hours

        assert 0 <= start_hour <= self.HOURS_IN_WEEK, "Start hour must be in first week"
        assert start_hour < end_hour, "Start hour must be before end hour"

        if end_hour - start_hour < self.minimum_dwell_time_in_hours:
            raise InvalidDistributionSliceException(
                f"start_hour: {start_hour} and end_hour: {end_hour} are too close given "
                f"minimum_dwell_time_in_hours: {self.minimum_dwell_time_in_hours}"
            )

        # get the distribution slice starting from start_hour and ending with end_hour
        not_normalized_distribution_slice = [
            ((hour_of_the_week - start_hour), fraction)
            for (hour_of_the_week, fraction) in self.hour_of_the_week_fraction_pairs
            if start_hour <= hour_of_the_week <= end_hour
        ]

        total_fraction_sum = sum((fraction for _, fraction in not_normalized_distribution_slice))
        distribution_slice = {
            hour_after_start: (hour_fraction / total_fraction_sum)
            for (hour_after_start, hour_fraction) in not_normalized_distribution_slice
        }
        return distribution_slice

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: "
            f"min={self.minimum_dwell_time_in_hours:.1f}h, "
            f"max={self.maximum_dwell_time_in_hours:.1f}h={self.maximum_dwell_time_in_hours / 24:.1f}d, "
            f"context='{self.context}'"
            f">"
        )
