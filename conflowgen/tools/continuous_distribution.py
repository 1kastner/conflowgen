from __future__ import annotations

import abc
import math
import typing

import numpy as np
import scipy.stats

from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistributionInterface


class ContinuousDistribution(abc.ABC):

    average: float
    variance: float
    minimum: float
    maximum: float

    distribution_types: typing.Dict[str, typing.Type[ContinuousDistribution]] = {}

    def __init__(
            self,
            average: typing.Optional[float],
            minimum: float,
            maximum: float,
            unit: typing.Optional[str] = None,
    ):
        """
        Args:
            average: The expected mean of the distribution.
            minimum: The minimum of the distribution. Smaller values are automatically set to zero.
            maximum: The maximum of the distribution. Larger values are automatically set to zero.
            unit: The unit for the average, minimum, and maximum. It is used for the ``__repr__`` implementation.
        """
        assert minimum < maximum, f"The assertion {minimum} < {maximum} failed."
        if average is not None:
            assert minimum < average < maximum, f"The assertion {minimum} < {average} < {maximum} failed."
        self.average = average
        self.minimum = minimum
        self.maximum = maximum

        self.unit = unit
        self.unit_repr, self.unit_repr_square = "", ""
        if unit:
            self.unit_repr = unit
            self.unit_repr_square = unit + "²"

    # noinspection PyMethodOverriding
    def __init_subclass__(cls, /, short_name: str) -> None:
        """
        Args:
            short_name: Provide a short name for the distribution. This is, e.g., used in the database.
        """
        super().__init_subclass__()
        cls.distribution_types[short_name] = cls
        cls.short_name = short_name

    @abc.abstractmethod
    def _get_probabilities_based_on_distribution(self, xs: typing.Sequence[float]) -> np.ndarray:
        pass

    @classmethod
    @abc.abstractmethod
    def from_database_entry(cls, entry: ContainerDwellTimeDistributionInterface) -> typing.Type[ContinuousDistribution]:
        """
        Args:
            entry: The database entry describing a continuous distribution.

        Returns:
            The loaded distribution instance.
        """
        pass

    def to_dict(self) -> typing.Dict:
        return {
            "distribution_name": self.short_name,
            "average_number_of_hours": self.average,
            "variance": self.variance,
            "maximum_number_of_hours": self.maximum,
            "minimum_number_of_hours": self.minimum
        }

    def get_probabilities(
            self,
            xs: typing.Sequence[float],
            reversed_distribution: bool = False
    ) -> np.ndarray:
        """
        Args:
            xs: Elements that are on the same scale as average, variance, minimum, and maximum
            reversed_distribution: Whether to reverse the probabilities

        Returns:
            The respective probability that element x of xs is drawn from this distribution.
        """
        xs = np.array(xs)
        densities = self._get_probabilities_based_on_distribution(xs)
        densities[xs < self.minimum] = 0
        densities[xs > self.maximum] = 0
        sum_of_all_densities = densities.sum()
        if not np.isnan(sum_of_all_densities) and sum_of_all_densities > 0:
            densities = densities / sum_of_all_densities
            if reversed_distribution:
                densities = np.flip(densities)
        else:
            densities = np.zeros_like(xs)
        return densities


class ClippedLogNormal(ContinuousDistribution, short_name="lognormal"):

    def __init__(
            self,
            average: float,
            variance: float,
            minimum: float,
            maximum: float,
            unit: typing.Optional[str] = None
    ):
        super().__init__(
            average=average,
            minimum=minimum,
            maximum=maximum,
            unit=unit
        )
        self.variance = variance
        self._lognorm = self._get_scipy_lognorm()

    # noinspection PyUnresolvedReferences
    def _get_scipy_lognorm(self) -> scipy.stats.rv_frozen:
        """
        See https://www.johndcook.com/blog/2022/02/24/find-log-normal-parameters/ for reference
        """
        shifted_average = self.average - self.minimum

        sigma2 = math.log(self.variance / shifted_average ** 2 + 1)
        mu = math.log(shifted_average) - sigma2 / 2

        scipy_shape = sigma2 ** 0.5
        scipy_scale = math.exp(mu)

        frozen_lognorm = scipy.stats.lognorm(s=scipy_shape, scale=scipy_scale, loc=self.minimum)

        return frozen_lognorm

    def _get_probabilities_based_on_distribution(self, xs: typing.Sequence[float]) -> np.ndarray:
        return self._lognorm.pdf(xs)

    @classmethod
    def from_database_entry(cls, entry: ContainerDwellTimeDistributionInterface) -> ClippedLogNormal:
        return cls(
            average=entry.average_number_of_hours,
            variance=entry.variance,
            minimum=entry.minimum_number_of_hours,
            maximum=entry.maximum_number_of_hours,
            unit="h"
        )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: "
            f"avg={self.average:.1f}{self.unit_repr}, "
            f"min={self.minimum:.1f}{self.unit_repr}, "
            f"max={self.maximum:.1f}{self.unit_repr}, "
            f"var={self.variance:.1f}{self.unit_repr_square}, "
            f"sd={self.variance ** .5:.1f}{self.unit_repr}"
            f">"
        )


class Uniform(ContinuousDistribution, short_name="uniform"):

    def __init__(
            self,
            minimum: float,
            maximum: float,
            unit: typing.Optional[str] = None
    ):
        super().__init__(
            average=None,
            minimum=minimum,
            maximum=maximum,
            unit=unit
        )

    def _get_probabilities_based_on_distribution(self, xs: typing.Sequence[float]) -> np.ndarray:
        return np.ones_like(xs)

    @classmethod
    def from_database_entry(cls, entry: ContainerDwellTimeDistributionInterface) -> Uniform:
        return cls(
            minimum=entry.minimum_number_of_hours,
            maximum=entry.maximum_number_of_hours,
            unit="h"
        )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: "
            f"min={self.minimum:.1f}{self.unit_repr}, "
            f"max={self.maximum:.1f}{self.unit_repr}"
            f">"
        )


def multiply_discretized_probability_densities(*probabilities: typing.Collection[float]) -> typing.Sequence[float]:
    assert len({len(p) for p in probabilities}) == 1, "All probability vectors have the same length, but found these:" \
                                                      f"'{ [len(p) for p in probabilities] } "
    for i, probability_vector in enumerate(probabilities):
        assert not np.isnan(probability_vector).any(), \
            f"All probability vector should contain only numbers, but found a NaN in vector {i}: {probability_vector}"

    np_probs = [np.array(probs, dtype=np.double) for probs in probabilities]
    multiplied_probabilities = np.multiply(*np_probs)
    sum_of_all_probabilities = multiplied_probabilities.sum()
    if np.isnan(sum_of_all_probabilities).any() or sum_of_all_probabilities == 0:
        normalized_probabilities = np.zeros_like(multiplied_probabilities)
    else:
        normalized_probabilities = multiplied_probabilities / sum_of_all_probabilities
    return normalized_probabilities
