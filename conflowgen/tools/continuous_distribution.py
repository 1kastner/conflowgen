from __future__ import annotations

import abc
import math
from typing import Collection, Sequence, Optional, Type, Dict

import numpy as np
import scipy.stats

from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistributionInterface


class ContinuousDistribution(abc.ABC):

    average: float
    minimum: float
    maximum: float

    distribution_types: Dict[str, Type[ContinuousDistribution]] = {}

    def __init__(
            self,
            average: float,
            minimum: float,
            maximum: float,
            unit: Optional[str] = None,
            reversed_distribution: bool = False
    ):
        """
        Args:
            average: The expected mean of the distribution.
            minimum: The minimum of the distribution. Smaller values are automatically set to zero.
            maximum: The maximum of the distribution. Larger values are automatically set to zero.
            unit: The unit for the average, minimum, and maximum. It is used for the __repr__ implementation.
            reversed_distribution: Whether the distribution is mirrored at the y-axis.
        """
        assert minimum < average < maximum, f"The assertion {minimum} < {average} < {maximum} failed."
        self.average = average
        self.minimum = minimum
        self.maximum = maximum
        self.reversed_distribution = reversed_distribution

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

    @abc.abstractmethod
    def _get_probabilities_based_on_distribution(self, xs: Sequence[float]) -> np.ndarray:
        pass

    @classmethod
    @abc.abstractmethod
    def from_entry(cls, entry: ContainerDwellTimeDistributionInterface) -> Type[ContinuousDistribution]:
        """
        Args:
            entry: The database entry describing a continuous distribution.

        Returns:
            The loaded distribution instance.
        """
        pass

    def get_probabilities(self, xs: Sequence[float]) -> np.ndarray:
        """
        Args:
            xs: Elements that are on the same scale as average, variance, minimum, and maximum

        Returns:
            The respective probability that element x of xs is drawn from this distribution.
        """
        xs = np.array(xs)
        densities = self._get_probabilities_based_on_distribution(xs)
        densities[xs <= self.minimum] = 0
        densities[xs >= self.maximum] = 0
        densities = densities / densities.sum()
        if self.reversed_distribution:
            densities = np.flip(densities)
        return densities

    @abc.abstractmethod
    def reversed(self) -> ContinuousDistribution:
        """
        Returns:
            A new instance of the distribution that reverses the x-axis.
        """
        pass


class ClippedLogNormal(ContinuousDistribution, short_name="lognormal"):

    variance: float

    def __init__(
            self,
            average: float,
            variance: float,
            minimum: float,
            maximum: float,
            unit: Optional[str] = None,
            reversed_distribution: bool = False
    ):
        super().__init__(
            average=average,
            minimum=minimum,
            maximum=maximum,
            unit=unit,
            reversed_distribution=reversed_distribution
        )
        self.variance = variance
        self._lognorm = self._get_scipy_lognorm()

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

    def _get_probabilities_based_on_distribution(self, xs: Sequence[float]) -> np.ndarray:
        return self._lognorm.pdf(xs)

    @classmethod
    def from_entry(cls, entry: ContainerDwellTimeDistributionInterface) -> ClippedLogNormal:
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
            f"rev={self.reversed_distribution}"
            f">"
        )

    def reversed(self) -> ClippedLogNormal:
        return self.__class__(
            average=self.average,
            minimum=self.minimum,
            maximum=self.maximum,
            variance=self.variance,
            unit=self.unit,
            reversed_distribution=(not self.reversed_distribution)
        )


def multiply_discretized_probability_densities(*probabilities: Collection[float]) -> Sequence[float]:
    assert len({len(p) for p in probabilities}) == 1, "All probability vectors have the same length"
    np_probs = [np.array(probs, dtype=np.double) for probs in probabilities]
    multiplied_probabilities = np.multiply(*np_probs)
    normalized_probabilities = multiplied_probabilities / multiplied_probabilities.sum()
    return normalized_probabilities
