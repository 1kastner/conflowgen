from __future__ import annotations

import abc
import math
from typing import Collection, Sequence, Optional

import numpy as np
import scipy.stats


class TheoreticalDistribution(abc.ABC):

    average: float
    minimum: float
    maximum: float

    def __init__(self, average: float, minimum: float, maximum: float):
        assert minimum < average < maximum, f"The assertion {minimum} < {average} < {maximum} failed."
        self.average = average
        self.minimum = minimum
        self.maximum = maximum

    @abc.abstractmethod
    def _get_probabilities_based_on_distribution(self, xs: np.typing.ArrayLike) -> np.typing.ArrayLike:
        pass

    def get_probabilities(self, xs: np.typing.ArrayLike) -> np.typing.ArrayLike:
        """

        Args:
            xs: Elements that are on the same scale as average, variance, minimum, and maximum

        Returns:
            The respective probability that element x as an element of xs is drawn from this distribution
        """
        xs = np.array(xs)
        densities = self._get_probabilities_based_on_distribution(xs)
        densities[xs <= self.minimum] = 0
        densities[xs >= self.maximum] = 0
        densities = densities / densities.sum()
        return densities


class ClippedLogNormal(TheoreticalDistribution):

    variance: float

    def __init__(self, average: float, variance: float, minimum: float, maximum: float, unit: Optional[str] = None):
        super().__init__(
            average=average,
            minimum=minimum,
            maximum=maximum
        )
        self.variance = variance
        self._lognorm = self._get_scipy_lognorm()

        self.unit_repr, self.unit_repr_square = "", ""
        if unit:
            self.unit_repr = unit
            self.unit_repr_square = unit + "²"

    def _get_scipy_lognorm(self) -> "scipy.stats.rv_frozen":
        # See https://www.johndcook.com/blog/2022/02/24/find-log-normal-parameters/ for reference
        sigma2 = math.log(self.variance / self.average ** 2 + 1)
        mu = math.log(self.average) - sigma2 / 2

        scipy_shape = sigma2 ** 0.5
        scipy_scale = math.exp(mu)

        frozen_lognorm = scipy.stats.lognorm(s=scipy_shape, scale=scipy_scale)

        return frozen_lognorm

    def _get_probabilities_based_on_distribution(self, xs: np.typing.ArrayLike) -> np.typing.ArrayLike:
        return self._lognorm.pdf(xs)

    def __repr__(self):

        return (
            f"<{self.__class__.__name__}: "
            f"avg={self.average:.1f}{self.unit_repr}, "
            f"min={self.minimum:.1f}{self.unit_repr}, "
            f"max={self.maximum:.1f}{self.unit_repr}, "
            f"var={self.variance:.1f}{self.unit_repr_square}>"
        )


def multiply_discretized_probability_densities(*probabilities: Collection[float]) -> Sequence[float]:
    assert len(set([len(p) for p in probabilities])) == 1, "All probability vectors have the same length"
    np_probs = [np.array(probs) for probs in probabilities]
    multiplied_probabilities = np.multiply(*np_probs)
    normalized_probabilities = multiplied_probabilities / multiplied_probabilities.sum()
    assert abs(sum(normalized_probabilities) - 1) < 0.001
    return normalized_probabilities
